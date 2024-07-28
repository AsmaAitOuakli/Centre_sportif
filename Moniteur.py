

################################# ajouter ca au complet#############################################################
from Utilisateur import Utilisateur
class Moniteur(Utilisateur):
    def __init__(self, nom_utilisateur, mot_de_passe, nom, prenom, email, telephone=None, adresse=None):
        super().__init__( nom_utilisateur, mot_de_passe, nom, prenom, email, telephone, adresse)
        self.type_utilisateur ="moniteur"

    @staticmethod
    def get_activities_with_moniteur():
        try:
            user = "ASAA"  
            password = "Maghreb1234"
            account = "lsyveyx-vd01067"
            conn = Utilisateur.connect_to_snowflake(user,password,account)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.Code_Activite, a.Nom_Activite
                FROM Centre_Sportif.Centre.Activites a
            """)
            activites = cursor.fetchall()
            cursor.close()
            conn.close()
            return activites
        except Exception as e:
            print(f"Erreur lors de la récupération des activités : {str(e)}")
            return None
     
 
    # def ajouter_disponibilite(self, jour, start_hour, end_hour, code_activite):
    #     try:
    #         user = "ASAA"  
    #         password = "Maghreb1234"
    #         account = "lsyveyx-vd01067"
    #         conn = Utilisateur.connect_to_snowflake(user,password,account)
    #         cursor = conn.cursor()
    #         cursor.execute("""
    #             INSERT INTO centre_sportif.centre.disponibilite(jour, start_hour, end_hour, code_activite, nom_utilisateur)
    #             VALUES (%s, %s, %s, %s, %s)
    #         """, (jour, start_hour, end_hour, code_activite, self.nom_utilisateur,))
    #         conn.commit()
    #         cursor.close()
    #         conn.close()
    #         return True
    #     except Exception as e:
    #         print(f"Erreur lors de l'ajout de la disponibilité : {str(e)}")
    #         return False

    def ajouter_disponibilite(self, jour, code_horaire):
        try:
            user = "ASAA"
            password = "Maghreb1234"
            account = "lsyveyx-vd01067"
            conn = Utilisateur.connect_to_snowflake(user, password, account)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO centre_sportif.centre.disponibilite(jour, code_horaire, nom_utilisateur)
                VALUES (%s, %s, %s)
            """, (jour, code_horaire, self.nom_utilisateur))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Erreur lors de l'ajout de la disponibilité : {str(e)}")
            return False

    def get_disponibilites(self):
        try:
            user = "ASAA"  
            password = "Maghreb1234"
            account = "lsyveyx-vd01067"
            conn = Utilisateur.connect_to_snowflake(user,password,account)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.jour, h.Start_Hour, h.End_Hour, a.Nom_Activite
                FROM Centre_Sportif.Centre.disponibilite d
                JOIN Centre_Sportif.Centre.horaire h ON d.code_horaire = h.id_horaire
                JOIN Centre_Sportif.Centre.activites a ON h.Code_Activite = a.Code_Activite
                WHERE d.nom_utilisateur = %s
            """, (self.nom_utilisateur,))
            disponibilites = cursor.fetchall()
            cursor.close()
            conn.close()
            return disponibilites
        except Exception as e:
            print(f"Erreur lors de la récupération des disponibilités : {str(e)}")
            return []


    @staticmethod
    def get_horaires():
        try:
            user = "ASAA"
            password = "Maghreb1234"
            account = "lsyveyx-vd01067"
            conn = Utilisateur.connect_to_snowflake(user, password, account)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT h.id_horaire, h.Start_Hour, h.End_Hour, h.Code_Activite, a.Nom_Activite
                FROM centre_sportif.centre.horaire h
                JOIN centre_sportif.centre.activites a ON h.Code_Activite = a.Code_Activite
            """)
            horaires = cursor.fetchall()
            cursor.close()
            conn.close()
            return horaires
        except Exception as e:
            print(f"Erreur lors de la récupération des horaires : {str(e)}")
            return None


