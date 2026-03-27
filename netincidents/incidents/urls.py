from django.urls import path
from . import views

urlpatterns = [
    # Accueil → dashboard
    path('', views.dashboard, name='accueil'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Incidents
    path('incidents/', views.liste_incidents, name='liste_incidents'),
    path('incidents/nouveau/', views.creer_incident, name='creer_incident'),
    path('incidents/<int:pk>/', views.detail_incident, name='detail_incident'),
    path('incidents/<int:pk>/modifier/', views.modifier_incident, name='modifier_incident'),
    path('incidents/<int:pk>/supprimer/', views.supprimer_incident, name='supprimer_incident'),
    path('incidents/<int:pk>/statut/', views.changer_statut_ajax, name='changer_statut_ajax'),

    # Équipements
    path('equipements/', views.liste_equipements, name='liste_equipements'),
    path('equipements/nouveau/', views.creer_equipement, name='creer_equipement'),
    path('equipements/<int:pk>/modifier/', views.modifier_equipement, name='modifier_equipement'),
    path('equipements/<int:pk>/supprimer/', views.supprimer_equipement, name='supprimer_equipement'),

    # Rapports
    path('rapports/', views.page_rapports, name='rapports'),
    path('rapports/pdf/', views.rapport_pdf, name='rapport_pdf_global'),
    path('rapports/pdf/<int:pk>/', views.rapport_pdf, name='rapport_pdf_incident'),

    # Historique
    path('historique/', views.historique_global, name='historique'),

    # Notifications
    path('notifications/', views.liste_notifications, name='notifications'),
    path('notifications/marquer-lues/', views.marquer_notifs_lues, name='marquer_notifs_lues'),

    # Profil
    path('profil/', views.mon_profil, name='mon_profil'),
]
