from Utilisateur import Utilisateur
class Client(Utilisateur):
    def __init__(self, nom_utilisateur, mot_de_passe, nom, prenom, email, telephone=None, adresse=None):
        super().__init__( nom_utilisateur, mot_de_passe, nom, prenom, email, telephone, adresse)
        self.type_utilisateur ="client"

    def get_user_id(self):
        user = "ASAA"
        password = "Maghreb1234"
        account = "lsyveyx-vd01067"
        conn = Utilisateur.connect_to_snowflake(user, password, account)

        if conn:
            try:
                cursor = conn.cursor()
                query = "SELECT ID FROM Centre_Sportif.Centre.Utilisateur WHERE NOM_UTILISATEUR = %s"
                cursor.execute(query, (self.nom_utilisateur,))
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                if result:
                    return result[0]
                else:
                    return None
            except Exception as e:
                print(f"Erreur lors de la récupération de l'ID utilisateur : {str(e)}")
                return None
        else:
            print("Connexion à Snowflake non établie.")
            return None

    def inscrire_a_activite(self, activite_id, date_inscription):
        user_id = self.get_user_id()
        if user_id is None:
            print("Utilisateur non trouvé.")
            return False

        user = "ASAA"
        password = "Maghreb1234"
        account = "lsyveyx-vd01067"
        conn = Utilisateur.connect_to_snowflake(user, password, account)

        if conn:
            try:
                cursor = conn.cursor()
                query = """
                INSERT INTO Centre_Sportif.Centre.Inscription_Activite (ID_UTILISATEUR, CODE_ACTIVITE, DATE_INSCRIPTION)
                VALUES (%s, %s, %s)
                """
                cursor.execute(query, (user_id, activite_id, date_inscription))
                conn.commit()
                cursor.close()
                conn.close()
                return True
            except Exception as e:
                print(f"Erreur lors de l'inscription à l'activité : {str(e)}")
                return False
        else:
            print("Connexion à Snowflake non établie.")
            return False