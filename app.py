from datetime import datetime
import secrets
import snowflake.connector
from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash
from Utilisateur import Utilisateur
from flask_mail import Mail, Message
import re
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
                return redirect(url_for('user'))
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


            if utilisateur.s_inscrire():
                # Envoyer un email de confirmation
                msg = Message('Votre inscription est réussie', recipients=[email])
                msg.body = f"Bonjour {prenom} {nom}, votre inscription est réussie."
                mail.send(msg)
                flash('Inscription réussie', 'success')
                return redirect(url_for('user'))  # Redirige vers la route 'user' après inscription réussie
            else:
                flash('Email existe déjà.', 'error')
                return render_template('accueil.html')

@app.route('/profile')
def profile():
    if 'user' in session:
        user_info = session['user']
        return render_template('profile.html', **user_info)
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
        return redirect(url_for('user'))
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
if __name__ == '__main__':
    app.run(debug=True)
