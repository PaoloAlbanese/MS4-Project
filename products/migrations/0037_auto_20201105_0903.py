# Generated by Django 3.1 on 2020-11-05 09:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0036_auto_20201105_0854'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='manufactorer',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['name']},
        ),
    ]
