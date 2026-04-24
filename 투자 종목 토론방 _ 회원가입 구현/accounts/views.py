from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from community.llm import analyze_investment_profile
from community.models import Comment, Post
from community.utils import load_assets
from .forms import KoreanAuthenticationForm, KoreanPasswordChangeForm, SignUpForm


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("community:asset_list")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = KoreanAuthenticationForm
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("community:asset_list")


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = KoreanPasswordChangeForm
    success_url = reverse_lazy("accounts:password_change_done")


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"


@login_required
def profile(request):
    user = request.user
    asset_map = {asset["id"]: asset["name"] for asset in load_assets()}
    interest_ids = [item for item in user.interest_stocks.split(",") if item]
    interest_names = [asset_map.get(asset_id, asset_id) for asset_id in interest_ids]
    posts = Post.objects.filter(author=user.username)
    comments = Comment.objects.filter(author=user.username).select_related("post")
    context = {
        "profile_user": user,
        "interest_names": interest_names,
        "posts": posts,
        "comments": comments,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def investment_analysis(request):
    user = request.user
    posts = Post.objects.filter(author=user.username)
    comments = Comment.objects.filter(author=user.username).select_related("post")
    result = analyze_investment_profile(posts, comments)
    context = {
        "result": result,
        "post_count": posts.count(),
        "comment_count": comments.count(),
    }
    return render(request, "accounts/investment_analysis.html", context)
