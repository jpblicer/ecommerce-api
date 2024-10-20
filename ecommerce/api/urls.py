from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemListCreate, CartViewSet

router = DefaultRouter()
router.register(r'cart', CartViewSet)

urlpatterns = [
    path('items/', ItemListCreate.as_view(), name = 'item-view-create'),
    path('cart/', include(router.urls))
]
