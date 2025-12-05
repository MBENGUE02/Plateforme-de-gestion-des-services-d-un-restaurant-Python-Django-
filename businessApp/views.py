from django.shortcuts import render, redirect, get_object_or_404
from .forms import ElementMenu, ElementMenuForm, ImageMenu, ImageMenuForm
from businessApp.models import Commande, LigneCommande, StatutCommande
# Create your views here.


