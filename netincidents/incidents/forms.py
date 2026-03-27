from django import forms
from django.contrib.auth.models import User
from .models import Incident, Commentaire, Equipement, ProfilUtilisateur


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            'titre', 'description', 'categorie', 'priorite',
            'statut', 'equipements', 'impact', 'cause_racine',
            'solution_appliquee', 'assigne_a',
        ]
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Panne switch cœur de réseau Bâtiment A'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Décrivez l\'incident en détail...'
            }),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'priorite': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'equipements': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'impact': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Quel est l\'impact sur les utilisateurs / services ?'
            }),
            'cause_racine': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Cause identifiée...'
            }),
            'solution_appliquee': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Actions correctives réalisées...'
            }),
            'assigne_a': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigne_a'].queryset = User.objects.filter(is_active=True)
        self.fields['assigne_a'].empty_label = "--- Non assigné ---"
        self.fields['equipements'].required = False
        for field in self.fields.values():
            if not field.required:
                field.label_suffix = ''


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['type_commentaire', 'contenu']
        widgets = {
            'type_commentaire': forms.Select(attrs={'class': 'form-select'}),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Votre commentaire ou action effectuée...'
            }),
        }


class EquipementForm(forms.ModelForm):
    class Meta:
        model = Equipement
        fields = ['nom', 'type_equipement', 'adresse_ip', 'localisation', 'description', 'statut']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type_equipement': forms.Select(attrs={'class': 'form-select'}),
            'adresse_ip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '192.168.1.1'}),
            'localisation': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }


class FiltreIncidentForm(forms.Form):
    recherche = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher un incident...'
        })
    )
    statut = forms.ChoiceField(
        required=False,
        choices=[('', 'Tous les statuts')] + Incident.STATUT,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priorite = forms.ChoiceField(
        required=False,
        choices=[('', 'Toutes priorités')] + Incident.PRIORITE,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    categorie = forms.ChoiceField(
        required=False,
        choices=[('', 'Toutes catégories')] + Incident.CATEGORIE,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class ProfilForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ProfilUtilisateur
        fields = ['telephone', 'departement', 'avatar']
        widgets = {
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'departement': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
