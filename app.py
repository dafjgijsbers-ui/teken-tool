import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

st.set_page_config(page_title="DEKO Zaag-Editor", layout="wide")

# --- CONFIGURATIE ---
L_WAAL = 210.0
B_WAAL = 100.0
H_WAAL = 50.0

# --- SIDEBAR ---
st.sidebar.header("Product Keuze")
type_keuze = st.sidebar.radio("Selecteer basisvorm:", ["Steen", "Hoek"])

st.sidebar.divider()

with st.sidebar.expander("Instellingen Zaagsnede", expanded=True):
    zaag_dikte = st.number_input("Dikte zaagblad (mm)", min_value=0.0, value=3.0, step=0.5)
    
    st.write("---")
    st.write("🟢 **Strips van de strek (L1)**")
    strip_maat = st.number_input("Gewenste strip dikte (mm)", min_value=1.0, max_value=45.0, value=23.0)
    dubbel_zagen = st.checkbox("Aan beide kanten zagen", value=True)

# --- LOGICA ---
# We berekenen de lijnen
# Strip 1: van 0 tot strip_maat
# Zaaggat 1: van strip_maat tot strip_maat + zaag_dikte
# Middenstuk: wat er overblijft
# Zaaggat 2 (indien dubbel): voor de tweede strip aan het einde

# --- VISUALISATIE ---
st.title(f"Zaagplan: Waalformaat {type_keuze}")

col1, col2 = st.columns([2, 1])

with col1:
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Basis steen tekenen
    omtrek = plt.Rectangle((0, 0), L_WAAL, B_WAAL, fill=None, edgecolor='black', linewidth=1)
    ax.add_patch(omtrek)
    
    # --- STRIP 1 (Links) ---
    # Het product
    ax.add_patch(plt.Rectangle((0, 0), strip_maat, B_WAAL, color='green', alpha=0.3))
    ax.text(strip_maat/2, B_WAAL/2, f"{strip_maat}\nmm", ha='center', va='center', weight='bold')
    
    # Het zaaggat (rood/wit gestreept of rood)
    ax.add_patch(plt.Rectangle((strip_maat, 0), zaag_dikte, B_WAAL, color='red', alpha=0.8))
    ax.text(strip_maat + (zaag_dikte/2), B_WAAL + 10, f"{zaag_dikte}", color='red', ha='center', fontsize=8)

    # --- STRIP 2 (Rechts, indien aangevinkt) ---
    midden_start = strip_maat + zaag_dikte
    midden_eind = L_WAAL
    
    if dubbel_zagen:
        midden_eind = L_WAAL - strip_maat - zaag_dikte
        # Tweede strip aan de rechterkant
        ax.add_patch(plt.Rectangle((L_WAAL - strip_maat, 0), strip_maat, B_WAAL, color='green', alpha=0.3))
        ax.text(L_WAAL - (strip_maat/2), B_WAAL/2, f"{strip_maat}\nmm", ha='center', va='center', weight='bold')
        
        # Tweede zaaggat
        ax.add_patch(plt.Rectangle((L_WAAL - strip_maat - zaag_dikte, 0), zaag_dikte, B_WAAL, color='red', alpha=0.8))
        ax.text(L_WAAL - strip_maat - (zaag_dikte/2), B_WAAL + 10, f"{zaag_dikte}", color='red', ha='center', fontsize=8)

    # --- MIDDENSTUK (Afval) ---
    afval_breedte = midden_eind - midden_start
    if afval_breedte > 0:
        ax.add_patch(plt.Rectangle((midden_start, 0), afval_breedte, B_WAAL, 
                                   hatch='///', fill=False, edgecolor='gray', alpha=0.4))
        ax.text(midden_start + (afval_breedte/2), B_WAAL/2, "REST", ha='center', color='gray')

    # Opmaak
    ax.set_xlim(-20, L_WAAL + 20)
    ax.set_ylim(-20, B_WAAL + 40)
    ax.set_aspect('equal')
    ax.axis('off')
    st.pyplot(fig)

with col2:
    st.subheader("📋 Productie Info")
    st.write(f"**Basismaat:** {int(L_WAAL)} x {int(B_WAAL)} x {int(H_WAAL)} mm")
    st.write(f"**Zaagverlies:** {zaag_dikte} mm per snede")
    
    st.info(f"Je haalt **{'2 strips' if dubbel_zagen else '1 strip'}** uit deze steen.")
    
    rest_maat = L_WAAL - (strip_maat * (2 if dubbel_zagen else 1)) - (zaag_dikte * (2 if dubbel_zagen else 1))
    st.warning(f"Resterend afvalstuk: **{round(rest_maat, 1)} mm**")

    if type_keuze == "Hoek":
        st.write("---")
        st.write("📐 **Hoek-specificatie:**")
        st.write("L-zijde 1: 210 mm")
        st.write("L-zijde 2: 100 mm")
        st.caption("De strips worden uit de lange zijdes gezaagd.")
