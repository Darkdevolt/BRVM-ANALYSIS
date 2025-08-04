import streamlit as st
import pandas as pd
import io

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(layout="wide", page_title="Analyse Financière BRVM")
st.title("📊 Application d'Analyse Financière (Version Simple)")

# --- Initialisation de l'état de la session ---
# 'df' sera notre base de données en mémoire pendant la session
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        "entreprise", "annee", "cours_action", "nombre_actions", "total_actifs",
        "capitaux_propres", "total_dettes", "actifs_courants", "dettes_courantes",
        "chiffre_affaires", "resultat_exploitation", "resultat_net"
    ])

# --- PARTIE 1 : CHARGEMENT DES DONNÉES ---
st.header("1. Chargez votre fichier de données")
st.markdown("Uploadez votre fichier `data.csv`. Si vous n'en avez pas, vous pouvez en télécharger un vide à la fin de la page.")

uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")

if uploaded_file is not None:
    # Si un fichier est uploadé, on l'utilise comme notre base de données
    st.session_state.df = pd.read_csv(uploaded_file)
    st.success("Fichier chargé avec succès !")

# Afficher les données actuellement en mémoire
st.subheader("Données actuelles en mémoire")
if not st.session_state.df.empty:
    st.dataframe(st.session_state.df)
else:
    st.info("Aucune donnée chargée. Veuillez uploader un fichier ou en ajouter via le formulaire ci-dessous.")

st.divider()

# --- PARTIE 2 : SAISIE ET MISE À JOUR ---
st.header("2. Saisir ou Mettre à Jour les Données")

# Le formulaire de saisie
with st.form("data_form", clear_on_submit=True):
    st.subheader("Formulaire de saisie")
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
    
    # Bouton de soumission du formulaire
    submitted = st.form_submit_button("Ajouter / Mettre à jour les données")

    if submitted:
        if not nom_entreprise or annee_analyse <= 2000:
            st.error("Le nom de l'entreprise et une année valide sont obligatoires !")
        else:
            new_row = {
                "entreprise": nom_entreprise,
                "annee": int(annee_analyse),
                "cours_action": cours_action,
                "nombre_actions": nombre_actions,
                "total_actifs": total_actifs,
                "capitaux_propres": capitaux_propres,
                "total_dettes": total_dettes,
                "chiffre_affaires": chiffre_affaires,
                "resultat_net": resultat_net,
                # Initialisez les autres colonnes si elles existent
                "actifs_courants": 0,
                "dettes_courantes": 0,
                "resultat_exploitation": 0,
            }
            df_new = pd.DataFrame([new_row])
            
            # Concaténer et supprimer les anciens doublons
            st.session_state.df = pd.concat([st.session_state.df, df_new], ignore_index=True)
            st.session_state.df = st.session_state.df.drop_duplicates(subset=['entreprise', 'annee'], keep='last')
            
            st.success(f"Données pour {nom_entreprise} ({annee_analyse}) ajoutées/mises à jour en mémoire. N'oubliez pas de télécharger le fichier !")

st.divider()

# --- PARTIE 3 : TÉLÉCHARGEMENT ---
st.header("3. Sauvegardez votre travail")
st.markdown("Cliquez ici pour télécharger le fichier `data.csv` contenant toutes vos modifications.")

# Convertir le DataFrame en CSV pour le téléchargement
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_df_to_csv(st.session_state.df)

st.download_button(
   label="📥 Télécharger data.csv",
   data=csv_data,
   file_name='data.csv',
   mime='text/csv',
)
