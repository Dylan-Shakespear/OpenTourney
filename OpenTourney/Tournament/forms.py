from django import forms
from django.contrib.auth.forms import AuthenticationForm


class CustomLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['remember_me'].widget.attrs.update({'class': 'form-check-input'})

    def get_user(self):
        user = super(CustomLoginForm, self).get_user()
        user.remember_me = self.cleaned_data.get('remember_me')
        return user
