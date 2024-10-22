from django.urls import path
from .views import ItemList, CartViewSet

urlpatterns = [
    path('items/', ItemList.as_view(), name = 'item-list'),
    path('cart/', CartViewSet.as_view({'post': 'add_item_to_cart', 'get': 'list'}), name='cart'),
    path('cart/checkout/', CartViewSet.as_view({'post': 'checkout'}), name='cart-checkout'),
]
