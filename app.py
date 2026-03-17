import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import pandas as pd

# Pagina instellingen
st.set_page_config(page_title="DEKO Maten Tool Pro", layout="wide")

# --- LOGO EN TITEL ---
LOGO_URL = "https://raw.githubusercontent.com/DennisDeko/teken-tool/main/deko_logo.jpg"
col_logo, col_titel = st.columns([1, 3])
with col_logo:
    # Gefixt: Breedte expliciet op 200px om errors te voorkomen
    st.image(LOGO_URL, width=200) 
with col_titel:
    st.title("DEKO Maatwerk Editor (mm)")

st.divider()

# --- SIDEBAR ---
vorm_type = st.sidebar.selectbox("Kies type", ["Steen", "Hoek"])
zaag_dikte = st.sidebar.slider("Dikte zaagblad (mm)", 0.0, 5.0, 3.0)

with st.sidebar.expander("Basis Afmetingen", expanded=True):
    if vorm_type == "Steen":
        l1 = st.number_input("Lengte L1 (mm)", min_value=1.0, value=210.0)
        l2 = st.number_input("Breedte L2 (mm)", min_value=1.0, value=100.0)
        h = st.number_input("Hoogte H (mm)", min_value=0.1, value=50.0)
        dikte = 0.0
        grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
        vlak_indices = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    else:
        l1 = st.number_input("Lengte L1 (mm)", min_value=1.0, value=210.0)
        l2 = st.number_input("Lengte L2 (mm)", min_value=1.0, value=100.0)
        dikte = st.number_input("Dikte D (mm)", min_value=0.1, value=23.0)
        h = st.number_input("Hoogte H (mm)", min_value=0.1, value=50.0)
        grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
        vlak_indices = [[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11], [0, 1, 7, 6], [1, 2, 8, 7], [2, 3, 9, 8], [3, 4, 10, 9], [4, 5, 11, 10], [5, 0, 6, 11]]

with st.sidebar.expander("Zaaglijnen", expanded=True):
    aantal_x = st.slider("Aantal X-snedes", 0, 4, 0)
    pos_x = [st.number_input(f"X{i+1} Positie", value=23.0 if i==0 else l1-23, key=f"x{i}") for i in range(aantal_x)]
    
    aantal_y = st.slider("Aantal Y-snedes", 0, 4, 0)
    pos_y = [st.number_input(f"Y{i+1} Positie", value=23.0 if i==0 else l2-23, key=f"y{i}") for i in range(aantal_y)]

# --- FUNCTIE VOOR SLIMME LABELS ---
def bereken_label(pos, max_maat):
    van_andere_kant = max_maat - pos
    if van_andere_kant < pos:
        return f"{int(pos)} ({int(van_andere_kant)} van rechts/boven)"
    return f"{int(pos)}"

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Zaagplan")
    # DPI op 80 om de 'DecompressionBombError' te voorkomen 
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    
    # Teken omtrek
    ax1.add_patch(plt.Polygon(grond_poly, fill=True, color='lightgray', alpha=0.2, edgecolor='black'))

    # X-snedes (Verticaal)
    for i, px in enumerate(pos_x):
        y_max = l2 if (vorm_type == "Steen" or px <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((px, 0), zaag_dikte, y_max, color='red', alpha=0.6))
        label = bereken_label(px, l1)
        ax1.text(px, y_max + 5, f"X{i+1}: {label}", color='red', fontsize=8, weight='bold', ha='center')

    # Y-snedes (Horizontaal)
    for i, py in enumerate(pos_y):
        x_max = l1 if (vorm_type == "Steen" or py <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((0, py), x_max, zaag_dikte, color='red', alpha=0.6))
        label = bereken_label(py, l2)
        ax1.text(x_max + 5, py, f"Y{i+1}: {label}", color='red', fontsize=8, weight='bold', va='center')

    ax1.set_aspect('equal')
    ax1.axis('off')
    st.pyplot(fig1, dpi=80) 

with col2:
    st.subheader("3D Preview")
    fig2 = plt.figure(figsize=(6, 5))
    ax2 = fig2.add_subplot(111, projection='3d')
    
    # 3D Punten genereren
    v_3d = []
    for p in grond_poly: v_3d.append([p[0], p[1], 0])
    for p in grond_poly: v_3d.append([p[0], p[1], h])
    v_3d = np.array(v_3d)
    vlakken = [[v_3d[i] for i in idx] for idx in vlak_indices]
    
    # Teken 3D Object
    ax2.add_collection3d(Poly3DCollection(vlakken, facecolors='cyan', edgecolors='black', alpha=0.1))

    # Toon zaagvlakken in 3D
    for px in pos_x:
        y_m = l2 if (vorm_type == "Steen" or px <= dikte) else dikte
        zv = [[px, 0, 0], [px+zaag_dikte, 0, 0], [px+zaag_dikte, y_m, h], [px, y_m, h]]
        ax2.add_collection3d(Poly3DCollection([zv], facecolors='red', alpha=0.5))

    limit = max(l1, l2, h)
    ax2.set_xlim(0, limit); ax2.set_ylim(0, limit); ax2.set_zlim(0, limit)
    ax2.view_init(elev=20, azim=-35)
    ax2.axis('off')
    st.pyplot(fig2, dpi=80)

# --- TABEL ---
st.divider()
st.subheader("📋 Zaagmaten Controle")
data = []
for i, px in enumerate(pos_x):
    data.append({"ID": f"X{i+1}", "Maat vanaf 0": f"{px} mm", "Maat vanaf overkant": f"{l1-px} mm"})
for i, py in enumerate(pos_y):
    data.append({"ID": f"Y{i+1}", "Maat vanaf 0": f"{py} mm", "Maat vanaf overkant": f"{l2-py} mm"})

if data:
    st.table(pd.DataFrame(data))
