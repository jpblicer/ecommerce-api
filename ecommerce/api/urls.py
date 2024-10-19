from django.urls import path
from . import views

urlpatterns = [
    path('items/', views.ItemListCreate.as_view(), name = 'item-view-create')
]
