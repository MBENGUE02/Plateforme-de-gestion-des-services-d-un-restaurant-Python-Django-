from django import forms
from .models import ElementMenu, ImageMenu, MenuJour, Reservation

class ElementMenuForm(forms.ModelForm):
    class Meta:
        model = ElementMenu
        fields = ['libelle', 'description', 'prix', 'categorie', 'allergenes', 'est_epuise', 'specialite_jour']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows' : 2}),
            'prix': forms.NumberInput(attrs={'class': 'form-control'}),
            #'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'allergenes': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'est_epuise': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'specialite_jour': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ImageMenuForm(forms.ModelForm):
    class Meta:
        model = ImageMenu
        fields = ['image']
        widgets = {
            'element': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class MenuJourForm(forms.ModelForm):
    plats = forms.ModelMultipleChoiceField(
        queryset=ElementMenu.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'size': '8'  # nombre d’éléments visibles sans scroll (modifiable)
        }),
        label="Sélectionnez les plats du jour"
    )

    class Meta:
        model = MenuJour
        fields = ['date', 'plats']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }
        labels = {
            'date': "Date du Menu",
            'plats': "Plats du jour"
        }


class AjouterPlatForm(forms.Form):
    plat_id = forms.IntegerField(widget=forms.HiddenInput())
    quantite = forms.IntegerField(min_value=1, initial=1, label='')


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre téléphone'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'heure': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'nombre_personnes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de personnes'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Message', 'rows': 5}),
        }