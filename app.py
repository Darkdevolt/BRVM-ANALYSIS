import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(layout="wide", page_title="Analyse Financière BRVM")

st.title("📊 Application d'Analyse Financière des Titres de la BRVM")

# --- CHARGEMENT DES DONNÉES DEPUIS LE FICHIER CSV ---
DATA_FILE = 'data.csv'

# Fonction pour charger les données ou créer un DataFrame vide si le fichier n'existe pas
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Crée un DataFrame vide avec les bonnes colonnes si le fichier n'existe pas
        return pd.DataFrame(columns=[
            "entreprise", "annee", "cours_action", "nombre_actions", "total_actifs",
            "capitaux_propres", "total_dettes", "actifs_courants", "dettes_courantes",
            "chiffre_affaires", "resultat_exploitation", "resultat_net", "cfo", "cfi", "cff"
        ])

# Charger les données existantes
df_data = load_data()

# Afficher une information sur la manière de mettre à jour les données
st.info(
    "**Comment ça marche ?** Cette application lit les données depuis le fichier `data.csv` de votre dépôt GitHub. "
    "Pour ajouter ou mettre à jour des données, modifiez le fichier `data.csv` localement, puis "
    "faites un `git push` vers votre dépôt. L'application se mettra à jour automatiquement."
)


# --- INTERFACE DE SAISIE (POUR SIMULATION ET CALCULS) ---
st.markdown("---")
st.header("Saisir les données pour une nouvelle analyse")
st.markdown("Les données saisies ici serviront à calculer les ratios ci-dessous. Pour les sauvegarder, ajoutez-les au fichier `data.csv`.")

# Utilisation de st.tabs pour organiser la saisie
tab_infos, tab_bilan, tab_resultat, tab_flux = st.tabs([
    "ℹ️ Infos Générales", 
    "⚖️ Bilan", 
    "📝 Compte de Résultat", 
    "🌊 Flux de Trésorerie"
])

with tab_infos:
    col1, col2 = st.columns(2)
    with col1:
        nom_entreprise = st.text_input("Nom de l'entreprise", placeholder="Ex: SOGB")
        annee_analyse = st.number_input("Année d'analyse", min_value=2010, max_value=2050, value=2024)
    with col2:
        cours_action = st.number_input("Cours actuel de l'action (FCFA)", min_value=0.0, format="%.2f")
        nombre_actions = st.number_input("Nombre d'actions en circulation", min_value=0)

with tab_bilan:
    col_actif, col_passif = st.columns(2)
    with col_actif:
        st.subheader("Actif")
        actifs_non_courants = st.number_input("Total Actifs Non Courants (Immobilisations)", key='anc', min_value=0.0, format="%.2f")
        actifs_courants = st.number_input("Total Actifs Courants", key='ac', min_value=0.0, format="%.2f")
        total_actifs = actifs_non_courants + actifs_courants
        st.metric(label="Total Actifs", value=f"{total_actifs:,.0f} FCFA")

    with col_passif:
        st.subheader("Passif et Capitaux Propres")
        capitaux_propres = st.number_input("Total Capitaux Propres", key='cp', min_value=0.0, format="%.2f")
        dettes_long_terme = st.number_input("Dettes à long terme", key='dlt', min_value=0.0, format="%.2f")
        dettes_courantes = st.number_input("Total Dettes Courantes", key='dc', min_value=0.0, format="%.2f")
        total_dettes = dettes_long_terme + dettes_courantes
        total_passifs_cp = total_dettes + capitaux_propres
        st.metric(label="Total Passifs + Capitaux Propres", value=f"{total_passifs_cp:,.0f} FCFA")
    
    if round(total_actifs, 2) != round(total_passifs_cp, 2) and total_actifs > 0:
        st.error("Déséquilibre du Bilan : Le Total Actifs doit être égal au Total Passifs + Capitaux Propres.")

with tab_resultat:
    col_produits, col_charges = st.columns(2)
    with col_produits:
        st.subheader("Produits")
        chiffre_affaires = st.number_input("Chiffre d'Affaires (Ventes)", key='ca', min_value=0.0, format="%.2f")
    with col_charges:
        st.subheader("Charges")
        cout_marchandises = st.number_input("Coût des marchandises vendues / Achats", key='cmv', min_value=0.0, format="%.2f")
        charges_personnel = st.number_input("Charges du personnel", key='cpn', min_value=0.0, format="%.2f")
        dotations_amortissements = st.number_input("Dotations aux amortissements", key='daa', min_value=0.0, format="%.2f")
    st.subheader("Résultats")
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        resultat_exploitation = st.number_input("Résultat d'Exploitation (EBIT)", key='ebit', format="%.2f")
    with col_res2:
        resultat_net = st.number_input("Résultat Net", key='rn', format="%.2f")

with tab_flux:
    st.header("Tableau de Flux de Trésorerie")
    flux_tresorerie_exploitation = st.number_input("Flux de trésorerie d'exploitation (CFO)", key='cfo', format="%.2f")
    flux_tresorerie_investissement = st.number_input("Flux de trésorerie d'investissement (CFI)", key='cfi', format="%.2f")
    flux_tresorerie_financement = st.number_input("Flux de trésorerie de financement (CFF)", key='cff', format="%.2f")

st.divider()

# --- SECTION D'ANALYSE : CALCUL ET AFFICHAGE DES RATIOS ---
st.header("🚀 Analyse des Ratios Financiers (Basée sur les données saisies ci-dessus)")

if chiffre_affaires > 0 and total_actifs > 0 and capitaux_propres > 0 and nombre_actions > 0 and cours_action > 0:
    # Calculs des ratios... (logique identique à la version précédente)
    marge_nette = resultat_net / chiffre_affaires
    roe = resultat_net / capitaux_propres
    roa = resultat_net / total_actifs
    ratio_courant = actifs_courants / dettes_courantes if dettes_courantes else 0
    ratio_endettement = total_dettes / total_actifs
    gearing = total_dettes / capitaux_propres
    capitalisation_boursiere = cours_action * nombre_actions
    bpa = resultat_net / nombre_actions
    per = cours_action / bpa if bpa != 0 else float('inf')
    pbr = capitalisation_boursiere / capitaux_propres
    
    # Affichage des Ratios (logique identique à la version précédente)
    st.subheader("📈 Ratios de Rentabilité")
    col1, col2, col3 = st.columns(3)
    col1.metric("Marge Nette", f"{marge_nette:.2%}")
    col2.metric("Return on Equity (ROE)", f"{roe:.2%}")
    col3.metric("Return on Assets (ROA)", f"{roa:.2%}")
    # ... autres affichages de ratios ...
else:
    st.warning("Veuillez saisir les données dans les onglets ci-dessus pour calculer les ratios.")

st.divider()

# --- AFFICHAGE DES DONNÉES HISTORIQUES SAUVEGARDÉES ---
st.header("Données Historiques (depuis `data.csv`)")
if not df_data.empty:
    st.dataframe(df_data)
else:
    st.write("Le fichier `data.csv` est vide ou n'a pas été trouvé dans le dépôt.")
