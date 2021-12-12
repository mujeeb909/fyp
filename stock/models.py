from django.db import models
from store.models import products, Color ,Size

class stock(models.Model):
    product = models.ForeignKey(products, on_delete=models.CASCADE , blank=True,null=True, related_name="product_stock")
    product_Size = models.ForeignKey(Size, on_delete=models.CASCADE , blank=True,null=True, related_name="product_size")
    product_Color = models.ForeignKey(Color, on_delete=models.CASCADE,  blank=True, null=True,related_name="product_color")
    date = models.DateField(auto_now=True)
    quantity = models.PositiveIntegerField()
    sale_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00, blank=True)

    def __str__(self):
        return self.product.title

