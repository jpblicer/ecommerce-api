from rest_framework import serializers
from .models import CartItem, Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "name", "price", "quantity"]

class CartSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())

    class Meta:
        model = CartItem
        fields = ['item', 'quantity']

    def validate_quantity(self, quantity):
        item_id = self.initial_data.get('item')
        item = Item.objects.get(id=item_id)

        if quantity > item.quantity:
            raise serializers.ValidationError(
                "{} exceeds remaining stock of {}.".format(item.name, item.quantity)
            )
        
        return quantity

    def create(self, validated_data):
        item = validated_data.pop('item')
        cart_item, created = CartItem.objects.get_or_create(
            cart=self.context['request'].cart,
            item=item,
            defaults={'quantity': validated_data['quantity']}
        )
        
        if not created:
            cart_item.quantity += validated_data['quantity']
            cart_item.save()
        
        return cart_item
