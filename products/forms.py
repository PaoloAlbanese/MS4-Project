from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, Manufactorer, CaroPics
from django.forms import ModelForm, ModelChoiceField

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=250, help_text='eg youremail@here.com')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'password1', 'password2', 'email')


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=50, required=True)
    name = forms.CharField(max_length=20, required=True)
    from_email = forms.EmailField(max_length=50, required=True)
    
    message = forms.CharField(
        max_length=500,
        required=True,
        widget=forms.Textarea(),
        help_text="",
    )

class AuthContactForm(forms.Form):
    subject = forms.CharField(max_length=50, required=True)
    # name = forms.CharField(max_length=20, required=False, disabled=True)
    # from_email = forms.EmailField(max_length=50, required=False, disabled=True)
    message = forms.CharField(
        max_length=500,
        required=True,
        widget=forms.Textarea(),
        help_text="",
    )    

class AddProductForm(ModelForm):
    prefix = 'addproduct'
    class Meta:
        model = Product
        exclude = ('provider',)

class AddBrandForm(ModelForm):
    prefix = 'addbrand'
    class Meta:
        model = Manufactorer
        fields = ('name',)

class AddSideForm(ModelForm):
    class Meta:
        model = CaroPics
        fields = ('product','image',)



class ProdList(forms.Form):
    lookupProd = forms.ModelChoiceField(label="Product", queryset=Product.objects.all().order_by('name'), empty_label="(Select Product)",widget=forms.Select(attrs={'onchange': 'this.form.submit();'}))
    
class EditProductForm(ModelForm):
    
    class Meta:
        model = Product
        exclude = ('provider',)