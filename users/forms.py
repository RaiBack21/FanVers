from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Message
from django.forms import ModelForm, FileInput

class CreationUserForm(UserCreationForm):
    # class Meta:
    #     model = User
    #     fields = ['username', 'email', 'password1', 'password2']
    #     labels = {
    #         'username': 'Логін',
    #         'email': 'Email',
    #         'password1': 'Пароль',
    #         'password2': 'Підтвердження пароля'
    #     }

    username = forms.CharField(label='Логін')
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Підтвердження пароля', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(CreationUserForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control input-box form-ensurance-header-control'})


class LoginForm(forms.Form):
    username = forms.CharField(label='Логін')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control input-box form-ensurance-header-control'})


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['username', 'email',
                  'about', 'image',
                  ]
        labels = {
            'username': 'Логін',
            'email': 'Email',
            'about': 'Детально про себе',
            'image': 'Змінити фото профілю',
        }
        widgets = {
            'image': FileInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control input-box form-ensurance-header-control'})



class AddFundsForm(forms.Form):
    amount = forms.DecimalField()

class PurchaseChapterForm(forms.Form):
    chapter_id = forms.IntegerField()


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']


class RegistrationForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
