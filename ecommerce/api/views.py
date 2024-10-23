import logging
from django.shortcuts import get_object_or_404
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
        logger.error("Error fetching items: {}".format(error))
        return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET", "POST"])
def handle_cart_request(request):
    cart, _ = Cart.objects.get_or_create(user=None)

    if request.method == "GET":
        cart_items = CartItem.objects.filter(cart=cart)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        requested_item_id = request.data.get('item')
        item_quantity_requested = request.data.get('quantity')

        item = get_object_or_404(Item, id=requested_item_id)
        quantity = int(item_quantity_requested)

        if quantity > item.quantity:
            return Response({
                "error": "Requested quantity exceeds available stock of {}.".format(item.quantity)
            }, status=status.HTTP_400_BAD_REQUEST)

        added_cart_item, _ = CartItem.objects.get_or_create(cart=cart, item=item)
        added_cart_item.quantity += quantity
        added_cart_item.save()

        serializer = CartSerializer(added_cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
def cart_checkout(request):
    cart, created = Cart.objects.get_or_create(user=None)

    if created or not CartItem.objects.filter(cart=cart).exists():
        return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

    cart_items = CartItem.objects.filter(cart=cart)
    purchased_items = []

    for cart_item in cart_items:
        if cart_item.quantity > cart_item.item.quantity:
            return Response({
                "error": "There are only {} remaining in stock for {}.".format(cart_item.item.quantity, cart_item.item.name)
            }, status=status.HTTP_400_BAD_REQUEST)

        PurchaseRecord.objects.create(item=cart_item.item, quantity=cart_item.quantity)
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
