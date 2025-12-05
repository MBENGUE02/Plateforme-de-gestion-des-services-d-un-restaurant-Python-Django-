from adminApp.models import Utilisateurs

class UtilisateurMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        utilisateur_id = request.session.get('utilisateur_id')
        if utilisateur_id:
            try:
                request.utilisateur = Utilisateurs.objects.get(id=utilisateur_id)
            except Utilisateurs.DoesNotExist:
                request.utilisateur = None
        else:
            request.utilisateur = None
        return self.get_response(request)
