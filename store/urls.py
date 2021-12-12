from django.urls import path
from django.conf.urls import url

from . import views as v

urlpatterns = [
    path('', v.index, name='index'),
    path('store', v.store, name='store'),
    path('category/<int:id>/', v.category_detail, name='category'),
    path('query/', v.SearchProductView.as_view(),name='query'),
    url(r'^api/get_places/', v.get_places, name='get_places'),
    path('detail/<int:id>/', v.detail, name='detail'),
    path('contact', v.contact, name='contact'),
    path('reload/<int:id>/', v.reload, name='reload'),
    path('size/<int:id>/', v.size_ajax, name='size'),
    path('color/<int:id>/', v.color_ajax, name='color'),
    path('subcategory/<int:id>/', v.subcategory_detail, name='subcategory'),
    ]