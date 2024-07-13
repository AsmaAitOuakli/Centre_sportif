const showPopup = document.querySelector('.btn');
const popupContainer = document.querySelector('.popup-container');
const popupContainerInscription = document.querySelector('.popup-container-inscription');
showPopup.onclick = () => {
    popupContainer.classList.add('active');
}
showPopupInscription.onclick = () => {
    popupContainerInscription.classList.add('active');
}

function togglePopup() {
    var popup = document.querySelector('.popup-container');
    var titre = document.getElementById('titre');
    if (popup.style.display === 'none' || popup.style.display === '') {
        popup.style.display = 'block';
        titre.style.display = 'none'; 
    } else {
        popup.style.display = 'none';
        titre.style.display = 'block'; 
    }
}
function togglePopupInscription() {
    var popup = document.querySelector('.popup-container-inscription');
    var titre = document.getElementById('titre');
    if (popup.style.display === 'none' || popup.style.display === '') {
        popup.style.display = 'block';
        titre.style.display = 'none'; 
    } else {
        popup.style.display = 'none';
        titre.style.display = 'block'; 
    }
}

document.getElementById("monFormulaire").addEventListener("submit", function(event) {
    event.preventDefault(); 

    const nom = document.getElementById("nom").value;
    const prenom = document.getElementById("prenom").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const telephone = document.getElementById("telephone").value;
    const adresse = document.getElementById("adresse").value;
    const type_utilisateur = document.getElementById("type_utilisateur").value;

    let isValid = true;
    let errorMessage = "";

    // Validation du nom et prénom
    if (!/^[a-zA-Z]{3,}$/.test(nom)) {
        isValid = false;
        errorMessage += "Le nom doit contenir uniquement des lettres et avoir plus de deux caractères.\n";
    }
    if (!/^[a-zA-Z]{3,}$/.test(prenom)) {
        isValid = false;
        errorMessage += "Le prénom doit contenir uniquement des lettres et avoir plus de deux caractères.\n";
    }

    // Validation de l'email
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        isValid = false;
        errorMessage += "L'adresse email n'est pas valide.\n";
    }

    // Validation du mot de passe
    if (password.length < 8) {
        isValid = false;
        errorMessage += "Le mot de passe doit avoir au moins 8 caractères.\n";
    }

    // Validation du téléphone (exemple de validation)
    if (!/^\d{10}$/.test(telephone)) {
        isValid = false;
        errorMessage += "Le numéro de téléphone doit contenir 10 chiffres.\n";
    }

    // Validation de l'adresse (exemple simple)
    if (adresse.trim() === "") {
        isValid = false;
        errorMessage += "L'adresse ne peut pas être vide.\n";
    }

    // Validation du type d'utilisateur (exemple simple)
    if (type_utilisateur.trim() === "") {
        isValid = false;
        errorMessage += "Le type d'utilisateur ne peut pas être vide.\n";
    }

    if (!isValid) {
        alert(errorMessage);
        return; // Arrête l'exécution si la validation échoue
    }

    const data = {
        nom: nom,
        prenom: prenom,
        email: email,
        password: password,
        telephone: telephone,
        adresse: adresse,
        dateNaissance: dateNaissance,
        type_utilisateur: type_utilisateur
    };

    fetch('/inscription', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
        } else {
            alert('Erreur lors de l\'inscription. ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'inscription. Veuillez réessayer.');
    });
});