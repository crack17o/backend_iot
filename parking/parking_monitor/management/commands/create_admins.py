"""
Script de gestion Django pour créer les administrateurs
Usage: python manage.py create_admins
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Crée les administrateurs du système'

    def handle(self, *args, **options):
        # Liste des admins à créer
        admins = [
            'Jael',
            'Stone',
            'Jelly',
            'Nehemy',
            'Nehemie',
            'Eddy',
            'Elyel',
            'Josephat',
            'Ruth',
            'Ernick',
            'Enoch',
            'Jonathan',
        ]
        
        password = '1234567890'
        created_count = 0
        updated_count = 0
        
        for username in admins:
            # Créer un email basé sur le nom d'utilisateur
            email = f"{username.lower()}@parking-intelligence.local"
            
            try:
                # Vérifier si l'utilisateur existe déjà
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'is_staff': True,
                        'is_superuser': True,
                    }
                )
                
                if created:
                    user.set_password(password)
                    user.save()
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Admin créé: {username}')
                    )
                else:
                    # Mettre à jour l'utilisateur existant pour s'assurer qu'il est admin
                    if not user.is_staff or not user.is_superuser:
                        user.is_staff = True
                        user.is_superuser = True
                        user.set_password(password)
                        user.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'↻ Admin mis à jour: {username}')
                        )
                    else:
                        # Réinitialiser le mot de passe même si l'utilisateur existe
                        user.set_password(password)
                        user.save()
                        self.stdout.write(
                            self.style.WARNING(f'↻ Mot de passe réinitialisé pour: {username}')
                        )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Erreur lors de la création de {username}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Terminé! {created_count} admin(s) créé(s), {updated_count} admin(s) mis à jour.'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f'Mot de passe pour tous les admins: {password}')
        )
