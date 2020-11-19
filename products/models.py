from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, blank=True)
    image = models.ImageField(upload_to='category', blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Manufactorer(models.Model):
    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name
   
    class Meta:
        ordering = ['name']

class Provider(models.Model):
    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        'Category', null=True, blank=False, on_delete=models.SET_NULL)
    manufactorer = models.ForeignKey(
        'Manufactorer', null=True, blank=False, on_delete=models.SET_NULL, help_text='if missing, you can add the maufactoer on the dedicated form on this page')
    provider = models.ManyToManyField(
        'Provider', blank=True)
    name = models.CharField(max_length=254,)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product', blank=False, null=False, default='product/mobile-2468068_1920.png')
    # image = models.ImageField(upload_to='product')
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    latest = models.BooleanField(default=False)
    best = models.BooleanField(default=False)

    def get_url(self):
        return reverse('product_detail', args=[self.id])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']    


class CaroPics(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE, blank=False)
    image=models.ImageField(blank=False)

    class Meta:
        verbose_name_plural = 'Caro Pics'



class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table='Cart'
        ordering = ['date_added']
    
    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity= models.IntegerField()
    active=models.BooleanField(default=True)

    class Meta:
        db_table='CartItem'
    
    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product



class Order(models.Model):
    token = models.CharField(max_length=254, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='EUR Order Total')
    emailAddress = models.EmailField(max_length=254, blank=True, verbose_name='Email Address')
    created = models.DateTimeField(auto_now_add=True)
    billingName = models.CharField(max_length=254, blank=True)
    billingAddressLine1 = models.CharField(max_length=254, blank=True)
    billingCity = models.CharField(max_length=254, blank=True)
    billingPostcode = models.CharField(max_length=254, blank=True)
    billingCountry = models.CharField(max_length=254, blank=True)
    shippingName = models.CharField(max_length=254, blank=True)
    shippingAddressLine1 = models.CharField(max_length=254, blank=True)
    shippingCity = models.CharField(max_length=254, blank=True)
    shippingPostcode = models.CharField(max_length=254, blank=True)
    shippingCountry = models.CharField(max_length=254, blank=True)
    

    class Meta:
        db_table='Order'
        ordering = ['-created']

    def __str__(self):
        return str(self.id)

class OrderItem(models.Model):
    product = models.CharField(max_length=250)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='EUR price')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        db_table = 'OrderItem'

    def sub_total(self):
        return self.quantity*self.price

    def __str__(self):
        return str(self.product)


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    reviewDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.content)

class userCartItem(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity= models.IntegerField()
    active=models.BooleanField(default=True)

    class Meta:
        db_table='userCartItem'
    
    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product        