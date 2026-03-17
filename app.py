import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd

# Pagina configuratie
st.set_page_config(page_title="DEKO Maten Tool Pro", layout="wide")

# --- LOGO EN TITEL ---
LOGO_URL = "https://raw.githubusercontent.com/DennisDeko/teken-tool/main/deko_logo.jpg"
col_logo, col_titel = st.columns([1, 3])
with col_logo:
    # 'width' gebruiken ipv 'use_container_width' om 2026 errors te voorkomen
    st.image(LOGO_URL, width=200) 
with col_titel:
    st.title("DEKO Maatwerk Editor - 3D Vlakken Fix")

st.divider()

# --- SIDEBAR ---
vorm_type = st.sidebar.selectbox("Kies type", ["Steen", "Hoek"])
zaag_dikte = st.sidebar.slider("Dikte zaagblad (mm)", 0.0, 5.0, 3.0)

with st.sidebar.expander("Basis Afmetingen", expanded=True):
    l1 = st.number_input("Lengte L1 (mm)", min_value=1.0, value=210.0)
    l2 = st.number_input("Breedte/Lengte L2 (mm)", min_value=1.0, value=100.0)
    h = st.number_input("Hoogte H (mm)", min_value=0.1, value=50.0)
    if vorm_type == "Steen":
        dikte = 0.0
        grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
        vlak_indices = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    else:
        dikte = st.number_input("Dikte D (mm)", min_value=0.1, value=23.0)
        grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
        vlak_indices = [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11], [0, 1, 7, 6], [1, 2, 8, 7], [2, 3, 9, 8], [3, 4, 10, 9], [4, 5, 11, 10], [5, 0, 6, 11]]

with st.sidebar.expander("Zaaglijnen", expanded=True):
    ax_count = st.slider("Aantal X-snedes", 0, 4, 0)
    pos_x = [st.number_input(f"X{i+1} Positie", value=23.0 if i==0 else l1-23, key=f"x{i}") for i in range(ax_count)]
    ay_count = st.slider("Aantal Y-snedes", 0, 4, 0)
    pos_y = [st.number_input(f"Y{i+1} Positie", value=23.0 if i==0 else l2-23, key=f"y{i}") for i in range(ay_count)]

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Zaagplan")
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    
    # Gebruik facecolor en edgecolor apart om warnings te voorkomen 
    poly = plt.Polygon(grond_poly, facecolor='lightgray', alpha=0.3, edgecolor='black', linewidth=1)
    ax1.add_patch(poly)

    # X-snedes (Verticaal)
    for i, px in enumerate(pos_x):
        y_max = l2 if (vorm_type == "Steen" or px <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((px, 0), zaag_dikte, y_max, facecolor='red', alpha=0.6))
        
        van_rechts = l1 - px
        label = f"X{i+1}: {int(px)}" if px <= l1/2 else f"X{i+1}: {int(px)} ({int(van_rechts)} v. R)"
        ax1.text(px, y_max + 5, label, color='red', fontsize=8, weight='bold', ha='center')

    # Y-snedes (Horizontaal)
    for i, py in enumerate(pos_y):
        x_max = l1 if (vorm_type == "Steen" or py <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((0, py), x_max, zaag_dikte, facecolor='red', alpha=0.6))
        
        van_boven = l2 - py
        label = f"Y{i+1}: {int(py)}" if py <= l2/2 else f"Y{i+1}: {int(py)} ({int(van_boven)} v. B)"
        ax1.text(x_max + 5, py, label, color='red', fontsize=8, weight='bold', va='center')

    ax1.set_aspect('equal')
    ax1.axis('off')
    # DPI op 80 om geheugenproblemen (DecompressionBomb) te voorkomen 
    st.pyplot(fig1, dpi=80) 

with col2:
    st.subheader("3D Preview")
    fig2 = plt.figure(figsize=(6, 5))
    ax2 = fig2.add_subplot(111, projection='3d')
    
    v_3d = np.array([ [p[0],p[1],0] for p in grond_poly ] + [ [p[0],p[1],h] for p in grond_poly ])
    vlakken = [[v_3d[i] for i in idx] for idx in vlak_indices]
    
    ax2.add_collection3d(Poly3DCollection(vlakken, facecolors='cyan', edgecolors='black', alpha=0.1))

    # 3D X-Vlakken
    for px in pos_x:
        y_m = l2 if (vorm_type == "Steen" or px <= dikte) else dikte
        zv = [[px, 0, 0], [px+zaag_dikte, 0, 0], [px+zaag_dikte, y_m, h], [px, y_m, h]]
        ax2.add_collection3d(Poly3DCollection([zv], facecolors='red', alpha=0.7))

    # 3D Y-Vlakken (Nu als echt horizontaal vlak door de steen)
    for py in pos_y:
        x_m = l1 if (vorm_type == "Steen" or py <= dikte) else dikte
        zv = [[0, py, 0], [x_m, py, 0], [x_m, py+zaag_dikte, h], [0, py+zaag_dikte, h]]
        ax2.add_collection3d(Poly3DCollection([zv], facecolors='red', alpha=0.7))

    limit = max(l1, l2, h)
    ax2.set_xlim(0, limit); ax2.set_ylim(0, limit); ax2.set_zlim(0, limit)
    ax2.view_init(elev=25, azim=-45)
    ax2.axis('off')
    st.pyplot(fig2, dpi=80)

# --- TABEL ---
st.divider()
st.subheader("📋 Productie Data")
data = []
for i, px in enumerate(pos_x):
    data.append({"ID": f"X{i+1}", "Maat vanaf 0": f"{px} mm", "Maat vanaf overkant": f"{l1-px} mm"})
for i, py in enumerate(pos_y):
    data.append({"ID": f"Y{i+1}", "Maat vanaf 0": f"{py} mm", "Maat vanaf overkant": f"{l2-py} mm"})

if data:
    st.table(pd.DataFrame(data))
