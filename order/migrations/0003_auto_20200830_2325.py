# Generated by Django 2.1.15 on 2020-08-30 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_auto_20200830_2319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='shipping',
            field=models.CharField(choices=[('TCS', 'TCS'), ('LEAOPARD', 'LEOPARD')], default='TCS', max_length=500, null=True),
        ),
    ]
