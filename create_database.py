"""
Script pour créer la base de données MySQL pour le projet parking
"""
import pymysql
from pymysql import Error

# Configuration de connexion MySQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,  # Port MySQL (3306 par défaut, ou 3307 selon votre configuration)
    'user': 'root',
    'password': 'jellymaweja7@gmail.com',
    'charset': 'utf8mb4'
}

# Nom de la base de données à créer
DATABASE_NAME = 'parking_db'

def create_database():
    """Crée la base de données si elle n'existe pas"""
    try:
        # Connexion à MySQL (sans spécifier de base de données)
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            # Créer la base de données si elle n'existe pas
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"[OK] Base de donnees '{DATABASE_NAME}' creee avec succes !")
            
            # Vérifier que la base existe
            cursor.execute("SHOW DATABASES LIKE %s", (DATABASE_NAME,))
            result = cursor.fetchone()
            
            if result:
                print(f"[OK] Verification : La base de donnees '{DATABASE_NAME}' existe bien.")
            else:
                print(f"[ERREUR] La base de donnees n'a pas pu etre creee.")
        
        connection.close()
        return True
        
    except Error as e:
        print(f"[ERREUR] Erreur lors de la creation de la base de donnees : {e}")
        print("\nVerifiez que :")
        print("1. MySQL est demarre")
        print("2. Les identifiants sont corrects (utilisateur, mot de passe, port)")
        print("3. L'utilisateur a les permissions pour creer des bases de donnees")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Création de la base de données MySQL")
    print("=" * 50)
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Port: {DB_CONFIG['port']}")
    print(f"User: {DB_CONFIG['user']}")
    print(f"Database: {DATABASE_NAME}")
    print("=" * 50)
    print()
    
    if create_database():
        print("\n[OK] Vous pouvez maintenant executer les migrations Django :")
        print("   python manage.py migrate")
    else:
        print("\n[ERREUR] Echec de la creation de la base de donnees.")
