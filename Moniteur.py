from Utilisateur import Utilisateur
class Moniteur(Utilisateur):
    def __init__(self, nom_utilisateur, mot_de_passe, nom, prenom, email, telephone=None, adresse=None):
        super().__init__( nom_utilisateur, mot_de_passe, nom, prenom, email, telephone, adresse)
        self.type_utilisateur ="moniteur"