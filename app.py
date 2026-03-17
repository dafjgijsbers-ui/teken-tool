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
    st.image(LOGO_URL, width=200) # Gefixt voor 2026 [cite: 7]
with col_titel:
    st.title("Universele Maten Tool Pro (mm)")

st.divider()

# --- SIDEBAR ---
vorm_type = st.sidebar.selectbox("Kies type", ["Steen", "Hoek"])
zaag_dikte = st.sidebar.slider("Dikte zaagblad (mm)", 0.0, 5.0, 3.0)

with st.sidebar.expander("Maat Steen", expanded=True):
    if vorm_type == "Steen":
        l1 = st.number_input("Lengte L1 (mm)", min_value=1.0, value=210.0)
        l2 = st.number_input("Breedte L2 (mm)", min_value=1.0, value=100.0)
        h = st.number_input("Hoogte H (mm)", min_value=0.1, value=50.0)
        dikte = 0.0
        grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
    else:
        l1 = st.number_input("Lengte L1 (mm)", min_value=1.0, value=210.0)
        l2 = st.number_input("Lengte L2 (mm)", min_value=1.0, value=100.0)
        dikte = st.number_input("Dikte D (mm)", min_value=0.1, value=23.0)
        h = st.number_input("Hoogte H (mm)", min_value=0.1, value=50.0)
        grond_poly = np.array([[0,0], [l1,0], [l1,dikte], [dikte,dikte], [dikte,l2], [0,l2]])

with st.sidebar.expander("Zaagsnede Instellingen", expanded=True):
    aantal_x = st.slider("Aantal Zaagsnedes X (Verticaal)", 0, 5, 0)
    pos_x = [st.number_input(f"X-{i+1} positie", value=23.0 if i==0 else l1-23, key=f"x{i}") for i in range(aantal_x)]
    aantal_y = st.slider("Aantal Zaagsnedes Y (Horizontaal)", 0, 5, 0)
    pos_y = [st.number_input(f"Y-{i+1} positie", value=23.0 if i==0 else l2-23, key=f"y{i}") for i in range(aantal_y)]

# --- VISUALISATIE ---
fig1, ax1 = plt.subplots(figsize=(10, 6))

# Teken de vorm
omtrek = plt.Polygon(grond_poly, fill=None, edgecolor='black', linewidth=1, alpha=0.3)
ax1.add_patch(omtrek)

# Hulpoplossing voor tekst labels
def get_label(pos, totaal):
    van_kant = totaal - pos
    if van_kant < pos:
        return f"{int(pos)} ({int(van_kant)} van overkant)"
    return f"{int(pos)}"

# Teken X snedes
for i, px in enumerate(pos_x):
    y_lim = l2 if (vorm_type == "Steen" or px <= dikte) else dikte
    ax1.add_patch(plt.Rectangle((px, 0), zaag_dikte, y_lim, color='red', alpha=0.5))
    label = get_label(px, l1)
    ax1.text(px + (zaag_dikte/2), y_lim + 5, f"X{i+1}: {label}", color='red', weight='bold', ha='center', fontsize=8)

# Teken Y snedes
for i, py in enumerate(pos_y):
    x_lim = l1 if (vorm_type == "Steen" or py <= dikte) else dikte
    ax1.add_patch(plt.Rectangle((0, py), x_lim, zaag_dikte, color='red', alpha=0.5))
    label = get_label(py, l2)
    ax1.text(x_lim + 5, py + (zaag_dikte/2), f"Y{i+1}: {label}", color='red', weight='bold', va='center', fontsize=8)

ax1.set_aspect('equal')
ax1.axis('off')
# Belangrijk: dpi=80 voorkomt de crash uit je logs [cite: 52]
st.pyplot(fig1, dpi=80) 

# --- TABEL ---
st.subheader("📋 Productie Overzicht")
overzicht = []
for i, px in enumerate(pos_x):
    overzicht.append({"Zaagsnede": f"X-{i+1}", "Vanaf Nul (mm)": px, "Vanaf Overkant (mm)": l1 - px})
for i, py in enumerate(pos_y):
    overzicht.append({"Zaagsnede": f"Y-{i+1}", "Vanaf Nul (mm)": py, "Vanaf Overkant (mm)": l2 - py})

if overzicht:
    st.table(pd.DataFrame(overzicht))
