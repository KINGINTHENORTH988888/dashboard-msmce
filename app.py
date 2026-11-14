import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Dashboard Stratégique MSMCE", page_icon="📊", layout="wide")

st.title("📊 Dashboard Stratégique : Rétention Client & ROI Marketing")
st.markdown("*Outil d'aide à la décision — Pilotage de la fidélisation et de la rentabilité commerciale*")
st.divider()

# Barre latérale : Paramètres de simulation
st.sidebar.header("🎛️ Paramètres Stratégiques")

clients_actifs = st.sidebar.number_input("Base clients actifs", min_value=100, max_value=100000, value=5000, step=100)
panier_moyen = st.sidebar.slider("Revenu mensuel moyen / client (MAD)", 50, 2000, 350, step=10)
marge_brute = st.sidebar.slider("Taux de marge brute (%)", 10, 90, 60) / 100
taux_churn = st.sidebar.slider("Taux d'attrition mensuel / Churn (%)", 1.0, 25.0, 5.0, step=0.5) / 100
cac = st.sidebar.number_input("Coût d'Acquisition Client - CAC (MAD)", min_value=50, max_value=5000, value=600, step=50)

st.sidebar.divider()
st.sidebar.subheader("🚀 Plan d'Action Fidélisation")
reduction_churn = st.sidebar.slider("Réduction visée du Churn (%)", 0, 50, 20) / 100
budget_fidelisation = st.sidebar.number_input("Budget campagne fidélisation / an (MAD)", min_value=0, max_value=1000000, value=80000, step=5000)

# Calculs des KPIs Actuels vs Projetés
duree_vie_actuelle = 1 / taux_churn
ltv_actuelle = panier_moyen * marge_brute * duree_vie_actuelle
ratio_ltv_cac_actuel = ltv_actuelle / cac
ca_annuel_actuel = clients_actifs * panier_moyen * 12

nouveau_churn = taux_churn * (1 - reduction_churn)
duree_vie_projetee = 1 / nouveau_churn
ltv_projetee = panier_moyen * marge_brute * duree_vie_projetee
ratio_ltv_cac_projete = ltv_projetee / cac

# Gain net généré par la rétention
clients_sauves_mois = clients_actifs * (taux_churn - nouveau_churn)
gain_marge_annuel = clients_sauves_mois * panier_moyen * marge_brute * 12
roi_fidelisation = ((gain_marge_annuel - budget_fidelisation) / budget_fidelisation * 100) if budget_fidelisation > 0 else 0

# Affichage des KPIs en haut (4 colonnes)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Durée de vie client", f"{duree_vie_projetee:.1f} mois", f"+{duree_vie_projetee - duree_vie_actuelle:.1f} mois")
col2.metric("LTV (Valeur Vie Client)", f"{ltv_projetee:,.0f} MAD", f"+{ltv_projetee - ltv_actuelle:,.0f} MAD")
col3.metric("Ratio LTV / CAC", f"{ratio_ltv_cac_projete:.2f}x", f"+{ratio_ltv_cac_projete - ratio_ltv_cac_actuel:.2f}x")
col4.metric("ROI Plan Fidélisation", f"{roi_fidelisation:,.1f} %", f"{gain_marge_annuel - budget_fidelisation:,.0f} MAD net")

st.divider()

# Graphiques interactifs (2 colonnes)
g1, g2 = st.columns(2)

with g1:
    st.subheader("📈 Évolution de la rétention sur 12 mois")
    mois = list(range(1, 13))
    cohorte_actuelle = [clients_actifs * ((1 - taux_churn) ** m) for m in mois]
    cohorte_projetee = [clients_actifs * ((1 - nouveau_churn) ** m) for m in mois]
    
    df_retention = pd.DataFrame({
        "Mois": mois * 2,
        "Clients restants": cohorte_actuelle + cohorte_projetee,
        "Scénario": ["Actuel (Sans action)"] * 12 + ["Projeté (Plan Fidélisation)"] * 12
    })
    
    fig_line = px.line(df_retention, x="Mois", y="Clients restants", color="Scénario", markers=True,
                       color_discrete_map={"Actuel (Sans action)": "#EF553B", "Projeté (Plan Fidélisation)": "#00CC96"})
    st.plotly_chart(fig_line, use_container_width=True)

with g2:
    st.subheader("💰 Comparaison Valeur Vie (LTV) vs Coût d'Acquisition (CAC)")
    df_bar = pd.DataFrame({
        "Indicateur": ["CAC (Coût)", "LTV Actuelle", "LTV Projetée"],
        "Montant (MAD)": [cac, ltv_actuelle, ltv_projetee]
    })
    fig_bar = px.bar(df_bar, x="Indicateur", y="Montant (MAD)", color="Indicateur", text_auto='.0f',
                     color_discrete_sequence=["#636EFA", "#FFA15A", "#00CC96"])
    st.plotly_chart(fig_bar, use_container_width=True)

# Diagnostic stratégique automatique
st.subheader("🧠 Diagnostic Stratégique")
if ratio_ltv_cac_projete < 1:
    st.error("⚠️ **Alerte Rentabilité :** Le coût d'acquisition dépasse la valeur générée par le client. Il faut réduire le CAC ou augmenter le panier moyen de toute urgence.")
elif ratio_ltv_cac_projete < 3:
    st.warning("⚖️ **Équilibre Fragile :** Le modèle est rentable mais sous le standard optimal (3x). La réduction du churn est votre meilleur levier de croissance.")
else:
    st.success("🏆 **Modèle Hautement Performant :** Votre ratio LTV/CAC dépasse le seuil de référence (3x). Vous disposez d'une marge de manœuvre solide pour accélérer l'acquisition.")
