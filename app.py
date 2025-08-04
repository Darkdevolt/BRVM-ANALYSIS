# app.py
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Analyse Financière BRVM")

st.title("📊 Application d'Analyse Financière des Titres de la BRVM")

# --- BARRE LATERALE POUR LA SAISIE DES DONNÉES ---
st.sidebar.header("Saisie des Données Financières")

# Informations générales
nom_entreprise = st.sidebar.text_input("Nom de l'entreprise")
annee_analyse = st.sidebar.number_input("Année d'analyse", min_value=2010, max_value=2050, value=2024)
cours_action = st.sidebar.number_input("Cours actuel de l'action (FCFA)", min_value=0.0, format="%.2f")
nombre_actions = st.sidebar.number_input("Nombre d'actions en circulation", min_value=0)


# --- Saisie du Compte de Résultat ---
with st.sidebar.expander("📝 Compte de Résultat"):
    chiffre_affaires = st.number_input("Chiffre d'Affaires (CA)", min_value=0.0, format="%.2f")
    cout_marchandises = st.number_input("Coût des marchandises vendues", min_value=0.0, format="%.2f")
    dotations_amortissements = st.number_input("Dotations aux amortissements et provisions", min_value=0.0, format="%.2f")
    resultat_exploitation = st.number_input("Résultat d'Exploitation (EBIT)", min_value=0.0, format="%.2f")
    resultat_financier = st.number_input("Résultat financier", format="%.2f") # Peut être négatif
    impots_benefices = st.number_input("Impôts sur les bénéfices", min_value=0.0, format="%.2f")
    resultat_net = st.number_input("Résultat Net", format="%.2f") # Peut être négatif

# --- Saisie du Bilan ---
with st.sidebar.expander("⚖️ Bilan"):
    # Actifs
    actifs_courants = st.number_input("Total Actifs Courants", min_value=0.0, format="%.2f")
    actifs_non_courants = st.number_input("Total Actifs Non Courants", min_value=0.0, format="%.2f")
    total_actifs = actifs_courants + actifs_non_courants
    st.sidebar.markdown(f"**Total Actifs : {total_actifs:,.2f} FCFA**")
    
    # Passifs
    dettes_courantes = st.number_input("Total Dettes Courantes", min_value=0.0, format="%.2f")
    dettes_long_terme = st.number_input("Dettes à long terme", min_value=0.0, format="%.2f")
    total_dettes = dettes_courantes + dettes_long_terme
    capitaux_propres = st.number_input("Total Capitaux Propres", min_value=0.0, format="%.2f")
    total_passifs_cp = total_dettes + capitaux_propres
    st.sidebar.markdown(f"**Total Passifs + CP : {total_passifs_cp:,.2f} FCFA**")
    
    # Vérification de l'équilibre du bilan
    if round(total_actifs, 2) != round(total_passifs_cp, 2):
        st.sidebar.error("Attention : Le total des actifs doit être égal au total des passifs + capitaux propres.")

# --- Saisie du Tableau de Flux de Trésorerie ---
with st.sidebar.expander("🌊 Tableau de Flux de Trésorerie"):
    flux_tresorerie_exploitation = st.number_input("Flux de trésorerie liés à l'exploitation (CFO)", format="%.2f")
    flux_tresorerie_investissement = st.number_input("Flux de trésorerie liés à l'investissement (CFI)", format="%.2f")
    flux_tresorerie_financement = st.number_input("Flux de trésorerie liés au financement (CFF)", format="%.2f")

st.sidebar.info("Veuillez remplir les champs avec les données des rapports financiers de l'entreprise.")
