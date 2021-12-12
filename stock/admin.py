from django.contrib import admin
# Register your models here.
from django.contrib import admin
from .models import stock
from store.models import products
# Register your models here.


class StockAdmin(admin.ModelAdmin):
    search_fields = ['quantity','price']
    date_hierarchy = 'date'
    list_display = ['quantity','date','product', 'product_Color', 'product_Size']
    list_filter =['sale_price', 'product']

    def psize(self, obj):
        return obj.Product_Size.size

    def pcolor(self, obj):
        return obj.Product_Color.color

    class Meta:
        model= stock
    ordering = ['product']


admin.site.register(stock , StockAdmin)