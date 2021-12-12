
from django.urls import path
from .views import *
urlpatterns = [

    path('review/<int:id>/', Itemreview , name='review'),

]