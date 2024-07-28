from datetime import datetime
import secrets
import snowflake.connector
from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash
from Utilisateur import Utilisateur
from flask_mail import Mail, Message
import re
from Activites import Activites
from Client import Client
from Inscription_Activite import Inscription_Activite
from Moniteur import Moniteur

app = Flask(__name__)
 
# Generate a random secret key
app.secret_key = secrets.token_hex(16) 
# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'asmaaitouakli@gmail.com'
app.config['MAIL_PASSWORD'] = 'otjw frme hfsm acjg'
app.config['MAIL_DEFAULT_SENDER'] = 'fausse.adresse@gmail.com'
mail = Mail(app)

# Route pour la page de login
@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/update')
def update():
    return render_template('profile.html')

@app.route('/delete')
def delete():
    return render_template('delete.html')

@app.route('/logout')

@app.route('/')
def login():
    return render_template('accueil.html')
#La route de connexion
@app.route('/check_user', methods=['POST'])
def check_user():
    user = "ASAA"
    password = "Maghreb1234"
    account = "lsyveyx-vd01067"
    conn = Utilisateur.connect_to_snowflake(user, password, account)
    if conn:
        nom_utilisateur = request.form['nom_utilisateur']
        mot_de_passe = request.form['mot_de_passe']
        utilisateur = Utilisateur(nom_utilisateur, mot_de_passe)
        if utilisateur.se_connecter():
            conn.close()
            user_info = utilisateur.get_utilisateur()
            if user_info:
                session['user'] = {
                    'nom_utilisateur': nom_utilisateur,
                    'nom': user_info['nom'],
                    'prenom': user_info['prenom'],
                    'email': user_info['email'],
                    'telephone': user_info['telephone'],
                    'adresse': user_info['adresse'],
                    'type_utilisateur': user_info['type_utilisateur'],
                    'mot_de_passe': user_info['mot_de_passe'] 
                }
                return redirect(url_for('afficher_activites'))
            else:
                return "Erreur lors de la récupération des informations utilisateur."
        else:
            return "Échec de la connexion."
    else:
        return "Erreur de connexion à la base de données."
# La route Pour Inscription    
@app.route('/inscription', methods=['GET', 'POST'])    
def inscription():
    if request.method == 'GET':
        return render_template('accueil.html')
    elif request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        telephone = request.form.get('telephone')
        adresse = request.form.get('adresse')
        dateNaissance_str = request.form.get('dateNaissance')
        type_utilisateur = request.form.get('type_utilisateur')
        # Convertir la chaîne dateNaissance_str en objet datetime.date
        dateNaissance = datetime.strptime(dateNaissance_str, '%Y-%m-%d').date()
        # Vérifier l'âge de l'utilisateur (au moins 15 ans)
        today = datetime.now().date()
        age_requis = today.year - 15
        if dateNaissance.year > age_requis:
                flash("Vous devez avoir au moins 15 ans pour vous inscrire.", 'error')
                return redirect(url_for('inscription'))
        # Validation des champs
        if not re.match(r'^[a-zA-Z]{3,}$', nom):
            flash('Le nom doit contenir uniquement des lettres et avoir plus de deux caractères.', 'error')
            return render_template('accueil.html')
        elif not re.match(r'^[a-zA-Z]{3,}$', prenom):
            flash('Le prénom doit contenir uniquement des lettres et avoir plus de deux caractères.', 'error')
            return render_template('accueil.html')
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            flash("L'adresse email n'est pas valide.", 'error')
            return render_template('accueil.html')
        elif telephone and not re.match(r'^\d{10}$', telephone):
            flash('Le numéro de téléphone doit contenir 10 chiffres.', 'error')
            return render_template('accueil.html')
        elif adresse and (len(adresse) < 5 or not adresse.strip()):
            flash("L'adresse doit contenir au moins 5 caractères.", 'error')
            return render_template('accueil.html')
        elif not type_utilisateur or type_utilisateur.strip() not in ['client', 'gestionnaire', 'moniteur', 'administrateur', 'prepose']:
            flash("Le type d'utilisateur est invalide.", 'error')
            return render_template('accueil.html')
        else:  
            # Création de l'objet utilisateur et inscription
            utilisateur = Utilisateur('', '', nom, prenom, email, telephone, adresse,type_utilisateur)
            utilisateur.dateNaissance = dateNaissance_str 
            nom_util,mdp=utilisateur.s_inscrire()
            if nom_util:
                # Envoyer un email de confirmation
                msg = Message('Votre inscription est réussie', recipients=[email])
                msg.body = f"Bonjour {prenom} {nom}, votre inscription est réussie.\n\n"
                msg.body += f"Voici vos informations de connexion :\n"
                msg.body += f"Nom d'utilisateur : {nom_util}\n"
                msg.body += f"Mot de passe : {mdp}\n\n"
                msg.body += "Merci de vous connecter avec ces informations."
                mail.send(msg)
                flash('Inscription réussie', 'success')
                return redirect(url_for('user'))  # Redirige vers la route 'user' après inscription réussie
            else:
                flash('Email existe déjà.', 'error')
                return render_template('accueil.html')
