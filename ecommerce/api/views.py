from rest_framework import generics, viewsets, status
from rest_framework.response import Response

from .serializers import ItemSerializer, CartSerializer
from .models import CartItem, Item, Cart

# Create your views here.

class ItemListCreate(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class CartViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = CartSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request):
        cart = request.user.cart
        queryset = Cart.objects.filter(cart=cart)
        serializer = CartSerializer(queryset, many=True)
        return Response(serializer.data)
