# Generated by Django 3.1 on 2020-09-10 21:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_auto_20200910_1517'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='billingAddress1',
            new_name='billingAddressLine1',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='shippingAddress1',
            new_name='shippingAddressLine1',
        ),
    ]