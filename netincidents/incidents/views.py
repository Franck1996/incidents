from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
import json
import calendar

from .models import Incident, Commentaire, Equipement, HistoriqueStatut, Notification, ProfilUtilisateur
from .forms import IncidentForm, CommentaireForm, EquipementForm, FiltreIncidentForm, ProfilForm
from .utils import generer_rapport_pdf
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth

@login_required
def dashboard(request):
    # Récupérer les paramètres de filtre depuis l'URL
    statut_filtre = request.GET.get('statut', '')
    priorite_filtre = request.GET.get('priorite', '')
    categorie_filtre = request.GET.get('categorie', '')
    recherche = request.GET.get('recherche', '')
    
    # Nouveaux filtres temporels
    periode = request.GET.get('periode', '')  # aujourdhui, hier, cette_semaine, semaine_derniere, ce_mois, mois_dernier, personnalise
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    
    # Base queryset pour les incidents
    incidents_queryset = Incident.objects.select_related('cree_par', 'assigne_a')
    
    # Appliquer les filtres de recherche
    if recherche:
        incidents_queryset = incidents_queryset.filter(
            Q(titre__icontains=recherche) | Q(description__icontains=recherche)
        )
    
    if statut_filtre:
        incidents_queryset = incidents_queryset.filter(statut=statut_filtre)
    
    if priorite_filtre:
        incidents_queryset = incidents_queryset.filter(priorite=priorite_filtre)
    
    if categorie_filtre:
        incidents_queryset = incidents_queryset.filter(categorie=categorie_filtre)
    
    # Appliquer les filtres temporels
    today = timezone.now().date()
    
    if periode == 'aujourdhui':
        incidents_queryset = incidents_queryset.filter(date_creation__date=today)
        periode_label = "Aujourd'hui"
    elif periode == 'hier':
        hier = today - timedelta(days=1)
        incidents_queryset = incidents_queryset.filter(date_creation__date=hier)
        periode_label = "Hier"
    elif periode == 'cette_semaine':
        debut_semaine = today - timedelta(days=today.weekday())
        incidents_queryset = incidents_queryset.filter(date_creation__date__gte=debut_semaine)
        periode_label = "Cette semaine"
    elif periode == 'semaine_derniere':
        debut_semaine_derniere = today - timedelta(days=today.weekday() + 7)
        fin_semaine_derniere = debut_semaine_derniere + timedelta(days=6)
        incidents_queryset = incidents_queryset.filter(
            date_creation__date__gte=debut_semaine_derniere,
            date_creation__date__lte=fin_semaine_derniere
        )
        periode_label = "Semaine dernière"
    elif periode == 'ce_mois':
        debut_mois = today.replace(day=1)
        incidents_queryset = incidents_queryset.filter(date_creation__date__gte=debut_mois)
        periode_label = "Ce mois"
    elif periode == 'mois_dernier':
        dernier_mois = today.replace(day=1) - timedelta(days=1)
        debut_mois_dernier = dernier_mois.replace(day=1)
        incidents_queryset = incidents_queryset.filter(
            date_creation__date__gte=debut_mois_dernier,
            date_creation__date__lte=dernier_mois
        )
        periode_label = "Mois dernier"
    elif periode == 'personnalise' and date_debut and date_fin:
        try:
            debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
            incidents_queryset = incidents_queryset.filter(
                date_creation__date__gte=debut,
                date_creation__date__lte=fin
            )
            periode_label = f"{date_debut} au {date_fin}"
        except:
            periode_label = "Toutes dates"
    else:
        periode_label = "Toutes dates"
    
    # Statistiques basées sur les filtres
    total = incidents_queryset.count()
    ouverts = incidents_queryset.filter(statut='ouvert').count()
    en_cours = incidents_queryset.filter(statut='en_cours').count()
    resolus = incidents_queryset.filter(statut='resolu').count()
    fermes = incidents_queryset.filter(statut='ferme').count()
    critiques = incidents_queryset.filter(priorite='critique', statut__in=['ouvert', 'en_cours']).count()
    
    # Derniers incidents avec les filtres appliqués
    derniers_incidents = incidents_queryset.order_by('-date_creation')[:10]
    
    # Incidents assignés à moi
    mes_incidents = incidents_queryset.filter(
        assigne_a=request.user,
        statut__in=['ouvert', 'en_cours']
    ).order_by('-priorite', '-date_creation')[:5]
    
    # Données pour graphiques (basées sur les filtres)
    stats_par_statut = list(
        incidents_queryset.values('statut').annotate(total=Count('id'))
    )
    stats_par_priorite = list(
        incidents_queryset.values('priorite').annotate(total=Count('id'))
    )
    stats_par_categorie = list(
        incidents_queryset.values('categorie').annotate(total=Count('id')).order_by('-total')[:6]
    )
    
    # Évolution temporelle selon la période sélectionnée
    if periode == 'cette_semaine' or periode == 'semaine_derniere' or periode == 'personnalise' and date_debut and date_fin:
        # Graphique par jour
        evolution_data = (
            incidents_queryset
            .annotate(jour=TruncDate('date_creation'))
            .values('jour')
            .annotate(total=Count('id'))
            .order_by('jour')
        )
        evolution_label = "par jour"
    elif periode == 'ce_mois' or periode == 'mois_dernier':
        # Graphique par semaine
        evolution_data = (
            incidents_queryset
            .annotate(semaine=TruncWeek('date_creation'))
            .values('semaine')
            .annotate(total=Count('id'))
            .order_by('semaine')
        )
        evolution_label = "par semaine"
    else:
        # Graphique par mois pour les périodes plus longues
        evolution_data = (
            incidents_queryset
            .annotate(mois=TruncMonth('date_creation'))
            .values('mois')
            .annotate(total=Count('id'))
            .order_by('mois')
        )
        evolution_label = "par mois"
    
    # Incidents des 7 derniers jours pour le graphique rapide
    date_limite = timezone.now() - timedelta(days=7)
    incidents_semaine = (
        Incident.objects.filter(date_creation__gte=date_limite)
        .annotate(jour=TruncDate('date_creation'))
        .values('jour')
        .annotate(total=Count('id'))
        .order_by('jour')
    )
    
    # Récupérer les valeurs uniques pour les filtres
    statuts = Incident.STATUT
    priorites = Incident.PRIORITE
    categories = Incident.CATEGORIE
    
    # Calcul du temps moyen de résolution
    incidents_resolus = incidents_queryset.filter(
        statut='resolu', 
        date_resolution__isnull=False
    )
    temps_moyen_resolution = None
    if incidents_resolus.exists():
        temps_total = sum(
            (inc.date_resolution - inc.date_creation).total_seconds() / 3600 
            for inc in incidents_resolus
        )
        temps_moyen_resolution = round(temps_total / incidents_resolus.count(), 1)
    
    notifications = Notification.objects.filter(
        utilisateur=request.user, lue=False
    ).order_by('-date_creation')[:5]
    
    context = {
        'total': total,
        'ouverts': ouverts,
        'en_cours': en_cours,
        'resolus': resolus,
        'fermes': fermes,
        'critiques': critiques,
        'derniers_incidents': derniers_incidents,
        'mes_incidents': mes_incidents,
        'stats_par_statut': json.dumps(stats_par_statut),
        'stats_par_priorite': json.dumps(stats_par_priorite),
        'stats_par_categorie': json.dumps(stats_par_categorie),
        'incidents_semaine': json.dumps([
            {'jour': str(i['jour']), 'total': i['total']} for i in incidents_semaine
        ]),
        'evolution_data': json.dumps([
            {'periode': str(item[list(item.keys())[0]]), 'total': item['total']} 
            for item in evolution_data
        ]),
        'evolution_label': evolution_label,
        'notifications': notifications,
        'nb_notifs': Notification.objects.filter(utilisateur=request.user, lue=False).count(),
        # Valeurs pour les filtres
        'statuts': statuts,
        'priorites': priorites,
        'categories': categories,
        # Valeurs actives des filtres
        'filtre_statut': statut_filtre,
        'filtre_priorite': priorite_filtre,
        'filtre_categorie': categorie_filtre,
        'recherche': recherche,
        'periode': periode,
        'periode_label': periode_label,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'temps_moyen_resolution': temps_moyen_resolution,
    }
    return render(request, 'incidents/dashboard.html', context)
