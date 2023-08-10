from django.contrib import admin
from .models import User, Listing, Watchlist, Bid, Comment, Category

# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    fields = ["name", "description", "lister", "start", "current", "imagelink", "category", "created_on", "status"]
    list_display = ('id', '__str__', 'lister') 

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'user') 

admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Category)