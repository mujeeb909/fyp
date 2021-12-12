from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User


class Banner(models.Model):
    image = models.ImageField(upload_to='banner_images', verbose_name='Banner_image')
    title  = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title



class category(models.Model):
    objects = None
    category_title = models.CharField(max_length=200)
    category_image = models.ImageField(upload_to="category")
    category_description = models.TextField()
    category_slug = models.SlugField(max_length=200)
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_title


class Sub_category(models.Model):
    category = models.ForeignKey(category, on_delete=models.CASCADE, null=True, related_name='subcategory')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="sub_category_images")
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Sub Categories"

    def __str__(self):
        return self.title

class ProductQuerySet(models.query.QuerySet):

  def active(self):
    return self.filter(active=True)

  def featured(self):
    return self.filter(featured=True, active=True)

  def search(self, query):
    lookups = (Q(title__icontains=query) |
               Q(description__icontains=query) |
               Q(default_price__icontains=query) |
               Q(slug__icontains=query)
    )
    return self.filter(lookups).distinct()


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def featured(self):
        return self.get_queryset().featured()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().active().search(query)

class Color(models.Model):
    title = models.CharField(max_length=120)
    price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00, blank=True, null=True)
    updated = models.DateTimeField(auto_now_add=False,auto_now=True)
    active= models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Size(models.Model):
    title = models.CharField(max_length=120)
    price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00, blank=True, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

# Create your models here.
class products(models.Model):
    title= models.CharField(max_length=120)
    Category = models.ForeignKey(category, blank=True, on_delete=models.CASCADE, related_name="itemcat")
    sub_category = models.ForeignKey(Sub_category, blank=True,null=True ,on_delete=models.CASCADE, related_name="productsub")
    slug= models.SlugField(blank=True, unique=True)
    description= models.TextField()
    featured= models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    timestamp= models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    default_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.0)
    discount_price = models.DecimalField(decimal_places=2, max_digits=20,default=0.0 ,blank=True, null=True)
    tag = models.CharField(max_length=120, null=True)
    default_img =models.ImageField(upload_to="product/images")
    product_color = models.ManyToManyField(Color, blank=True)
    product_size = models.ManyToManyField(Size, blank=True)

    objects = ProductManager()

    class Meta:
        db_table = 'products'
        index_together = (('id', 'slug'),)
#product title will shown in admin method below
    def __str__(self):
        return self.title


class Image(models.Model):
    product = models.ForeignKey(products,on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to="product/images")
