from django import forms
from django.contrib.auth.models import User

from .models import Incident


class WorkflowIncidentForm(forms.ModelForm):
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
                'placeholder': 'Ex: Panne switch coeur de reseau Batiment A'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': "Decrivez l'incident en detail..."
            }),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'priorite': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'equipements': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'impact': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': "Quel est l'impact sur les utilisateurs / services ?"
            }),
            'cause_racine': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Cause identifiee...'
            }),
            'solution_appliquee': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Actions correctives realisees...'
            }),
            'assigne_a': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['assigne_a'].queryset = User.objects.filter(is_active=True)
        self.fields['assigne_a'].empty_label = "--- Non assigne ---"
        self.fields['equipements'].required = False
        for field in self.fields.values():
            if not field.required:
                field.label_suffix = ''

        role = self._get_role()
        if role == 'utilisateur':
            self.fields['statut'].initial = 'ouvert'
            self.fields['statut'].choices = [('ouvert', 'Ouvert')]
            self.fields['statut'].disabled = True
            self.fields['assigne_a'].queryset = User.objects.filter(is_active=True, profil__role='admin')
        elif role == 'admin':
            self.fields['assigne_a'].queryset = User.objects.filter(is_active=True, profil__role='technicien')
        elif role == 'technicien':
            self.fields['assigne_a'].queryset = User.objects.filter(pk=getattr(self.user, 'pk', None))
            self.fields['assigne_a'].disabled = True
            self.fields['statut'].choices = [
                ('en_cours', 'En cours'),
                ('resolu', 'Resolu'),
                ('ferme', 'Ferme'),
            ]

    def _get_role(self):
        if not self.user:
            return None
        if self.user.is_superuser:
            return 'admin'
        profil = getattr(self.user, 'profil', None)
        return getattr(profil, 'role', None)


#On peut tester dans cet ordre avec python manage.py runserver :
#
#Connecte-toi avec utilisateur1 / user123, crée un incident.
#Résultat attendu : statut ouvert, assigné automatiquement à admin.
#
#Connecte-toi avec admin / admin123, ouvre cet incident et modifie-le.
#Résultat attendu : l’admin peut l’adresser à technicien1 et le faire passer en prise en charge.
#
#Connecte-toi avec technicien1 / tech123.
#Résultat attendu : il ne voit que ses incidents assignés, peut les mettre en_cours, resolu, puis ferme.
#
#Retourne sur utilisateur1.
#Résultat attendu : l’utilisateur voit l’évolution de son incident mais ne peut pas faire les actions réservées.