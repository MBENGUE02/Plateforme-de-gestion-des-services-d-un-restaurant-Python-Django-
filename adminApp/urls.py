from django.urls import path
from . import views


urlpatterns = [
    #path('dashboard/', views.dashboard, name='admin_dashboard'),
    path('employes/', views.liste_employes, name='liste_employes'),
    path('plats/', views.liste_plats, name='liste_plats'),
    path('menus/', views.gestion_menu_jour, name='gestion_menu_jour'),
    path('taches/', views.gestion_taches, name='gestion_taches'),
    path('commandes/', views.gestion_commandes, name='gestion_commandes'),
    path('commandes/<int:commande_id>/', views.detail_commande, name='detail_commande'),
    path('reservations/', views.liste_reservations, name='liste_reservations'),
    path('reservations/<int:reservation_id>/', views.detail_reservation, name='detail_reservation'),
    path('statistiques/', views.statistiques, name='statistiques'),
]
