import snowflake.connector
from flask import Flask, jsonify, render_template, request
import bcrypt
import datetime
class Utilisateur:
    @classmethod
    def connect_to_snowflake(cls, user, password, account):
        try:
            conn = snowflake.connector.connect(
                user=user,
                password=password,
                account=account,
                database='Centre_Sportif',
                schema='centre'
            )
            return conn
        except Exception as e:
            print(f"Erreur lors de la connexion a Snowflake : {str(e)}")
            return None

    def __init__(self, nom_utilisateur, mot_de_passe, nom='', prenom='', email='', telephone=None, adresse=None,type_utilisateur=''):
        self.nom_utilisateur = nom_utilisateur
        self.mot_de_passe = mot_de_passe
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.telephone = telephone
        self.adresse = adresse
        self.type_utilisateur=type_utilisateur

    def se_connecter(self):
        user = "ASAA"  
        password = "Maghreb1234"
        account = "lsyveyx-vd01067"
        conn = self.connect_to_snowflake(user, password, account)

        if conn:
            if self.verifier_identite(conn):
                conn.close()
                return True
            else:
                conn.close()
                return False
        else:
            return False

   
    def verifier_identite(self, conn):
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(f"SELECT mot_de_passe FROM Centre_Sportif.Centre.Utilisateur WHERE nom_utilisateur = '{self.nom_utilisateur}'")
                row = cursor.fetchone()

                if row:
                    stored_password = row[0]
                    if bcrypt.checkpw(self.mot_de_passe.encode('utf-8'), stored_password.encode('utf-8')):
                        print("Utilisateur trouvé.")
                        return True
                    else:
                        print("Mot de passe incorrect.")
                        return False
                else:
                    print("Utilisateur non trouvé.")
                    return False

                cursor.close()
            except Exception as e:
                print(f"Erreur lors de la vérification de l'utilisateur : {str(e)}")
                return False
        else:
            print("Connexion à Snowflake non établie.")
            return False
        
    def s_inscrire(self):
        user = "ASAA"
        password = "Maghreb1234"
        account = "lsyveyx-vd01067"
        conn = Utilisateur.connect_to_snowflake(user, password, account)

        if conn:
            try:
                cursor = conn.cursor()
                date = datetime.datetime.now()
                curantDate = date.year
                # Vérification de l'existence de l'email
                email_query = """SELECT EMAIL FROM Centre_Sportif.Centre.Utilisateur WHERE EMAIL = %s"""
                cursor.execute(email_query, (self.email,))
                email_exists = cursor.fetchone()

                if email_exists:
                    print("Email déjà existant.")
                    return False

                # Génération du nom d'utilisateur
                self.nom_utilisateur = self.nom[:2].lower() + self.prenom[:2].lower() +str(curantDate)

                # Calcul du mot de passe
                annee_naissance = self.dateNaissance.split('-')[0]
                self.mot_de_passe = self.nom[-2:].lower() + "ifitness" + annee_naissance
                hashed_password = bcrypt.hashpw(self.mot_de_passe.encode('utf-8'), bcrypt.gensalt())

                # Insertion de l'utilisateur dans la base de données
                query = """
                INSERT INTO Centre_Sportif.Centre.Utilisateur (NOM_UTILISATEUR, MOT_DE_PASSE, NOM, PRENOM, EMAIL, TELEPHONE, ADRESSE, TYPE_UTILISATEUR)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (self.nom_utilisateur, hashed_password.decode('utf-8'), self.nom, self.prenom, self.email, self.telephone, self.adresse, "client"))
                conn.commit()

                print("Utilisateur inscrit avec succès.")
                cursor.close()
                conn.close()
                return True

            except Exception as e:
                print(f"Erreur lors de l'inscription : {str(e)}")
                return False

        else:
            print("Connexion à Snowflake non établie.")
            return False

    def get_utilisateur(self):
        user = "ASAA"  
        password = "Maghreb1234"
        account = "lsyveyx-vd01067"
        conn = self.connect_to_snowflake(user, password, account)
        if conn :
            try:
                cursor = conn.cursor()
                cursor.execute(f"""
                SELECT nom, prenom, email, telephone, adresse
                FROM Centre_Sportif.Centre.Utilisateur
                WHERE nom_utilisateur = '{self.nom_utilisateur}'
                """)
                row = cursor.fetchone()

                
                if row:
                    self.nom = row[0]
                    self.prenom = row[1]
                    self.email = row[2]
                    self.telephone = row[3]
                    self.adresse = row[4]
                    utilisateur_info = {
                        'nom': self.nom,
                        'prenom': self.prenom,
                        'email': self.email,
                        'telephone': self.telephone,
                        'adresse': self.adresse
                    }
                    return utilisateur_info

                    
            except Exception as e:
                print(f"Erreur lors de la verification de l'utilisateur : {str(e)}")
                return None
            finally:
                cursor.close()
                conn.close()
        else:
            return None
    def updateprofile(self):
        user = "ASAA"  
        password = "Maghreb1234"
        account = "lsyveyx-vd01067"
        conn = self.connect_to_snowflake(user, password, account)

        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    UPDATE Centre_Sportif.Centre.Utilisateur
                    SET NOM = %s, PRENOM = %s, EMAIL = %s, TELEPHONE = %s, ADRESSE = %s
                    WHERE NOM_UTILISATEUR = %s
                """
               
                print("Executing query:", query)
                print("With values:", (self.nom, self.prenom, self.email, self.telephone, self.adresse, self.nom_utilisateur))
            
                cursor.execute(query, (self.nom, self.prenom, self.email, self.telephone, self.adresse, self.nom_utilisateur))
                conn.commit()

                print("Profile updated successfully.")
                cursor.close()
                conn.close()
                return True

            except Exception as e:
                print(f"Error updating profile: {str(e)}")
                return False

        else:
            print("Connection to Snowflake not established.")
            return False
    def delete_utilisateur(self):
     user = "ASAA"  
     password = "Maghreb1234"
     account = "lsyveyx-vd01067"
     conn = self.connect_to_snowflake(user, password, account)

     if conn:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM Centre_Sportif.Centre.Utilisateur WHERE nom_utilisateur = %s"
            print("Executing query:", query)
            print("With value:", self.nom_utilisateur)
            
            cursor.execute(query, (self.nom_utilisateur,))
            conn.commit()

            print("Profile deleted successfully.")
            cursor.close()
            conn.close()
            return True

        except Exception as e:
            print(f"Error deleting profile: {str(e)}")
            return False

     else:
        print("Connection to Snowflake not established.")
        return False

