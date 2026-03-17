import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Pagina instellingen
st.set_page_config(page_title="DEKO Zaag Tool", layout="wide")

# Logo en Titel
LOGO_URL = "https://raw.githubusercontent.com/DennisDeko/teken-tool/main/deko_logo.jpg"
col_l, col_r = st.columns([1, 4])
with col_l:
    try:
        st.image(LOGO_URL, width=150)
    except:
        st.write("DEKO LOGO")
with col_r:
    st.title("DEKO Transformatie Editor")

# --- SIDEBAR ---
st.sidebar.header("Configuratie")
vorm_type = st.sidebar.selectbox("Basisvorm", ["Waalformaat Steen", "Waalformaat Hoek"])

# Standaardmaten
L, B, H = 210, 100, 50
D = 23 # Dikte strip bij hoek

with st.sidebar.expander("Zaag Instellingen", expanded=True):
    zaag_dikte = st.number_input("Zaagblad dikte (mm)", 0.0, 10.0, 3.0)
    
    st.write("---")
    links_actief = st.checkbox("Zaagsnede Links", value=True)
    if links_actief:
        maat_links = st.number_input("Dikte Strip Links (mm)", 1, L, 23)
        
    rechts_actief = st.checkbox("Zaagsnede Rechts")
    if rechts_actief:
        maat_rechts = st.number_input("Dikte Strip Rechts (mm)", 1, L, 23)

# --- VISUALISATIE ---
fig, ax = plt.subplots(figsize=(10, 5))

# Teken Basis
if vorm_type == "Waalformaat Hoek":
    # L-vorm tekenen
    pts = np.array([[0,0], [L,0], [L,D], [D,D], [D,B], [0,B], [0,0]])
    ax.plot(pts[:,0], pts[:,1], color='black', lw=2)
    ax.fill(pts[:,0], pts[:,1], color='lightgray', alpha=0.1)
else:
    # Steen tekenen
    rect = plt.Rectangle((0,0), L, B, fill=None, edgecolor='black', lw=2)
    ax.add_patch(rect)

# Zaagfuncties
def teken_snede(pos, kant):
    if kant == "links":
        # Groen product
        ax.add_patch(plt.Rectangle((0,0), pos, B, color='green', alpha=0.3))
        # Rood zaaggat
        ax.add_patch(plt.Rectangle((pos, 0), zaag_dikte, B, color='red', alpha=0.6))
        # Arcering afval
        ax.add_patch(plt.Rectangle((pos + zaag_dikte, 0), L - (pos+zaag_dikte), B, hatch='///', fill=False, color='gray', alpha=0.3))
        ax.text(pos/2, B/2, f"{pos}", ha='center', weight='bold')
    
    if kant == "rechts":
        ax.add_patch(plt.Rectangle((L-pos, 0), pos, B, color='green', alpha=0.3))
        ax.add_patch(plt.Rectangle((L-pos-zaag_dikte, 0), zaag_dikte, B, color='red', alpha=0.6))
        ax.text(L-pos/2, B/2, f"{pos}", ha='center', weight='bold')

if links_actief: teken_snede(maat_links, "links")
if rechts_actief: teken_snede(maat_rechts, "rechts")

ax.set_aspect('equal')
ax.axis('off')
st.pyplot(fig)

# Tabel met resultaten
st.subheader("Resultaat Maten")
res_data = {
    "Omschrijving": ["Lengte", "Breedte", "Hoogte", "Zaagverlies"],
    "Maat (mm)": [L, B, H, zaag_dikte]
}
st.table(pd.DataFrame(res_data))
