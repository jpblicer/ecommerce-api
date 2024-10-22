from rest_framework import generics, viewsets, status
from rest_framework.response import Response

from .serializers import ItemSerializer, CartSerializer
from .models import CartItem, Item, Cart

class ItemList(generics.ListAPIView):
    queryset = Item.objects.filter(quantity__gt=0)
    serializer_class = ItemSerializer

class CartViewSet(viewsets.ViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartSerializer

    def create(self, request):
        item_id = request.data.get('item')
        quantity = request.data.get('quantity')
        cart, created = Cart.objects.get_or_create(user=None)

        if quantity is None:
            return Response({"error": "Quantity is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response({"error": "Quantity must be a valid positive integer."}, status=status.HTTP_400_BAD_REQUEST)


        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        if quantity > item.quantity:
            return Response({"error": "{} only has stock of {}.".format(item.name, item.quantity)},
                            status=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0:
            return Response({"error": "Invalid quantity requested. Must be a positive number."},
                            status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)

        item.quantity -= quantity
        cart_item.quantity = quantity
        item.save()
        cart_item.save()

        return Response(CartSerializer(cart_item).data, status=status.HTTP_201_CREATED)

    def list(self, request):
        cart, created = Cart.objects.get_or_create(user=None)
        queryset = CartItem.objects.filter(cart=cart)
        serializer = CartSerializer(queryset, many=True)
        return Response(serializer.data)

    def checkout(self, request):
        cart, created = Cart.objects.get_or_create(user=None)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response({"message": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        for cart_item in cart_items:
            item = cart_item.item
            if item.quantity < cart_item.quantity:
                return Response({"error": "Insufficient stock for {}.".format(item.name)}, status=status.HTTP_400_BAD_REQUEST)
        
            item.quantity -= cart_item.quantity
            item.save()

        cart_items.delete()

        return Response({"message": "Checkout successful."}, status=status.HTTP_200_OK)
