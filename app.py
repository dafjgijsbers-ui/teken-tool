import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd

st.set_page_config(page_title="DEKO Maten Tool Pro", layout="wide")

# --- LOGO EN TITEL ---
LOGO_URL = "https://raw.githubusercontent.com/DennisDeko/teken-tool/main/deko_logo.jpg"

col_logo, col_titel = st.columns([1, 3])
with col_logo:
    # GEFIXT: use_container_width vervangen door width="stretch" voor 2026 compatibiliteit
    st.image(LOGO_URL, width=200) 
with col_titel:
    st.title("Universele Maten Tool Pro (mm)")

st.divider()

# --- SIDEBAR INSTELLINGEN ---
vorm_type = st.sidebar.selectbox("Kies type", ["Steen", "Hoek"])
st.sidebar.divider()

# Nieuw: Zaagblad dikte
zaag_dikte = st.sidebar.slider("Dikte zaagblad (mm)", 0.0, 5.0, 3.0)

# 1. Maat Steen
with st.sidebar.expander("Maat Steen", expanded=True):
    if vorm_type == "Steen":
        st.write("🟢 **Zijde L1**")
        l1 = st.number_input("Lengte (mm)", min_value=1.0, value=210.0, key="l1_s")
        st.write("🔵 **Zijde L2**")
        l2 = st.number_input("Breedte (mm)", min_value=1.0, value=100.0, key="l2_s")
        st.write("⚪ **Hoogte H**")
        h = st.number_input("Hoogte (mm)", min_value=0.1, value=50.0, key="h_s")
        dikte = 0.0
        grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
        vlak_indices = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
        labels_2d = [{'pos': [l1/2, -15], 'text': f'L1: {int(l1)}', 'color': 'green'},
                     {'pos': [l1 + 15, l2/2], 'text': f'L2: {int(l2)}', 'color': 'blue', 'rotation': 90}]
    else:
        st.write("🟢 **Zijde L1**")
        l1 = st.number_input("Lengte L1 (mm)", min_value=1.0, value=210.0, key="l1_h")
        st.write("🔵 **Zijde L2**")
        l2 = st.number_input("Lengte L2 (mm)", min_value=1.0, value=100.0, key="l2_h")
        limiet = float(min(l1, l2))
        st.write("🟠 **Dikte D**")
        dikte = st.number_input("Dikte (mm)", min_value=0.1, max_value=limiet, value=23.0, key="d_h")
        st.write("⚪ **Hoogte H**")
        h = st.number_input("Hoogte (mm)", min_value=0.1, value=50.0, key="h_h")
        grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
        vlak_indices = [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11], [0, 1, 7, 6], [1, 2, 8, 7], [2, 3, 9, 8], [3, 4, 10, 9], [4, 5, 11, 10], [5, 0, 6, 11]]
        labels_2d = [{'pos': [l1/2, -15], 'text': f'L1: {int(l1)}', 'color': 'green'},
                     {'pos': [-15, l2/2], 'text': f'L2: {int(l2)}', 'color': 'blue', 'rotation': 90},
                     {'pos': [dikte/2, dikte + 10], 'text': f'D: {int(dikte)}', 'color': 'orange'}]

# 2. Zaagsnede
with st.sidebar.expander("Zaagsnede Instellingen", expanded=False):
    st.write("🔴 **Verticale sneden**")
    aantal_x = st.slider("Aantal Zaagsnedes X", 0, 5, 0)
    posities_x = [st.number_input(f"X-{i+1} (mm)", value=50.0 + (i*50.0), key=f"x_{i}") for i in range(aantal_x)]
    st.write("🔴 **Horizontale sneden**")
    aantal_y = st.slider("Aantal Zaagsnedes Y", 0, 5, 0)
    posities_y = [st.number_input(f"Y-{i+1} (mm)", value=25.0 + (i*25.0), key=f"y_{i}") for i in range(aantal_y)]

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"2D Bovenaanzicht")
    fig1, ax1 = plt.subplots()
    
    # Teken basis
    omtrek = plt.Polygon(grond_poly, fill=None, edgecolor='black', linewidth=1, alpha=0.3)
    ax1.add_patch(omtrek)
    
    # Kleur zijden
    if vorm_type == "Steen":
        ax1.plot([0, l1], [0, 0], color='green', linewidth=4)
        ax1.plot([l1, l1], [0, l2], color='blue', linewidth=4)
    else:
        ax1.plot([0, l1], [0, 0], color='green', linewidth=4)
        ax1.plot([0, 0], [0, l2], color='blue', linewidth=4)

    # Zaagsnedes inclusief dikte
    for i, px in enumerate(posities_x):
        y_lim = l2 if (vorm_type == "Steen" or px <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((px, 0), zaag_dikte, y_lim, color='red', alpha=0.5))
        ax1.text(px, y_lim + 5, f"X{i+1}", color='red', weight='bold')

    for i, py in enumerate(posities_y):
        x_lim = l1 if (vorm_type == "Steen" or py <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((0, py), x_lim, zaag_dikte, color='red', alpha=0.5))
        ax1.text(x_lim + 5, py, f"Y{i+1}", color='red', weight='bold')
    
    ax1.set_aspect('equal')
    ax1.axis('off')
    # GEFIXT: dpi=80 voorkomt de DecompressionBombError
    st.pyplot(fig1, dpi=80) 

with col2:
    st.subheader(f"3D Model")
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111, projection='3d')
    
    v_3d = []
    for p in grond_poly: v_3d.append([p[0], p[1], 0])
    for p in grond_poly: v_3d.append([p[0], p[1], h])
    v_3d = np.array(v_3d)
    vlakken = [[v_3d[i] for i in idx] for idx in vlak_indices]
    
    poly3d = Poly3DCollection(vlakken, facecolors='cyan', linewidths=0.5, edgecolors='black', alpha=.1)
    ax2.add_collection3d(poly3d)
    
    # Zaagsnedes in 3D
    for px in posities_x:
        y_t = l2 if (vorm_type == "Steen" or px <= dikte) else dikte
        zv = np.array([[px,0,0], [px+zaag_dikte,0,0], [px+zaag_dikte,y_t,0], [px,y_t,0]])
        ax2.add_collection3d(Poly3DCollection([zv], facecolors='red', alpha=0.5))

    ax2.set_xlim(0, max(l1, l2)); ax2.set_ylim(0, max(l1, l2)); ax2.set_zlim(0, max(l1, l2))
    ax2.axis('off')
    # GEFIXT: dpi=80 voorkomt de DecompressionBombError
    st.pyplot(fig2, dpi=80)

# --- OVERZICHT ---
st.table(pd.DataFrame({"Item": ["L1", "L2", "H", "Dikte Zaag"], "Waarde": [l1, l2, h, zaag_dikte]}))
