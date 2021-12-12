from django.contrib import admin
from  .models import *
# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'shipping_address',
                    'billing_address',
                    'payment',
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'payment',
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'start_date']
    search_fields = [
        'user__username',
        'ref_code'
    ]



class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']

class paymentCodAdmin(admin.ModelAdmin):
    list_filter = ['user', 'timestamp']

admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(PaymentCod,paymentCodAdmin)
admin.site.register(Address, AddressAdmin)