"""
URL configuration for codehub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from store import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    path("register/",views.SignupView.as_view(),name="signup"),

    path("",views.LoginView.as_view(),name="login"),

    path("index/",views.IndexView.as_view(),name="index"),

    path("profile/<int:pk>/update",views.UserprofileUpdateView.as_view(),name="profile-update"),

    path("project/sell/",views.ProjectSellView.as_view(),name="project-add"),

    path("myworks/all/",views.ProjectListView.as_view(),name="myworks"),

    path("works/<int:pk>/remove",views.ProjectDeleteView.as_view(),name="work-delete"),

    path("project/<int:pk>/details",views.ProjectDetailView.as_view(),name="project-detail"),

    path("project/<int:pk>/wishlistadd",views.AddtoWishlist.as_view(),name="addtoWishlist"),

    path("wishlist/summary/",views.MyCartView.as_view(),name="cart-summary"),

    path("wishlist/<int:pk>/remove",views.WishListItemRemoveview.as_view(),name="wishlistitem-remove"),

    path("payment/",views.CheckOutView.as_view(),name="checkout"),

    path("payment/verification/",views.PaymentVerificationView.as_view(),name="payment-verification"),

    path("ordersummary/",views.MyPurchaseView.as_view(),name="orders"),

    path("review/<int:pk>/add",views.ReviewCreateView.as_view(),name="review-add")




] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
