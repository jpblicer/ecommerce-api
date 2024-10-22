from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    name = models.CharField(max_length = 100)
    price = models.IntegerField()
    quantity = models.PositiveIntegerField(default=0)

# Price is assumed to be in Yen without decimals.

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    items = models.ManyToManyField(Item, through='CartItem')

# For now there is no authenticated user. Just allow for anonymous user

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('cart', 'item')

class PurchaseRecord(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} of {} purchased on {}".format(self.quantity, self.item.name, self.timestamp)
