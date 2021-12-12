from django.contrib import admin
from  .models import *
from stock.models import stock
# Register your models here.

class StockInline(admin.StackedInline):
    model = stock
    extra = 1

class ImageInline(admin.StackedInline):
    model = Image
    extra = 1
    max_num = 2

class ProductAdmin(admin.ModelAdmin):
    search_fields = ['title','description']
    date_hierarchy = 'timestamp'
    list_display = ['__str__','title', 'active', 'timestamp','updated','Category','default_price']
    list_editable = ['active','default_price']
    list_filter =['active']
    readonly_fields = ['updated','timestamp']
    prepopulated_fields = {"slug": ("title",)}

    inlines = (ImageInline,StockInline)

    class Meta:
        model= products

admin.site.register(products, ProductAdmin)

class ImageAdmin(admin.ModelAdmin):
    readonly_fields = []
    list_display = ['product', ]
admin.site.register(Image, ImageAdmin)

class categoryAdmin(admin.ModelAdmin):
            search_fields = ['category_title', 'category_description']
            list_display = ['category_title', 'category_description']
            prepopulated_fields = {"category_slug": ("category_title",)}
            class Meta:
                model = category

admin.site.register(category,categoryAdmin )
admin.site.register(Banner)
admin.site.register(Sub_category)
admin.site.register(Color)
admin.site.register(Size)