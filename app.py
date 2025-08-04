import streamlit as st
import pandas as pd
from github import Github, UnknownObjectException
import io

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(layout="wide", page_title="Analyse Financière BRVM")
st.title("📊 Application d'Analyse Financière BRVM")

# --- CONNEXION SÉCURISÉE À GITHUB ---
# Cette partie utilise le fichier secrets.toml que vous avez configuré
try:
    GITHUB_TOKEN = st.secrets["github"]["token"]
    REPO_NAME = st.secrets["github"]["repo"]
    CSV_PATH = st.secrets["github"]["path"]
    
    # Authentification auprès de GitHub
    g = Github(GITHUB_TOKEN)
    # Récupération du dépôt
    repo = g.get_repo(REPO_NAME)
    github_ok = True
except Exception as e:
    st.error(f"Erreur de connexion à GitHub. Avez-vous bien configuré le fichier .streamlit/secrets.toml ?")
    st.error(f"Détail de l'erreur : {e}")
    github_ok = False

# --- FONCTIONS POUR LIRE ET ÉCRIRE LES DONNÉES ---

def load_data_from_github():
    """Charge le contenu du fichier CSV depuis GitHub via l'API."""
    if not github_ok: return pd.DataFrame()
    try:
        file_content = repo.get_contents(CSV_PATH)
        csv_data = file_content.decoded_content.decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_data))
        return df
    except UnknownObjectException:
        st.warning(f"Le fichier '{CSV_PATH}' est introuvable sur le dépôt. Un nouveau sera créé.")
        return pd.DataFrame(columns=[
            "entreprise", "annee", "cours_action", "nombre_actions", "total_actifs", "capitaux_propres",
            "total_dettes", "actifs_courants", "dettes_courantes", "chiffre_affaires",
            "resultat_exploitation", "resultat_net"
        ])
    except Exception as e:
        st.error(f"Erreur de chargement des données : {e}")
        return pd.DataFrame()

def update_data_on_github(df_to_save):
    """Convertit le DataFrame en CSV et le pousse vers GitHub."""
    if not github_ok: return False
    try:
        csv_string = df_to_save.to_csv(index=False)
        commit_message = f"Mise à jour des données via l'application Streamlit"
        
        # On vérifie si le fichier existe pour savoir s'il faut le créer ou le mettre à jour
        try:
            file = repo.get_contents(CSV_PATH)
            repo.update_file(file.path, commit_message, csv_string, file.sha)
        except UnknownObjectException:
            repo.create_file(CSV_PATH, commit_message, csv_string)
        return True
    except Exception as e:
        st.error(f"Impossible de mettre à jour le fichier sur GitHub : {e}")
        return False

# --- INTERFACE DE L'APPLICATION ---

# Charger les données une seule fois au début
df_data = load_data_from_github()

st.header("Aperçu des Données Actuelles")
st.markdown("Voici les données actuellement présentes dans votre fichier `data.csv` sur GitHub.")
st.dataframe(df_data)

st.divider()

st.header("Ajouter ou Mettre à Jour des Données")
with st.form("data_form"):
    st.markdown("Remplissez les champs et cliquez sur 'Mettre à Jour' pour sauvegarder sur GitHub.")
    
    # Formulaire de saisie
    col1, col2 = st.columns(2)
    with col1:
        nom_entreprise = st.text_input("Nom de l'entreprise")
        annee_analyse = st.number_input("Année d'analyse", min_value=2010, step=1)
        cours_action = st.number_input("Cours de l'action", min_value=0.0)
        nombre_actions = st.number_input("Nombre d'actions", min_value=0)
    with col2:
        total_actifs = st.number_input("Total Actifs", min_value=0.0)
        capitaux_propres = st.number_input("Total Capitaux Propres", min_value=0.0)
        total_dettes = st.number_input("Total Dettes", min_value=0.0)
        chiffre_affaires = st.number_input("Chiffre d'Affaires", min_value=0.0)
        resultat_net = st.number_input("Résultat Net")
    
    submitted = st.form_submit_button("🚀 Mettre à Jour sur GitHub")

    if submitted:
        if not nom_entreprise or annee_analyse <= 2000:
            st.error("Le nom de l'entreprise et une année valide sont obligatoires !")
        else:
            new_row = {
                "entreprise": nom_entreprise, "annee": int(annee_analyse), "cours_action": cours_action,
                "nombre_actions": nombre_actions, "total_actifs": total_actifs, "capitaux_propres": capitaux_propres,
                "total_dettes": total_dettes, "chiffre_affaires": chiffre_affaires, "resultat_net": resultat_net,
                "actifs_courants": 0, "dettes_courantes": 0, "resultat_exploitation": 0,
            }
            
            with st.spinner("Connexion à GitHub et sauvegarde des données..."):
                df_new = pd.DataFrame([new_row])
                df_updated = pd.concat([df_data, df_new], ignore_index=True)
                df_updated = df_updated.drop_duplicates(subset=['entreprise', 'annee'], keep='last').sort_values(by=['entreprise', 'annee'])
                
                success = update_data_on_github(df_updated)
                if success:
                    st.success("Fichier mis à jour avec succès sur GitHub !")
                    st.balloons()
