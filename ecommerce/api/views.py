from rest_framework import generics, viewsets, status
from rest_framework.response import Response

from .serializers import ItemSerializer, CartSerializer
from .models import CartItem, Item, Cart

# Create your views here.

class ItemList(generics.ListAPIView):
    queryset = Item.objects.filter(quantity__gt=0)
    serializer_class = ItemSerializer

class CartViewSet(viewsets.ViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartSerializer

    def create(self, request):
        item_id = request.data.get('item')
        quantity = request.data.get('quantity')
        cart = request.user.cart

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({"Item not found."}, status=status.HTTP_404_NOT_FOUND)

        if quantity > item.quantity:
            return Response({"{} is out of stock. remaining stock is {}.".format(item.name, item.quantity)},
                            status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)

        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        item.quantity -= quantity
        item.save()

        return Response(CartSerializer(cart_item).data, status=status.HTTP_201_CREATED)

    def list(self, request):
        cart = request.user.cart
        queryset = Cart.objects.filter(cart=cart)
        serializer = CartSerializer(queryset, many=True)
        return Response(serializer.data)