# La route de Profil
@app.route('/profile')
def profile():
    if 'user' in session:
        user_info = session['user']
        nom_utilisateur = user_info['nom_utilisateur']
        mot_de_passe = user_info.get('mot_de_passe')  # Assurez-vous que ce champ est bien présent dans la session
        nom = user_info['nom']
        prenom = user_info['prenom']
        email = user_info['email']

        client = Client(nom_utilisateur, mot_de_passe, nom, prenom, email)
        try:
            id_utilisateur = client.get_user_id()
            user = "ASAA"
            password = "Maghreb1234"
            account = "lsyveyx-vd01067"
            conn = snowflake.connector.connect(
                user=user,
                password=password,
                account=account
            )
            cursor = conn.cursor()
            query = """
                SELECT a.Nom_Activite, a.IMAGE, a.Code_Activite
                FROM Centre_Sportif.Centre.Activites a
                JOIN Centre_Sportif.Centre.Inscription_Activite ia ON a.Code_Activite = ia.Code_Activite
                WHERE ia.ID_UTILISATEUR = %s
            """
            cursor.execute(query, (id_utilisateur,))
            activites_inscrites = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Erreur lors de la récupération des activités inscrites : {str(e)}")
            activites_inscrites = []
        return render_template('profile.html', prenom=user_info['prenom'], nom=user_info['nom'], nom_utilisateur=nom_utilisateur, email=user_info['email'], telephone=user_info['telephone'], adresse=user_info['adresse'], activites_inscrites=activites_inscrites)
    else:
        return redirect(url_for('login'))
# LA ROUTE DE MODIFICATION DE PROFIL
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    nom_utilisateur = session['user']['nom_utilisateur']
    nom = request.form['nom']
    prenom = request.form['prenom']
    email = request.form['email']
    telephone = request.form['telephone']
    adresse = request.form['adresse']
    
    utilisateur = Utilisateur(nom_utilisateur, '', nom, prenom, email, telephone, adresse)
    if utilisateur.updateprofile():
        # Update session data
        session['user'].update({
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'telephone': telephone,
            'adresse': adresse
        })
        return redirect(url_for('profil'))
    else:
        return "Error updating profile."
# LA ROUTE DE SUPPRISSION DE PROFIL
@app.route('/delete_profile', methods=['POST'])
def delete_profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    nom_utilisateur = session['user']['nom_utilisateur']
    utilisateur = Utilisateur(nom_utilisateur)
    if utilisateur.delete_utilisateur():
        session.pop('user', None)
        return redirect(url_for('login'))
    else:
        return "Error deleting profile."
# LA ROUTE DE DECONNEXION    
@app.route('/deconnexion', methods=['POST'])
def deconnexion():
    session.clear() 
    return redirect(url_for('login')) 
