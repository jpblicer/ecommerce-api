from django.urls import path
from .views import ItemList, CartViewSet

urlpatterns = [
    path('items/', ItemList.as_view(), name = 'item-list'),
    path('cart/', CartViewSet.as_view({'post': 'create', 'get': 'list'}), name='cart'),
]
