from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm

from community.utils import load_assets
from .models import CustomUser


def asset_choices():
    return [(asset["id"], asset["name"]) for asset in load_assets()]


class SignUpForm(UserCreationForm):
    error_messages = {
        "password_mismatch": "비밀번호와 비밀번호 확인이 일치하지 않습니다.",
    }

    nickname = forms.CharField(label="닉네임", max_length=50)
    profile_image = forms.ImageField(label="프로필 이미지", required=False)
    interest_stocks = forms.MultipleChoiceField(
        label="관심 종목",
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = ("username", "password1", "password2", "nickname", "profile_image", "interest_stocks")
        labels = {
            "username": "아이디",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["interest_stocks"].choices = asset_choices()
        self.fields["username"].help_text = ""
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""

    def clean_interest_stocks(self):
        return ",".join(self.cleaned_data.get("interest_stocks", []))

    def clean_username(self):
        username = self.cleaned_data["username"]
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("이미 사용 중인 아이디입니다.")
        return username


class KoreanAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="아이디")
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput)

    error_messages = {
        "invalid_login": "아이디 또는 비밀번호가 올바르지 않습니다.",
        "inactive": "비활성화된 계정입니다.",
    }


class KoreanPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="현재 비밀번호", widget=forms.PasswordInput)
    new_password1 = forms.CharField(label="새 비밀번호", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="새 비밀번호 확인", widget=forms.PasswordInput)

    error_messages = {
        "password_incorrect": "현재 비밀번호가 올바르지 않습니다.",
        "password_mismatch": "새 비밀번호와 확인 비밀번호가 일치하지 않습니다.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].help_text = ""
        self.fields["new_password2"].help_text = ""
