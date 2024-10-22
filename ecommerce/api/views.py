from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import ItemSerializer, CartSerializer
from .models import CartItem, Item, Cart

@api_view(["GET"])
def items_list(request):
    try:
        items = Item.objects.filter(quantity__gt=0)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)
    except Exception as error:
        return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["GET", "POST"])
def handle_cart_request(request):
    cart, created = Cart.objects.get_or_create(user=None)

# List Items in Cart
    if request.method == "GET":
        cart_items = CartItem.objects.all()
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)

# Add Item to Cart
    elif request.method == "POST":
        requested_item_id = request.data.get('item')
        item_quantity_requested = request.data.get('quantity')

        item = Item.objects.get(id = requested_item_id)
        quantity = int(item_quantity_requested)

        item.quantity -= quantity
        item.save()

        added_cart_item, created = CartItem.objects.get_or_create(cart = cart, item=item)
        added_cart_item.quantity += quantity

        added_cart_item.save()

        serializer = CartSerializer(added_cart_item)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def cart_checkout(request):
    cart, created = Cart.objects.get_or_create(user=None)
    
    cart_items = CartItem.objects.filter(cart=cart)

    cart_items.delete()
    
    return Response({"message": "Checkout successful."}, status=status.HTTP_200_OK)
