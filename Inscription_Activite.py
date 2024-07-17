import snowflake.connector

class Inscription_Activite:
    def __init__(self, code_Activite, Id_Utilisateur, ID_HORAIRE, date):
        self.code_Activite = code_Activite
        self.Id_Utilisateur = Id_Utilisateur
        self.ID_HORAIRE = ID_HORAIRE
        self.date = date

class Inscription_Activite:
    def __init__(self,code_Activite, Id_Utilisateur, date):
        self.code_Activite=code_Activite
        self.Id_Utilisateur=Id_Utilisateur
        self.date=date

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

            print(f"Erreur lors de la connexion à Snowflake : {str(e)}")
            print(f"Erreur lors de la connexion a Snowflake : {str(e)}")
            return None

    def annuler_inscription(self):
        user = "ASAA"
        password = "Maghreb1234"
        account = "lsyveyx-vd01067"
        conn = Inscription_Activite.connect_to_snowflake(user, password, account)

        if conn:
            try:
                cursor = conn.cursor()
                query = "DELETE FROM Centre_Sportif.Centre.Inscription_activite WHERE id_utilisateur = %s AND code_activite = %s and ID_HORAIRE= %s"
                cursor.execute(query, (self.Id_Utilisateur, self.code_Activite, self.ID_HORAIRE))
                print(f"Exécution de la requête : {query} avec id_utilisateur = {self.Id_Utilisateur} et code_activite = {self.code_Activite} et ID_HORAIRE = {self.ID_HORAIRE}")
                conn.commit()
                query = "DELETE FROM Centre_Sportif.Centre.Inscription_activite WHERE id_utilisateur = %s AND code_activite = %s"
                cursor.execute(query, (self.Id_Utilisateur, self.code_Activite))
                print(f"Exécution de la requête : {query} avec id_utilisateur = {self.Id_Utilisateur} et code_activite = {self.code_Activite}")
                conn.commit()  
                cursor.close()
                conn.close()
                return True
            except Exception as e:
                print(f"Erreur lors de la suppression de l'inscription : {str(e)}")
                return False
        else:
            print("Connexion à Snowflake non établie.")
            return False
