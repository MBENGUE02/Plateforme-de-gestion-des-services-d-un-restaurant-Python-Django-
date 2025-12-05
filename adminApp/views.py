from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib import messages
from .forms import UtilisateurForm, TacheForm
from businessApp.forms import ElementMenuForm, MenuJourForm, ImageMenu
from .models import Utilisateurs, Tache, TypeUtilisateur
from businessApp.models import ElementMenu, MenuJour, Commande, StatutCommande, Reservation
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from businessApp.models import Commande, LigneCommande, ElementMenu
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.utils.timezone import now, timedelta

# decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from adminApp.models import Utilisateurs

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        utilisateur_id = request.session.get('utilisateur_id')
        if not utilisateur_id:
            return redirect('authentification')

        try:
            utilisateur = Utilisateurs.objects.get(id=utilisateur_id)
        except Utilisateurs.DoesNotExist:
            return redirect('authentification')

        if utilisateur.type_utilisateur.libelle.lower() != 'admin':
            return HttpResponseForbidden("Accès réservé à l'administrateur")

        return view_func(request, *args, **kwargs)
    return wrapper



@admin_required
def liste_employes(request):
    utilisateur_instance = None
    edit_mode = False

    if 'edit_employe' in request.GET:
        utilisateur_instance = get_object_or_404(Utilisateurs, id=request.GET.get('edit_employe'))
        edit_mode = True
    elif 'delete_employe' in request.GET:
        Utilisateurs.objects.filter(id=request.GET.get('delete_employe')).delete()
        return redirect('liste_employes')

    if request.method == 'POST':
        employe_id = request.POST.get('employe_id')
        if employe_id:
            utilisateur_instance = get_object_or_404(Utilisateurs, id=employe_id)
            form = UtilisateurForm(request.POST, instance=utilisateur_instance)
            edit_mode = True
        else:
            form = UtilisateurForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('liste_employes')
    else:
        form = UtilisateurForm(instance=utilisateur_instance)

    employes = Utilisateurs.objects.all()

    return render(request, 'src/employe.html', {
        'utilisateur_form': form,
        'employes': employes,
        'edit_mode': edit_mode,
        'employe_id': utilisateur_instance.id if utilisateur_instance else '',
    })

@admin_required
def liste_plats(request):
    plat_instance = None
    edit_mode = False

    # Vérifie si on veut modifier
    if 'edit_plat' in request.GET:
        plat_instance = get_object_or_404(ElementMenu, id=request.GET.get('edit_plat'))
        edit_mode = True

    # Suppression
    elif 'delete_plat' in request.GET:
        plat_to_delete = get_object_or_404(ElementMenu, id=request.GET.get('delete_plat'))
        plat_to_delete.images.all().delete()  # Supprimer les images liées
        plat_to_delete.delete()
        return redirect('liste_plats')

    # POST : création ou modification
    if request.method == 'POST':
        plat_id = request.POST.get('plat_id')
        if plat_id:
            plat_instance = get_object_or_404(ElementMenu, id=plat_id)
            form = ElementMenuForm(request.POST, instance=plat_instance)
            edit_mode = True
        else:
            form = ElementMenuForm(request.POST)

        if form.is_valid():
            plat_saved = form.save()
            for f in request.FILES.getlist('images'):
                ImageMenu.objects.create(element=plat_saved, image=f)  # nom correct du champ FK
            return redirect('liste_plats')
    else:
        form = ElementMenuForm(instance=plat_instance)

    plats = ElementMenu.objects.all()

    return render(request, 'src/plat.html', {
        'element_menu_form': form,
        'plats': plats,
        'edit_mode': edit_mode,
        'plat_id': plat_instance.id if plat_instance else '',
    })

@admin_required
def gestion_menu_jour(request):
    menus_jour = MenuJour.objects.all().order_by('-date')
    edit_mode = False
    form = MenuJourForm()
    menu_id = None

    # Modifier un menu existant (GET)
    if 'edit_menu' in request.GET:
        edit_mode = True
        menu_id = request.GET.get('edit_menu')
        menu = get_object_or_404(MenuJour, id=menu_id)
        form = MenuJourForm(instance=menu)

    # Supprimer un menu (GET)
    elif 'delete_menu' in request.GET:
        menu_id = request.GET.get('delete_menu')
        menu = get_object_or_404(MenuJour, id=menu_id)
        menu.delete()
        return redirect('gestion_menu_jour')

    # Soumission du formulaire (POST)
    elif request.method == 'POST':
        menu_id_post = request.POST.get('menu_id')
        if menu_id_post:
            menu = get_object_or_404(MenuJour, id=menu_id_post)
            form = MenuJourForm(request.POST, instance=menu)
            edit_mode = True
            menu_id = menu.id
        else:
            form = MenuJourForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('gestion_menu_jour')

    return render(request, 'src/menu_jour.html', {
        'form': form,
        'menus_jour': menus_jour,
        'edit_mode': edit_mode,
        'menu_id': menu_id,
    })

@admin_required
def gestion_taches(request):
    types_autorises = TypeUtilisateur.objects.filter(libelle__in=['cuisinier', 'serveur'])
    personnels = Utilisateurs.objects.filter(type_utilisateur__in=types_autorises)

    # DEBUG : Affiche en console les personnes filtrées
    print("Types autorisés:", list(types_autorises.values_list('libelle', flat=True)))
    print("Personnels filtrés:", list(personnels.values_list('prenom', 'nom', 'type_utilisateur__libelle')))

    if request.method == 'POST':
        form = TacheForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_taches')
    else:
        form = TacheForm()

    taches = Tache.objects.all().order_by('date', 'heure_debut')

    return render(request, 'src/taches.html', {
        'form': form,
        'taches': taches,
        'personnels': personnels,
    })


