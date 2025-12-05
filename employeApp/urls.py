from django.urls import path
from . import views

urlpatterns = [
    path('employe/', views.page_employe, name='page_employe'),
    path('plat/<int:plat_id>/toggle/', views.toggle_dispo_plat, name='toggle_dispo_plat'),
    path('commande/<int:commande_id>/servie/', views.marquer_commande_servie, name='marquer_commande_servie'),
    path('commande/<int:commande_id>/prete/', views.marquer_commande_prete, name='marquer_commande_prete'),
    path('commande/<int:commande_id>/servie/', views.marquer_commande_servie, name='marquer_commande_servie'),
]
