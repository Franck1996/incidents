from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Equipement(models.Model):
    """Équipement réseau (routeur, switch, serveur, etc.)"""
    NOM_TYPES = [
        ('routeur', 'Routeur'),
        ('switch', 'Switch'),
        ('firewall', 'Firewall'),
        ('serveur', 'Serveur'),
        ('point_acces', 'Point d\'accès Wi-Fi'),
        ('lien_wan', 'Lien WAN'),
        ('autre', 'Autre'),
    ]
    STATUS = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('maintenance', 'En maintenance'),
    ]
    nom = models.CharField(max_length=100, verbose_name="Nom")
    type_equipement = models.CharField(max_length=30, choices=NOM_TYPES, default='autre')
    adresse_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    localisation = models.CharField(max_length=200, verbose_name="Localisation", blank=True)
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUS, default='actif')
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Équipement"
        verbose_name_plural = "Équipements"
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.adresse_ip or 'sans IP'})"


class Incident(models.Model):
    """Incident réseau principal"""
    PRIORITE = [
        ('critique', 'Critique'),
        ('haute', 'Haute'),
        ('moyenne', 'Moyenne'),
        ('basse', 'Basse'),
    ]
    STATUT = [
        ('ouvert', 'Ouvert'),
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
        ('ferme', 'Fermé'),
    ]
    CATEGORIE = [
        ('panne_reseau', 'Panne réseau'),
        ('lenteur', 'Lenteur / Dégradation'),
        ('securite', 'Incident de sécurité'),
        ('configuration', 'Erreur de configuration'),
        ('materiel', 'Défaillance matérielle'),
        ('logiciel', 'Incident logiciel'),
        ('connectivite', 'Perte de connectivité'),
        ('autre', 'Autre'),
    ]

    titre = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    categorie = models.CharField(max_length=30, choices=CATEGORIE, default='autre', verbose_name="Catégorie")
    priorite = models.CharField(max_length=20, choices=PRIORITE, default='moyenne', verbose_name="Priorité")
    statut = models.CharField(max_length=20, choices=STATUT, default='ouvert', verbose_name="Statut")

    equipements = models.ManyToManyField(Equipement, blank=True, verbose_name="Équipements concernés")

    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    date_resolution = models.DateTimeField(null=True, blank=True, verbose_name="Date de résolution")
    date_fermeture = models.DateTimeField(null=True, blank=True, verbose_name="Date de fermeture")

    cree_par = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='incidents_crees', verbose_name="Créé par"
    )
    assigne_a = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='incidents_assignes', verbose_name="Assigné à"
    )

    impact = models.TextField(blank=True, verbose_name="Impact métier")
    cause_racine = models.TextField(blank=True, verbose_name="Cause racine")
    solution_appliquee = models.TextField(blank=True, verbose_name="Solution appliquée")

    class Meta:
        verbose_name = "Incident"
        verbose_name_plural = "Incidents"
        ordering = ['-date_creation']

    def __str__(self):
        return f"[{self.get_priorite_display()}] {self.titre}"

    def duree_resolution(self):
        if self.date_resolution and self.date_creation:
            delta = self.date_resolution - self.date_creation
            heures = delta.total_seconds() / 3600
            return round(heures, 1)
        return None

    def couleur_priorite(self):
        couleurs = {
            'critique': 'danger',
            'haute': 'warning',
            'moyenne': 'info',
            'basse': 'success',
        }
        return couleurs.get(self.priorite, 'secondary')

    def couleur_statut(self):
        couleurs = {
            'ouvert': 'danger',
            'en_cours': 'warning',
            'resolu': 'success',
            'ferme': 'secondary',
        }
        return couleurs.get(self.statut, 'secondary')


class Commentaire(models.Model):
    """Commentaire / action sur un incident"""
    TYPE_COMMENTAIRE = [
        ('commentaire', 'Commentaire'),
        ('action', 'Action effectuée'),
        ('escalade', 'Escalade'),
        ('mise_a_jour', 'Mise à jour statut'),
    ]
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='commentaires')
    auteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    type_commentaire = models.CharField(max_length=20, choices=TYPE_COMMENTAIRE, default='commentaire')
    contenu = models.TextField(verbose_name="Contenu")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_creation']
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"

    def __str__(self):
        return f"Commentaire de {self.auteur} sur #{self.incident.id}"


class HistoriqueStatut(models.Model):
    """Historique des changements de statut d'un incident"""
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='historique')
    ancien_statut = models.CharField(max_length=20)
    nouveau_statut = models.CharField(max_length=20)
    modifie_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_changement = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_changement']
        verbose_name = "Historique statut"

    def __str__(self):
        return f"Incident #{self.incident.id}: {self.ancien_statut} → {self.nouveau_statut}"


class Notification(models.Model):
    """Notifications internes"""
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"Notif pour {self.utilisateur}: {self.message[:50]}"


class ProfilUtilisateur(models.Model):
    """Profil étendu utilisateur"""
    ROLES = [
        ('admin', 'Administrateur'),
        ('technicien', 'Technicien réseau'),
        ('superviseur', 'Superviseur'),
        ('utilisateur', 'Utilisateur'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    role = models.CharField(max_length=20, choices=ROLES, default='utilisateur')
    telephone = models.CharField(max_length=20, blank=True)
    departement = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"Profil de {self.user.username} ({self.get_role_display()})"
