from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import timedelta, datetime, timezone
from math import ceil

class User(AbstractUser):
    pass

# Auction duration in minutes
AUCTION_DURATION = 216000

class Auction(models.Model):
    category_choice = (
        ("services", "services"),
        ('fashion', 'fashion'),
        ("home supplies", "home supplies"),
        ("electronics", "electronics")
    )
    active_choice =(("active" , "active"),
                    ("not active", "non active"))
    category = models.CharField(choices=category_choice, max_length=62)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    desc = models.CharField(max_length=2000, blank=True)
    image = models.URLField(blank=True, max_length=500 )
    min_value = models.IntegerField()
    date_added = models.DateTimeField()
    is_active = models.CharField(choices=active_choice,max_length=62)
    winner = models.ForeignKey(User, on_delete=models.SET("(deleted)"),
                               blank=True,
                               null=True,
                               related_name="auction_winner",
                               related_query_name="auction_winner")
    final_value = models.IntegerField(blank=True, null=True)

    def resolve(self):
        if self.is_active:
            # If expired
            if self.has_expired():
                # Define winner
                highest_bid = Bid.objects.filter(auction=self).order_by('-amount').order_by('date').first()
                if highest_bid:
                    self.winner = highest_bid.bidder
                    self.final_value = highest_bid.amount
                self.is_active = False
                self.save()

    # Helper function that determines if the auction has expired
    def has_expired(self):
        now = datetime.now(timezone.utc)
        expiration = self.date_added + timedelta(minutes=AUCTION_DURATION)
        if now > expiration:
            return True
        else:
            return False

    # Returns the ceiling of remaining_time in minutes
    @property
    def remaining_minutes(self):
        if self.is_active:
            now = datetime.now(timezone.utc)
            expiration = self.date_added + timedelta(minutes=AUCTION_DURATION)
            minutes_remaining = ceil((expiration - now).total_seconds() / 60)
            return(minutes_remaining)
        else:
            return(0)

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    amount = models.IntegerField()
    # is_cancelled = models.BooleanField(default=False)
    date = models.DateTimeField('when the bid was made')

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(
        'Auction', on_delete=models.CASCADE, related_name='comments')
    date_posted = models.DateTimeField(auto_now_add=True)
    comments = models.CharField(max_length=300)

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    watch_list = models.ForeignKey(Auction, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'watch_list')
