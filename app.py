import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np

# --- 1. CONFIGURATIE ---
st.set_page_config(page_title="DEKO Maten Tool Pro", layout="wide")

# --- 2. LOGO EN TITEL ---
LOGO_URL = "https://raw.githubusercontent.com/DennisDeko/teken-tool/main/deko_logo.jpg"
col_logo, col_titel = st.columns([1, 4])
with col_logo:
    try:
        st.image(LOGO_URL, width=150)
    except:
        st.write("Tag: DEKO") # Fallback als logo niet laadt

with col_titel:
    st.title("DEKO Maatwerk Editor Pro")
    st.caption("Interactief zaagplan met 2D & 3D visualisatie")

# --- 3. SIDEBAR: INPUT ---
st.sidebar.header("📐 Afmetingen & Instellingen")
vorm_type = st.sidebar.selectbox("Type Steen", ["Steen (Rechthoek)", "Hoek (L-vorm)"])
zaag_dikte = st.sidebar.number_input("Zaagblad dikte (mm)", 0.0, 10.0, 3.0, step=0.5)

with st.sidebar.expander("Basis Maten", expanded=True):
    l1 = st.number_input("Lengte L1 (mm)", value=210.0)
    l2 = st.number_input("Breedte L2 (mm)", value=100.0)
    h = st.number_input("Hoogte H (mm)", value=50.0)
    dikte = st.number_input("Dikte D (mm)", value=23.0) if vorm_type == "Hoek (L-vorm)" else 0.0

with st.sidebar.expander("✂️ Zaaglijnen", expanded=True):
    ax = st.slider("Aantal X-snedes", 0, 4, 1)
    pos_x = [st.number_input(f"X{i+1}", value=23.0 + (i*50), key=f"x{i}") for i in range(ax)]
    st.divider()
    ay = st.slider("Aantal Y-snedes", 0, 4, 0)
    pos_y = [st.number_input(f"Y{i+1}", value=23.0 + (i*50), key=f"y{i}") for i in range(ay)]

# --- 4. GEOMETRIE ENGINE (Berekeningen) ---
def calculate_geometry():
    if vorm_type == "Steen (Rechthoek)":
        # Punten voor een rechthoekig blok
        v = np.array([[0,0,0], [l1,0,0], [l1,l2,0], [0,l2,0], [0,0,h], [l1,0,h], [l1,l2,h], [0,l2,h]])
        # Triangulatie indices voor Mesh3d
        i = [0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7, 0, 1, 5, 0, 5, 4, 1, 2, 6, 1, 6, 5, 2, 3, 7, 2, 7, 6, 3, 0, 4, 3, 4, 7]
        poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
    else:
        # Punten voor een L-vorm (6 onder, 6 boven)
        v_o = [[0,0,0], [l1,0,0], [l1,dikte,0], [dikte,dikte,0], [dikte,l2,0], [0,l2,0]]
        v = np.array(v_o + [[p[0], p[1], h] for p in v_o])
        i = [0,1,2, 0,2,3, 0,3,5, 3,4,5, 6,7,8, 6,8,9, 6,9,11, 9,10,11]
        poly = np.array([[p[0], p[1]] for p in v_o])
    return v, i, poly

vertices, indices, grond_poly = calculate_geometry()

