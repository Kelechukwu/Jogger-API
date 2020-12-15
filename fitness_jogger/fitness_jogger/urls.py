"""fitness_jogger URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from api import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', views.UsersViewSet, 'users')
router.register(r'jogs', views.JogsViewSet, 'jogs')
router.register(r'myjogs', views.UserJogsViewSet, 'myjogs')
router.register(r'profile', views.UserProfileViewSet, 'profile')


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include(router.urls)),
    # path("myjogs", views.UserJogs.as_view()),
    path("signup", views.SignUp.as_view(), name='signup'),
    path('login', TokenObtainPairView.as_view(), name='login'),
    path("weekly_report/<user_id>", views.UserWeeklyReportView.as_view()),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]
