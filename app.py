import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(layout="wide", page_title="Analyse Financière BRVM")

st.title("📊 Application d'Analyse Financière des Titres de la BRVM")
st.markdown("Saisissez les données financières dans les onglets ci-dessous pour calculer les ratios clés.")

# --- DÉFINITION DES CHAMPS DE SAISIE DANS DES ONGLETS ---

# Utilisation de st.tabs pour organiser la saisie sur la page principale
tab_infos, tab_bilan, tab_resultat, tab_flux = st.tabs([
    "ℹ️ Infos Générales", 
    "⚖️ Bilan", 
    "📝 Compte de Résultat", 
    "🌊 Flux de Trésorerie"
])

with tab_infos:
    st.header("Informations Générales et Données de Marché")
    col1, col2 = st.columns(2)
    with col1:
        nom_entreprise = st.text_input("Nom de l'entreprise", placeholder="Ex: SOGB")
        annee_analyse = st.number_input("Année d'analyse", min_value=2010, max_value=2050, value=2024)
    with col2:
        cours_action = st.number_input("Cours actuel de l'action (FCFA)", min_value=0.0, format="%.2f")
        nombre_actions = st.number_input("Nombre d'actions en circulation", min_value=0, help="Nombre total d'actions qui composent le capital social.")

with tab_bilan:
    st.header("Bilan Financier")
    col_actif, col_passif = st.columns(2)

    with col_actif:
        st.subheader("Actif")
        actifs_non_courants = st.number_input("Total Actifs Non Courants (Immobilisations)", min_value=0.0, format="%.2f")
        actifs_courants = st.number_input("Total Actifs Courants (Stocks, Créances, etc.)", min_value=0.0, format="%.2f")
        total_actifs = actifs_non_courants + actifs_courants
        st.metric(label="Total Actifs", value=f"{total_actifs:,.0f} FCFA")

    with col_passif:
        st.subheader("Passif et Capitaux Propres")
        capitaux_propres = st.number_input("Total Capitaux Propres", min_value=0.0, format="%.2f")
        dettes_long_terme = st.number_input("Dettes à long terme", min_value=0.0, format="%.2f")
        dettes_courantes = st.number_input("Total Dettes Courantes (Fournisseurs, etc.)", min_value=0.0, format="%.2f")
        total_dettes = dettes_long_terme + dettes_courantes
        total_passifs_cp = total_dettes + capitaux_propres
        st.metric(label="Total Passifs + Capitaux Propres", value=f"{total_passifs_cp:,.0f} FCFA")
    
    # Vérification de l'équilibre du bilan
    if round(total_actifs, 2) != round(total_passifs_cp, 2) and total_actifs > 0:
        st.error("Déséquilibre du Bilan : Le Total Actifs doit être égal au Total Passifs + Capitaux Propres.")

with tab_resultat:
    st.header("Compte de Résultat")
    col_produits, col_charges = st.columns(2)
    
    with col_produits:
        st.subheader("Produits")
        chiffre_affaires = st.number_input("Chiffre d'Affaires (Ventes)", min_value=0.0, format="%.2f")
        # Ajoutez d'autres lignes de produits si nécessaire
        # ...

    with col_charges:
        st.subheader("Charges")
        cout_marchandises = st.number_input("Coût des marchandises vendues / Achats", min_value=0.0, format="%.2f")
        charges_personnel = st.number_input("Charges du personnel", min_value=0.0, format="%.2f")
        dotations_amortissements = st.number_input("Dotations aux amortissements et provisions", min_value=0.0, format="%.2f")
        # Ajoutez d'autres lignes de charges si nécessaire
        # ...

    st.subheader("Résultats")
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        resultat_exploitation = st.number_input("Résultat d'Exploitation (EBIT)", format="%.2f")
    with col_res2:
        resultat_net = st.number_input("Résultat Net", format="%.2f")

with tab_flux:
    st.header("Tableau de Flux de Trésorerie")
    flux_tresorerie_exploitation = st.number_input("Flux de trésorerie liés à l'exploitation (CFO)", format="%.2f")
    flux_tresorerie_investissement = st.number_input("Flux de trésorerie liés à l'investissement (CFI)", format="%.2f")
    flux_tresorerie_financement = st.number_input("Flux de trésorerie liés au financement (CFF)", format="%.2f")

st.divider()

# --- CONNEXION À GOOGLE SHEETS ET LOGIQUE DE SAUVEGARDE ---

# Établir la connexion (nécessite une configuration des secrets Streamlit)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    gsheet_ok = True
except Exception:
    st.warning("La connexion à Google Sheets a échoué. La sauvegarde/chargement est désactivée. Veuillez configurer vos `secrets.toml`.")
    gsheet_ok = False

