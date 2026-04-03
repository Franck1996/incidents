from django.utils import timezone

from .models import ProfilUtilisateur


def presence_utilisateurs(request):
    profils = []
    total_en_ligne = 0

    if request.user.is_authenticated:
        limite = timezone.now() - timezone.timedelta(minutes=5)
        profils = list(
            ProfilUtilisateur.objects.select_related('user')
            .filter(user__is_active=True)
            .order_by('user__username')
        )
        profils.sort(
            key=lambda profil: (
                0 if profil.derniere_activite and profil.derniere_activite >= limite else 1,
                -(profil.derniere_activite.timestamp()) if profil.derniere_activite else float('inf'),
                profil.user.username.lower(),
            )
        )
        total_en_ligne = sum(1 for profil in profils if profil.derniere_activite and profil.derniere_activite >= limite)

    return {
        'utilisateurs_connectes': profils,
        'total_utilisateurs_en_ligne': total_en_ligne,
    }
