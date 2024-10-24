from django.urls import path
from .views import cart_checkout, handle_cart_request, items_list

urlpatterns = [
    path('items/', items_list, name = 'items-list'),
    path('cart/', handle_cart_request, name = 'cart-items'),
    path('cart/checkout/', cart_checkout, name = 'cart-checkout'),
]