if gsheet_ok:
    if st.button("💾 Sauvegarder les données saisies"):
        if not nom_entreprise or annee_analyse <= 0:
            st.error("Veuillez saisir au moins un nom d'entreprise et une année valide avant de sauvegarder.")
        else:
            # Créer un DataFrame avec les nouvelles données
            new_data = pd.DataFrame([{
                "entreprise": nom_entreprise,
                "annee": annee_analyse,
                "cours_action": cours_action,
                "nombre_actions": nombre_actions,
                "total_actifs": total_actifs,
                "capitaux_propres": capitaux_propres,
                "total_dettes": total_dettes,
                "actifs_courants": actifs_courants,
                "dettes_courantes": dettes_courantes,
                "chiffre_affaires": chiffre_affaires,
                "resultat_exploitation": resultat_exploitation,
                "resultat_net": resultat_net,
                "cfo": flux_tresorerie_exploitation,
                "cfi": flux_tresorerie_investissement,
                "cff": flux_tresorerie_financement,
            }])
            
            # Mettre à jour la feuille Google Sheets
            # Note: il est mieux d'ajouter une nouvelle ligne que de tout écraser.
            # La méthode .update ajoute les données à la fin de la feuille.
            conn.update(worksheet="VotreNomDeFeuille", data=new_data)
            st.success(f"Les données de {nom_entreprise} pour {annee_analyse} ont été sauvegardées avec succès !")


st.divider()

# --- SECTION D'ANALYSE : CALCUL ET AFFICHAGE DES RATIOS ---

st.header("🚀 Analyse des Ratios Financiers")

# Vérifier si les données essentielles sont présentes pour éviter les erreurs
if chiffre_affaires > 0 and total_actifs > 0 and capitaux_propres > 0 and nombre_actions > 0 and cours_action > 0:
    
    # Ratios de Rentabilité
    marge_nette = resultat_net / chiffre_affaires
    roe = resultat_net / capitaux_propres  # Return on Equity
    roa = resultat_net / total_actifs  # Return on Assets

    # Ratios de Liquidité
    ratio_courant = actifs_courants / dettes_courantes if dettes_courantes else 0
    
    # Ratios de Solvabilité / Levier
    ratio_endettement = total_dettes / total_actifs
    gearing = total_dettes / capitaux_propres # Debt to Equity
    
    # Ratios de Marché (Valorisation)
    capitalisation_boursiere = cours_action * nombre_actions
    bpa = resultat_net / nombre_actions # Bénéfice Par Action (EPS)
    per = cours_action / bpa if bpa > 0 else float('inf') # Price-to-Earnings Ratio (P/E)
    pbr = capitalisation_boursiere / capitaux_propres # Price-to-Book Ratio (P/B)
    
    # --- Affichage des Ratios ---
    st.subheader("📈 Ratios de Rentabilité")
    col1, col2, col3 = st.columns(3)
    col1.metric("Marge Nette", f"{marge_nette:.2%}", help="Résultat Net / Chiffre d'Affaires")
    col2.metric("Return on Equity (ROE)", f"{roe:.2%}", help="Résultat Net / Capitaux Propres. Mesure la rentabilité des fonds propres.")
    col3.metric("Return on Assets (ROA)", f"{roa:.2%}", help="Résultat Net / Total Actifs. Mesure l'efficacité à générer du profit avec les actifs.")

    st.subheader("💧 Ratios de Liquidité")
    col1, col2 = st.columns(2)
    col1.metric("Ratio de liquidité générale", f"{ratio_courant:.2f}", help="Actifs Courants / Dettes Courantes. Capacité à payer les dettes à court terme.")

    st.subheader("🏗️ Ratios de Solvabilité")
    col1, col2 = st.columns(2)
    col1.metric("Ratio d'endettement", f"{ratio_endettement:.2%}", help="Total Dettes / Total Actifs. Part des actifs financée par la dette.")
    col2.metric("Levier Financier (D/E)", f"{gearing:.2f}", help="Total Dettes / Capitaux Propres. Niveau d'endettement par rapport aux fonds propres.")
    
    st.subheader("💰 Ratios de Valorisation")
    col1, col2, col3 = st.columns(3)
    col1.metric("Capitalisation Boursière", f"{capitalisation_boursiere:,.0f} FCFA")
    col2.metric("PER (Price-to-Earnings)", f"{per:.2f}" if per != float('inf') else "N/A", help="Cours de l'action / Bénéfice par action. Indique combien d'années de bénéfices l'investisseur paie.")
    col3.metric("PBR (Price-to-Book)", f"{pbr:.2f}", help="Capitalisation Boursière / Capitaux Propres. Compare la valeur de marché à la valeur comptable.")

else:
    st.info("Veuillez remplir les données financières essentielles (CA, Actifs, CP, Infos marché) pour calculer les ratios.")
