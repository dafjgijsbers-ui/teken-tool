import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURATIE ---
st.set_page_config(page_title="DEKO Maten Tool Pro", layout="wide")

# --- LOGO EN TITEL ---
LOGO_URL = "https://raw.githubusercontent.com/DennisDeko/teken-tool/main/deko_logo.jpg"
col_logo, col_titel = st.columns([1, 4])
with col_logo:
    st.image(LOGO_URL, width=150)
with col_titel:
    st.title("DEKO Maatwerk Editor Pro")
    st.caption("Interactieve 3D Visualisatie & Zaagplan")

# --- SIDEBAR: INPUT ---
st.sidebar.header("📐 Instellingen")
vorm_type = st.sidebar.selectbox("Type Steen", ["Steen (Rechthoek)", "Hoek (L-vorm)"])
zaag_dikte = st.sidebar.number_input("Zaagblad dikte (mm)", 0.0, 10.0, 3.0, step=0.5)

with st.sidebar.expander("Basis Afmetingen", expanded=True):
    l1 = st.number_input("Lengte L1 (mm)", value=210.0)
    l2 = st.number_input("Breedte L2 (mm)", value=100.0)
    h = st.number_input("Hoogte H (mm)", value=50.0)
    
    dikte = 0.0
    if vorm_type == "Hoek (L-vorm)":
        dikte = st.number_input("Dikte D (mm)", value=23.0)
        # Validatie: Dikte mag niet groter zijn dan L1 of L2
        if dikte >= l1 or dikte >= l2:
            st.error("Dikte D moet kleiner zijn dan L1 en L2!")

with st.sidebar.expander("✂️ Zaaglijnen (X & Y)", expanded=True):
    # Dynamische kolommen voor X-snedes
    ax = st.slider("Aantal X-snedes", 0, 4, 1)
    cols_x = st.columns(2)
    pos_x = []
    for i in range(ax):
        with cols_x[i % 2]:
            val = st.number_input(f"X{i+1}", value=23.0 + (i*50), key=f"x{i}")
            pos_x.append(val)
            if val > l1:
                st.warning(f"X{i+1} valt buiten L1!")

    st.divider()

    # Dynamische kolommen voor Y-snedes
    ay = st.slider("Aantal Y-snedes", 0, 4, 0)
    cols_y = st.columns(2)
    pos_y = []
    for i in range(ay):
        with cols_y[i % 2]:
            val = st.number_input(f"Y{i+1}", value=23.0 + (i*50), key=f"y{i}")
            pos_y.append(val)
            if val > l2:
                st.warning(f"Y{i+1} valt buiten L2!")

# --- LOGICA: GEOMETRIE DEFINITIES ---
if vorm_type == "Steen (Rechthoek)":
    # 8 hoekpunten van een box
    vertices = np.array([
        [0,0,0], [l1,0,0], [l1,l2,0], [0,l2,0],
        [0,0,h], [l1,0,h], [l1,l2,h], [0,l2,h]
    ])
    indices = [0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7, 0, 1, 5, 0, 5, 4, 1, 2, 6, 1, 6, 5, 2, 3, 7, 2, 7, 6, 3, 0, 4, 3, 4, 7]
    grond_poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
else:
    # L-vorm hoekpunten (6 onder, 6 boven)
    v_onder = [[0,0,0], [l1,0,0], [l1,dikte,0], [dikte,dikte,0], [dikte,l2,0], [0,l2,0]]
    v_boven = [[p[0], p[1], h] for p in v_onder]
    vertices = np.array(v_onder + v_boven)
    # Simpele triangulatie voor L-vorm (handmatig voor Mesh3d)
    indices = [0,1,2, 0,2,3, 0,3,5, 3,4,5, 6,7,8, 6,8,9, 6,9,11, 9,10,11] # Bodem & Top (versimpeld)
    grond_poly = np.array([[p[0], p[1]] for p in v_onder])

