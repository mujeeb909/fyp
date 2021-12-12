from django.db import models
from store.models import products
from django.contrib.auth.models import User
# Create your models here.


RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
class review(models.Model):
    item = models.ForeignKey(products,on_delete=models.CASCADE, related_name="itemreview")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review_title = models.CharField(max_length=120, blank= True)
    review = models.TextField()
    review_predict = models.CharField(max_length=120, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)

    def __str__(self):
        return self.item.title