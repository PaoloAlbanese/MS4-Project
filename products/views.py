from django.shortcuts import render, redirect, reverse, get_object_or_404
from .models import Category, Product, Manufactorer, Cart, CartItem, Order, OrderItem, Review, userCartItem, CaroPics
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
import stripe
from django.conf import settings
from django.contrib.auth.models import Group, User
from .forms import SignUpForm, ContactForm, AuthContactForm, AddProductForm, AddBrandForm, AddSideForm, EditProductForm, ProdList
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import path, re_path
import re


def latest(request):
    
    warnUser = request.session.get('warnUser')
    if not warnUser:
      warnUser=""
   
    ids_in_user_cart=[]
    olditems =()
    
    cart_items = ()
    in_cart=[]
    not_in_cart = []
 
    if request.user.is_authenticated:
        if userCartItem:
            cart_items=userCartItem.objects.filter(user=request.user)
            
            for cart_item in cart_items:
                prod_id=cart_item.product.id
                prod=Product.objects.get(id=prod_id)
                if prod.stock > 0:
                    if cart_item.quantity > prod.stock:
                        cart_item.quantity = prod.stock
                        cart_item.save()

                        warnUser +="\n- the quantity for "+ prod.name + " has decreased in your cart due to stock reduction - "
                        request.session['warnUser']= warnUser
                        
                        print ('qui warning se ancora stock',warnUser)
                if prod.stock == 0:
                    cart_item.delete()
                      
                    warnUser +="\n- " + prod.name + "- has run out of stock while it was still placed in the cart - "
                    request.session['warnUser']= warnUser    
                    print ('qui warning se ancora stock',warnUser)
                
                    
        try:
            
            if 'priortolog' in request.session:
                priortolog = request.session['priortolog']
                olditems=CartItem.objects.filter(cart=priortolog)
                
                for i in olditems:
                    print('prior e ',str(i.product), i.quantity)
                for i in cart_items:
                    print('costi usercartese', str(i.product), i.quantity)    

                for cart_item in cart_items:
                    prod_id=cart_item.product.id
                    prod=Product.objects.get(id=prod_id)
                    cumulative_prod_qty=cart_item.quantity
                    for olditem in olditems:
                        if olditem.product.id == cart_item.product.id:
                            cumulative_prod_qty=cart_item.quantity + olditem.quantity
                            if prod.stock > 0:
                                if cumulative_prod_qty <= prod.stock:
                                    cart_item.quantity += olditem.quantity
                                    cart_item.save()
                                else:
                                    cart_item.quantity=prod.stock
                                    warnUser +="\n- the quantity for "+ prod.name + " has been adjusted in your cart due to changed stock availability - "
                                    request.session['warnUser']= warnUser
                            if prod.stock == 0:
                                cart_item.delete()
                                warnUser +="\n- " + prod.name + "- has run out of stock while it was being placed in the cart - "
                                request.session['warnUser']= warnUser    
                                print ('qui warning a causa di cumul 0 stock',warnUser)
                    ids_in_user_cart.append(cart_item.product.id)    
                
                                 

                for olditem in olditems:
                    if olditem.product.id not in ids_in_user_cart:
                        userCartItem.objects.create(product= olditem.product, quantity= olditem.quantity, user=request.user)
                        
                           
                for itema in cart_items:
                    print('i totali per ', str(itema.product), itema.quantity)

                del request.session['priortolog']    

           
        except ObjectDoesNotExist:
            print('non ha userCartese')

            
    else:
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,active=True)
        
        except ObjectDoesNotExist:
            pass

    # print ('qui dovea esser il warning ',warning)   

    callheader = 'Check Out the Latest Arrivals!'
    products = Product.objects.filter(latest=True)
    new_arrivals_page=True
    pageTitle= 'Home'
    thisView = "latest"
    alphaArrow="fa-sort-alpha-up"
    alphaVar = None
    alphaDir ="desc"
    AnnSort=""
    euroL=None
    euroR=None
    euroSortL = ""
    euroSortR = "fa-2x"
    euroDir = "asc"

    if cart_items:
        for i in cart_items:
            in_cart.append(i.product.id)
        

        for product in products:
            if product.id not in in_cart:
                not_in_cart.append(product.id)

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

            if sortkey == 'name':
                if direction == 'asc':
                   AnnSort = "(A to Z)" 
                elif direction == 'desc': 
                    AnnSort = " (Z to A)"
                elif alphaDir == 'asc':
                    AnnSort = "(A to Z)"
                elif alphaDir == 'desc':
                    AnnSort = " (Z to A)"

            elif sortkey == 'price':
                if direction == 'asc':
                    AnnSort = "(Cheapest First)"
                elif direction == 'desc':
                    AnnSort = "(Cheapest Last)"    

        if 'alphaArrow' in request.GET:
            alphaVar = request.GET['alphaArrow']
            if alphaVar == "fa-sort-alpha-up":
                alphaArrow = "fa-sort-alpha-down"
                alphaDir ="asc"
                AnnSort = " (Z to A)"
            else:
                alphaArrow = "fa-sort-alpha-up"
                alphaDir ="desc"
                AnnSort = " (A to Z)"

        if 'euroSortL' in request.GET:
            euroL= request.GET['euroSortL']
            if euroL == "fa-2x":
                euroSortL=""
                euroSortR="fa-2x"
                euroDir="asc"
                AnnSort = "(Cheapest Last)"
            else:
                euroSortL="fa-2x"
                euroSortR=""
                euroDir="desc"
                AnnSort = "(Cheapest First)"       

    this_url = request.path
    referer_view = get_referer_view(request)

    context = {
        'products': products,
        'callheader': callheader,
        'new_arrivals_page':new_arrivals_page,
        'pageTitle': pageTitle,
        'thisView' : thisView,
        'alphaArrow':alphaArrow,
        'alphaDir':alphaDir,
        'euroSortL':euroSortL,
        'euroSortR':euroSortR,
        'euroDir':euroDir,
        'AnnSort':AnnSort,
        'cart_items':cart_items,
        'not_in_cart':not_in_cart,
        'warnUser':warnUser,
        'this_url':this_url,
        'referer_view':referer_view,
    }
    
    if cart_items and not request.user.is_authenticated:
        request.session['priortolog']= cart.id
    
    
    return render(request, 'index.html', context)

