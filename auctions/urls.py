from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new-listing", views.newListing, name="newListing"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category_name>", views.categoryListings, name="categoryListings"),
    path("Your-listings", views.yourListings, name="yourListings"),
    path("listing/<int:id>/bid", views.addBid, name="addBid"),
    path("listing/<int:id>/watchlist", views.addAndRemoveWatchlist, name="addAndRemoveWatchlist"),
    path("listing/<int:id>/closeListing", views.closeListing, name="closeListing"),
    path("listing/<int:id>/comment", views.comment, name="comment"),
]
