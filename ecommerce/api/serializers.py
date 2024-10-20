from rest_framework import serializers
from .models import CartItem, Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name", "price", "quantity"]

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['item', 'quantity']

    def validate_quantity(self, data):
        item = data['item']
        quantity = data['quantity']

        if quantity >= item.quantity:
            raise serializers.ValidationError("{} exceeds remaining stock of {}.".format(item.name, item.quantity))
        
        return data
