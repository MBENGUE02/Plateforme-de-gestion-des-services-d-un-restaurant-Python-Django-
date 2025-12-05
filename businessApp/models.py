from django.db import models
from adminApp.models import Utilisateurs

class Table(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    capacite = models.PositiveIntegerField()

    def __str__(self):
        return f"Table {self.numero} (Capacité: {self.capacite})"

# Reservation d'une table
class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_place = models.PositiveIntegerField()
    date_reservation = models.DateField()  # Modifié ici
    heure = models.TimeField()
    utilisateur = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE, related_name='reservations')
    tables = models.ManyToManyField(Table, related_name='reservations')
    statut = models.CharField(max_length=50, choices=[
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('annulee', 'Annulée')
    ], default='en_attente')

    def __str__(self):
        return f"Réservation {self.id} - {self.utilisateur.nom} le {self.date_reservation}"


# Cathegorie
class Categorie(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


# Produit ou plat du menu
class ElementMenu(models.Model):
    id = models.AutoField(primary_key=True)
    libelle = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    #image = models.ImageField(upload_to='menu/')
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    allergenes = models.ManyToManyField('Allergene', related_name='plats', blank=True)
    est_epuise = models.BooleanField(default=False)
    specialite_jour = models.BooleanField(default=False)

    def __str__(self):
        return self.libelle
    
class ImageMenu(models.Model):
    element = models.ForeignKey(ElementMenu, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='menu/')

    def __str__(self):
        return f"Image de {self.element.libelle}"
    

class MenuJour(models.Model):
    date = models.DateField(unique=True)
    plats = models.ManyToManyField(ElementMenu, related_name='menus_jour')

    def __str__(self):
        return f"Menu du {self.date}"



# Allergène
class Allergene(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    libelle = models.CharField(max_length=50)


    def __str__(self):
        return self.libelle

# Statut de commande (Ex: En cours, Livrée, Annulée)
class StatutCommande(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    libelle = models.CharField(max_length=50)

    def __str__(self):
        return self.libelle

# Commande d’un client
class Commande(models.Model):
    id = models.AutoField(primary_key=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.ForeignKey(StatutCommande, on_delete=models.PROTECT, related_name='commandes')
    utilisateur = models.ForeignKey(Utilisateurs, on_delete=models.CASCADE, related_name='commandes')

    def __str__(self):
        return f"Commande {self.id} - {self.utilisateur.nom} ({self.date_commande.date()})"

# Ligne de commande (chaque plat commandé)
class LigneCommande(models.Model):
    id = models.AutoField(primary_key=True)
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    plat = models.ForeignKey(ElementMenu, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantite} x {self.plat.libelle} (Commande {self.commande.id})"

    @property
    def total_ligne(self):
        return self.quantite * self.prix_unitaire

# Facture liée à une commande
class Facture(models.Model):
    id = models.IntegerField(primary_key=True)
    numero = models.CharField(max_length=50, unique=True)
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name='facture')
    date_facture = models.DateTimeField(auto_now_add=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Facture {self.numero} (Commande {self.commande.id})"


class Statistique(models.Model):
    date = models.DateField()
    chiffre_affaires = models.DecimalField(max_digits=12, decimal_places=2)
    nombre_commandes = models.PositiveIntegerField()
    nombre_clients = models.PositiveIntegerField()
