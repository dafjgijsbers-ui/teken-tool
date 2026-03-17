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
    st.image(LOGO_URL, width=200) 
with col_titel:
    st.title("DEKO Maatwerk Editor - 3D Vlakken")

# --- SIDEBAR ---
vorm_type = st.sidebar.selectbox("Kies type", ["Steen", "Hoek"])
zaag_dikte = st.sidebar.slider("Dikte zaagblad (mm)", 0.0, 5.0, 3.0)

with st.sidebar.expander("Basis Afmetingen", expanded=True):
    if vorm_type == "Steen":
        l1, l2, h = st.number_input("L1", value=210.0), st.number_input("L2", value=100.0), st.number_input("H", value=50.0)
        dikte = 0.0
        grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
        vlak_indices = [[0,1,2,3], [4,5,6,7], [0,1,5,4], [1,2,6,5], [2,3,7,6], [3,0,4,7]]
    else:
        l1, l2, h = st.number_input("L1", value=210.0), st.number_input("L2", value=100.0), st.number_input("H", value=50.0)
        dikte = st.number_input("Dikte D", value=23.0)
        grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])
        vlak_indices = [[0,1,2,3,4,5], [6,7,8,9,10,11], [0,1,7,6], [1,2,8,7], [2,3,9,8], [3,4,10,9], [4,5,11,10], [5,0,6,11]]

with st.sidebar.expander("Zaaglijnen", expanded=True):
    ax = st.slider("Aantal X-snedes", 0, 4, 0)
    pos_x = [st.number_input(f"X{i+1}", value=23.0 if i==0 else l1-23, key=f"x{i}") for i in range(ax)]
    ay = st.slider("Aantal Y-snedes", 0, 4, 0)
    pos_y = [st.number_input(f"Y{i+1}", value=23.0 if i==0 else l2-23, key=f"y{i}") for i in range(ay)]

# --- VISUALISATIE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2D Plan")
    fig1, ax1 = plt.subplots()
    ax1.add_patch(plt.Polygon(grond_poly, facecolor='gray', alpha=0.1, edgecolor='black'))
    
    for i, px in enumerate(pos_x):
        y_m = l2 if (vorm_type=="Steen" or px<=dikte) else dikte
        ax1.add_patch(plt.Rectangle((px, 0), zaag_dikte, y_m, facecolor='red', alpha=0.6))
        txt = f"X{i+1}: {int(px)}" if px <= l1/2 else f"X{i+1}: {int(px)} ({int(l1-px)} van R)"
        ax1.text(px, y_m+5, txt, color='red', weight='bold', fontsize=8, ha='center')

    for i, py in enumerate(pos_y):
        x_m = l1 if (vorm_type=="Steen" or py<=dikte) else dikte
        ax1.add_patch(plt.Rectangle((0, py), x_m, zaag_dikte, facecolor='red', alpha=0.6))
        txt = f"Y{i+1}: {int(py)}" if py <= l2/2 else f"Y{i+1}: {int(py)} ({int(l2-py)} van B)"
        ax1.text(x_m+5, py, txt, color='red', weight='bold', fontsize=8, va='center')

    ax1.set_aspect('equal'); ax1.axis('off')
    st.pyplot(fig1, dpi=80) # DPI fix tegen crashes [cite: 52]

with col2:
    st.subheader("3D Vlakken")
    fig2 = plt.figure(); ax2 = fig2.add_subplot(111, projection='3d')
    v_3d = np.array([ [p[0],p[1],0] for p in grond_poly ] + [ [p[0],p[1],h] for p in grond_poly ])
    ax2.add_collection3d(Poly3DCollection([[v_3d[i] for i in idx] for idx in vlak_indices], facecolors='cyan', alpha=0.1, edgecolors='black'))

    # X-VLAKKEN (Verticaal door de steen)
    for px in pos_x:
        y_top = l2 if (vorm_type=="Steen" or px<=dikte) else dikte
        vlak = [[px,0,0], [px+zaag_dikte,0,0], [px+zaag_dikte,y_top,h], [px,y_top,h]]
        ax2.add_collection3d(Poly3DCollection([vlak], facecolors='red', alpha=0.7))

    # Y-VLAKKEN (Horizontaal door de steen)
    for py in pos_y:
        x_top = l1 if (vorm_type=="Steen" or py<=dikte) else dikte
        vlak = [[0,py,0], [x_top,py,0], [x_top,py+zaag_dikte,h], [0,py+zaag_dikte,h]]
        ax2.add_collection3d(Poly3DCollection([vlak], facecolors='red', alpha=0.7))

    ax2.set_xlim(0, max(l1,l2)); ax2.set_ylim(0, max(l1,l2)); ax2.set_zlim(0, max(l1,l2))
    ax2.view_init(elev=25, azim=-45); ax2.axis('off')
    st.pyplot(fig2, dpi=80)
