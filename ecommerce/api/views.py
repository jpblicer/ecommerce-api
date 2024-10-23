import logging
from django.utils.ipv6 import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import ItemSerializer, CartSerializer
from .models import CartItem, Item, Cart, PurchaseRecord

logger = logging.getLogger(__name__)

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
   
        try:
            item = Item.objects.get(id=requested_item_id)
        except Item.DoesNotExist:
            return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        quantity = int(item_quantity_requested)

        added_cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
        added_cart_item.quantity += quantity
        added_cart_item.save()

        serializer = CartSerializer(added_cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
def cart_checkout(request):
    cart, created = Cart.objects.get_or_create(user=None)
    
    if not created:
        cart_items = CartItem.objects.filter(cart=cart)

        purchased_items = []
        
        for cart_item in cart_items:
            if cart_item.quantity > cart_item.item.quantity:
                return Response({"error": "There is only {} reamining in stock for {}.".format(cart_item.item.quantity, cart_item.item.name)}, 
                                status=status.HTTP_400_BAD_REQUEST)

            PurchaseRecord.objects.create(
                item=cart_item.item,
                quantity=cart_item.quantity
            )

            cart_item.item.quantity -= cart_item.quantity
            cart_item.item.save()

            purchased_items.append({
                'item_id': cart_item.item.id,
                'item_name': cart_item.item.name,
                'item_quantity': cart_item.quantity
            })

        logger.info("Items purchased: {}".format(purchased_items))

        cart_items.delete()
        return Response({"message": "Checkout successful."}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)
