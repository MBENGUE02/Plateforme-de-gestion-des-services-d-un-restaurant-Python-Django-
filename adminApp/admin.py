from django.contrib import admin
from .models import Permission, TypeUtilisateur, Utilisateurs, Tache, Contact, Adresse
# Register your models here.


admin.site.register(Permission)
admin.site.register(TypeUtilisateur)
admin.site.register(Utilisateurs)
admin.site.register(Tache)
admin.site.register(Contact)
admin.site.register(Adresse)
