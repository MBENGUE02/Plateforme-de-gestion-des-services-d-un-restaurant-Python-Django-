from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from adminApp.models import Utilisateurs, Tache
from businessApp.models import Commande, LigneCommande, ElementMenu, StatutCommande, MenuJour
from django.contrib import messages
from datetime import date

# Create your views here.

def page_employe(request):
    utilisateur_id = request.session.get('utilisateur_id')
    if not utilisateur_id:
        return redirect('authentification')

    utilisateur = get_object_or_404(Utilisateurs, id=utilisateur_id)
    type_util = utilisateur.type_utilisateur.libelle.lower()

    if type_util not in ['serveur', 'cuisinier']:
        messages.error(request, "Accès réservé aux membres du personnel.")
        return redirect('accueil')  # ou une autre page sécurisée

    taches = Tache.objects.filter(personnel=utilisateur)
    commandes = Commande.objects.select_related('statut', 'utilisateur').prefetch_related('lignes__plat')
    menu_du_jour = MenuJour.objects.filter(date=date.today()).first()

    return render(request, 'src/page_employe.html', {
        'utilisateur': utilisateur,
        'taches': taches,
        'commandes': commandes,
        'est_cuisinier': type_util == 'cuisinier',
        'est_serveur': type_util == 'serveur',
        'menu_du_jour': menu_du_jour,
    })


def toggle_dispo_plat(request, plat_id):
    utilisateur = get_object_or_404(Utilisateurs, id=request.session.get('utilisateur_id'))
    if utilisateur.type_utilisateur.libelle.lower() != 'cuisinier':
        messages.error(request, "Accès réservé aux cuisiniers.")
        return redirect('page_employe')

    plat = get_object_or_404(ElementMenu, id=plat_id)
    plat.est_epuise = not plat.est_epuise
    plat.save()
    return redirect('page_employe')

def marquer_commande_prete(request, commande_id):
    if request.method == 'POST':
        commande = get_object_or_404(Commande, id=commande_id)
        statut_prete = get_object_or_404(StatutCommande, code='prete')
        commande.statut = statut_prete
        commande.save()
        messages.success(request, f"La commande #{commande.id} a été marquée comme PRÊTE.")
    return redirect('page_employe')


def marquer_commande_servie(request, commande_id):
    if request.method == 'POST':
        commande = get_object_or_404(Commande, id=commande_id)
        statut_livree = get_object_or_404(StatutCommande, code='livree')
        commande.statut = statut_livree
        commande.save()
        messages.success(request, f"Commande #{commande.id} marquée comme SERVIE.")
    return redirect('page_employe')
