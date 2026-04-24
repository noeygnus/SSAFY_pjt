from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("password/change/", views.CustomPasswordChangeView.as_view(), name="password_change"),
    path("password/change/done/", views.CustomPasswordChangeDoneView.as_view(), name="password_change_done"),
    path("profile/", views.profile, name="profile"),
    path("profile/analysis/", views.investment_analysis, name="investment_analysis"),
]