def types(request, num):

    cart_items = ()
    in_cart=[]
    not_in_cart = []

    if request.user.is_authenticated:
        try:
            cart_items=userCartItem.objects.filter(user=request.user)
        except ObjectDoesNotExist:
            pass
    else:
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,active=True)
        except ObjectDoesNotExist:
            pass

    callheader = Category.objects.get(id=num)
    products = Product.objects.filter(category=num)
    pageTitle= Category.objects.get(id=num)
    thisView = "types"
    alphaArrow="fa-sort-alpha-up"
    alphaVar = None
    alphaDir ="desc"
    AnnSort=""
    euroL=None
    euroR=None
    euroSortL = ""
    euroSortR = "fa-2x"
    euroDir = "asc"

    if cart_items:
        for i in cart_items:
            in_cart.append(i.product.id)
        

        for product in products:
            if product.id not in in_cart:
                not_in_cart.append(product.id)

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

            if sortkey == 'name':
                if direction == 'asc':
                   AnnSort = "(A to Z)" 
                elif direction == 'desc': 
                    AnnSort = " (Z to A)"
                elif alphaDir == 'asc':
                    AnnSort = "(A to Z)"
                elif alphaDir == 'desc':
                    AnnSort = " (Z to A)"

            elif sortkey == 'price':
                if direction == 'asc':
                    AnnSort = "(Cheapest First)"
                elif direction == 'desc':
                    AnnSort = "(Cheapest Last)"

        if 'alphaArrow' in request.GET:
            alphaVar = request.GET['alphaArrow']
            if alphaVar == "fa-sort-alpha-up":
                alphaArrow = "fa-sort-alpha-down"
                alphaDir ="asc"
                AnnSort = " (Z to A)"
            else:
                alphaArrow = "fa-sort-alpha-up"
                alphaDir ="desc"
                AnnSort = " (A to Z)"

        if 'euroSortL' in request.GET:
            euroL= request.GET['euroSortL']
            if euroL == "fa-2x":
                euroSortL=""
                euroSortR="fa-2x"
                euroDir="asc"
                AnnSort = "(Cheapest Last)"
            else:
                euroSortL="fa-2x"
                euroSortR=""
                euroDir="desc"
                AnnSort = "(Cheapest First)"  


    this_url = request.path
    referer_view = get_referer_view(request)

    context = {
        'products': products,
        'callheader': callheader,
        'pageTitle': pageTitle,
        'thisView' : thisView,
        'num':num,
        'alphaArrow':alphaArrow,
        'alphaDir':alphaDir,
        'euroSortL':euroSortL,
        'euroSortR':euroSortR,
        'euroDir':euroDir,
        'AnnSort':AnnSort,
        'cart_items':cart_items,
        'not_in_cart':not_in_cart,
        'this_url':this_url,
        'referer_view':referer_view,
        
    }

    return render(request, 'index.html', context)


