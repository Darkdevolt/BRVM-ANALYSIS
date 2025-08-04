import streamlit as st
import pandas as pd
from github import Github, UnknownObjectException
import io

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(layout="wide", page_title="Analyse Financière BRVM")

# --- CONNEXION À GITHUB ---
# Utilise les secrets de Streamlit pour une connexion sécurisée
try:
    GITHUB_TOKEN = st.secrets["github"]["token"]
    GITHUB_REPO = st.secrets["github"]["repo"]
    CSV_PATH = st.secrets["github"]["path"]
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)
    github_ok = True
except Exception as e:
    st.error(f"Erreur de connexion à GitHub. Vérifiez vos secrets.toml: {e}")
    github_ok = False

# --- FONCTIONS UTILITAIRES ---

def load_data_from_github():
    """Charge le contenu du fichier CSV depuis GitHub."""
    if not github_ok: return pd.DataFrame()
    try:
        # Récupère le contenu du fichier
        file_content = repo.get_contents(CSV_PATH)
        # Décode le contenu (qui est en base64)
        csv_data = file_content.decoded_content.decode('utf-8')
        # Lit les données avec pandas
        df = pd.read_csv(io.StringIO(csv_data))
        return df
    except UnknownObjectException:
        # Si le fichier n'existe pas, retourne un DataFrame vide avec les bonnes colonnes
        st.warning(f"Le fichier '{CSV_PATH}' est introuvable sur le dépôt. Un nouveau fichier sera créé lors de la première mise à jour.")
        return pd.DataFrame(columns=[
            "entreprise", "annee", "cours_action", "nombre_actions", "total_actifs", "capitaux_propres",
            "total_dettes", "actifs_courants", "dettes_courantes", "chiffre_affaires",
            "resultat_exploitation", "resultat_net", "cfo", "cfi", "cff"
        ])
    except Exception as e:
        st.error(f"Erreur lors du chargement des données depuis GitHub: {e}")
        return pd.DataFrame()

def render_input_form(data=None):
    """Affiche le formulaire de saisie, pré-rempli si des données sont fournies."""
    data = data if data is not None else {}
    
    st.subheader("Saisir ou modifier les informations financières")
    tab_infos, tab_bilan, tab_resultat, tab_flux = st.tabs([
        "ℹ️ Infos Générales", "⚖️ Bilan", "📝 Compte de Résultat", "🌊 Flux de Trésorerie"
    ])

    with tab_infos:
        col1, col2 = st.columns(2)
        with col1:
            nom_entreprise = st.text_input("Nom de l'entreprise", value=data.get("entreprise", ""), key="nom_entreprise")
            annee_analyse = st.number_input("Année d'analyse", min_value=2010, max_value=2050, value=data.get("annee", 2024), key="annee")
        with col2:
            cours_action = st.number_input("Cours de l'action (FCFA)", min_value=0.0, value=data.get("cours_action", 0.0), format="%.2f", key="cours_action")
            nombre_actions = st.number_input("Nombre d'actions", min_value=0, value=data.get("nombre_actions", 0), key="nombre_actions")

    with tab_bilan:
        col_actif, col_passif = st.columns(2)
        with col_actif:
            actifs_courants = st.number_input("Total Actifs Courants", min_value=0.0, value=data.get("actifs_courants", 0.0), format="%.2f", key="ac")
        with col_passif:
            dettes_courantes = st.number_input("Total Dettes Courantes", min_value=0.0, value=data.get("dettes_courantes", 0.0), format="%.2f", key="dc")
            total_dettes = st.number_input("Total Dettes (court et long terme)", min_value=0.0, value=data.get("total_dettes", 0.0), format="%.2f", key="total_dettes")
            capitaux_propres = st.number_input("Total Capitaux Propres", min_value=0.0, value=data.get("capitaux_propres", 0.0), format="%.2f", key="cp")
        total_actifs = st.number_input("Total Actifs", min_value=0.0, value=data.get("total_actifs", 0.0), format="%.2f", key="total_actifs")

    with tab_resultat:
        chiffre_affaires = st.number_input("Chiffre d'Affaires (Ventes)", min_value=0.0, value=data.get("chiffre_affaires", 0.0), format="%.2f", key="ca")
        resultat_exploitation = st.number_input("Résultat d'Exploitation (EBIT)", value=data.get("resultat_exploitation", 0.0), format="%.2f", key="ebit")
        resultat_net = st.number_input("Résultat Net", value=data.get("resultat_net", 0.0), format="%.2f", key="rn")

    with tab_flux:
        cfo = st.number_input("Flux de trésorerie d'exploitation (CFO)", value=data.get("cfo", 0.0), format="%.2f", key="cfo")
        cfi = st.number_input("Flux de trésorerie d'investissement (CFI)", value=data.get("cfi", 0.0), format="%.2f", key="cfi")
        cff = st.number_input("Flux de trésorerie de financement (CFF)", value=data.get("cff", 0.0), format="%.2f", key="cff")

