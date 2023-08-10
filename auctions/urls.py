from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add", views.add, name="add"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("bid", views.bid, name="bid"),
    path("categories", views.categories, name="categories"),
    path("updatewatchlist/<int:listing_id>", views.update_watchlist, name="updatewatchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("category/<int:category_id>", views.category, name="category"),
    path("close/<int:listing_id>", views.close, name="close")
]
