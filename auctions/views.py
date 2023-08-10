from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import auth
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist as DoesNotExist

from .models import User, Listing, Watchlist, Bid, Comment, Category

def get_user(request):
    if request.user.is_authenticated:

        try: 
            user =  User.objects.get(pk=int(request.user.id))
            return user
        except DoesNotExist:
            return None
        
def check_integer(number):
    try:
        number = int(number)
        return number
    except:
        return None


def index(request):
    listings = Listing.objects.all()

    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return redirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return redirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def add(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            name = request.POST["title"]
            description = request.POST["description"]
            start = request.POST["start"]
            volpicture = request.POST["picture"]
            volcategory = request.POST["category"]

            if not name:
                messages.error(request, "Name of the listing is required!")
                return render(request, "auctions/add.html")

            if not description:
                messages.error(request, "Description of the listing is required!")
                return render(request, "auctions/add.html")

            if not start:
                messages.error(request, "Starting price of the listing is required!")
                return render(request, "auctions/add.html",)
            
            try:
                volcategory = int(volcategory)
            except:
                volcategory = None

            if volcategory is not None:
                try: 
                    category = Category.objects.get(pk=int(volcategory))
                except DoesNotExist:
                    messages.error(request, "The category you provided for the item does not exist.")
                    return redirect(reverse("add"))
            else:
                category = Category.objects.get(pk=2)

            picture = volpicture if volpicture else None

            try:
                lister = get_user(request)
                if lister is not None:
                    addlisting = Listing(name = name, lister = lister, description = description, start = start, current = start, imagelink = picture, category = category)
                    addlisting.save()
                    messages.success(request, "Your listing was successfully added!")
                    return redirect(reverse("add"))
                else:
                    messages.error(request, "Invalid user request!")
                    return redirect(reverse("add"))
            except Exception as e:
                messages.error(request, e)
                return redirect(reverse("add"))
        else:
            return render(request, "auctions/add.html")
    else:
        messages.error(request, "Please log in to create a listing.")
        return redirect(reverse("login"))


def listing(request, listing_id):
    if request.user.is_authenticated:
        user = get_user(request)
        watchlist_items = [item.item for item in user.watchlist.all()] 

    try: 
        item = Listing.objects.get(pk=int(listing_id))
    except DoesNotExist:
        messages.error(request, "The item you wanted to check does not exist.")
        return render(request, "auctions/listing.html")

    bids = len([bid.amount for bid in item.bid_details.all()])

    comments = [comment for comment in Comment.objects.filter(item=item).order_by('-submitted_on')]

    if request.user.is_authenticated and item in watchlist_items:
        return render(request, "auctions/listing.html", {
            "listing": item, "watchlist": True, "bid": bids, "comments": comments
        })
    
    elif request.user.is_authenticated and item not in watchlist_items:
        return render(request, "auctions/listing.html", {
            "listing": item, "watchlist": False, "bid": bids, "comments": comments
        })
    
    else:
        return render(request, "auctions/listing.html", {
            "listing": item, "watchlist": False, "bid": bids, "comments": comments
        })
    

def bid(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            user = get_user(request)
            item_id = check_integer(request.POST["id"])
            bid = request.POST["amount"]
            if item_id is not None:
                try:
                    item = Listing.objects.get(pk=item_id)
                except DoesNotExist:
                    return redirect(reverse("listing", args=(item_id,)))
                
                try: 
                    bid = float(bid)
                except:
                    messages.error(request, "You need to put a valid number for your bid.")
                    return redirect(reverse("listing", kwargs={'listing_id': int(item_id)}))

                if item.current < bid:
                    try:
                        addbid = Bid(user = user, item = item, amount = bid)
                        item.current = bid
                        item.winner = user
                        addbid.save()
                        item.save()
                        messages.success(request, f"Your bid amount of ${bid} was successfully submitted and accepted!")
                        return redirect(reverse("listing", kwargs={'listing_id': int(item_id)}))
                    except:
                        messages.error(request, "We encountered an error while trying to submit your bid, try again later!")
                        return redirect(reverse("listing", kwargs={'listing_id': int(item_id)}))
                else:
                    messages.error(request, "Your bid amount is lower than or equal to the current highest bid! Submit a better one.")
                    return redirect(reverse("listing", kwargs={'listing_id': int(item_id)}))
            else:
                messages.error(request, "You provided an invalid listing ID.")
                return redirect(reverse("index"))
        else:
            messages.error(request, "You provided an invalid request.")
            return redirect(reverse("index"))
    else:
        messages.error(request, "You need to login to submit a bid.")
        return redirect(reverse("login"))
    

def update_watchlist(request, listing_id):
    if request.user.is_authenticated:
        user = get_user(request)
        try:
            listing = Listing.objects.get(pk=listing_id)
        except DoesNotExist:
            return redirect(reverse("listing", kwargs={'listing_id': int(listing_id)}))

        deletewlitem = Watchlist.objects.filter(item=listing).first()

        if deletewlitem is not None:
            try:
                deletewlitem.delete()
                messages.success(request, "Item has been removed from your watchlist!")
                return redirect(reverse("listing", kwargs={'listing_id': int(listing_id)}))
            except:
                messages.error(request, "We encountered an error while updating your watchlist. Try again later.")
                return redirect(reverse("listing", kwargs={'listing_id': int(listing_id)}))

        else:
            try:
                addwlitem = Watchlist(user = user, item = listing)
                addwlitem.save()
                messages.success(request, "Item has been added to your watchlist!")
                return redirect(reverse("listing", kwargs={'listing_id': int(listing_id)}))
            except:
                messages.error(request, "We encountered an error while updating your watchlist. Try again later.")
                return redirect(reverse("listing", kwargs={'listing_id': int(listing_id)}))

    else:
        messages.error(request, "You are not logged-in! Login to access watchlists.")
        return redirect("login")
        

def watchlist(request):
    if request.user.is_authenticated:
        user = get_user(request)
        watchlist = [item.item for item in user.watchlist.all()]
        return render(request, "auctions/watchlist.html", {
            "watchlist": watchlist
        })
        
    else:
        messages.error(request, "You are not logged-in! Login to access watchlists.")
        return redirect(reverse("login"))


def comment(request, listing_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            user = get_user(request)
            comment = request.POST["comment"]
            if user is not None:
                try:
                    listing = Listing.objects.get(pk=listing_id)
                except DoesNotExist:
                    return redirect(reverse("listing", kwargs={'listing_id': int(listing_id)}))
            
                if comment is not None:

                    try:
                        newcomment = Comment(user = user, item = listing, comment = comment)
                        newcomment.save()
                        messages.success(request, "Your comment was submitted successfully!")
                        return redirect(reverse("listing", kwargs={'listing_id': int(listing_id)}))
                    except:
                        messages.error(request, "We encountered an error while submitting your comment. Try again later.")
                        return redirect(reverse("listing", kwargs={'listing_id': int(listing_id)}))
    else:
        messages.error(request, "You need to login to provide comments.")
        return redirect(reverse("login"))


def categories(request):
    categories = Category.objects.all().order_by("name")
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category(request, category_id):
    try: 
        category = Category.objects.get(id=category_id)
    except DoesNotExist:
        messages.error(request, "The category that you chose does not exist.")
        return redirect(reverse("categories"))
    
    listings = Listing.objects.filter(category=category).all().order_by("-created_on")

    return render(request, "auctions/category.html", {
        "items": listings, "category": category
    })

def close(request, listing_id):
    if request.user.is_authenticated:
        user = get_user(request)
        try:
            listing = Listing.objects.get(id=listing_id)
        except DoesNotExist:
            messages.error(request, "The listing you submitted does not exist.")
            return redirect(reverse("listing"), kwargs={"listing_id": int(listing_id)})
        
        bids = len([bid.amount for bid in listing.bid_details.all()])

        if listing.lister == user and bids > 0:
            listing.status = False
            listing.winner = Bid.objects.filter(item=listing, amount=listing.current).first().user
            listing.save()
            messages.success(request, "Listing has successfully been closed!")
            return redirect(reverse("listing", kwargs={"listing_id": listing.id}))
        elif listing.lister == user and bids == 0:
            listing.status = False
            listing.save()
            messages.success(request, "Listing has successfully been closed!")
            return redirect(reverse("listing", kwargs={"listing_id": listing.id}))
        else:
            messages.error(request, "You are not the one who submitted this listing!")
            return redirect(reverse("listing", kwargs={"listing_id": listing.id}))
    else:
        messages.error(request, "You need to login to close a listing that you submitted.")
        return redirect(reverse("login"))