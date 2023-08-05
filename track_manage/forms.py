from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Ваше имя пользователя',
                                                                            'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль', 'class': 'form-control'}))


class SearchForm(forms.Form):
    search_input = forms.CharField(max_length=150,
                                   widget=forms.TextInput(attrs={'placeholder': _('Номер вагона'),
                                                                 'class': 'form-control form-control-navbar'}))


class ExcelFileForm(forms.Form):
    file_input = forms.FileField(label="Excel файл",
                                 widget=forms.FileInput(attrs={'class': 'form-control form-control-navbar'}))
