from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import User, Category, AuctionListing, Comment, Bid, Watchlist
from django.contrib.auth.decorators import login_required
from django.contrib import messages




def index(request):
    listings = AuctionListing.objects.filter(is_active=True).all()
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
            return HttpResponseRedirect(reverse(request.GET.get("next") or "index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")



def newListing(request):
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, "auctions/newListing.html", {
            "categories": categories
        })
    else:
        title = request.POST['title']
        description = request.POST['description']
        imageUrl = request.POST['image-url']
        price = request.POST['price']
        category_name = request.POST['category']
        category = Category.objects.get(name=category_name)
        user = request.user

        listing = AuctionListing(
            title = title,
            description = description,
            img_url = imageUrl,
            starting_price = price,
            category = category,
            user = user
            )
        listing.save()
        return HttpResponseRedirect(reverse("index"))
    

def listing(request, id):
    listing = AuctionListing.objects.get(id=id)
    comments = Comment.objects.filter(listing = listing)
    if request.user.is_authenticated:
        find = Watchlist.objects.filter(user=request.user, listing=listing)
        is_inlist = find.exists()
    else:
        is_inlist = False

    highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
    if highest_bid:
        highest_bidder = highest_bid.bidder 
    else:
        highest_bidder = None

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "is_inlist": is_inlist,
        "winner": highest_bidder,
        "comments": comments
    })
    

def watchlist(request):
    userWatchlist =  Watchlist.objects.filter(user=request.user).all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": userWatchlist
    })


@login_required(login_url='login')
def addAndRemoveWatchlist(request, id):
    user = request.user
    listing =  AuctionListing.objects.get(id=id)
    comments = Comment.objects.filter(listing=listing)
    find = Watchlist.objects.filter(user=user, listing=listing)
    is_inlist = find.exists()
    if request.method == "POST":
        if is_inlist:
            find.delete()
            print("Removed from Watchlist")
        else:
            Watchlist.objects.create(user=user, listing=listing)
            print("Added to Watchlist") 

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "is_inlist": not is_inlist,
            "comments": comments
        })
    else:
        return redirect("listing", id=id) 
    
@login_required(login_url='login')
def addBid(request, id):
    bidder = request.user
    listing = AuctionListing.objects.get(id=id)
    current_price = listing.current_price
    starting_price = listing.starting_price

    if request.method == "POST":
        try:
            amount = float(request.POST["amount"])
        except ValueError:
            messages.error(request, "Invalid bid amount.")
            return redirect("listing", id=id)

        if not current_price:
            if amount >= starting_price:
                listing.current_price = amount
                bid = Bid(bidder=bidder, listing=listing, amount=amount)
                bid.save()
                listing.save()
                messages.success(request, "Your bid has been placed successfully!")
            else:
                messages.error(request, "Your bid must be at least as large as the starting price.")
        else:
            if amount > current_price:
                listing.current_price = amount
                bid = Bid(bidder=bidder, listing=listing, amount=amount)
                bid.save()
                listing.save()
                messages.success(request, "Your bid has been placed successfully!")
            else:
                messages.error(request, "Your bid must be bigger than the highest bid.")

    return redirect("listing", id=id)

def closeListing(request, id):
    listing = AuctionListing.objects.get(id=id)

    if listing.user == request.user:
        listing.is_active = False

        highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()

        if highest_bid:
            highest_bidder = highest_bid.bidder 
        else:
            highest_bidder = None
        
        listing.save()
        messages.success(request, "The auction has been closed.")
        is_inlist = Watchlist.objects.filter(user=request.user, listing=listing).exists()

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "winner": highest_bidder,
            "is_inlist": is_inlist
        })

@login_required(login_url='login')
def comment(request, id):
    if request.method == "POST":
        listing = AuctionListing.objects.get(id=id)
        user = request.user
        comment = request.POST["comment"]
        comment = Comment(
            listing = listing,
            user = user,
            comment = comment
        )
        comment.save()
        comments = Comment.objects.filter(listing = listing)
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments
        })

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def categoryListings(request, category_name):
    category = Category.objects.get(name=category_name)
    listings = AuctionListing.objects.filter(category = category, is_active=True).all()
    return render(request, "auctions/categoryListings.html", {
        "listings": listings,
        "category": category
    })


def yourListings(request):
    listings = AuctionListing.objects.filter(user = request.user).all()
    return render(request, "auctions/yourListings.html", {
        "listings": listings,
    })