def brand(request, num):
    
    cart_items = ()
    in_cart=[]
    not_in_cart = []

    if request.user.is_authenticated:
        try:
            cart_items=userCartItem.objects.filter(user=request.user)
        except ObjectDoesNotExist:
            pass
    else:
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,active=True)
        except ObjectDoesNotExist:
            pass
    
    callheader = Manufactorer.objects.get(id=num)
    products = Product.objects.filter(manufactorer=num)
    pageTitle = Manufactorer.objects.get(id=num)
    thisView = "brand"
    AnnSort=""
    alphaArrow="fa-sort-alpha-up"
    alphaVar = None
    alphaDir ="desc"
    euroL=None
    euroR=None
    euroSortL = ""
    euroSortR = "fa-2x"
    euroDir = "asc"

    if cart_items:
        for i in cart_items:
            in_cart.append(i.product.id)
        

        for product in products:
            if product.id not in in_cart:
                not_in_cart.append(product.id)
    
    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

            if sortkey == 'name':
                if direction == 'asc':
                   AnnSort = "(A to Z)" 
                elif direction == 'desc': 
                    AnnSort = " (Z to A)"
                elif alphaDir == 'asc':
                    AnnSort = "(A to Z)"
                elif alphaDir == 'desc':
                    AnnSort = " (Z to A)"

            elif sortkey == 'price':
                if direction == 'asc':
                    AnnSort = "(Cheapest First)"
                elif direction == 'desc':
                    AnnSort = "(Cheapest Last)"

        if 'alphaArrow' in request.GET:
            alphaVar = request.GET['alphaArrow']
            if alphaVar == "fa-sort-alpha-up":
                alphaArrow = "fa-sort-alpha-down"
                alphaDir ="asc"
                AnnSort = " (Z to A)"
            else:
                alphaArrow = "fa-sort-alpha-up"
                alphaDir ="desc"
                AnnSort = " (A to Z)"           

        if 'euroSortL' in request.GET:
            euroL= request.GET['euroSortL']
            if euroL == "fa-2x":
                euroSortL=""
                euroSortR="fa-2x"
                euroDir="asc"
                AnnSort = "(Cheapest Last)"
            else:
                euroSortL="fa-2x"
                euroSortR=""
                euroDir="desc"
                AnnSort = "(Cheapest First)"

    this_url = request.path
    referer_view = get_referer_view(request)

    context = {
        'products': products,
        'callheader': callheader,
        'pageTitle': pageTitle,
        'thisView' : thisView,
        'num':num,
        'alphaArrow':alphaArrow,
        'alphaDir':alphaDir,
        'euroSortL':euroSortL,
        'euroSortR':euroSortR,
        'euroDir':euroDir,
        'AnnSort':AnnSort,
        'cart_items':cart_items,
        'not_in_cart':not_in_cart,
        'this_url':this_url,
        'referer_view':referer_view,
    }


    return render(request, 'index.html', context)

