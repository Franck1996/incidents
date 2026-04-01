from django.utils import timezone

from .models import ProfilUtilisateur


class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            ProfilUtilisateur.objects.update_or_create(
                user=request.user,
                defaults={'derniere_activite': timezone.now()},
            )
        return self.get_response(request)
