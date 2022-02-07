from django.urls import path
from . import views


app_name = "users"

urlpatterns = [
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("profile", views.profile_view, name="profile"),
    path("logout", views.logout_view, name="logout"),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('user_list', views.UserList.as_view(), name='user_list')
]