from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('apropos', views.apropos, name='apropos'),
    path('menu', views.menu, name='menu'),
    path('chef', views.chef, name='chef'),
    path('galerie', views.galerie, name='galerie'),
    path('auth', views.authentification, name='authentification'),
    path('menu-du-jour/', views.menu_du_jour, name='menu_du_jour'),
    path('panier', views.voir_panier, name='voir_panier'),
    path('retirer/<int:plat_id>/', views.retirer_du_panier, name='retirer_du_panier'),
    path('ajouter/<int:plat_id>/', views.ajouter_panier, name='ajouter_panier'),
    path('valider', views.valider_commande, name='valider_commande'),
    path('facture/<int:commande_id>/', views.facture_pdf, name='facture_pdf'),
    path('confirmation/', views.confirmation_commande, name='confirmation_commande'),
    path('reservation/', views.reservation_view, name='reserver_table'),
    path('reservation/confirmation/', views.confirmation_reservation, name='confirmation_reservation'),
    path('logout/', views.deconnexion, name='deconnexion'),
    path('mon-historique/', views.historique_utilisateur, name='historique_utilisateur'),
]