def all_products(request):

    cart_items = ()
    in_cart=[]
    not_in_cart = []

    if request.user.is_authenticated:
        try:
            cart_items=userCartItem.objects.filter(user=request.user)
        except ObjectDoesNotExist:
            pass
    else:
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,active=True)
        except ObjectDoesNotExist:
            pass
    
    
    callheader = 'All Products'
    
    products = Product.objects.all()
    query = None
    pageTitle = 'All Products'
    sort = None
    direction=None
    AnnSort=""
    thisView = "products" 
    alphaArrow = None
    alphaVar = None
    alphaDir=None
    euroL=None
    euroR=None
    euroSortL = ""
    euroSortR = "fa-2x"
    euroDir = "asc"

    if cart_items:
        for i in cart_items:
            in_cart.append(i.product.id)
        

        for product in products:
            if product.id not in in_cart:
                not_in_cart.append(product.id)


    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

            if sortkey == 'name':
                if direction == 'asc':
                   AnnSort = "(A to Z)" 
                elif direction == 'desc': 
                    AnnSort = " (Z to A)"
                elif alphaDir == 'asc':
                    AnnSort = "(A to Z)"
                elif alphaDir == 'desc':
                    AnnSort = " (Z to A)"

            elif sortkey == 'price':
                if direction == 'asc':
                    AnnSort = "(Cheapest First)"
                elif direction == 'desc':
                    AnnSort = "(Cheapest Last)"

        if 'alphaArrow' in request.GET:
            alphaVar = request.GET['alphaArrow']
            if alphaVar == "fa-sort-alpha-up":
                alphaArrow = "fa-sort-alpha-down"
                alphaDir ="asc"
                AnnSort = " (Z to A)"
            else:
                alphaArrow = "fa-sort-alpha-up"
                alphaDir ="desc"
                AnnSort = "(A to Z)"            
        else:
            alphaArrow="fa-sort-alpha-up"
            alphaDir ="desc"

        if 'euroSortL' in request.GET:
            euroL= request.GET['euroSortL']
            if euroL == "fa-2x":
                euroSortL=""
                euroSortR="fa-2x"
                euroDir="asc"
                AnnSort = "(Cheapest Last)"
                
            else:
                euroSortL="fa-2x"
                euroSortR=""
                euroDir="desc"
                AnnSort = "(Cheapest First)"


        if 'q' in request.GET:
            query = request.GET['q']

        
            
            callheader ='Search results for: '+ str(query)
            if not query:
                # messages.error(request, "You didn't enter any search criteria!")
                
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            
            products = products.filter(queries)
            if not products:
                callheader = "Your search returned no match"               
            

    else:
        callheader = "You didn't enter any search criteria!"
        products = None

            
    this_url = request.path
    referer_view = get_referer_view(request)            
            
                
    # current_sorting = f'{sort}_{direction}'
    context = {
        'callheader': callheader,
        'products': products,
        'search_term': query,
        'pageTitle': pageTitle,
        # 'current_sorting': current_sorting,
        'thisView' : thisView,
        'alphaArrow':alphaArrow,
        'alphaDir':alphaDir,
        'euroSortL':euroSortL,
        'euroSortR':euroSortR,
        'euroDir':euroDir,
        'AnnSort':AnnSort,
        'cart_items':cart_items,
        'not_in_cart':not_in_cart,
        'this_url':this_url,
        'referer_view':referer_view,
        
    }

    return render(request, 'index.html', context)

def showAll(request):

    cart_items = ()
    in_cart=[]
    not_in_cart = []

    if request.user.is_authenticated:
        try:
            cart_items=userCartItem.objects.filter(user=request.user)
        except ObjectDoesNotExist:
            pass
    else:
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,active=True)
        except ObjectDoesNotExist:
            pass

    
    callheader = 'Showing all Products'
    products = Product.objects.all
    pageTitle= 'all products'
    thisView = "show_all"
    AnnSort=""
    alphaArrow="fa-sort-alpha-up"
    alphaVar = None
    alphaDir ="desc"
    euroL=None
    euroR=None
    euroSortL = ""
    euroSortR = "fa-2x"
    euroDir = "asc"
    prod_id = None
    source=""

    if cart_items:
        for i in cart_items:
            in_cart.append(i.product.id)
        

        for i in Product.objects.all().iterator():
            

            prod_id = i.id
            if prod_id not in in_cart:
                not_in_cart.append(prod_id)


    if request.GET:

        # if 'source' in request.GET:
        #         source= request.GET['source']

        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            
            
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = Product.objects.order_by(sortkey)

            if sortkey == 'name':
                if direction == 'asc':
                   AnnSort = "(A to Z)" 
                elif direction == 'desc': 
                    AnnSort = " (Z to A)"
                elif alphaDir == 'asc':
                    AnnSort = "(A to Z)"
                elif alphaDir == 'desc':
                    AnnSort = " (Z to A)"

            elif sortkey == 'price':
                if direction == 'asc':
                    AnnSort = "(Cheapest First)"
                elif direction == 'desc':
                    AnnSort = "(Cheapest Last)"

        if 'alphaArrow' in request.GET:
            alphaVar = request.GET['alphaArrow']
            if alphaVar == "fa-sort-alpha-up":
                alphaArrow = "fa-sort-alpha-down"
                alphaDir ="asc"
                AnnSort = " (Z to A)"
            else:
                alphaArrow = "fa-sort-alpha-up"
                alphaDir ="desc"
                AnnSort = " (A to Z)"

        if 'euroSortL' in request.GET:
            euroL= request.GET['euroSortL']
            if euroL == "fa-2x":
                euroSortL=""
                euroSortR="fa-2x"
                euroDir="asc"
                AnnSort = "(Cheapest Last)"
            else:
                euroSortL="fa-2x"
                euroSortR=""
                euroDir="desc"
                AnnSort = "(Cheapest First)"  


    
    this_url = request.path
    referer_view = get_referer_view(request)

    context = {
        'products': products,
        'callheader': callheader,
        'pageTitle': pageTitle,
        'thisView':thisView,
        'alphaArrow':alphaArrow,
        'alphaDir':alphaDir,
        'euroSortL':euroSortL,
        'euroSortR':euroSortR,
        'euroDir':euroDir,
        'AnnSort':AnnSort,
        'cart_items':cart_items,
        'not_in_cart':not_in_cart,
        # 'source':source,
        'this_url':this_url,
        'referer_view':referer_view,
    }
    # print('view is: ', thisView)
    # print('source is: ', source)
    # previous_url = request.build_absolute_uri()
    # previous_url = request.META.get('HTTP_REFERER')
    # this_url = request.build_absolute_uri()

    

    # print('previous_url is: ', previous_url)
    print('this_url: ', this_url)
    print('referer_view: ', referer_view)


    return render(request, 'index.html', context)



