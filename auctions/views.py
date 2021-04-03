from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.decorators import login_required
from datetime import datetime, timezone
from django.urls import reverse

from .models import *
from .forms import auctions_new,CommentForm,Activeform

def index(request):
    Listings = Auction.objects.all().values()
    print(Listings)
    return render(request, "auctions/index.html", {
        "auction_list": Listings
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
            return HttpResponseRedirect(reverse("index"))
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




def auctions(request):
    # Get all auctions, newest first
    auction_list = Auction.objects.order_by('-date_added')
    for a in auction_list:
        a.resolve()
    template = loader.get_template('auctions/index.html')
    context = {
        'title': "All auctions",
        'auction_list': auction_list,
    }
    return HttpResponse(template.render(context, request))

# Details on some auction
def detail(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    auction.resolve()
    already_bid = False
    if request.user.is_authenticated:
        if auction.author == request.user:
            own_auction = True
            return render(request, 'auctions/detail.html', {'auction': auction, 'own_auction': own_auction})

        user_bid = Bid.objects.filter(bidder=request.user).filter(auction=auction).first()
        if user_bid:
            already_bid = True
            bid_amount = user_bid.amount
            return render(request, 'auctions/detail.html', {'auction': auction, 'already_bid': already_bid, 'bid_amount': bid_amount})

    return render(request, 'auctions/detail.html', {'auction': auction, 'already_bid': already_bid})
    # try:
    #     auction = Auction.objects.get(pk=auction_id)
    # except Auction.DoesNotExist:
    #     raise Http404("Auction does not exist")
    # return render(request, 'auctions/detail.html', {'auction': auction})

# def results(request, auction_id):
#     response = "You're looking at the results of auction %s."
#     return HttpResponse(response % auction_id)

@login_required
def close(request,id):
    post = Auction.objects.get( id=id)
    context = {
        "title": post.title,
        "description": post.desc,
        "image": post.image,
        "min_value": post.min_value,
        "category": post.category,
        "comments": post.comments,
        "post.comment": post.comments
    }
    if request.method == "POST":

        formcl = Activeform(request.POST)

        if formcl.is_valid():
            produ = formcl.save()
            produ.save()

            return HttpResponseRedirect('/', auction_id=auction_id)
    else:
        formcl = Activeform(initial={'author_id': request.user.id, 'is_active': None})
    return render(request,"auctions/close.html",{"formcl": Activeform} )


# Bid on some auction
@login_required
def bid(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    auction.resolve()
    bid = Bid.objects.filter(bidder=request.user).filter(auction=auction).first()


    if not auction.is_active:
        return render(request, 'auctions/detail.html', {
            'auction': auction,
            'error_message': "The auction has expired.",
        })

    try:
        bid_amount = request.POST['amount']
        # Prevent user from entering an empty or invalid bid
        if not bid_amount or int(bid_amount) < auction.min_value:
            raise(KeyError)
        if not bid:
            # Create new Bid object if it does not exist
            bid = Bid()
            bid.auction = auction
            bid.bidder = request.user
        bid.amount = bid_amount
        bid.date = datetime.now(timezone.utc)
    except (KeyError):
        # Redisplay the auction details.
        return render(request, 'auctions/detail.html', {
            'auction': auction,
            'error_message': "Invalid bid amount.",
        })
    else:
        bid.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        # return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
        return HttpResponseRedirect(reverse('my_bids', args=()))

        # TODO redirect to my bids
        # template = loader.get_template('auctions/my_bids.html')
        # context = {
        #     'my_bids_list': my_bids_list,
        # }
        # return HttpResponse(template.render(context, request))

        # return HttpResponse(f"You just bid {bid_amount} on auction {auction_id}.")

# Create auction
@login_required
def create(request):
    if request.method == "POST":

        form = auctions_new(request.POST)

        if form.is_valid():
            prod = form.save(commit=False)
            prod.By = request.user
            prod.bid = None
            prod.save()

            return HttpResponseRedirect('/')

    else:
        form = auctions_new(initial={'user': request.user, 'bid': None})
    return render(request, 'auctions/create.html', {'form': auctions_new})
def categories(request):
    return render(request, "auctions/categories.html")


def fashion(request):
    listing = Auction.objects.filter(category='fashion')
    return render(request, "auctions/fashion.html", {
        "listing": listing,
    })


def home_supplies(request):
    listing = Auction.objects.filter(category='home supplies')
    return render(request, "auctions/home_supplies.html", {
        "listing": listing,
    })


def electronics(request):
    listing = Auction.objects.filter(category='Electronics')
    return render(request, "auctions/electronics.html", {
        "listing": listing,
    })


def services(request):
    listing = Auction.objects.filter(category='Services')
    return render(request, "auctions/services.html", {
        "listing": listing,
    })


@login_required
def my_auctions(request):
    # Get all auctions by user, sorted by date
    my_auctions_list = Auction.objects.all().filter(author=request.user).order_by('-date_added')
    for a in my_auctions_list:
        a.resolve()
    template = loader.get_template('auctions/my_auctions.html')
    context = {
        'my_auctions_list': my_auctions_list,
    }
    return HttpResponse(template.render(context, request))

@login_required
def my_bids(request):
    # Get all bids by user, sorted by date
    my_bids_list = Bid.objects.all().filter(bidder=request.user).order_by('-date')
    for b in my_bids_list:
        b.auction.resolve()

    template = loader.get_template('auctions/my_bids.html')
    context = {
        'my_bids_list': my_bids_list,
    }
    return HttpResponse(template.render(context, request))

@login_required
def get_comments(request, id):
    post = get_object_or_404(Auction, id=id)
    context = {
        "title": post.title,
        "description": post.desc,
        "image": post.image,
        "min_value": post.min_value,
        "category": post.category,
        "comments": post.comments,
        "post.comment": post.comments
    }
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.auction = post
            comment.user = request.user
            comment.save()


            return redirect('detail',auction_id=id)

    else:
        form = CommentForm()
    return render(request, 'auctions/addcomment.html', {'CommentForm': form})


def watchlist(request):
    if request.user:

        w = Watchlist.objects.filter(user=request.user)
        items = []
        for i in w:
            items.append(Auction.objects.filter(id=i.watch_list))
            w = Watchlist()
            w.user = request.user
            w.watch_list = i.watch_list
            w.save()
            return render(request, 'auctions/watchlist.html', {
                "listing": w,
            })

    return render(request, 'auctions/watchlist.html', {
                "listing": w,
            })

def removewatchlist(request,auction_id):
    if request.user:
        try:
            w = Watchlist.objects.get(user=request.user,auction_id=auction_id)
            w.delete()
            return redirect('watchlist',auction_id=auction_id)
        except:
            return redirect('watchlist',auction_id=auction_id)
    else:
        return redirect('index')
