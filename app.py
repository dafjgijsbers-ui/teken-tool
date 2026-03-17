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
    st.caption("Geoptimaliseerd met @st.fragment voor betere prestaties")

# --- SIDEBAR: INPUT ---
st.sidebar.header("📐 Instellingen")
vorm_type = st.sidebar.selectbox("Type Steen", ["Steen (Rechthoek)", "Hoek (L-vorm)"])
zaag_dikte = st.sidebar.number_input("Zaagblad dikte (mm)", 0.0, 10.0, 3.0, step=0.5)

with st.sidebar.expander("Basis Afmetingen", expanded=True):
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

# --- GEOMETRIE BEREKENING (Buiten fragment voor data-consistentie) ---
def get_geometry():
    if vorm_type == "Steen (Rechthoek)":
        v = np.array([[0,0,0], [l1,0,0], [l1,l2,0], [0,l2,0], [0,0,h], [l1,0,h], [l1,l2,h], [0,l2,h]])
        i = [0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7, 0, 1, 5, 0, 5, 4, 1, 2, 6, 1, 6, 5, 2, 3, 7, 2, 7, 6, 3, 0, 4, 3, 4, 7]
        poly = np.array([[0,0], [l1,0], [l1,l2], [0,l2]])
    else:
        v_o = [[0,0,0], [l1,0,0], [l1,dikte,0], [dikte,dikte,0], [dikte,l2,0], [0,l2,0]]
        v = np.array(v_o + [[p[0], p[1], h] for p in v_o])
        i = [0,1,2, 0,2,3, 0,3,5, 3,4,5, 6,7,8, 6,8,9, 6,9,11, 9,10,11]
        poly = np.array([[p[0], p[1]] for p in v_o])
    return v, i, poly

vertices, indices, grond_poly = get_geometry()

# --- VISUALISATIE FRAGMENT ---
@st.fragment
def render_visuals(vertices, indices, grond_poly, pos_x, pos_y, zaag_dikte):
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("📋 2D Plan")
        fig2d, ax2d = plt.subplots(figsize=(5, 5))
        ax2d.add_patch(plt.Polygon(grond_poly, facecolor='#e0e0e0', edgecolor='black', lw=2))
        
        for i, px in enumerate(pos_x):
            y_m = l2 if (vorm_type.startswith("Steen") or px <= dikte) else dikte
            ax2d.add_patch(plt.Rectangle((px, 0), zaag_dikte, y_m, color='red', alpha=0.7))
        
        for i, py in enumerate(pos_y):
            x_m = l1 if (vorm_type.startswith("Steen") or py <= dikte) else dikte
            ax2d.add_patch(plt.Rectangle((0, py), x_m, zaag_dikte, color='darkred', alpha=0.7))
            
        ax2d.set_aspect('equal'); ax2d.axis('off')
        st.pyplot(fig2d)

    with col_right:
        st.subheader("📦 3D View")
        fig3d = go.Figure()
        fig3d.add_trace(go.Mesh3d(x=vertices[:,0], y=vertices[:,1], z=vertices[:,2], 
                                 i=indices[::3], j=indices[1::3], k=indices[2::3], 
                                 color='lightblue', opacity=0.4))
        
        # Voeg zaagsnedes toe als rode Mesh3d objecten
        for px in pos_x:
            y_m = l2 if (vorm_type.startswith("Steen") or px <= dikte) else dikte
            fig3d.add_trace(go.Mesh3d(x=[px, px+zaag_dikte, px+zaag_dikte, px, px, px+zaag_dikte, px+zaag_dikte, px],
                                     y=[0, 0, y_m, y_m, 0, 0, y_m, y_m],
                                     z=[0, 0, 0, 0, h, h, h, h],
                                     i=[0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7], j=[1, 2, 3, 3, 0, 1, 5, 6, 7, 7, 4, 5], k=[2, 3, 0, 1, 2, 3, 6, 7, 4, 5, 6, 7],
                                     color='red', opacity=0.8))

        fig3d.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0, r=0, b=0, t=0))
        st.plotly_chart(fig3d, use_container_width=True)

# Roep het fragment aan
render_visuals(vertices, indices, grond_poly, pos_x, pos_y, zaag_dikte)

# --- STATISTIEKEN (Buiten fragment) ---
st.divider()
st.subheader("📊 Zaaglijst")
if pos_x or pos_y:
    df = [{"Snede": f"X{i+1}", "Positie": p, "Richting": "Verticaal"} for i, p in enumerate(pos_x)] + \
         [{"Snede": f"Y{i+1}", "Positie": p, "Richting": "Horizontaal"} for i, p in enumerate(pos_y)]
    st.table(df)
