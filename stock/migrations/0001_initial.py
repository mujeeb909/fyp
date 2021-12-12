# Generated by Django 3.0.8 on 2020-07-10 20:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now=True)),
                ('quantity', models.PositiveIntegerField()),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=20)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_stock', to='store.products')),
                ('product_Color', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_color', to='store.Color')),
                ('product_Size', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_size', to='store.Size')),
            ],
        ),
    ]