# --- 5. VISUALISATIE (FRAGMENT) ---
@st.fragment
def show_visuals(vertices, indices, grond_poly, pos_x, pos_y):
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("📋 2D Technisch Plan")
        fig2d = plt.figure(figsize=(6, 6))
        ax2d = fig2d.add_subplot(111)
        
        # Basisvorm tekenen
        ax2d.add_patch(plt.Polygon(grond_poly, facecolor='#f0f0f0', edgecolor='black', lw=2))
        
        # X-zaaglijnen (Rood)
        for i, px in enumerate(pos_x):
            y_limit = l2 if (vorm_type.startswith("Steen") or px <= dikte) else dikte
            ax2d.add_patch(plt.Rectangle((px, 0), zaag_dikte, y_limit, color='red', alpha=0.6))
            ax2d.text(px + (zaag_dikte/2), y_limit + 5, f"X{i+1}", color='red', ha='center', weight='bold')
        
        # Y-zaaglijnen (Donkerrood)
        for i, py in enumerate(pos_y):
            x_limit = l1 if (vorm_type.startswith("Steen") or py <= dikte) else dikte
            ax2d.add_patch(plt.Rectangle((0, py), x_limit, zaag_dikte, color='darkred', alpha=0.6))
            ax2d.text(x_limit + 5, py + (zaag_dikte/2), f"Y{i+1}", color='darkred', va='center', weight='bold')
            
        ax2d.set_aspect('equal')
        ax2d.axis('off')
        st.pyplot(fig2d, clear_figure=True)

    with col_right:
        st.subheader("📦 3D Inspectie")
        fig3d = go.Figure()
        
        # De Steen zelf
        fig3d.add_trace(go.Mesh3d(
            x=vertices[:,0], y=vertices[:,1], z=vertices[:,2], 
            i=indices[::3], j=indices[1::3], k=indices[2::3], 
            color='lightblue', opacity=0.3, name="Materiaal"
        ))
        
        # Zaagvolumes toevoegen (X)
        for px in pos_x:
            y_lim = l2 if (vorm_type.startswith("Steen") or px <= dikte) else dikte
            fig3d.add_trace(go.Mesh3d(
                x=[px, px+zaag_dikte, px+zaag_dikte, px, px, px+zaag_dikte, px+zaag_dikte, px],
                y=[0, 0, y_lim, y_lim, 0, 0, y_lim, y_lim],
                z=[0, 0, 0, 0, h, h, h, h],
                i=[0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7], j=[1, 2, 3, 3, 0, 1, 5, 6, 7, 7, 4, 5], k=[2, 3, 0, 1, 2, 3, 6, 7, 4, 5, 6, 7],
                color='red', opacity=0.7
            ))

        # Zaagvolumes toevoegen (Y)
        for py in pos_y:
            x_lim = l1 if (vorm_type.startswith("Steen") or py <= dikte) else dikte
            fig3d.add_trace(go.Mesh3d(
                x=[0, x_lim, x_lim, 0, 0, x_lim, x_lim, 0],
                y=[py, py, py+zaag_dikte, py+zaag_dikte, py, py, py+zaag_dikte, py+zaag_dikte],
                z=[0, 0, 0, 0, h, h, h, h],
                i=[0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7], j=[1, 2, 3, 3, 0, 1, 5, 6, 7, 7, 4, 5], k=[2, 3, 0, 1, 2, 3, 6, 7, 4, 5, 6, 7],
                color='darkred', opacity=0.7
            ))

        fig3d.update_layout(
            scene=dict(aspectmode='data', xaxis_title='L1', yaxis_title='L2', zaxis_title='H'),
            margin=dict(l=0, r=0, b=0, t=0),
            height=500
        )
        st.plotly_chart(fig3d, use_container_width=True)

# Start de visualisatie
show_visuals(vertices, indices, grond_poly, pos_x, pos_y)

# --- 6. DATA OVERZICHT ---
st.divider()
st.subheader("📊 Zaag Specificaties")
if pos_x or pos_y:
    overzicht = []
    for i, x in enumerate(pos_x): overzicht.append({"ID": f"X{i+1}", "Positie (mm)": x, "Type": "Verticaal"})
    for i, y in enumerate(pos_y): overzicht.append({"ID": f"Y{i+1}", "Positie (mm)": y, "Type": "Horizontaal"})
    st.dataframe(overzicht, use_container_width=True)
else:
    st.info("Voeg zaaglijnen toe in de sidebar om de details te bekijken.")