# LA ROUTE D'AFFICHAGE DES ACTIVITES
@app.route('/activites', methods=['GET'])
def afficher_activites():
    # Récupère les activités depuis la base de données
    activites = Activites.get_activities_with_moniteur()
    # activites = Activites.get_activities_with_moniteur()
    if activites is None:
        flash("Erreur lors de la récupération des activités.", 'error')
        return redirect(url_for('user'))  # Redirige vers la page d'utilisateur en cas d'erreur
    return render_template('Activites.html', activites=activites)
# LA ROUTE D'INSCRIPTION A UNE ACTIVITE
@app.route('/inscription_activite/<activite_id>', methods=['POST'])
def inscription_activite(activite_id):
    if 'user' not in session:
        flash('Veuillez vous connecter pour vous inscrire à une activité.', 'error')
        return redirect(url_for('login'))
    
    nom_utilisateur = session['user']['nom_utilisateur']
    date_actuelle = datetime.now().strftime('%Y-%m-%d')

    client = Client(nom_utilisateur, '', '', '', '', '', '')
    if client.inscrire_a_activite(activite_id, date_actuelle):
        flash('Inscription à l\'activité réussie.', 'success')
        return redirect(url_for('horaire_activity', id_activity=activite_id))
    else:
        flash('Une erreur s\'est produite lors de l\'inscription à l\'activité.', 'error')
        return redirect(url_for('afficher_activites'))
# LA ROUTE DE L'HORAIRE D'UNE ACTIVITE
@app.route('/horaires_activites/<string:id_activity>', methods=['GET'])
def horaire_activity(id_activity):
    print(id_activity)
    if 'user' not in session:
        flash('Veuillez vous connecter pour vous inscrire à une activité.', 'error')
        return redirect(url_for('login'))
    nom_utilisateur = session['user']['nom_utilisateur']
    horaire=Activites.horaire_activites(id_activity)
    return render_template('horaires_activites.html', horaire=horaire)
# LA ROUTE POUR ANNULER L'INSCRIPTION A UNE ACTIVITER
@app.route('/annuler_inscription', methods=['POST'])
def annuler_inscription():
    if 'user' not in session:
        return redirect(url_for('login'))
    nom_utilisateur = session['user']['nom_utilisateur']
    code_activite = request.form['code_activite']
    client = Client(nom_utilisateur, "", "", "", "", "", "")
    inscription = Inscription_Activite(code_activite, client.get_user_id(),'')
    print(f"Suppression de l'inscription pour l'activité {code_activite} et l'utilisateur {client.get_user_id()}")
    if inscription.annuler_inscription():
        print("Inscription annulée avec succès.")
        return redirect(url_for('profile'))
    else:
        return "Erreur lors de l'annulation de l'inscription."

# la route vers la gestion des activites
@app.route('/gestion_activites')
def gestion_activites():
    activities = Activites.get_activities()
    return render_template('gestion_activites.html', activities=activities)

# pour afficher le formulaire de modification
@app.route('/modifier_activite/<code_activite>', methods=['GET'])
def modifier_activite(code_activite):
    #recuperer les information avec le code_activite
    activite = Activites.get_activity_bycode(code_activite)
    if activite:
        return render_template('modifier_activite.html', activite=activite)
    else:
        return "Activité non trouvee"  


# la route por la modification
@app.route('/update_activity', methods=['POST'])
def update_activity():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Récupérer les données du formulaire
    code_activite = request.form['code_activite']
    nom_activite = request.form['nom_activite']
    description = request.form['description']
    prix = request.form['prix']
    image = request.form['image']
    
    activite = Activites(code_activite, nom_activite, description, prix, image)
    if activite.Update_Activite():
        return redirect(url_for('gestion_activites'))
    else:
        return "Erreur lors de la mise à jour de l'activité."

