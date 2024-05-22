from django.urls import path

from . import views
from . import user_info

app_name = "roulette"
urlpatterns = [
    path("", views.index, name="index"),
    path("get_status/", views.get_status, name="get_status"),
    path("get_user_info/<int:first_request>", views.get_user_info, name="get_user_info"),
    path("get_user_info/", views.get_user_info, name="get_user_info"),
    path("get_wallet/", views.get_wallet, name="get_wallet"),
    path("get_history/<int:num>", views.get_history, name="get_history"),
    path("check_auth/", views.check_auth, name="check_auth"),
    path("make_bet/", views.make_bet, name="make_bet"),
    path("about/", views.about, name="about"),
    path("user/", user_info.user, name="user"),
]