import logging
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import csrf_exempt

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
        return Response({
            "error": {
                "en": "An error occurred while fetching items.",
                "ja": "アイテムを取得中にエラーが発生しました。"
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET", "POST"])
def handle_cart_request(request):
    user = request.user if request.user.is_authenticated else None
    cart, _ = Cart.objects.get_or_create(user=user)
    
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
                "error": {
                    "en": "Requested quantity exceeds available stock of {}.".format(item.quantity),
                    "ja": "{}の在庫が超過しています。".format(item.quantity)
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        current_cart_item = CartItem.objects.filter(cart=cart, item=item).first()
        if current_cart_item:
            total_quantity_in_cart = current_cart_item.quantity + quantity
        else:
            total_quantity_in_cart = quantity

        if total_quantity_in_cart > item.quantity:
            return Response({
                "error": {
                    "en": "Total quantity in cart exceeds available stock of {}.".format(item.quantity),
                    "ja": "{}の在庫が超過しています。".format(item.quantity)
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        added_cart_item, _ = CartItem.objects.get_or_create(cart=cart, item=item)
        added_cart_item.quantity += quantity
        added_cart_item.save()

        serializer = CartSerializer(added_cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def cart_checkout(request):
    user = request.user if request.user.is_authenticated else None
    cart, created = Cart.objects.get_or_create(user=user)

    if  not CartItem.objects.filter(cart=cart).exists():
        return Response({
            "error": {
                "en": "Cart is empty.",
                "ja": "カートは空です。"
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    cart_items = CartItem.objects.filter(cart=cart)
    purchased_items = []

    for cart_item in cart_items:
        if cart_item.quantity > cart_item.item.quantity:
            return Response({
                "error": {
                    "en": "Only {} remaining in stock for {}.".format(cart_item.item.quantity, cart_item.item.name),
                    "ja": "{}の在庫が残り{}個です。".format(cart_item.item.name, cart_item.item.quantity)
                }
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
    return Response({"message": {
        "en": "Checkout successful.",
        "ja": "チェックアウトが成功しました。"
    }}, status=status.HTTP_200_OK)
