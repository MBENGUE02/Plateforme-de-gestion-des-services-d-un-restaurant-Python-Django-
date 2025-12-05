from django.shortcuts import render, redirect, get_object_or_404
from .forms import InscriptionForm
from adminApp.models import TypeUtilisateur, Utilisateurs
from django.contrib import messages
from businessApp.models import MenuJour, Commande, StatutCommande, LigneCommande,ElementMenu, Reservation, Table
from businessApp.forms import AjouterPlatForm, ReservationForm
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import AnonymousUser
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import check_password
from .forms import ConnexionForm
from datetime import datetime
from django.urls import reverse
# decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from adminApp.models import Utilisateurs
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from weasyprint import HTML
from businessApp.models import Commande
from datetime import date


def client_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        utilisateur_id = request.session.get('utilisateur_id')
        if not utilisateur_id:
            return redirect('authentification')

        try:
            utilisateur = Utilisateurs.objects.get(id=utilisateur_id)
        except Utilisateurs.DoesNotExist:
            return redirect('authentification')

        if utilisateur.type_utilisateur.libelle.lower() != 'client':
            return HttpResponseForbidden("Accès réservé au client")

        return view_func(request, *args, **kwargs)
    return wrapper




# Create your views here.

def accueil(request):
    return render(request, 'src/acceuil.html', {})

def apropos(request):
    return render(request, 'src/apropos.html', {})

def menu(request):
    return render(request, 'src/menu.html', {})

def chef(request):
    return render(request, 'src/chef.html', {})

def galerie(request):
    return render(request, 'src/galerie.html', {})

def login(request):
    return render(request, 'src/login.html', {})


def authentification(request):
    mode = request.GET.get('mode', 'connexion')

    if request.method == 'POST':
        if 'connexion' in request.POST:
            form_connexion = ConnexionForm(request.POST)
            form_inscription = InscriptionForm()
            mode = 'connexion'

            if form_connexion.is_valid():
                login_input = form_connexion.cleaned_data['login']
                password_input = form_connexion.cleaned_data['password']

                try:
                    utilisateur = Utilisateurs.objects.get(login=login_input)
                    if utilisateur.password == password_input: 
                        request.session['utilisateur_id'] = utilisateur.id
                        request.session['utilisateur_nom'] = f"{utilisateur.prenom} {utilisateur.nom}"

                        # Redirection en fonction du rôle
                        role = utilisateur.type_utilisateur.libelle.lower()

                        if role == 'admin':
                            return redirect('statistiques')
                        elif role == 'client':
                            return redirect('accueil')
                        elif role == 'cuisinier':
                            return redirect('page_employe') 
                        elif role == 'serveur':
                            return redirect('page_employe') 
                        else:
                            return redirect('accueil')

                    else:
                        messages.error(request, "Mot de passe incorrect.")
                except Utilisateurs.DoesNotExist:
                    messages.error(request, "Utilisateur introuvable.")

        elif 'inscription' in request.POST:
            form_inscription = InscriptionForm(request.POST)
            form_connexion = ConnexionForm()
            mode = 'inscription'

            if form_inscription.is_valid():
                utilisateur = form_inscription.save(commit=False)
                try:
                    type_client = TypeUtilisateur.objects.get(libelle='Client')
                    utilisateur.type_utilisateur = type_client
                    utilisateur.save()
                    messages.success(request, "Inscription réussie. Vous pouvez maintenant vous connecter.")
                    return redirect('authentification')
                except TypeUtilisateur.DoesNotExist:
                    messages.error(request, "Type 'Client' introuvable.")

    else:
        form_connexion = ConnexionForm()
        form_inscription = InscriptionForm()

    return render(request, 'src/login.html', {
        'form_connexion': form_connexion,
        'form_inscription': form_inscription,
        'mode': mode
    })


def deconnexion(request):
   
    request.session.flush()  
    messages.success(request, "Déconnexion réussie.")
    return redirect('authentification')  


def menu_du_jour(request):
    today = timezone.localdate()  # Date du jour
    try:
        menu = MenuJour.objects.get(date=today)
        # Exclure les plats épuisés ici
        plats = menu.plats.filter(est_epuise=False)
    except MenuJour.DoesNotExist:
        plats = []

    panier = request.session.get("panier", {})
    panier_count = sum(panier.values())

    return render(request, 'src/menu.html', {
        'plats': plats,
        'date': today,
        'panier_count': panier_count
    })


