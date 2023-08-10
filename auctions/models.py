from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    pass

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, null=False, blank=False)

    def __str__(self):
        return f"{self.id} - {self.name}"

class Listing(models.Model):
    id = models.AutoField(primary_key=True)
    lister = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(null=False, blank=False)
    start = models.FloatField(null=False, blank=False)
    current = models.FloatField(null=True, blank=True)
    status = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    imagelink = models.CharField(max_length=510, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category")
    created_on = models.DateTimeField(null=False, default = now)

    def __str__(self):
        return self.name


class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid_details")
    amount = models.FloatField(null=False, blank=False)
    submitted_on = models.DateTimeField(null=False, default = now)

    def __str__(self):
        return f"${self.amount} bid by {self.user.username}"

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(null=False, blank=False, default=1)
    submitted_on = models.DateTimeField(null=False, default = now)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.submitted_on}"

class Watchlist(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchdetails")
    added_on = models.DateTimeField(null=False, default = now)

    def __str__(self):
        return self.item.name

