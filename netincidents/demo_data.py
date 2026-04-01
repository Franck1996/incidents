"""
Script de peuplement de la base de données avec des données de démonstration.
Usage : python manage.py shell < demo_data.py
   ou : python manage.py runscript demo_data  (avec django-extensions)
"""
import os
import django
import sys

# Setup Django si lancé directement
if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netincidents.settings')
    django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from incidents.models import Incident, Equipement, Commentaire, HistoriqueStatut, ProfilUtilisateur

print("🚀 Création des données de démonstration...")

# ── UTILISATEURS ──────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@netincidents.ci', 'admin123')
    ProfilUtilisateur.objects.create(user=admin, role='admin', departement='DSI', telephone='+225 07 00 00 00')
    print("✓ Superuser 'admin' créé (mdp: admin123)")

if not User.objects.filter(username='technicien1').exists():
    tech1 = User.objects.create_user('technicien1', 'tech1@net.ci', 'tech123', first_name='Kouassi', last_name='Aman')
    ProfilUtilisateur.objects.create(user=tech1, role='technicien', departement='Réseau', telephone='+225 07 11 22 33')
    print("✓ Utilisateur 'technicien1' créé (mdp: tech123)")

if not User.objects.filter(username='superviseur').exists():
    sup = User.objects.create_user('superviseur', 'sup@net.ci', 'sup123', first_name='Adjoua', last_name='Brou')
    ProfilUtilisateur.objects.create(user=sup, role='superviseur', departement='DSI')
    print("✓ Utilisateur 'superviseur' créé (mdp: sup123)")

admin = User.objects.get(username='admin')
tech1 = User.objects.get(username='technicien1')
sup   = User.objects.get(username='superviseur')

# ── ÉQUIPEMENTS ───────────────────────────────────────────────
equipements_data = [
    ('Switch Cœur Bât. A', 'switch', '10.0.0.1', 'Bâtiment A - Salle serveurs', 'actif'),
    ('Routeur Principal MPLS', 'routeur', '192.168.1.1', 'Datacenter Central', 'actif'),
    ('Firewall Périmétrique', 'firewall', '10.10.0.1', 'DMZ - Entrée réseau', 'actif'),
    ('Serveur DNS Primaire', 'serveur', '10.0.0.53', 'Salle serveurs DC', 'actif'),
    ('Switch Accès Bureau 2', 'switch', '10.1.2.10', 'Bâtiment B - 2ème étage', 'actif'),
    ('AP Wi-Fi Zone Cafétéria', 'point_acces', '10.2.0.15', 'Cafétéria RDC', 'maintenance'),
    ('Lien Fibre Opérateur A', 'lien_wan', None, 'POP Opérateur - Abidjan Plateau', 'actif'),
    ('Switch Distribution RDC', 'switch', '10.0.1.2', 'Bâtiment C - RDC', 'inactif'),
]

equipements = []
for nom, type_eq, ip, loc, statut in equipements_data:
    eq, created = Equipement.objects.get_or_create(
        nom=nom,
        defaults={'type_equipement': type_eq, 'adresse_ip': ip, 'localisation': loc, 'statut': statut}
    )
    equipements.append(eq)

print(f"✓ {len(equipements)} équipements créés")

