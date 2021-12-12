from django.urls import path
from django.conf.urls import url
from . import views as v

urlpatterns = [
    path('ordersummary/', v.OrderSummaryView.as_view(), name='ordersummary'),
    path('add-to-cart/<int:id>', v.add_to_cart, name='add-to-cart'),
    path('update-cart/<int:id>', v.update_cart, name='update-cart'),
    path('remove-from-cart/<int:id>', v.remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<int:id>', v.remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('checkout/', v.CheckoutView.as_view(), name='checkout'),
    path('order_complete', v.order_complete, name='order_complete'),
    path('cancel_order/<int:id>', v.cancel_order, name='cancel_order'),
    path('payment/<payment_option>/', v.PaymentView.as_view(), name='payment'),
    path('paymentcod/<payment_option>/', v.PaymentViewCod.as_view(), name='paymentcod'),
    ]