# --- VISUALISATIE: 2D PLAN (MATPLOTLIB) ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📋 2D Technisch Plan")
    fig1, ax1 = plt.subplots(figsize=(5, 5))
    ax1.add_patch(plt.Polygon(grond_poly, facecolor='#e0e0e0', edgecolor='black', lw=2, label="Steen"))
    
    # Teken X-snedes
    for i, px in enumerate(pos_x):
        y_max = l2 if (vorm_type.startswith("Steen") or px <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((px, 0), zaag_dikte, y_max, color='red', alpha=0.7))
        ax1.text(px + (zaag_dikte/2), y_max + 2, f"X{i+1}", color='red', ha='center', fontsize=9, weight='bold')

    # Teken Y-snedes
    for i, py in enumerate(pos_y):
        x_max = l1 if (vorm_type.startswith("Steen") or py <= dikte) else dikte
        ax1.add_patch(plt.Rectangle((0, py), x_max, zaag_dikte, color='red', alpha=0.7))
        ax1.text(x_max + 2, py + (zaag_dikte/2), f"Y{i+1}", color='red', va='center', fontsize=9, weight='bold')

    ax1.set_aspect('equal')
    ax1.axis('off')
    st.pyplot(fig1)

# --- VISUALISATIE: 3D INTERACTIEF (PLOTLY) ---
with col_right:
    st.subheader("📦 3D Inspectie")
    fig3d = go.Figure()

    # De Steen/Hoek zelf
    fig3d.add_trace(go.Mesh3d(
        x=vertices[:,0], y=vertices[:,1], z=vertices[:,2],
        i=indices[::3], j=indices[1::3], k=indices[2::3],
        color='lightblue', opacity=0.5, name="Steen"
    ))

    # Zaagvlakken toevoegen (als boxen voor volume)
    for px in pos_x:
        y_max = l2 if (vorm_type.startswith("Steen") or px <= dikte) else dikte
        fig3d.add_trace(go.Mesh3d(
            x=[px, px+zaag_dikte, px+zaag_dikte, px, px, px+zaag_dikte, px+zaag_dikte, px],
            y=[0, 0, y_max, y_max, 0, 0, y_max, y_max],
            z=[0, 0, 0, 0, h, h, h, h],
            i=[0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7], j=[1, 2, 3, 3, 0, 1, 5, 6, 7, 7, 4, 5], k=[2, 3, 0, 1, 2, 3, 6, 7, 4, 5, 6, 7],
            color='red', opacity=0.8, name=f"X-Cut"
        ))

    for py in pos_y:
        x_max = l1 if (vorm_type.startswith("Steen") or py <= dikte) else dikte
        fig3d.add_trace(go.Mesh3d(
            x=[0, x_max, x_max, 0, 0, x_max, x_max, 0],
            y=[py, py, py+zaag_dikte, py+zaag_dikte, py, py, py+zaag_dikte, py+zaag_dikte],
            z=[0, 0, 0, 0, h, h, h, h],
            i=[0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7], j=[1, 2, 3, 3, 0, 1, 5, 6, 7, 7, 4, 5], k=[2, 3, 0, 1, 2, 3, 6, 7, 4, 5, 6, 7],
            color='darkred', opacity=0.8, name=f"Y-Cut"
        ))

    fig3d.update_layout(
        scene=dict(aspectmode='data', xaxis_title='L1 (mm)', yaxis_title='L2 (mm)', zaxis_title='H (mm)'),
        margin=dict(l=0, r=0, b=0, t=0)
    )
    st.plotly_chart(fig3d, use_container_width=True)

# --- OVERZICHTSTABEL ---
st.divider()
st.subheader("📊 Zaag Specificaties")
data = {
    "Onderdeel": [f"X{i+1}" for i in range(len(pos_x))] + [f"Y{i+1}" for i in range(len(pos_y))],
    "Positie (mm)": pos_x + pos_y,
    "Type": ["Verticaal (X)"] * len(pos_x) + ["Horizontaal (Y)"] * len(pos_y)
}
st.table(data)
