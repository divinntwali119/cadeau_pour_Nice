"""
=============================================================
FORMULAIRES — App Accounts
=============================================================
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class ConnexionForm(AuthenticationForm):
    """Formulaire de connexion personnalisé avec styles."""

    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Votre identifiant ou email',
            'id': 'id_username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'id': 'id_password',
            'autocomplete': 'current-password',
        })
    )


class InscriptionForm(forms.ModelForm):
    """Formulaire d'inscription d'un nouveau membre."""

    telephone = forms.CharField(
        label="Numéro de téléphone",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+243 ... ou 09...',
            'autocomplete': 'tel',
        })
    )
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Minimum 8 caractères',
            'autocomplete': 'new-password',
        }),
        min_length=8,
        help_text="Minimum 8 caractères."
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Répétez le mot de passe',
            'autocomplete': 'new-password',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': "Nom d'utilisateur",
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Adresse e-mail',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Identifiant unique',
                'autocomplete': 'username',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Votre prénom',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Votre nom de famille',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'votre@email.com',
                'autocomplete': 'email',
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà pris. Veuillez en choisir un autre.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("Un compte avec cet email existe déjà.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return password2
