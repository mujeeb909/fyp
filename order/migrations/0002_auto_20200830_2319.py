# Generated by Django 2.1.15 on 2020-08-30 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='refund_granted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='refund_requested',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping',
            field=models.CharField(choices=[('TCS', 'TCS'), ('LEOPARD', 'LEOPARD')], max_length=500, null=True),
        ),
    ]