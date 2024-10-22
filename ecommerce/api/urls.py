from django.urls import path
from .views import items_list, cart_items_list

urlpatterns = [
    path('items/', items_list, name = 'items-list'),
    path('cart/', cart_items_list, name = 'cart-items-list'),
    # path('cart/checkout/', cart_checkout = 'cart-checkout'),
]