@client_required
@require_POST
def ajouter_panier(request, plat_id):
    quantite = int(request.POST.get("quantite", 1))
    panier = request.session.get("panier", {})

    if str(plat_id) in panier:
        panier[str(plat_id)] += quantite
    else:
        panier[str(plat_id)] = quantite

    request.session["panier"] = panier
    return redirect('menu_du_jour')


@client_required
def retirer_du_panier(request, plat_id):
    panier = request.session.get('panier', {})

    if str(plat_id) in panier:
        del panier[str(plat_id)]
        request.session['panier'] = panier
        request.session.modified = True

    return redirect('voir_panier') 


def voir_panier(request):
    panier = request.session.get("panier", {})
    articles = []
    total = 0

    for plat_id, quantite in panier.items():
        plat = get_object_or_404(ElementMenu, id=plat_id)
        sous_total = plat.prix * quantite
        total += sous_total
        articles.append({
            "plat": plat,
            "quantite": quantite,
            "sous_total": sous_total
        })

    context = {
        "articles": articles,
        "total": total
    }
    return render(request, 'src/panier.html', context)

@client_required
@require_POST
def valider_commande(request):
    numero = request.POST.get("numero")
    code = request.POST.get("code")

    if not numero or not code:
        messages.error(request, "Veuillez saisir votre numéro de téléphone et votre code de paiement.")
        return redirect('voir_panier')

    if code != "0000":  
        messages.error(request, "Code de paiement incorrect. Paiement refusé.")
        return redirect('voir_panier')

    panier = request.session.get("panier", {})
    if not panier:
        messages.warning(request, "Votre panier est vide.")
        return redirect('menu_du_jour')

    utilisateur_id = request.session.get("utilisateur_id")
    if not utilisateur_id:
        messages.warning(request, "Vous devez vous connecter pour valider la commande.")
        return redirect('authentification')

    try:
        utilisateur = Utilisateurs.objects.get(id=utilisateur_id)
    except Utilisateurs.DoesNotExist:
        messages.error(request, "Utilisateur introuvable. Veuillez vous reconnecter.")
        return redirect('authentification')

    statut, _ = StatutCommande.objects.get_or_create(
        code="EN_COURS",
        defaults={'libelle': 'En cours de préparation'}
    )

    total = 0
    commande = Commande.objects.create(
        utilisateur=utilisateur,
        statut=statut,
        montant_total=0,
    )

    for plat_id, quantite in panier.items():
        plat = get_object_or_404(ElementMenu, id=plat_id)
        LigneCommande.objects.create(
            commande=commande,
            plat=plat,
            quantite=quantite,
            prix_unitaire=plat.prix
        )
        total += plat.prix * quantite

    commande.montant_total = total
    commande.save()
    request.session["panier"] = {}

    messages.success(request, f"Commande enregistrée avec succès. Paiement simulé avec {numero}.")
    return redirect(reverse('confirmation_commande') + f'?commande_id={commande.id}')


@client_required
def confirmation_commande(request):
    commande_id = request.GET.get('commande_id')
    context = {}
    if commande_id:
        context['commande_id'] = commande_id
    return render(request, 'src/confirmation_commande.html', context)



@require_POST
@login_required
def ajouter_commande_depuis_menu(request):
    form = AjouterPlatForm(request.POST)
    if form.is_valid():
        plat_id = form.cleaned_data['plat_id']
        quantite = form.cleaned_data['quantite']
        plat = get_object_or_404(ElementMenu, id=plat_id)

        statut_en_attente = StatutCommande.objects.get(code='EN_ATTENTE')
        commande, _ = Commande.objects.get_or_create(
            utilisateur=request.user,
            statut=statut_en_attente,
            defaults={'montant_total': 0}
        )

        ligne, created = LigneCommande.objects.get_or_create(
            commande=commande,
            plat=plat,
            defaults={'quantite': quantite, 'prix_unitaire': plat.prix}
        )
        if not created:
            ligne.quantite += quantite
            ligne.save()

        commande.montant_total = sum(
            l.quantite * l.prix_unitaire for l in commande.lignes.all()
        )
        commande.save()

    return redirect('menu_du_jour')  # ou 'voir_commande'



from itertools import combinations

from datetime import datetime, date
from itertools import combinations
from django.shortcuts import render, redirect
from django.contrib import messages