# ── INCIDENTS ─────────────────────────────────────────────────
incidents_data = [
    {
        'titre': 'Panne totale du switch cœur Bâtiment A',
        'description': 'Le switch de distribution principal du bâtiment A ne répond plus aux requêtes ping depuis 14h30. Tous les utilisateurs du bâtiment sont impactés.',
        'categorie': 'panne_reseau',
        'priorite': 'critique',
        'statut': 'en_cours',
        'impact': 'Environ 150 utilisateurs sans accès réseau. Applications métier inaccessibles.',
        'cause_racine': 'Surchauffe du module d\'alimentation suite à une coupure de climatisation.',
        'solution_appliquee': '',
        'assigne': tech1,
        'eq_indices': [0],
        'jours': -1,
    },
    {
        'titre': 'Lenteurs importantes sur le réseau Wi-Fi zone cafétéria',
        'description': 'Les utilisateurs se plaignent de débits très lents sur le Wi-Fi depuis ce matin. Tests de débit montrent 0.5 Mbps au lieu de 50 Mbps attendus.',
        'categorie': 'lenteur',
        'priorite': 'haute',
        'statut': 'ouvert',
        'impact': 'Environ 30 utilisateurs mobiles affectés lors des pauses.',
        'cause_racine': '',
        'solution_appliquee': '',
        'assigne': tech1,
        'eq_indices': [5],
        'jours': -2,
    },
    {
        'titre': 'Tentatives d\'intrusion détectées sur le firewall',
        'description': 'Le SIEM a déclenché des alertes niveau 4 pour des tentatives de brute-force SSH répétées depuis plusieurs IPs externes. Plus de 5000 tentatives en 2 heures.',
        'categorie': 'securite',
        'priorite': 'critique',
        'statut': 'en_cours',
        'impact': 'Risque de compromission du périmètre réseau. Audit de sécurité requis.',
        'cause_racine': 'Règle firewall trop permissive sur le port 22 en entrée.',
        'solution_appliquee': 'Blocage temporaire des IPs sources. Règles ACL renforcées.',
        'assigne': sup,
        'eq_indices': [2],
        'jours': -1,
    },
    {
        'titre': 'Perte de connectivité lien WAN opérateur',
        'description': 'Le lien fibre principale avec l\'opérateur A est down depuis 08h15. Le lien de secours a pris le relais automatiquement mais avec une bande passante réduite.',
        'categorie': 'connectivite',
        'priorite': 'haute',
        'statut': 'resolu',
        'impact': 'Dégradation des performances Internet. Accès aux services cloud ralenti.',
        'cause_racine': 'Rupture physique de la fibre lors de travaux de voirie.',
        'solution_appliquee': 'Opérateur a dépêché une équipe. Fibre réparée et testée à 22h45.',
        'assigne': tech1,
        'eq_indices': [1, 6],
        'jours': -5,
    },
    {
        'titre': 'Mauvaise configuration VLAN switch Bureau 2',
        'description': 'Après une mise à jour de configuration, les postes du bureau 2 ne peuvent plus accéder au serveur d\'impression partagé. VLAN mal configuré.',
        'categorie': 'configuration',
        'priorite': 'moyenne',
        'statut': 'resolu',
        'impact': '12 utilisateurs sans accès à l\'imprimante réseau.',
        'cause_racine': 'Erreur de taggage VLAN 20 sur les ports trunk lors d\'une maintenance préventive.',
        'solution_appliquee': 'Correction de la configuration VLAN. Tests validés et service restauré.',
        'assigne': tech1,
        'eq_indices': [4],
        'jours': -10,
    },
    {
        'titre': 'Serveur DNS primaire intermittent',
        'description': 'Des résolutions DNS échouent de manière sporadique depuis 3 jours. Les logs montrent des timeouts sur certaines zones de résolution.',
        'categorie': 'logiciel',
        'priorite': 'haute',
        'statut': 'ouvert',
        'impact': 'Certains accès web aléatoirement lents ou en erreur pour tous les utilisateurs.',
        'cause_racine': '',
        'solution_appliquee': '',
        'assigne': None,
        'eq_indices': [3],
        'jours': -3,
    },
    {
        'titre': 'Incident résolu - Switch RDC Bâtiment C hors tension',
        'description': 'Suite à une maintenance électrique planifiée, le switch du RDC a été mis hors tension par erreur.',
        'categorie': 'materiel',
        'priorite': 'moyenne',
        'statut': 'ferme',
        'impact': 'RDC Bâtiment C sans réseau pendant 45 minutes.',
        'cause_racine': 'Mauvais circuit électrique coupé lors de la maintenance.',
        'solution_appliquee': 'Remise sous tension du switch. Processus de maintenance mis à jour.',
        'assigne': tech1,
        'eq_indices': [7],
        'jours': -15,
    },
    {
        'titre': 'Saturation bande passante lien MPLS',
        'description': 'Taux d\'utilisation du lien MPLS principal à 98% depuis ce matin. Les applications temps réel (VoIP) sont dégradées.',
        'categorie': 'lenteur',
        'priorite': 'haute',
        'statut': 'en_cours',
        'impact': 'Qualité des appels VoIP très dégradée. Réunions Teams instables.',
        'cause_racine': 'Sauvegarde non planifiée déclenchée à tort vers un site distant.',
        'solution_appliquee': 'Arrêt de la sauvegarde parasite. QoS revue pour prioriser la VoIP.',
        'assigne': sup,
        'eq_indices': [1],
        'jours': 0,
    },
]

created_incidents = []
for data in incidents_data:
    inc = Incident.objects.create(
        titre=data['titre'],
        description=data['description'],
        categorie=data['categorie'],
        priorite=data['priorite'],
        statut=data['statut'],
        impact=data.get('impact', ''),
        cause_racine=data.get('cause_racine', ''),
        solution_appliquee=data.get('solution_appliquee', ''),
        cree_par=data.get('cree_par', admin),
        assigne_a=data.get('assigne'),
        date_creation=timezone.now() + timedelta(days=data['jours']),
    )
    for idx in data['eq_indices']:
        if idx < len(equipements):
            inc.equipements.add(equipements[idx])

    if data['statut'] == 'resolu':
        inc.date_resolution = timezone.now() + timedelta(days=data['jours'] + 1)
        inc.save()

    # Historique initial
    HistoriqueStatut.objects.create(
        incident=inc, ancien_statut='', nouveau_statut=inc.statut,
        modifie_par=admin, commentaire='Incident créé'
    )
    created_incidents.append(inc)

print(f"✓ {len(created_incidents)} incidents créés")

# ── COMMENTAIRES ──────────────────────────────────────────────
commentaires_demo = [
    (created_incidents[0], tech1, 'action', 'Intervention sur site. Module PSU défaillant identifié. Commande pièce de remplacement en cours.'),
    (created_incidents[0], sup, 'escalade', 'Escalade au fournisseur pour livraison urgente du module PSU. Délai estimé : 4 heures.'),
    (created_incidents[2], sup, 'action', 'Analyse des logs firewall en cours. Extraction des IPs malveillantes pour blacklistage permanent.'),
    (created_incidents[2], admin, 'commentaire', 'Contacter l\'équipe CERT-CI pour notification de l\'incident de sécurité selon procédure.'),
    (created_incidents[3], tech1, 'mise_a_jour', 'Opérateur confirmé sur site. Réparation en cours. ETR 3 heures.'),
    (created_incidents[3], tech1, 'action', 'Fibre réparée, tests de débit OK. Bascule retour sur lien principal réussie.'),
    (created_incidents[7], tech1, 'action', 'Sauvegarde parasite identifiée et stoppée. Analyse de la charge réseau en temps réel.'),
]

for inc, auteur, type_c, contenu in commentaires_demo:
    Commentaire.objects.create(incident=inc, auteur=auteur, type_commentaire=type_c, contenu=contenu)

print(f"✓ {len(commentaires_demo)} commentaires créés")
print("\n✅ Données de démonstration chargées avec succès !")
print("\n📋 Comptes disponibles :")
print("   admin        / admin123  (Administrateur)")
print("   technicien1  / tech123   (Technicien réseau)")
print("   superviseur  / sup123    (Superviseur)")
print("\n🚀 Lancez le serveur : python manage.py runserver")
