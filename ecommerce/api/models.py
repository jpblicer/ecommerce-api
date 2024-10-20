from django.db import models

# Create your models here.

class Item(models.Model):
    name = models.CharField(max_length = 100)
    price = models.IntegerField()
    quantity = models.IntegerField()

class Cart(models.Model):
    items = models.ManyToManyField(Item, through='CartItem')

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField

    class Meta:
        unique_together = ('cart', 'item')
