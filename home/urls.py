from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),

    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name="register"),
    path('logout/', views.logoutPage, name="logout"),
    path('about/', views.aboutPage, name="about"),
    path('profile/<str:pk>', views.profilePage, name="profile"),
]
