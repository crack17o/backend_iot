"""
Vues d'authentification personnalisées
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


def login_view(request):
    """
    Page de connexion pour les administrateurs
    """
    if request.user.is_authenticated:
        return redirect('web:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_staff or user.is_superuser:
                    login(request, user)
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('web:dashboard')
                else:
                    messages.error(request, "Vous n'avez pas les permissions nécessaires. Seuls les administrateurs peuvent accéder à cette application.")
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            messages.error(request, "Veuillez remplir tous les champs.")
    
    return render(request, 'login.html')


def logout_view(request):
    """
    Déconnexion
    """
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('login')
