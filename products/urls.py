from django.urls import path
from . import views

urlpatterns = [
    path('types/<int:num>/', views.types, name='types'),
    path('brand/<int:num>/', views.brand, name='brand'),
    path('all_products/', views.all_products, name='products'),
    path('Show_all_products/', views.showAll, name='show_all'),
    path('product_detail/<int:product_id>/', views.productPage, name='product_detail'),
    path('',views.latest, name='latest'),
    path('cart/add/<int:product_id>', views.add_cart, name='add_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/remove/<int:product_id>', views.cart_remove, name='cart_remove'),
    path('cart/remove_product/<int:product_id>', views.cart_remove_product, name='cart_remove_product'),
    path('thankyou/<int:order_id>', views.thanks_page, name='thanks_page'),
    path('account/create/', views.SignupView, name='signup'),
    path('account/signin/', views.SigninView, name='signin'),
    path('account/signout/', views.SignoutView, name='signout'),
    path('order_history/', views.orderHistory, name='order_history'),
    path('order/<int:order_id>/', views.viewOrder, name='order_detail'),
    path('contact/', views.contact, name='contact'),
    path('trashAll/', views.trashAll, name='trashAll'),
    path('add_product/', views.AddProduct, name='add_product'),
    path('add_brand/', views.AddBrand, name='add_brand'),
]
