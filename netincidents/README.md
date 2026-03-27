# 🌐 NetIncidents — Application de Gestion d'Incidents Réseaux

Application web Django professionnelle pour la gestion complète des incidents réseaux.

---

## 🚀 Installation rapide (VS Code)

### 1. Prérequis
- Python 3.10+
- pip

### 2. Installation des dépendances

```bash
cd netincidents

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate

# Activer l'environnement (Linux/Mac)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Initialisation de la base de données

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Charger les données de démonstration

```bash
python demo_data.py
```

### 5. Lancer le serveur

```bash
python manage.py runserver
```

Accéder à l'application : **http://127.0.0.1:8000**

---

## 👤 Comptes de connexion

| Utilisateur    | Mot de passe | Rôle              |
|----------------|--------------|-------------------|
| `admin`        | `admin123`   | Administrateur    |
| `technicien1`  | `tech123`    | Technicien réseau |
| `superviseur`  | `sup123`     | Superviseur       |

Interface d'administration Django : **http://127.0.0.1:8000/admin/**

---

## 📦 Structure du projet

```
netincidents/
├── manage.py
├── requirements.txt
├── demo_data.py             ← Données de démo
├── netincidents/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── incidents/
    ├── models.py            ← Modèles de données
    ├── views.py             ← Logique métier
    ├── urls.py              ← Routage URL
    ├── forms.py             ← Formulaires
    ├── admin.py             ← Interface admin
    ├── utils.py             ← Génération PDF
    ├── apps.py
    └── templates/incidents/
        ├── base.html        ← Layout principal (sidebar)
        ├── login.html       ← Page de connexion
        ├── dashboard.html   ← Tableau de bord + graphiques
        ├── liste_incidents.html
        ├── detail_incident.html
        ├── form_incident.html
        ├── liste_equipements.html
        ├── form_equipement.html
        ├── rapports.html
        ├── historique.html
        ├── notifications.html
        ├── profil.html
        ├── confirmer_suppression.html
        └── confirmer_suppression_eq.html
```

---

## ✨ Fonctionnalités

### Gestion des incidents
- ✅ Création, modification, suppression d'incidents
- ✅ Catégories : panne réseau, sécurité, lenteur, configuration, etc.
- ✅ Priorités : Critique / Haute / Moyenne / Basse
- ✅ Statuts : Ouvert → En cours → Résolu → Fermé
- ✅ Assignation à un technicien
- ✅ Lien avec les équipements concernés
- ✅ Champ impact métier, cause racine, solution appliquée
- ✅ Changement de statut rapide (clic ou AJAX)

### Journal d'activité
- ✅ Commentaires par type (commentaire, action, escalade, mise à jour)
- ✅ Timeline visuelle par incident
- ✅ Historique global de tous les changements de statut

### Équipements réseau
- ✅ CRUD complet : routeur, switch, firewall, serveur, Wi-Fi, WAN
- ✅ Adresse IP, localisation, statut
- ✅ Lien vers les incidents associés

### Rapports PDF
- ✅ Rapport par incident (fiche détaillée)
- ✅ Rapport global filtrable (statut, priorité, dates)
- ✅ Export PDF professionnel avec ReportLab
- ✅ Statistiques récapitulatives dans le rapport

### Dashboard
- ✅ KPIs temps réel (total, ouverts, en cours, résolus, critiques)
- ✅ Alerte incidents critiques
- ✅ Graphiques Chart.js : statuts, priorités, tendance semaine
- ✅ Tableau des derniers incidents
- ✅ Mes incidents assignés

### Autres
- ✅ Système de notifications internes
- ✅ Profil utilisateur avec avatar
- ✅ Pagination sur toutes les listes
- ✅ Filtres et recherche avancés
- ✅ Tri des colonnes
- ✅ Mode sombre / clair (toggle)
- ✅ Design responsive (mobile-friendly)
- ✅ Interface admin Django complète

---

## 🛠️ Dépannage

**Erreur "No module named 'reportlab'"** :
```bash
pip install reportlab
```
Sans ReportLab, les rapports seront générés en `.txt` (fallback automatique).

**Réinitialiser la base de données** :
```bash
del db.sqlite3          # Windows
rm db.sqlite3           # Linux/Mac
python manage.py migrate
python demo_data.py
```
