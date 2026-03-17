import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np

# --- 1. INITIALISATIE ---
st.set_page_config(page_title="DEKO Tool", layout="wide")

# --- 2. SIDEBAR (Buiten fragment voor stabiliteit) ---
st.sidebar.title("📐 Instellingen")
vorm = st.sidebar.selectbox("Vorm", ["Rechthoek", "L-vorm"])
l1 = st.sidebar.slider("Lengte L1", 100, 500, 210)
l2 = st.sidebar.slider("Breedte L2", 50, 300, 100)
h = st.sidebar.slider("Hoogte H", 10, 100, 50)

# --- 3. VISUALISATIE (Met @st.fragment voor snelheid) ---
@st.fragment
def render_visuals():
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 2D Plan")
        fig, ax = plt.subplots(figsize=(5, 5))
        # Teken een simpele basisvorm
        ax.add_patch(plt.Rectangle((0, 0), l1, l2, color='lightgrey', ec='black'))
        ax.set_aspect('equal')
        ax.axis('off')
        st.pyplot(fig, clear_figure=True)
        
    with col2:
        st.subheader("📦 3D Inspectie")
        # Simpele 3D mesh voor stabiliteitstest
        fig3d = go.Figure(data=[go.Mesh3d(
            x=[0, l1, l1, 0, 0, l1, l1, 0],
            y=[0, 0, l2, l2, 0, 0, l2, l2],
            z=[0, 0, 0, 0, h, h, h, h],
            i=[0, 1, 2, 0, 2, 3, 4, 5, 6, 4, 6, 7],
            j=[1, 2, 3, 3, 0, 1, 5, 6, 7, 7, 4, 5],
            k=[2, 3, 0, 1, 2, 3, 6, 7, 4, 5, 6, 7],
            color='lightblue', opacity=0.5
        )])
        fig3d.update_layout(margin=dict(l=0, r=0, b=0, t=0))
        
        # Gebruik width='stretch' zoals vereist in 2026 logs
        st.plotly_chart(fig3d, width='stretch')

# Uitvoeren
st.write("### DEKO Maatwerk Editor")
render_visuals()

# --- 4. DATA ---
st.divider()
st.info(f"Huidige selectie: {vorm} ({l1}x{l2}x{h} mm)")
