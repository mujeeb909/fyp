from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from store.models import products , Color ,Size


# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)
post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)




class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='orderitemcolor', blank=True, null=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='orderitemsize', blank=True, null=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of ({self.item.title})" + "|" + str(self.color) + "|" +str(self.size)

    def get_total_item_price(self):
        return self.quantity * self.item.default_price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.default_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


# class Coupon(models.Model):
#     code = models.CharField(max_length=15)
#     amount = models.DecimalField(decimal_places=2, max_digits=20, default=0.00 ,blank=True)
#
#     def __str__(self):
#         return self.code
TCS = 'TCS'
LEAOPARD = 'LEAOPARD'
SHIPPING_CHOICES = (
    (TCS, 'TCS'),
    (LEAOPARD, 'LEOPARD'),
)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    # coupon = models.ForeignKey(
    #     'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    paymentCod = models.ForeignKey(
        'PaymentCod', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    shipping = models.CharField(choices=SHIPPING_CHOICES, max_length=500, null=True,  default=TCS)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total


ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=20, default=0.00 ,blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

Payment_CHOICES = (
    ('pending', 'pending'),
    ('approved', 'approved'),
)
class PaymentCod(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=20, default=0.0 , blank=True, null=True)
    payment_choice = models.CharField(choices=Payment_CHOICES, max_length=10, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username