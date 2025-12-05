from django import forms
from .models import Utilisateurs, Tache

class UtilisateurForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Mot de passe"
    )

    class Meta:
        model = Utilisateurs
        fields = [
            'prenom',
            'nom',
            'login',
            'password',
            'telephone',
            'mail',
            'type_utilisateur'
        ]
        labels = {
            'prenom': 'Prénom',
            'nom': 'Nom',
            'login': 'Nom d’utilisateur',
            'password': 'Mot de passe',
            'telephone': 'Téléphone',
            'mail': 'Email',
            'type_utilisateur': 'Type d’utilisateur',
        }
        widgets = {
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'login': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'mail': forms.EmailInput(attrs={'class': 'form-control'}),
            'type_utilisateur': forms.Select(attrs={'class': 'form-select'}),
        }


class TacheForm(forms.ModelForm):
    class Meta:
        model = Tache
        fields = ['personnel', 'description', 'date', 'heure_debut', 'heure_fin']
        widgets = {
            'personnel': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
