from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm


class PersianAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="نام کاربری", widget=forms.TextInput(attrs={"autocomplete": "username", "autofocus": True}))
    password = forms.CharField(label="گذرواژه", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))
    error_messages = {"invalid_login": "نام کاربری یا گذرواژه صحیح نیست.", "inactive": "این حساب کاربری غیرفعال است."}


class PersianPasswordChangeForm(PasswordChangeForm):
    error_messages = {**PasswordChangeForm.error_messages, "password_incorrect": "گذرواژه فعلی صحیح نیست.", "password_mismatch": "گذرواژه جدید و تکرار آن یکسان نیستند."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {"old_password": "گذرواژه فعلی", "new_password1": "گذرواژه جدید", "new_password2": "تکرار گذرواژه جدید"}
        for name, label in labels.items():
            self.fields[name].label = label
            self.fields[name].help_text = ""
            self.fields[name].widget.attrs.update({"autocomplete": "current-password" if name == "old_password" else "new-password"})
