import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd

st.set_page_config(page_title="DEKO Waalformaat Tool", layout="wide")

# --- LOGO EN TITEL ---
LOGO_URL = "https://raw.githubusercontent.com/DennisDeko/teken-tool/main/deko_logo.jpg"

col_logo, col_titel = st.columns([1, 3])
with col_logo:
    st.image(LOGO_URL, width=200) 
with col_titel:
    st.title("Waalformaat Zaag-Editor (mm)")

st.divider()

# --- STANDAARD WAALFORMAAT WAARDES ---
L_WAAL = 210.0
B_WAAL = 100.0
H_WAAL = 50.0

# --- SIDEBAR ---
st.sidebar.header("Baksteen Type: Waalformaat")
st.sidebar.info(f"Standaardmaten: {int(L_WAAL)}x{int(B_WAAL)}x{int(H_WAAL)} mm")

with st.sidebar.expander("Zaagsnedes Aanbrengen", expanded=True):
    st.write("🟢 **Verticale Zaagsnede (X)**")
    zaag_x = st.number_input("Positie vanaf links (mm)", min_value=0.0, max_value=L_WAAL, value=150.0)
    
    st.write("🔵 **Horizontale Zaagsnede (Y)**")
    zaag_y = st.number_input("Positie vanaf onder (mm)", min_value=0.0, max_value=B_WAAL, value=B_WAAL)

# --- BEREKENING RESTSTUK ---
# We gaan ervan uit dat het stuk linksonder (0,0 tot zaag_x, zaag_y) het product is.
overgebleven_breedte = zaag_x
overgebleven_diepte = zaag_y

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Zaagplan (Arcering = Afval)")
    fig1, ax1 = plt.subplots()
    
    # 1. De volledige steen (omtrek)
    omtrek = plt.Rectangle((0, 0), L_WAAL, B_WAAL, fill=None, edgecolor='black', linewidth=1)
    ax1.add_patch(omtrek)
    
    # 2. Het deel dat WEG gaat (Arcering)
    # Rechts van de verticale zaagsnede
    afval_rechts = plt.Rectangle((zaag_x, 0), L_WAAL - zaag_x, B_WAAL, 
                                  hatch='///', fill=False, edgecolor='gray', alpha=0.5)
    ax1.add_patch(afval_rechts)
    
    # Boven de horizontale zaagsnede (voor het resterende deel)
    afval_boven = plt.Rectangle((0, zaag_y), zaag_x, B_WAAL - zaag_y, 
                                 hatch='\\\\\\', fill=False, edgecolor='gray', alpha=0.5)
    ax1.add_patch(afval_boven)
    
    # 3. Het product (Duidelijke lijnen)
    ax1.plot([0, zaag_x], [0, 0], color='green', linewidth=3) # Onder
    ax1.plot([0, 0], [0, zaag_y], color='blue', linewidth=3)   # Links
    ax1.plot([zaag_x, zaag_x], [0, zaag_y], color='red', linestyle='--') # Zaaglijn X
    ax1.plot([0, zaag_x], [zaag_y, zaag_y], color='red', linestyle='--') # Zaaglijn Y

    # Maten bij de zaaglijnen
    ax1.text(zaag_x/2, -10, f"{int(zaag_x)} mm", color='green', weight='bold', ha='center')
    ax1.text(-15, zaag_y/2, f"{int(zaag_y)} mm", color='blue', weight='bold', va='center', rotation=90)

    ax1.set_xlim(-30, L_WAAL + 30); ax1.set_ylim(-30, B_WAAL + 30); ax1.set_aspect('equal')
    ax1.axis('off')
    st.pyplot(fig1)

with col2:
    st.subheader("3D Resultaat")
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111, projection='3d')
    
    # Teken alleen het overgebleven deel in 3D
    def draw_box(ax, x, y, z, dx, dy, dz, color, alpha):
        v = np.array([[x,y,z], [x+dx,y,z], [x+dx,y+dy,z], [x,y+dy,z],
                      [x,y,z+dz], [x+dx,y,z+dz], [x+dx,y+dy,z+dz], [x,y+dy,z+dz]])
        indices = [[0,1,2,3], [4,5,6,7], [0,1,5,4], [1,2,6,5], [2,3,7,6], [3,0,4,7]]
        faces = [[v[i] for i in idx] for idx in indices]
        ax.add_collection3d(Poly3DCollection(faces, facecolors=color, linewidths=1, edgecolors='blue', alpha=alpha))

    # Het product
    draw_box(ax2, 0, 0, 0, zaag_x, zaag_y, H_WAAL, 'cyan', 0.6)
    
    # De reststukken (heel licht transparant om te laten zien wat er was)
    draw_box(ax2, 0, 0, 0, L_WAAL, B_WAAL, H_WAAL, 'gray', 0.05)

    ax2.set_xlim(0, L_WAAL); ax2.set_ylim(0, L_WAAL); ax2.set_zlim(0, L_WAAL)
    ax2.view_init(elev=20, azim=-35)
    st.pyplot(fig2)

# --- OVERZICHT ---
st.divider()
st.subheader("📋 Zaaginstructie")
col_a, col_b = st.columns(2)
with col_a:
    st.metric("Product Lengte", f"{int(zaag_x)} mm")
    st.metric("Product Breedte", f"{int(zaag_y)} mm")
with col_b:
    st.metric("Afval Lengte", f"{int(L_WAAL - zaag_x)} mm")
    st.metric("Afval Breedte", f"{int(B_WAAL - zaag_y)} mm")
