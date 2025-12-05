from django.db import models
from django.contrib.auth.models import User

class Permission(models.Model):
    id = models.AutoField(primary_key=True)
    libelle = models.CharField(max_length=100)

    def __str__(self):
        return self.libelle


class TypeUtilisateur(models.Model):
    id = models.AutoField(primary_key=True)
    libelle = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(Permission, related_name="types_utilisateurs")

    def __str__(self):
        return self.libelle

# Modèle Utilisateurs
class Utilisateurs(models.Model):
    id = models.AutoField(primary_key=True)
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)  # conseillé : hasher ensuite le password
    telephone = models.CharField(null=True)
    mail = models.EmailField(null=True)
    type_utilisateur = models.ForeignKey(TypeUtilisateur, on_delete=models.PROTECT, related_name='utilisateurs')


    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
# Tâches et plannings du personnel
class Tache(models.Model):
    personnel = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE)
    description = models.TextField()
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

# Modèle Contact
class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=20)
    mail = models.EmailField(max_length=100, unique=True)
    utilisateur = models.OneToOneField(Utilisateurs, on_delete=models.CASCADE, related_name='contact')

    def __str__(self):
        return f"{self.mail} ({self.telephone})"

# Modèle Adresse
class Adresse(models.Model):
    id = models.AutoField(primary_key=True)
    rue = models.CharField(max_length=255)
    ville = models.CharField(max_length=100)
    utilisateur = models.OneToOneField(Utilisateurs, on_delete=models.CASCADE, related_name='adresse')

    def __str__(self):
        return f"{self.rue}, {self.ville}"