def get_referer_view(request, default=None):
    ''' 
    Return the referer view of the current request

    Example:

        def some_view(request):
            ...
            referer_view = get_referer_view(request)
            return HttpResponseRedirect(referer_view, '/accounts/login/')
    '''

    # if the user typed the url directly in the browser's address bar
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return default

    # remove the protocol and split the url at the slashes
    referer = re.sub('^https?:\/\/', '', referer).split('/')
    # if referer[0] != request.META.get('SERVER_NAME'):
    #     return default

    # add the slash at the relative path's view and finished
    referer = u'/' + u'/'.join(referer[1:])
    return referer




def productPage(request, product_id):
    try:
        producto = Product.objects.get(id=product_id)
    except Exception as e:
        raise e

    if request.method == 'POST' and request.user.is_authenticated and request.POST['content'].strip()!='':
        Review.objects.create(product=producto, user=request.user, content = request.POST['content'])
    
    reviews = Review.objects.filter(product=producto,)
    caropics = CaroPics.objects.filter(product=producto)
    context = {
        'producto': producto,
        'reviews':reviews,
        'caropics':caropics,
        
    }
    for i in caropics:
        print(str(caropics))
        print(str(producto.id))
    return render(request, 'product.html', context)

def cart(request):
    return render(request, 'cart.html')

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    
    product = Product.objects.get(id=product_id)

    if request.user.is_authenticated:
        try:   
            cart_item = userCartItem.objects.get(product=product, user=request.user)
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity +=1
                cart_item.save()
                
        except userCartItem.DoesNotExist:
            cart_item=userCartItem.objects.create(product= product, quantity= 1, user=request.user)
            cart_item.save()
            
    else:
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id = _cart_id(request))
            cart.save()
        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity +=1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item=CartItem.objects.create(product= product, quantity= 1, cart=cart)
            cart_item.save()

    if 'source' in request.GET:
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('cart_detail')

def cart_detail(request, total=0, counter=0, cart_items=None):
    
    warnUser = request.session.get('warnUser')
    if not warnUser:
      warnUser=""
    else:
        del request.session['warnUser']

    if request.user.is_authenticated:
        try:
           cart_items=userCartItem.objects.filter(user=request.user)
           for cart_item in cart_items:
                total += (cart_item.product.price*cart_item.quantity)
                counter+=cart_item.quantity 
        except ObjectDoesNotExist:
            print('fail in logged user cart details')
    else:        
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,active=True)
            for cart_item in cart_items:
                total += (cart_item.product.price*cart_item.quantity)
                counter+=cart_item.quantity
        except ObjectDoesNotExist:
            print('fail in anonymous user cart details')

    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_total = int(total*100)
    description = 'Mobile Central - New Order'
    data_key = settings.STRIPE_PUBLISHABLE_KEY
    if request.method == 'POST':
        print(request.POST)
       
        try:
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            billingName = request.POST['stripeBillingName']
            billingAddressLine1 = request.POST['stripeBillingAddressLine1']
            billingCity = request.POST['stripeBillingAddressCity']
            billingPostcode = request.POST['stripeBillingAddressZip']
            billingCountry = request.POST['stripeBillingAddressCountryCode']
            shippingName = request.POST['stripeShippingName']
            shippingAddressLine1 = request.POST['stripeShippingAddressLine1']
            shippingCity = request.POST['stripeShippingAddressCity']
            shippingPostcode = request.POST['stripeShippingAddressZip']
            shippingCountry = request.POST['stripeShippingAddressCountryCode']


            customer = stripe.Customer.create(email=email, source=token)
            charge = stripe.Charge.create(amount=stripe_total, currency='eur', description=description, customer=customer.id)

            #Create the Order

            try:
                order_details = Order.objects.create(
                    token=token,
                    total=total,
                    emailAddress=email,
                    billingName=billingName,
                    billingAddressLine1=billingAddressLine1,
                    billingCity=billingCity,
                    billingPostcode=billingPostcode,
                    billingCountry=billingCountry,
                    shippingName=shippingName,
                    shippingAddressLine1=shippingAddressLine1,
                    shippingCity=shippingCity,
                    shippingPostcode=shippingPostcode,
                    shippingCountry=shippingCountry,
                    

                )
                order_details.save()
                for order_item in cart_items:
                    or_item=OrderItem.objects.create(product = order_item.product.name, quantity = order_item.quantity, price = order_item.product.price, order = order_details)
                    or_item.save()

                    #Reduce Stock
                    products = Product.objects.get(id=order_item.product.id)
                    products.stock = int(order_item.product.stock - order_item.quantity)
                    products.save()
                    order_item.delete()

                    #print a message when the order is created
                    print('the order has been created')
                return redirect('thanks_page', order_details.id)
            except ObjectDoesNotExist:
                pass



        except stripe.error.CardError as e:
            return False, e

    return render(request, 'cart.html', dict(cart_items=cart_items, total=total, counter=counter, data_key=data_key, stripe_total=stripe_total, description=description, warnUser=warnUser ))