# ─── INCIDENTS ────────────────────────────────────────────────────────────────

@login_required
def liste_incidents(request):
    form_filtre = FiltreIncidentForm(request.GET)
    qs = Incident.objects.select_related('cree_par', 'assigne_a').prefetch_related('equipements')

    if form_filtre.is_valid():
        data = form_filtre.cleaned_data
        if data.get('recherche'):
            q = data['recherche']
            qs = qs.filter(Q(titre__icontains=q) | Q(description__icontains=q))
        if data.get('statut'):
            qs = qs.filter(statut=data['statut'])
        if data.get('priorite'):
            qs = qs.filter(priorite=data['priorite'])
        if data.get('categorie'):
            qs = qs.filter(categorie=data['categorie'])
        if data.get('date_debut'):
            qs = qs.filter(date_creation__date__gte=data['date_debut'])
        if data.get('date_fin'):
            qs = qs.filter(date_creation__date__lte=data['date_fin'])

    # Tri
    tri = request.GET.get('tri', '-date_creation')
    qs = qs.order_by(tri)

    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    nb_notifs = Notification.objects.filter(utilisateur=request.user, lue=False).count()

    return render(request, 'incidents/liste_incidents.html', {
        'page_obj': page_obj,
        'form_filtre': form_filtre,
        'tri': tri,
        'nb_notifs': nb_notifs,
    })