@client_required
def reservation_view(request):
    utilisateur_id = request.session.get("utilisateur_id")
    if not utilisateur_id:
        return redirect("authentification")

    try:
        utilisateur = Utilisateurs.objects.get(id=utilisateur_id)
    except Utilisateurs.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
        return redirect("authentification")

    if request.method == "POST":
        try:
            nombre_place = int(request.POST.get("nombre_place"))
            heure = request.POST.get("heure")
            date_reservation = request.POST.get("date_reservation")

            date_obj = datetime.strptime(date_reservation, "%Y-%m-%d").date()
            heure_obj = datetime.strptime(heure, "%H:%M").time()
        except (ValueError, TypeError):
            return render(request, 'src/acceuil.html', {
                'error': "Date, heure ou nombre invalide.",
                'today': date.today()
            })

        # ❌ Blocage si la date est dans le passé
        if date_obj < date.today():
            return render(request, 'src/acceuil.html', {
                'error': "Impossible de réserver pour une date passée.",
                'today': date.today()
            })

        # ❌ Optionnel : blocage pour heure passée aujourd'hui
        if date_obj == date.today() and heure_obj <= datetime.now().time():
            return render(request, 'src/acceuil.html', {
                'error': "Impossible de réserver pour une heure déjà passée.",
                'today': date.today()
            })

        # Récupérer les tables déjà réservées
        reservations_existantes = Reservation.objects.filter(
            date_reservation=date_obj,
            heure=heure_obj
        )
        tables_occupees = Table.objects.filter(
            reservations__in=reservations_existantes
        ).distinct()

        tables_disponibles = Table.objects.exclude(
            id__in=tables_occupees.values_list('id', flat=True)
        ).order_by('capacite')

        # Recherche de combinaison optimale de tables
        allocation = None
        for i in range(1, len(tables_disponibles) + 1):
            for comb in combinations(tables_disponibles, i):
                total = sum(t.capacite for t in comb)
                if total >= nombre_place:
                    allocation = comb
                    break
            if allocation:
                break

        if not allocation:
            return render(request, 'src/acceuil.html', {
                'error': "Aucune table disponible pour ce nombre de places à cette date et heure.",
                'today': date.today()
            })

        # Création de la réservation
        reservation = Reservation.objects.create(
            nombre_place=nombre_place,
            heure=heure_obj,
            date_reservation=date_obj,
            utilisateur=utilisateur
        )
        reservation.tables.set(allocation)

        return redirect("confirmation_reservation")

    # GET: afficher le formulaire
    return render(request, "src/acceuil.html", {
        'today': date.today()
    })



@client_required
def confirmation_reservation(request):
    utilisateur_id = request.session.get("utilisateur_id")
    if not utilisateur_id:
        return redirect("authentification")

    try:
        utilisateur = Utilisateurs.objects.get(id=utilisateur_id)
    except Utilisateurs.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
        return redirect("authentification")

    # Récupérer la dernière réservation de ce client
    reservation = utilisateur.reservations.order_by('-id').first()

    if not reservation:
        messages.error(request, "Aucune réservation trouvée.")
        return redirect("reserver_table")

    tables = reservation.tables.all()

    return render(request, 'src/confirmation_reservation.html', {
        'reservation': reservation,
        'tables': tables
    })



@client_required
def facture_pdf(request, commande_id):
    commande = get_object_or_404(Commande, pk=commande_id)
    
    # Récupérer les lignes de la commande
    lignes = commande.lignes.all()  # ou le nom correct de la relation
    
    # Calculer le total par ligne (quantite * prix_unitaire)
    for ligne in lignes:
        ligne.montant_total = ligne.quantite * ligne.prix_unitaire
    
    # Passer la commande ET les lignes au template
    context = {
        'commande': commande,
        'lignes': lignes,
    }
    
    html_content = render(request, 'src/facture_pdf.html', context).content.decode('utf-8')
    
    pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_commande_{commande_id}.pdf"'
    return response


@client_required
def historique_utilisateur(request):
    utilisateur_id = request.session.get('utilisateur_id')
    if not utilisateur_id:
        return redirect('authentification')  # ou ta page login

    commandes = Commande.objects.filter(utilisateur_id=utilisateur_id).order_by('-date_commande')
    reservations = Reservation.objects.filter(utilisateur_id=utilisateur_id).order_by('-date_reservation')

    return render(request, 'src/historique.html', {
        'commandes': commandes,
        'reservations': reservations,
    })

