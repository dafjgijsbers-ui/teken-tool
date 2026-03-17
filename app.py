import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="DEKO Hoek-Editor", layout="wide")

# --- AFMETINGEN WAALFORMAAT ---
L = 210.0
B = 100.0
H = 50.0
D = 23.0 # Dikte van de steen/strip zelf

st.title("📐 DEKO Professionele Hoek-Editor")
st.write("Stel je zaagsnedes in voor een Waalformaat hoekstuk.")

# --- SIDEBAR: ZAAGINSTELLINGEN ---
st.sidebar.header("Zaag Instellingen")
zaag_dikte = st.sidebar.slider("Dikte zaagblad (mm)", 0.0, 5.0, 3.0, 0.5)

st.sidebar.subheader("Selecteer Zaagsnedes")
# Vier kanten selectie
z_links = st.sidebar.checkbox("Zaag van Links (Kop 1)")
if z_links:
    val_links = st.sidebar.number_input("Maat links (mm)", 5.0, L, 23.0)

z_rechts = st.sidebar.checkbox("Zaag van Rechts (Kop 2)")
if z_rechts:
    val_rechts = st.sidebar.number_input("Maat rechts (mm)", 5.0, L, 23.0)

z_boven = st.sidebar.checkbox("Zaag van Boven (Strek 1)")
if z_boven:
    val_boven = st.sidebar.number_input("Maat boven (mm)", 5.0, B, 23.0)

z_onder = st.sidebar.checkbox("Zaag van Onder (Strek 2)")
if z_onder:
    val_onder = st.sidebar.number_input("Maat onder (mm)", 5.0, B, 23.0)

# --- VISUALISATIE LOGICA ---
fig, ax = plt.subplots(figsize=(10, 6))

# 1. Teken de basis HOEK-vorm (L-vorm)
# Punten van de L-vorm (buitenom en binnenkant)
# (0,0) -> (L,0) -> (L,D) -> (D,D) -> (D,B) -> (0,B) -> back to (0,0)
hoek_x = [0, L, L, D, D, 0, 0]
hoek_y = [0, 0, D, D, B, B, 0]
ax.plot(hoek_x, hoek_y, color='black', linewidth=2)
ax.fill(hoek_x, hoek_y, color='lightgray', alpha=0.2, label="Basis Hoeksteen")

# 2. Functie om zaaglijnen en arcering te tekenen
def teken_zaag(positie, kant):
    if kant == "links":
        # Product deel (groen)
        ax.add_patch(plt.Rectangle((0, 0), positie, B, color='green', alpha=0.3))
        # Zaaggat (rood)
        ax.add_patch(plt.Rectangle((positie, 0), zaag_dikte, B, color='red', alpha=0.6))
        # Afval (arcering)
        ax.add_patch(plt.Rectangle((positie + zaag_dikte, 0), L - positie - zaag_dikte, B, hatch='///', fill=False, color='gray', alpha=0.3))
        ax.text(positie/2, -10, f"{positie}", color='green', fontweight='bold', ha='center')
        ax.text(positie + zaag_dikte/2, B + 5, f"{zaag_dikte}", color='red', fontsize=8, ha='center')

    elif kant == "rechts":
        start_x = L - positie
        ax.add_patch(plt.Rectangle((start_x, 0), positie, B, color='green', alpha=0.3))
        ax.add_patch(plt.Rectangle((start_x - zaag_dikte, 0), zaag_dikte, B, color='red', alpha=0.6))
        ax.add_patch(plt.Rectangle((0, 0), start_x - zaag_dikte, B, hatch='\\\\\\', fill=False, color='gray', alpha=0.3))
        ax.text(L - positie/2, -10, f"{positie}", color='green', fontweight='bold', ha='center')

    elif kant == "boven":
        start_y = B - positie
        ax.add_patch(plt.Rectangle((0, start_y), L, positie, color='green', alpha=0.2))
        ax.add_patch(plt.Rectangle((0, start_y - zaag_dikte), L, zaag_dikte, color='red', alpha=0.6))
        ax.add_patch(plt.Rectangle((0, 0), L, start_y - zaag_dikte, hatch='---', fill=False, color='gray', alpha=0.3))
        ax.text(-15, B - positie/2, f"{positie}", color='green', fontweight='bold', va='center', rotation=90)

    elif kant == "onder":
        ax.add_patch(plt.Rectangle((0, 0), L, positie, color='green', alpha=0.2))
        ax.add_patch(plt.Rectangle((0, positie), L, zaag_dikte, color='red', alpha=0.6))
        ax.add_patch(plt.Rectangle((0, positie + zaag_dikte), L, B - positie - zaag_dikte, hatch='|||', fill=False, color='gray', alpha=0.3))
        ax.text(-15, positie/2, f"{positie}", color='green', fontweight='bold', va='center', rotation=90)

# Toepassen van de geselecteerde zagingen
if z_links: teken_zaag(val_links, "links")
if z_rechts: teken_zaag(val_rechts, "rechts")
if z_boven: teken_zaag(val_boven, "boven")
if z_onder: teken_zaag(val_onder, "onder")

# Opmaak van de plot
ax.set_aspect('equal')
ax.set_xlim(-40, L + 40)
ax.set_ylim(-40, B + 40)
ax.axis('off')

# --- DISPLAY ---
col1, col2 = st.columns([3, 1])
with col1:
    st.pyplot(fig)

with col2:
    st.subheader("Details")
    st.write(f"**Basis:** Waalformaat Hoek")
    st.write(f"**Zaagblad:** {zaag_dikte} mm")
    st.divider()
    if z_links or z_rechts or z_boven or z_onder:
        st.success("Zaagplan actief")
        st.info("Groen = Product\nRood = Zaagsnede\nArcering = Afval")
    else:
        st.warning("Geen zaagsnedes geselecteerd.")