def cart_remove (request, product_id):
    
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        cart_item=userCartItem.objects.get(user=request.user, product=product)
        if cart_item.quantity > 1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()


    if 'source' in request.GET:
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('cart_detail')

    return redirect('cart_detail')

def cart_remove_product(request, product_id):

    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        cart_item=userCartItem.objects.get(user=request.user, product=product)
        cart_item.delete()
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.delete()

    return redirect('cart_detail') 

def trashAll(request):
        if request.user.is_authenticated:
            cart_items=userCartItem.objects.filter(user=request.user)
            cart_items.delete()
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart)
            cart_items.delete()
        return redirect('cart_detail')


def thanks_page (request, order_id):

    emailJSid= settings.EMAILJS_USER_ID
    emailJSsendOrd = settings.EMAILJS_SENDORD
    listone=""
    

    if order_id:
        customer_order = get_object_or_404(Order, id=order_id)

        # email = str(request.user.email)
        
        # order = Order.objects.get(id=order_id, emailAddress=email)
        order = Order.objects.get(id=order_id)
        # email = order.emailAddress
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            sub_total = item.quantity * item.price
            item_name = str(item)
            item_qty = item.quantity
            item_price = item.price

            listone += "," + item_name +","  + str(item_qty) +" X € " + str(item_price) +",subtotal: € " + str(sub_total)+","
   
        
        

    return render(request, 'thankyou.html', {'customer_order':customer_order,'order':order,'order_items':order_items,'listone':listone,'emailJSid':emailJSid, 'emailJSsendOrd':emailJSsendOrd,})


def SignupView(request):
    emailJSid= settings.EMAILJS_USER_ID
    emailJSsignup = settings.EMAILJS_SIGNUP
    upform = ""
    dear = ""
    emailTo = ""
    yourID = ""
    dearCapt=""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        upform = form

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            signup_user = User.objects.get(username=username)
            customer_group = Group.objects.get(name='Customer')
            customer_group.user_set.add(signup_user)
            dear = upform.cleaned_data.get('first_name')
            dearCapt = dear.capitalize()
            emailTo = upform.cleaned_data.get('email')
            yourID = upform.cleaned_data.get('username')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form, 'upform': upform, 'dear': dearCapt, 'emailTo': emailTo, 'yourID': yourID,'emailJSid':emailJSid, 'emailJSsignup':emailJSsignup, })


