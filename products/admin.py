from django.contrib import admin
from .models import Category, Product, Manufactorer, Provider, Order, OrderItem, Review, CaroPics

# Register your models here.

admin.site.register(Category)
# admin.site.register(Product)
admin.site.register(Manufactorer)
admin.site.register(Provider)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','price', 'stock','category','latest','best','available']
    list_editable = ['price', 'stock','latest','best','available']
    list_per_page = 10

admin.site.register(Product, ProductAdmin)

class OrderItemAdmin(admin.TabularInline):
    model=OrderItem
    fieldsets = [
        ('Product', {'fields':['product'],}),
        ('Quantity', {'fields':['quantity'],}),
        ('Price', {'fields':['price'],}),

    ]
    readonly_fields = ['product','quantity','price']
    can_delete = False
    max_num = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','billingName','emailAddress','created']
    list_display_links = ['id','billingName']
    search_fields = ['id','billingName','emailAddress']
    readonly_fields = ['id', 'token', 'total', 'emailAddress','created','billingAddressLine1','billingCity','billingPostcode','billingCountry','shippingAddressLine1','shippingCity','shippingPostcode','shippingCountry']

    fieldsets = [
    ('ORDER INFORMATION', {'fields':['id', 'token', 'total','created']}),
    ('BILLING INFORMATION', {'fields':['billingName', 'billingAddressLine1','billingCity','billingPostcode','billingCountry','emailAddress']}),
    ('SHIPPING INFORMATION', {'fields':['shippingName', 'shippingAddressLine1','shippingCity','shippingPostcode','shippingCountry']})
    ]

    inlines= [OrderItemAdmin,]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False    

admin.site.register(Review)
admin.site.register(OrderItem)


class CaroPicsAdmin(admin.ModelAdmin):
    list_display = ['product','image']

admin.site.register(CaroPics)    