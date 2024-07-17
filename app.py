from datetime import datetime
import secrets
import snowflake.connector
from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash
from Utilisateur import Utilisateur
from flask_mail import Mail, Message
import re
from Activites import Activites
from Inscription_Activite import Inscription_Activite
from Client import Client
app = Flask(__name__)
 
# Generate a random secret key
app.secret_key = secrets.token_hex(16) 
# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # E.g., smtp.gmail.com
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
                    'adresse': user_info['adresse']
                }
                return redirect(url_for('afficher_activites'))
            else:
                return "Erreur lors de la récupération des informations utilisateur."
        else:
            return "Échec de la connexion."
    else:
        return "Erreur de connexion à la base de données."
    
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

# @app.route('/profile')
# def profile():
#     if 'user' in session:
#         user_info = session['user']
#         return render_template('profile.html', **user_info)
#     else:
#         return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user' in session:
        user_info = session['user']
        nom_utilisateur = user_info['nom_utilisateur']
        mot_de_passe = user_info.get('mot_de_passe')  # Assurez-vous que ce champ est bien présent dans la session
        nom = user_info['nom']
        prenom = user_info['prenom']
        email = user_info['email']
        
        # Instanciez l'objet Client avec les informations nécessaires
        client = Client(nom_utilisateur, mot_de_passe, nom, prenom, email)

        try:
            # Récupérez l'ID utilisateur à partir de la méthode de la classe Client
            id_utilisateur = client.get_user_id()  # Assurez-vous que cette méthode retourne l'ID utilisateur
            
            # Connect to Snowflake and retrieve activities the user is signed up for
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
               SELECT a.Nom_Activite, a.IMAGE, a.Code_Activite ,h.DATE_OF_ACTIVITY,h.START_HOUR,h.END_HOUR
                FROM Centre_Sportif.Centre.Activites a
                JOIN Centre_Sportif.Centre.Inscription_Activite ia join centre_sportif.centre.horaire h  ON a.Code_Activite = ia.Code_Activite
                and h.id_horaire=ia.id_horaire WHERE ia.ID_UTILISATEUR = %s
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
        return redirect(url_for('profile'))
    else:
        return "Error updating profile."

@app.route('/delete_profile', methods=['POST'])
def delete_profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    nom_utilisateur = session['user']['nom_utilisateur']
    utilisateur = Utilisateur(nom_utilisateur)  # No mot_de_passe needed for deletion

    if utilisateur.delete_utilisateur():
        session.pop('user', None)
        return redirect(url_for('login'))
    else:
        return "Error deleting profile."
@app.route('/deconnexion', methods=['POST'])
def deconnexion():
    session.clear() 
    return redirect(url_for('login')) 

@app.route('/activites', methods=['GET'])
def afficher_activites():
    # Récupère les activités depuis la base de données
    activites = Activites.get_activities()
    if activites is None:
        flash("Erreur lors de la récupération des activités.", 'error')
        return redirect(url_for('user'))  # Redirige vers la page d'utilisateur en cas d'erreur

    # Rend le template 'activite.html' en passant les activités récupérées
    return render_template('Activites.html', activites=activites)



@app.route('/inscription_activite/<string:activite_id>', methods=['POST'])
def inscription_activite(activite_id):
    if 'user' not in session:
        flash('Veuillez vous connecter pour vous inscrire à une activité.', 'error')
        return redirect(url_for('login'))
    
    nom_utilisateur = session['user']['nom_utilisateur']
    date_actuelle = datetime.now().strftime('%Y-%m-%d')
    horaire_id= request.form.get('horaire_id') 
    # print(f"ggggggggggggggggggggggggggggggggggggggg :{horaire_id}")
    client = Client(nom_utilisateur, '', '', '', '', '', '')

    if client.inscrire_a_activite(activite_id, date_actuelle,horaire_id):
        # Succès de l'inscription, mettre à jour le nombre de places disponibles
        if Activites.decrementer_nombre_places(activite_id):
            flash('Inscription à l\'activité réussie.', 'success')
        else:
            flash('Une erreur s\'est produite lors de la mise à jour du nombre de places disponibles.', 'error')
    else:
        flash('Une erreur s\'est produite lors de l\'inscription à l\'activité.', 'error')

    return redirect(url_for('afficher_activites'))
# LA ROUTE POUR ANNULER L'INSCRIPTION A UNE ACTIVITER
@app.route('/annuler_inscription', methods=['POST'])
def annuler_inscription():
    if 'user' not in session:
        return redirect(url_for('login'))
    nom_utilisateur = session['user']['nom_utilisateur']
    code_activite = request.form['code_activite']
    id_horaire = request.form['id_horaire']
    client = Client(nom_utilisateur, "", "", "", "", "", "")
    inscription = Inscription_Activite(code_activite, client.get_user_id(), id_horaire, '')  # Provide the appropriate date if needed
    print(f"Suppression de l'inscription pour l'activité {code_activite}, l'utilisateur {client.get_user_id()}, et l'horaire {id_horaire}")
    if inscription.annuler_inscription():
        print("Inscription annulée avec succès.")
        return redirect(url_for('profile'))
    else:
        return "Erreur lors de l'annulation de l'inscription."


@app.route('/activite/<string:code_activite>', methods=['GET'])
def afficher_detail_activite(code_activite):
    # Récupère l'activité spécifique depuis la base de données
    activite = Activites.get_activity_by_code(code_activite)

    if activite:
        print(f"Image URL: {activite.Image}")  # Vérifiez l'URL de l'image récupérée
        horaire=Activites.horaire_activites(code_activite)
        # Rend le template 'activite_detail.html' en passant l'activité récupérée
        return render_template('activite_detail.html', activite=activite, horaire=horaire)
    else:
        flash("Erreur lors de la récupération de l'activité.", 'error')
        return redirect(url_for('afficher_activites'))  # Redirige vers la liste des activités en cas d'erreur



if __name__ == '__main__':
    app.run(debug=True)
