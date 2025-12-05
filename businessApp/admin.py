from django.contrib import admin
from .models import  Categorie, Commande, LigneCommande, Facture, ElementMenu, Allergene, StatutCommande, Statistique, ImageMenu, MenuJour, Reservation
# Register your models here.


admin.site.register(Categorie)
admin.site.register(Commande)
admin.site.register(LigneCommande)
admin.site.register(Facture)
admin.site.register(ElementMenu)
admin.site.register(ImageMenu)
admin.site.register(MenuJour)
admin.site.register(Allergene)
admin.site.register(StatutCommande)
admin.site.register(Statistique)
admin.site.register(Reservation)