@app.route('/ajouter_activite', methods=['GET'])
def afficher_formulaire_ajouter_activite():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('ajouter_activite.html')

@app.route('/ajouter_activite', methods=['POST'])
def ajouter_activite():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        code_activite = request.form['code_activite']
        nom_activite = request.form['nom_activite']
        description = request.form['description']
        prix = request.form['prix']
        image = request.form['image']

        activite = Activites(code_activite, nom_activite, description, prix, image)
        if activite.add_activity():
            return redirect(url_for('gestion_activites'))
        else:
            return "Erreur lors de la mise à jour de l'activité."
    except KeyError as e:
        return f"Missing form key: {str(e)}"
################### ajouter ca salma##########################
@app.route('/ajouter_disponibilite_moniteur', methods=['GET', 'POST'])
def ajouter_disponibilite_moniteur():
    if 'user' in session and session['user']['type_utilisateur'] == 'moniteur':
        if request.method == 'GET':
            activites = Activites.get_activities()
            horaires = Moniteur.get_horaires() 
            return render_template('ajouter_disponibilite_moniteur.html', activites=activites, horaires=horaires)
        elif request.method == 'POST':
            user = session['user']
            moniteur = Moniteur(user['nom_utilisateur'], user['mot_de_passe'], user['nom'], user['prenom'], user['email'])
            jour = request.form['jour']
            code_horaire = request.form['code_horaire']
            if moniteur.ajouter_disponibilite(jour, code_horaire):
                flash('Disponibilité ajoutée avec succès', 'success')
            else:
                flash('Erreur lors de l\'ajout de la disponibilité', 'error')
            return redirect(url_for('profile'))
    else:
        return redirect(url_for('login'))


# @app.route('/ajouter_disponibilite_moniteur', methods=['GET', 'POST'])
# def ajouter_disponibilite_moniteur():
#     if 'user' in session and session['user']['type_utilisateur'] == 'moniteur':
#         if request.method == 'GET':
#             activites = Moniteur.get_activities_with_moniteur()
#             return render_template('ajouter_disponibilite_moniteur.html', activites=activites)
#         elif request.method == 'POST':
#             user = session['user']
#             moniteur = Moniteur(user['nom_utilisateur'], user['mot_de_passe'], user['nom'], user['prenom'], user['email'])
#             jour = request.form['jour']
#             start_hour = request.form['start_hour']
#             end_hour = request.form['end_hour']
#             code_activite = request.form['code_activite']
#             if moniteur.ajouter_disponibilite(jour, start_hour, end_hour, code_activite):
#                 flash('Disponibilité ajoutée avec succès', 'success')
#             else:
#                 flash('Erreur lors de l\'ajout de la disponibilité', 'error')
#             return redirect(url_for('profile'))
#     else:
#         return redirect(url_for('login'))
################################ ajouter ca ##################################################
@app.route('/voir_disponibilites_moniteur')
def voir_disponibilites_moniteur():
    if 'user' in session and session['user']['type_utilisateur'] == 'moniteur':
        user = session['user']
        moniteur = Moniteur(user['nom_utilisateur'], user['mot_de_passe'], user['nom'], user['prenom'], user['email'])
        disponibilites = moniteur.get_disponibilites()
        if disponibilites is None:
            disponibilites = []
        return render_template('disponibilites_moniteur.html', disponibilites=disponibilites)
    else:
        return redirect(url_for('login'))


# @app.route('/voir_disponibilites_moniteur')
# def voir_disponibilites_moniteur():
#     if 'user' in session and session['user']['type_utilisateur'] == 'moniteur':
#         user = session['user']
#         moniteur = Moniteur(user['nom_utilisateur'], user['mot_de_passe'], user['nom'], user['prenom'], user['email'])
#         disponibilites = moniteur.get_disponibilites()
#         if disponibilites is None:
#             disponibilites = []
#         return render_template('disponibilites_moniteur.html', disponibilites=disponibilites)
#     else:
#         return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