# --- INTERFACE PRINCIPALE ---

st.sidebar.title("Navigation")
page = st.sidebar.radio("Choisissez votre section", ["Analyse des Données", "Mettre à Jour les Données"])

df_data = load_data_from_github()

if page == "Analyse des Données":
    st.title("📊 Analyse des Données Financières")
    st.markdown("Visualisez les données stockées et analysez les ratios d'une entreprise.")
    
    if not df_data.empty:
        st.subheader("Données stockées sur GitHub")
        st.dataframe(df_data)
        
        st.subheader("Analyse par entreprise")
        entreprises_disponibles = df_data['entreprise'].unique()
        entreprise_selectionnee = st.selectbox("Choisissez une entreprise à analyser", entreprises_disponibles)
        
        data_entreprise = df_data[df_data['entreprise'] == entreprise_selectionnee].iloc[-1]
        
        # Ici, vous pouvez afficher les ratios calculés pour l'entreprise sélectionnée
        st.write(f"Ratios pour {entreprise_selectionnee} ({int(data_entreprise['annee'])})")
        # (Ajoutez ici la logique d'affichage des ratios comme dans les versions précédentes)

    else:
        st.info("Aucune donnée à analyser. Allez dans la section 'Mettre à Jour' pour en ajouter.")

elif page == "Mettre à Jour les Données":
    st.title("✍️ Mettre à Jour le Fichier de Données")
    st.markdown("Utilisez ce formulaire pour ajouter de nouvelles données au fichier `data.csv` sur GitHub.")
    
    render_input_form() # Affiche le formulaire de saisie
    
    if st.button("Mettre à jour le fichier CSV sur GitHub"):
        # Récupération des données du formulaire via st.session_state (grâce aux 'key')
        new_row = {
            "entreprise": st.session_state.nom_entreprise,
            "annee": st.session_state.annee,
            "cours_action": st.session_state.cours_action,
            "nombre_actions": st.session_state.nombre_actions,
            "total_actifs": st.session_state.total_actifs,
            "capitaux_propres": st.session_state.cp,
            "total_dettes": st.session_state.total_dettes,
            "actifs_courants": st.session_state.ac,
            "dettes_courantes": st.session_state.dc,
            "chiffre_affaires": st.session_state.ca,
            "resultat_exploitation": st.session_state.ebit,
            "resultat_net": st.session_state.rn,
            "cfo": st.session_state.cfo,
            "cfi": st.session_state.cfi,
            "cff": st.session_state.cff,
        }
        
        if not new_row["entreprise"] or new_row["annee"] <= 2000:
            st.error("Le nom de l'entreprise et l'année sont obligatoires.")
        else:
            with st.spinner("Mise à jour du fichier sur GitHub..."):
                df_new = pd.DataFrame([new_row])
                df_updated = pd.concat([df_data, df_new], ignore_index=True).drop_duplicates(subset=['entreprise', 'annee'], keep='last')
                
                csv_string = df_updated.to_csv(index=False)
                commit_message = f"Data update for {new_row['entreprise']} {new_row['annee']} via Streamlit app"
                
                try:
                    # Vérifie si le fichier existe pour savoir s'il faut le créer ou le mettre à jour
                    try:
                        file = repo.get_contents(CSV_PATH)
                        repo.update_file(file.path, commit_message, csv_string, file.sha)
                        st.success("Fichier mis à jour avec succès sur GitHub !")
                    except UnknownObjectException:
                        repo.create_file(CSV_PATH, commit_message, csv_string)
                        st.success("Fichier créé et mis à jour avec succès sur GitHub !")
                        
                    st.balloons()
                except Exception as e:
                    st.error(f"Une erreur est survenue lors de la mise à jour : {e}")
