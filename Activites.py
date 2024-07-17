import snowflake.connector
class Activites():
    def __init__(self, Code_Activite, Nom_Activite, description, prix, Image, NOMBRE_PLACES_DISPONIBLE):
        self.Code_Activite = Code_Activite
        self.Nom_Activite = Nom_Activite
        self.description = description
        self.prix = prix
        self.Image = Image
        self.NOMBRE_PLACES_DISPONIBLE = NOMBRE_PLACES_DISPONIBLE

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
    @classmethod
    def get_activities(cls):
        user = "ASAA"  
        password = "Maghreb1234"
        account = "lsyveyx-vd01067"
        
        conn = cls.connect_to_snowflake(user, password, account)

        if conn:
            try:
                cursor = conn.cursor()

                # Requête SQL pour récupérer les activités
                query = "SELECT Code_Activite, Nom_Activite, description, prix, Image, NOMBRE_PLACES_DISPONIBLE FROM centre_sportif.centre.activites"
                cursor.execute(query)

                # Récupération de tous les résultats
                activities = []
                for row in cursor.fetchall():
                    activities.append(cls(*row))  # Crée une instance Activites pour chaque ligne de résultat

                # Fermeture du curseur et de la connexion
                cursor.close()
                conn.close()

                return activities
            except Exception as e:
                print(f"Erreur lors de la récupération des activités : {str(e)}")
                return []
        else:
            print("Connexion à Snowflake non établie.")
            return []
    @classmethod
    def get_activity_by_code(cls, Code_Activite):
        user = "ASAA"
        password = "Maghreb1234"
        account = "lsyveyx-vd01067"
        
        conn = cls.connect_to_snowflake(user, password, account)

        if conn:
            try:
                cursor = conn.cursor()
                query = "SELECT Code_Activite, Nom_Activite, description, prix, Image, NOMBRE_PLACES_DISPONIBLE FROM centre_sportif.centre.activites WHERE Code_Activite = %s"
                cursor.execute(query, (Code_Activite, ))                # Récupération du résultat
                row = cursor.fetchone()
                cursor.close()
                conn.close()

                if row:
                    return cls(*row)  
                else:
                    return None
            except Exception as e:
                print(f"Erreur lors de la récupération de l'activité : {str(e)}")
                return None
        else:
            print("Connexion à Snowflake non établie.")
            return None
        
    @staticmethod
    def decrementer_nombre_places(activite_id):
        user = "ASAA"
        password = "Maghreb1234"
        account = "lsyveyx-vd01067"
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account
        )

        if conn:
            try:
                cursor = conn.cursor()

                cursor.execute("SELECT NOMBRE_PLACES_DISPONIBLE FROM Centre_Sportif.Centre.Activites WHERE CODE_ACTIVITE = %s", (activite_id,))
                places_disponibles = cursor.fetchone()[0]

                if places_disponibles > 0:
                    cursor.execute("UPDATE Centre_Sportif.Centre.Activites SET NOMBRE_PLACES_DISPONIBLE = NOMBRE_PLACES_DISPONIBLE - 1 WHERE CODE_ACTIVITE = %s", (activite_id,))
                    conn.commit()
                    return True
                else:
                    return False

            except Exception as e:
                print(f"Erreur lors de la décrémentation des places disponibles : {str(e)}")
                return False

            finally:
                cursor.close()
                conn.close()

        else:
            print("Connexion à Snowflake non établie.")
            return False






    @classmethod    
    def horaire_activites(cls, id_activity):
        user = "ASAA"  
        password = "Maghreb1234"
        account = "lsyveyx-vd01067"
    
        conn = cls.connect_to_snowflake(user, password, account)

        if conn:
            try:
                cursor = conn.cursor()
                query = """
                SELECT *
                FROM centre_sportif.centre.horaire
                WHERE CODE_ACTIVITE = %s
                """
                cursor.execute(query, (id_activity,))
                results = cursor.fetchall()  # Use fetchall() if multiple rows are expected
                print(results)
                
                # Convert results to a list of dictionaries for easier usage in templates
                schedule_details = [
                    {
                        
                        'ID_HORAIRE' :row[0],
                        'date_of_activity': row[1],
                        'start_hour': row[2],
                        'end_hour': row[3]
                        
                    }
                    for row in results
                ]
                
                cursor.close()
                return schedule_details
            except snowflake.connector.errors.Error as e:
                print(f"Query failed: {e}")
                return []
            finally:
                conn.close()
        else:
            print("Failed to connect to Snowflake")
            return []