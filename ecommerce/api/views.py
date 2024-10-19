from django.shortcuts import render
from rest_framework import generics

from ecommerce.api.serializers import ItemSerializer
from .models import Item

# Create your views here.

class ItemListCreate(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
