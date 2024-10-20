from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemList, CartViewSet

router = DefaultRouter()
router.register(r'cart', CartViewSet)

urlpatterns = [
    path('items/', ItemList.as_view(), name = 'item-list'),
    path('cart/', include(router.urls))
]