def AddProduct(request):
    pName=""
    AddProd=()
    bName=""
    AddBrand=()
    AddSidePic=()
    EditProd=()
    cProduct=""
    eName=""
    pForm = AddProductForm() 
    bForm = AddBrandForm()
    cForm = AddSideForm()
    eForm= EditProductForm()
    lookupProd = ProdList()
    dpForm=()
    caropics=()
    selSideProd=""
    sidePicDeletion=""
    pic_to_del=""
    subForm=""
    TheSidePic=""
    Dear=""
    selprodId=""
    pDeleted=""
    theresPic=""
    p_to_change=""
    pChanged = ""

    if request.user.is_authenticated and request.user.first_name:
        Dear= str(request.user.first_name)
    if request.method == 'POST':
        print(request.POST)
        if 'subForm' in request.POST:
            subForm = request.POST['subForm']
        if 'pic_to_del' in request.POST:
            pic_to_del = request.POST['pic_to_del']

        print('quale is: ', subForm)
        print('pic_to_del is: ', pic_to_del)
        if subForm == 'prod':
            
            try:
                pForm = AddProductForm(request.POST, request.FILES)
                
                if pForm.is_valid():
                    pForm.save()
                    # name = request.POST['name']
                    AddProd=pForm.instance
                    pName=AddProd.name

            except:
                pForm = AddProductForm() 

        elif  subForm == 'sidepic':   
            try:    
                cForm = AddSideForm(request.POST, request.FILES)

                if cForm.is_valid():
                    cForm.save()
                    AddSidePic=cForm.instance
                    # bName = request.POST['name']
                    cProduct = AddSidePic.product
            except:
                cForm = AddSideForm()

        elif  subForm == 'brand':   
            try:    
                bForm = AddBrandForm(request.POST)

                if bForm.is_valid():
                    bForm.save()
                    AddBrand=bForm.instance
                    # bName = request.POST['name']
                    bName = AddBrand.name
            except:
                bForm = AddBrandForm()

        elif subForm == 'findProd':
            theProd = request.POST['lookupProd']
            # print('theProd is: ', theProd)
            selProd=Product.objects.get(id=theProd)
            print(selProd)
            EditProd=EditProductForm(instance=selProd)
            # print(EditProd)
            eForm=EditProd
            selprodId=theProd

        elif subForm == 'editProd':

            try:
                eForm=EditProductForm(request.POST, request.FILES)
                if 'with_prod_id' in request.POST:
                    with_prod_id = request.POST['with_prod_id']
                    pickprod= Product.objects.get(id=with_prod_id)
                else:
                    theProd = request.POST['name']
                    pickprod= Product.objects.get(name=theProd)

                if 'p_to_del' in request.POST:
                    # print('theProd is: ', theProd)
                    
                    # print (pickprod)
                    print (str(eForm))
                    # print(str(request.POST))
                    print ('Imma delete', pickprod )
                    # if eForm.is_valid():
                        
                    pDeleted=str(pickprod)

                    pickprod.delete()
                    # eForm = EditProductForm(request.POST, request.FILES)
                    # EditProd=EditProductForm(instance=theProd )
                    # if eForm.is_valid():
                    #     EditProd=eForm
                    #     EditProd.save()
                    #     # eForm.save()
                    #     # # name = request.POST['name']
                    #     # EditProd=eForm.instance
                    #     eName=EditProd.name
                    
                elif 'p_to_del' not in request.POST:
                    
                    
                    
                    p_to_change = Product.objects.get(id=pickprod.id)
                    print('p_to change isss: ', p_to_change)
                    eName = str(pickprod)
                    if 'name' in request.POST:

                        p_to_change.name = request.POST['name']
                        pChanged = p_to_change
                    if 'price' in request.POST:    
                        p_to_change.price = request.POST['price']
                        pChanged = p_to_change
                    if 'description' in request.POST:
                        p_to_change.description = request.POST['description']
                        pChanged = p_to_change
                    if 'stock' in request.POST:    
                        p_to_change.stock = request.POST['stock']
                        pChanged = p_to_change
                    if 'available' in request.POST:
                        if 'available' in request.POST:
                            available = request.POST['available']
                            if available == 'on':
                                p_to_change.available = True
                                pChanged = p_to_change
                    else:
                        p_to_change.available = False
                    if 'latest' in request.POST:
                        latest = request.POST['latest']
                        if latest == 'on':
                            p_to_change.latest = True
                            pChanged = p_to_change
                    else:
                        p_to_change.latest = False
                    if 'best' in request.POST:
                        best = request.POST['best']
                        if best == 'on':
                            p_to_change.best = True
                            pChanged = p_to_change
                    else:
                        p_to_change.best = False

                    if 'category' in request.POST:
                        upCategory = request.POST['category']
                        pickCateg = Category.objects.get(id=upCategory)
                        p_to_change.category = pickCateg
                        pChanged = p_to_change

                    if 'image' in request.FILES:
                            upImage = request.FILES['image']
                            p_to_change.image = upImage
                            theresPic = str(p_to_change)
                            print('thersePic', theresPic)
                            pChanged = p_to_change
                    p_to_change.save()

            except Exception as e :
                raise e
                # eForm = EditProductForm()
        
        elif subForm == 'findSideProd':
            theProd = request.POST['lookupProd']
            # print('theProd is: ', theProd)
            selSideProd=Product.objects.get(id=theProd)
            # print(selProd)
            # delSideProd=EditProductForm(instance=selProd)
            # # print(EditProd)
            # eForm=EditProd
            caropics = CaroPics.objects.filter(product=selSideProd)
            print(str(caropics))

        if pic_to_del :
            print('ok del side pic lo sente')
            

            # SidePicId = request.POST['pic_to_del']
            # print(str(SidePicId))
            TheSidePic = CaroPics.objects.get(id=pic_to_del)
            TheSidePic.delete()

            print('il caro Side pic e\': (stu basatru)',str(TheSidePic))
            sidePicDeletion="deleted"

            
            


    else:
        pForm = AddProductForm()
        bForm = AddBrandForm()
        cForm = AddSideForm()
        eForm = AddProductForm() 
        dpForm=()

    this_url = request.path
    referer_view = get_referer_view(request)

    context={
        'pForm':pForm,
        'pName':pName,
        'AddProd':AddProd,
        'AddBrand':AddBrand,
        'AddSidePic':AddSidePic,
        'bForm':bForm,
        'bName':bName,
        'cProduct':cProduct,
        'cForm':cForm,
        'eForm':eForm,
        'EditProd':EditProd,
        'eName':eName,
        'lookupProd':lookupProd,
        'caropics':caropics,
        'selSideProd':selSideProd,
        'sidePicDeletion':sidePicDeletion,
        'dpForm':dpForm,
        'TheSidePic':TheSidePic,
        'Dear':Dear,
        'selprodId':selprodId,
        'this_url':this_url,
        'referer_view':referer_view,
        'pDeleted':pDeleted,
        'theresPic':theresPic,
        'p_to_change':p_to_change,
        'pChanged': pChanged,

    }
    return render (request,'addProduct.html',context)

