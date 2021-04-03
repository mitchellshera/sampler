from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("create", views.create, name="create"),
    path("auctions", views.auctions, name="auctions"),
    # Example: /auctions/5/
    path('detail/<int:auction_id>/', views.detail, name='detail'),
    # Example: /auctions/5/results/
    # path('<int:auction_id>/results/', views.results, name='results'),
    # Example: /auctions/5/bid/
    path('<int:auction_id>/bid/', views.bid, name='bid'),
    path("categories/fashion", views.fashion, name="fashion"),
    path("categories/services", views.services, name="services"),
    path("categories/home_supplies", views.home_supplies, name="home supplies"),
    path('detail/<int:id>/comments/', views.get_comments, name="comments"),
    #Example: detail/2/comment
    path("categories/electronics", views.electronics, name="electronics"),
    path("categories", views.categories , name= "categories"),
    path("my_bids", views.my_bids, name="my_bids"),
    path("my_auctions", views.my_auctions, name="my_auctions"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("close", views.close, name="close"),
    path("register", views.register, name="register")
]
