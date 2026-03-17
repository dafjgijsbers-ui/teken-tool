import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="DEKO Zaag-Transformaties", layout="wide")

# --- DATA: ALLE VORMEN VAN DEKO.NU ---
TRANSFORMATIES = {
    "Strippen (2-zijdig)": {"basis": "Steen", "sneden": ["links", "rechts"], "omschrijving": "Haalt 2 strippen uit 1 volle steen."},
    "Strippen (1-zijdig)": {"basis": "Steen", "sneden": ["links"], "omschrijving": "Haalt 1 strip uit de strek."},
    "Hoeken": {"basis": "Hoek", "sneden": ["links", "onder"], "omschrijving": "Standaard L-vormige hoekstrip."},
    "Hoeken plat (kopbakje)": {"basis": "Hoek", "sneden": ["links", "rechts", "onder"], "omschrijving": "Hoek met extra inkorting."},
    "Sparren": {"basis": "Steen", "sneden": ["boven", "onder"], "omschrijving": "Zagen van de strekkanten (hoogte aanpassing)."},
    "Afkorten": {"basis": "Steen", "sneden": ["links", "rechts"], "omschrijving": "De steen op lengte zagen."},
    "Koppen": {"basis": "Steen", "sneden": ["links"], "omschrijving": "Zagen van de kopse kant."},
    "Kopstrippen": {"basis": "Steen", "sneden": ["kop_strip"], "omschrijving": "Dunne strips van de kopse kant."},
    "Zolen / Bakjes": {"basis": "Hoek", "sneden": ["onder"], "omschrijving": "Transformeren naar een U-vorm of zool."},
    "Kimstenen / Ytong": {"basis": "Blok", "sneden": ["onder", "boven"], "omschrijving": "Grote blokken op maat zagen."}
}

# --- SIDEBAR ---
st.sidebar.image("https://raw.githubusercontent.com/DennisDeko/teken-tool/main/deko_logo.jpg", width=150)
st.sidebar.header("Selecteer Transformatie")
keuze = st.sidebar.selectbox("Kies type:", list(TRANSFORMATIES.keys()))

st.sidebar.divider()
st.sidebar.write(f"**Info:** {TRANSFORMATIES[keuze]['omschrijving']}")

with st.sidebar.expander("Maten & Zaagblad", expanded=True):
    l_base = st.number_input("Basis Lengte (mm)", value=210)
    b_base = st.number_input("Basis Breedte (mm)", value=100)
    h_base = st.number_input("Basis Hoogte (mm)", value=50)
    dikte_zaag = st.slider("Zaagblad dikte (mm)", 0.0, 5.0, 3.0)

# --- ZAAGLIJNEN GENEREREN ---
actieve_sneden = {}
st.sidebar.subheader("Zaagmaten")
for kant in TRANSFORMATIES[keuze]["sneden"]:
    label = f"Maat {kant.capitalize()} (mm)"
    actieve_sneden[kant] = st.sidebar.number_input(label, min_value=1, max_value=210, value=23)

# --- VISUALISATIE ---
st.title(f"Plan: {keuze}")

fig, ax = plt.subplots(figsize=(10, 6))

# Basis tekenen
if TRANSFORMATIES[keuze]["basis"] == "Hoek":
    d_hoek = 23
    points = np.array([[0,0], [l_base,0], [l_base,d_hoek], [d_hoek,d_hoek], [d_hoek,b_base], [0,b_base], [0,0]])
    ax.plot(points[:,0], points[:,1], color='black', linewidth=2)
    ax.fill(points[:,0], points[:,1], color='lightgray', alpha=0.2)
else:
    rect = plt.Rectangle((0, 0), l_base, b_base, fill=None, edgecolor='black', linewidth=2)
    ax.add_patch(rect)

# Zaaglijnen tekenen met arcering
def draw_saw_effect(pos, side):
    if side == "links":
        # Product
        ax.add_patch(plt.Rectangle((0, 0), pos, b_base, color='green', alpha=0.3))
        # Zaaggat
        ax.add_patch(plt.Rectangle((pos, 0), dikte_zaag, b_base, color='red', alpha=0.7))
        # Afval
        ax.add_patch(plt.Rectangle((pos + dikte_zaag, 0), l_base - pos - dikte_zaag, b_base, hatch='///', fill=False, color='gray'))
    elif side == "rechts":
        # Product aan rechterkant
        ax.add_patch(plt.Rectangle((l_base - pos, 0), pos, b_base, color='green', alpha=0.3))
        # Zaaggat
        ax.add_patch(plt.Rectangle((l_base - pos - dikte_zaag, 0), dikte_zaag, b_base, color='red', alpha=0.7))
        # Afval (wordt complexer bij combi, maar we tekenen het gat)
        ax.text(l_base - pos/2, b_base/2, f"{pos}", ha='center', weight='bold')

for s_kant, s_pos in actieve_sneden.items():
    draw_saw_effect(s_pos, s_kant)

ax.set_aspect('equal')
ax.axis('off')
st.pyplot(fig)

# --- TABEL ---
st.divider()
st.subheader("📋 Productie Overzicht")
data = {"Onderdeel": ["Basis", "Zaagblad"], "Waarde": [f"{l_base}x{b_base}x{h_base} mm", f"{dikte_zaag} mm"]}
for k, v in actieve_sneden.items():
    data["Onderdeel"].append(f"Zaagsnede {k}")
    data["Waarde"].append(f"{v} mm")
st.table(data)