def AddBrand(request):
    bName=""
    AddBrand=()
    if request.method == 'POST':
        bForm = AddBrandForm(request.POST)

        if bForm.is_valid():
            bForm.save()
            AddBrand=bForm.instance
            bName = request.POST['name']
            
    else:
        bForm = AddBrandForm()

    context={
        'bForm':bForm,
        'bName':bName,
        'AddBrand':AddBrand,   
    }
    return render(request,'addBrand.html',context)  

def SigninView(request):
    if request.method =='POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request,user)


                try:
                    cart=Cart.objects.get(cart_id=_cart_id(request))
                    cart_items=CartItem.objects.filter(cart=cart,active=True)

                except ObjectDoesNotExist:
                    pass

                return redirect('latest')
            else:
                return redirect ('signup')

        

    else:
        form = AuthenticationForm()
    return render(request, 'signin.html', {'form':form})

def SignoutView(request):
    logout(request)
    return redirect('signin')

@login_required(redirect_field_name='next',login_url='signin')
def orderHistory(request):
    if request.user.is_authenticated:
        email = str(request.user.email)
        order_details = Order.objects.filter(emailAddress=email)
    return render(request,'orders_list.html',{'order_details':order_details}) 

@login_required(redirect_field_name='next',login_url='signin')
def viewOrder(request, order_id):
    if request.user.is_authenticated:
        email = str(request.user.email)
        order = Order.objects.get(id=order_id, emailAddress=email)
        order_items = OrderItem.objects.filter(order=order)
    return render(request, 'order_detail.html', {'order':order,'order_items':order_items,})

def contact(request):
    emailJSid= settings.EMAILJS_USER_ID
    # emailJSsendMessage = settings.EMAILJS_SIGNUP

    
    if request.method=="POST":
        if request.user.is_authenticated:
            form=AuthContactForm(request.POST)
        else:
            form=ContactForm(request.POST)
        subject=""
        message=""
        if form.is_valid():


            if request.user.is_authenticated: 
                name = request.user.first_name
                from_email = request.user.email
                captName = name.title()
                
            else:
                from_email= form.cleaned_data.get('from_email')
                name= form.cleaned_data.get('name')
                captName = name.title()
                

            message= form.cleaned_data.get('message')    
            subject= form.cleaned_data.get('subject')

            return render(request, 'contact_success.html',{'message':message,'name':captName, 'emailTo':from_email,'subject':subject,'emailJSid':emailJSid})

    else:
        if request.user.is_authenticated:
            form = AuthContactForm()
        else:
            form= ContactForm()
    return render(request, 'contact.html', {'form':form})