@admin_required
def gestion_commandes(request):
    commandes = Commande.objects.select_related('utilisateur', 'statut').order_by('-date_commande')
    return render(request, 'src/commandes.html', {
        'commandes': commandes
    })



@admin_required
def detail_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    lignes = commande.lignes.select_related('plat').all()
    statuts = StatutCommande.objects.all()

    if request.method == 'POST':
        new_statut_id = request.POST.get('statut')
        if new_statut_id:
            commande.statut_id = new_statut_id
            commande.save()
            messages.success(request, "Statut mis à jour.")
            return redirect('detail_commande', commande_id=commande.id)

    return render(request, 'src/detail_commande.html', {
        'commande': commande,
        'lignes': lignes,
        'statuts': statuts
    })



@admin_required
def liste_reservations(request):
    reservations = Reservation.objects.all().order_by('-date_reservation')
    return render(request, 'src/liste_reservations.html', {'reservations': reservations})

@admin_required
def detail_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == "POST":
        nouveau_statut = request.POST.get('statut')

        if nouveau_statut in ['confirmee', 'annulee', 'en_attente']:
            ancien_statut = reservation.statut
            reservation.statut = nouveau_statut
            reservation.save()

            # Envoi d'e-mail selon le nouveau statut
            sujet = None
            message = None

            if nouveau_statut == 'confirmee':
                sujet = "Confirmation de votre réservation"
                message = (
                    f"Bonjour {reservation.utilisateur.nom},\n\n"
                    f"Votre réservation pour le {reservation.date_reservation.strftime('%d/%m/%Y')} à {reservation.heure.strftime('%H:%M')} a été CONFIRMÉE.\n\n"
                    f"Merci et à bientôt !\nAl Mountakha"
                )

            elif nouveau_statut == 'annulee':
                sujet = "Annulation de votre réservation"
                message = (
                    f"Bonjour {reservation.utilisateur.nom},\n\n"
                    f"Nous sommes désolés de vous informer que votre réservation pour le {reservation.date_reservation.strftime('%d/%m/%Y')} à {reservation.heure.strftime('%H:%M')} a été ANNULÉE.\n\n"
                    f"Pour toute question, n’hésitez pas à nous contacter.\nCordialement,\nAl Mountakha"
                )

            if sujet and message:
                try:
                    send_mail(
                        sujet,
                        message,
                        'modou99mbengue@gmail.com',  # expéditeur
                        [reservation.utilisateur.mail],  # destinataire
                        fail_silently=False
                    )
                except Exception as e:
                    messages.warning(request, f"Statut mis à jour mais l'e-mail n'a pas pu être envoyé. Erreur : {e}")

            messages.success(request, "Statut de la réservation mis à jour avec succès.")
        else:
            messages.error(request, "Statut invalide.")

        return redirect('liste_reservations')

    return render(request, 'src/detail_reservation.html', {'reservation': reservation})


@admin_required
def statistiques(request):
    # Ventes par jour/semaine/mois
    ventes_journalieres = (
        Commande.objects
        .annotate(jour=TruncDay('date_commande'))
        .values('jour')
        .annotate(total=Sum('montant_total'))
        .order_by('-jour')[:7]
    )

    ventes_hebdomadaires = (
        Commande.objects
        .annotate(semaine=TruncWeek('date_commande'))
        .values('semaine')
        .annotate(total=Sum('montant_total'))
        .order_by('-semaine')[:4]
    )

    ventes_mensuelles = (
        Commande.objects
        .annotate(mois=TruncMonth('date_commande'))
        .values('mois')
        .annotate(total=Sum('montant_total'))
        .order_by('-mois')[:6]
    )

    # Plats populaires
    plats_populaires = (
        LigneCommande.objects
        .values('plat__libelle')
        .annotate(qte_totale=Sum('quantite'))
        .order_by('-qte_totale')[:10]
    )

    # Nombre total de clients
    clients_type = TypeUtilisateur.objects.get(libelle__iexact='client')
    total_clients = Utilisateurs.objects.filter(type_utilisateur=clients_type).count()

    # Clients actifs (ayant passé commande dans les 30 derniers jours)
    clients_actifs = Utilisateurs.objects.filter(
        type_utilisateur=clients_type,
        commandes__date_commande__gte=now() - timedelta(days=30)
    ).distinct().count()



    # Nombre total d'employés (serveurs + cuisiniers)
    employe_types = TypeUtilisateur.objects.filter(libelle__in=['serveur', 'cuisinier'])
    total_employes = Utilisateurs.objects.filter(type_utilisateur__in=employe_types).count()

    

    return render(request, 'src/adminpanel.html', {
        'ventes_journalieres': ventes_journalieres,
        'ventes_hebdomadaires': ventes_hebdomadaires,
        'ventes_mensuelles': ventes_mensuelles,
        'plats_populaires': plats_populaires,
        'total_clients': total_clients,
        'clients_actifs': clients_actifs,
        'total_employes': total_employes,
    })


@admin_required
def gestion_employes(request):
    query = request.GET.get('q', '')
    if query:
        employes = Utilisateurs.objects.filter(
            Q(prenom__icontains=query) |
            Q(nom__icontains=query) |
            Q(login__icontains=query) |
            Q(mail__icontains=query) |
            Q(telephone__icontains=query)
        )
    else:
        employes = Utilisateurs.objects.all()

    context = {
        'employes': employes,
    }
    return render(request, 'src/employe.html', context)