@login_required
def detail_incident(request, pk):
    incident = get_object_or_404(
        Incident.objects.select_related('cree_par', 'assigne_a').prefetch_related('equipements', 'commentaires__auteur'),
        pk=pk
    )
    form_commentaire = CommentaireForm()

    if request.method == 'POST':
        form_commentaire = CommentaireForm(request.POST)
        if form_commentaire.is_valid():
            commentaire = form_commentaire.save(commit=False)
            commentaire.incident = incident
            commentaire.auteur = request.user
            commentaire.save()
            messages.success(request, 'Commentaire ajouté avec succès.')
            return redirect('detail_incident', pk=pk)

    historique = HistoriqueStatut.objects.filter(incident=incident).select_related('modifie_par')
    nb_notifs = Notification.objects.filter(utilisateur=request.user, lue=False).count()

    return render(request, 'incidents/detail_incident.html', {
        'incident': incident,
        'form_commentaire': form_commentaire,
        'historique': historique,
        'nb_notifs': nb_notifs,
    })


@login_required
def creer_incident(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.cree_par = request.user
            incident.save()
            form.save_m2m()

            # Créer historique initial
            HistoriqueStatut.objects.create(
                incident=incident,
                ancien_statut='',
                nouveau_statut=incident.statut,
                modifie_par=request.user,
                commentaire='Incident créé'
            )

            # Notification si assigné
            if incident.assigne_a and incident.assigne_a != request.user:
                Notification.objects.create(
                    utilisateur=incident.assigne_a,
                    incident=incident,
                    message=f'Nouvel incident assigné : {incident.titre}'
                )

            messages.success(request, f'Incident #{incident.id} créé avec succès.')
            return redirect('detail_incident', pk=incident.pk)
    else:
        form = IncidentForm()

    nb_notifs = Notification.objects.filter(utilisateur=request.user, lue=False).count()
    return render(request, 'incidents/form_incident.html', {
        'form': form, 'action': 'Créer', 'nb_notifs': nb_notifs
    })


@login_required
def modifier_incident(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    ancien_statut = incident.statut

    if request.method == 'POST':
        form = IncidentForm(request.POST, instance=incident)
        if form.is_valid():
            incident = form.save(commit=False)

            # Enregistrer changement de statut
            nouveau_statut = form.cleaned_data['statut']
            if ancien_statut != nouveau_statut:
                if nouveau_statut == 'resolu':
                    incident.date_resolution = timezone.now()
                elif nouveau_statut == 'ferme':
                    incident.date_fermeture = timezone.now()

                HistoriqueStatut.objects.create(
                    incident=incident,
                    ancien_statut=ancien_statut,
                    nouveau_statut=nouveau_statut,
                    modifie_par=request.user,
                )

                # Notification au créateur
                if incident.cree_par and incident.cree_par != request.user:
                    Notification.objects.create(
                        utilisateur=incident.cree_par,
                        incident=incident,
                        message=f'Incident #{incident.id} : statut changé en "{nouveau_statut}"'
                    )

            incident.save()
            form.save_m2m()
            messages.success(request, f'Incident #{incident.id} modifié avec succès.')
            return redirect('detail_incident', pk=incident.pk)
    else:
        form = IncidentForm(instance=incident)

    nb_notifs = Notification.objects.filter(utilisateur=request.user, lue=False).count()
    return render(request, 'incidents/form_incident.html', {
        'form': form, 'action': 'Modifier', 'incident': incident, 'nb_notifs': nb_notifs
    })


@login_required
def supprimer_incident(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == 'POST':
        num = incident.id
        incident.delete()
        messages.success(request, f'Incident #{num} supprimé.')
        return redirect('liste_incidents')
    nb_notifs = Notification.objects.filter(utilisateur=request.user, lue=False).count()
    return render(request, 'incidents/confirmer_suppression.html', {
        'incident': incident, 'nb_notifs': nb_notifs
    })


@login_required
def changer_statut_ajax(request, pk):
    """Changement rapide de statut via AJAX"""
    if request.method == 'POST':
        incident = get_object_or_404(Incident, pk=pk)
        data = json.loads(request.body)
        nouveau_statut = data.get('statut')

        statuts_valides = [s[0] for s in Incident.STATUT]
        if nouveau_statut in statuts_valides:
            ancien = incident.statut
            incident.statut = nouveau_statut
            if nouveau_statut == 'resolu':
                incident.date_resolution = timezone.now()
            elif nouveau_statut == 'ferme':
                incident.date_fermeture = timezone.now()
            incident.save()

            HistoriqueStatut.objects.create(
                incident=incident,
                ancien_statut=ancien,
                nouveau_statut=nouveau_statut,
                modifie_par=request.user,
            )
            return JsonResponse({'success': True, 'statut': nouveau_statut})
    return JsonResponse({'success': False}, status=400)


# ─── ÉQUIPEMENTS ──────────────────────────────────────────────────────────────

@login_required
def liste_equipements(request):
    equipements = Equipement.objects.annotate(nb_incidents=Count('incident'))
    nb_notifs = Notification.objects.filter(utilisateur=request.user, lue=False).count()
    return render(request, 'incidents/liste_equipements.html', {
        'equipements': equipements, 'nb_notifs': nb_notifs
    })


@login_required
def creer_equipement(request):
    if request.method == 'POST':
        form = EquipementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Équipement ajouté avec succès.')
            return redirect('liste_equipements')
    else:
        form = EquipementForm()
    nb_notifs = Notification.objects.filter(utilisateur=request.user, lue=False).count()
    return render(request, 'incidents/form_equipement.html', {
        'form': form, 'action': 'Ajouter', 'nb_notifs': nb_notifs
    })


@login_required
def modifier_equipement(request, pk):
    equipement = get_object_or_404(Equipement, pk=pk)
    if request.method == 'POST':
        form = EquipementForm(request.POST, instance=equipement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Équipement modifié.')
            return redirect('liste_equipements')
    else:
        form = EquipementForm(instance=equipement)
    nb_notifs = Notification.objects.filter(utilisateur=request.user, lue=False).count()
    return render(request, 'incidents/form_equipement.html', {
        'form': form, 'action': 'Modifier', 'equipement': equipement, 'nb_notifs': nb_notifs
    })


@login_required
def supprimer_equipement(request, pk):
    equipement = get_object_or_404(Equipement, pk=pk)
    if request.method == 'POST':
        equipement.delete()
        messages.success(request, 'Équipement supprimé.')
        return redirect('liste_equipements')
    nb_notifs = Notification.objects.filter(utilisateur=request.user, lue=False).count()
    return render(request, 'incidents/confirmer_suppression_eq.html', {
        'equipement': equipement, 'nb_notifs': nb_notifs
    })


# ─── RAPPORTS ─────────────────────────────────────────────────────────────────

@login_required
def rapport_pdf(request, pk=None):
    """Rapport PDF d'un incident ou de tous les incidents"""
    if pk:
        incidents = [get_object_or_404(Incident, pk=pk)]
        titre = f"Rapport Incident #{pk}"
    else:
        form_filtre = FiltreIncidentForm(request.GET)
        qs = Incident.objects.select_related('cree_par', 'assigne_a').prefetch_related('equipements')
        if form_filtre.is_valid():
            data = form_filtre.cleaned_data
            if data.get('statut'):
                qs = qs.filter(statut=data['statut'])
            if data.get('priorite'):
                qs = qs.filter(priorite=data['priorite'])
            if data.get('date_debut'):
                qs = qs.filter(date_creation__date__gte=data['date_debut'])
            if data.get('date_fin'):
                qs = qs.filter(date_creation__date__lte=data['date_fin'])
        incidents = list(qs.order_by('-date_creation'))
        titre = "Rapport Global - Incidents Réseaux"

    pdf_response = generer_rapport_pdf(incidents, titre, request.user)
    return pdf_response


@login_required
def page_rapports(request):
    form_filtre = FiltreIncidentForm(request.GET)
    nb_notifs = Notification.objects.filter(utilisateur=request.user, lue=False).count()

    stats = {
        'total': Incident.objects.count(),
        'ouverts': Incident.objects.filter(statut='ouvert').count(),
        'en_cours': Incident.objects.filter(statut='en_cours').count(),
        'resolus': Incident.objects.filter(statut='resolu').count(),
        'fermes': Incident.objects.filter(statut='ferme').count(),
        'critiques': Incident.objects.filter(priorite='critique').count(),
        'hautes': Incident.objects.filter(priorite='haute').count(),
    }

    return render(request, 'incidents/rapports.html', {
        'form_filtre': form_filtre,
        'stats': stats,
        'nb_notifs': nb_notifs,
    })


# ─── HISTORIQUE ───────────────────────────────────────────────────────────────

@login_required
def historique_global(request):
    historique = HistoriqueStatut.objects.select_related(
        'incident', 'modifie_par'
    ).order_by('-date_changement')

    paginator = Paginator(historique, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    nb_notifs = Notification.objects.filter(utilisateur=request.user, lue=False).count()

    return render(request, 'incidents/historique.html', {
        'page_obj': page_obj, 'nb_notifs': nb_notifs
    })


# ─── NOTIFICATIONS ────────────────────────────────────────────────────────────

@login_required
def marquer_notifs_lues(request):
    Notification.objects.filter(utilisateur=request.user, lue=False).update(lue=True)
    return JsonResponse({'success': True})


@login_required
def liste_notifications(request):
    notifications = Notification.objects.filter(
        utilisateur=request.user
    ).order_by('-date_creation')
    nb_notifs = Notification.objects.filter(utilisateur=request.user, lue=False).count()
    return render(request, 'incidents/notifications.html', {
        'notifications': notifications, 'nb_notifs': nb_notifs
    })


# ─── PROFIL ────────────────────────────────────────────────────────────────────

@login_required
def mon_profil(request):
    profil, _ = ProfilUtilisateur.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=profil)
        if form.is_valid():
            profil = form.save()
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data.get('email', '')
            request.user.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('mon_profil')
    else:
        form = ProfilForm(instance=profil, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })

    nb_notifs = Notification.objects.filter(utilisateur=request.user, lue=False).count()
    mes_incidents_recents = Incident.objects.filter(
        cree_par=request.user
    ).order_by('-date_creation')[:5]

    return render(request, 'incidents/profil.html', {
        'form': form, 'profil': profil,
        'mes_incidents_recents': mes_incidents_recents,
        'nb_notifs': nb_notifs,
    })
