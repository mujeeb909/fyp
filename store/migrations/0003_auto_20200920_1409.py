# Generated by Django 2.1.15 on 2020-09-20 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_products_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='default_price',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='products',
            name='discount_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
    ]
