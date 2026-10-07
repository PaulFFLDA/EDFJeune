import io
import html
import zipfile
import urllib.request
from datetime import date, datetime

import pandas as pd
import streamlit as st

# Import optionnel sécurisé
try:
    from streamlit_sortables import sort_items
except ImportError:
    sort_items = None

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    HRFlowable,
)
from reportlab.lib.units import mm

# ============================================================
# CONFIGURATION ET STYLE
# ============================================================

st.set_page_config(
    page_title="France Lutte Jeunes",
    page_icon="🤼",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main { background-color: #f6f8fb; }
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
    .hero {
        padding: 1.6rem 2rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #172033, #263957);
        color: white;
        margin-bottom: 1.5rem;
    }
    .hero h1 { margin-bottom: 0.3rem; }
    .hero p { opacity: 0.85; margin-bottom: 0; }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e6eaf0;
        padding: 1rem;
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# IDENTITÉ VISUELLE FFLDA
# ============================================================

FFLDA_LOGO_SOURCE_URL = "https://www.fflutte.com/content/uploads/2021/10/3-1-1024x576.jpg"

@st.cache_data(ttl=86400, show_spinner=False)
def get_fflda_logo_bytes():
    """Télécharge et recadre le logo officiel pour l'application/PDF."""
    try:
        from PIL import Image
        req = urllib.request.Request(
            FFLDA_LOGO_SOURCE_URL, 
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read()
        image = Image.open(io.BytesIO(raw)).convert("RGB")
        width, height = image.size
        crop = image.crop((0, 0, width // 2, height // 2))
        out = io.BytesIO()
        crop.save(out, format="PNG", optimize=True)
        return out.getvalue()
    except Exception:
        return None

# ============================================================
# INITIALIZATION DU SESSION STATE
# ============================================================

if "athletes" not in st.session_state:
    st.session_state.athletes = [
        {
            "Nom": "Martin", "Prénom": "Lucas", "Club": "Club de Caen", "Style": "Lutte libre",
            "Catégorie": "U17 - 65 kg", "Catégorie poids": "65 kg", "Date de naissance": "2009-04-12",
            "Collectif": "France U17", "Entraîneur": "Thomas Dupont", "Objectif": "Championnats d'Europe U17"
        },
        {
            "Nom": "Durand", "Prénom": "Hugo", "Club": "Lutte Dijon", "Style": "Lutte libre",
            "Catégorie": "U20 - 74 kg", "Catégorie poids": "74 kg", "Date de naissance": "2007-08-21",
            "Collectif": "France U20", "Entraîneur": "Pierre Bernard", "Objectif": "Sélection internationale"
        }
    ]

if "competitions" not in st.session_state:
    st.session_state.competitions = [
        {"Athlète": "Lucas Martin", "Date": "2026-09-12", "Compétition": "TNR Paris", "Catégorie": "65 kg"},
        {"Athlète": "Lucas Martin", "Date": "2026-09-20", "Compétition": "Championnat de France", "Catégorie": "65 kg"},
        {"Athlète": "Hugo Durand", "Date": "2026-09-20", "Compétition": "TNR Paris", "Catégorie": "74 kg"}
    ]

if "selection_proposals" not in st.session_state:
    st.session_state.selection_proposals = []

if "convocations" not in st.session_state:
    st.session_state.convocations = []

if "selection_criteria" not in st.session_state:
    st.session_state.selection_criteria = [
        "Résultats sportifs",
        "Évaluation technique / référent",
        "État de forme et préparation",
        "Adéquation catégorie / poids",
        "Engagement et assiduité",
        "Disponibilité pour la compétition",
    ]

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def athlete_names():
    return [f"{a.get('Prénom', '')} {a.get('Nom', '')}".strip() for a in st.session_state.athletes]

def get_athlete(full_name):
    for a in st.session_state.athletes:
        if f"{a.get('Prénom', '')} {a.get('Nom', '')}".strip() == full_name:
            return a
    return None

def competition_names():
    return sorted(set(
        str(x.get("Compétition", "")).strip()
        for x in st.session_state.competitions
        if str(x.get("Compétition", "")).strip()
    ))

def get_proposals_for_competition(competition):
    return [x for x in st.session_state.selection_proposals if x.get("Compétition") == competition]

def get_proposal(competition, athlete_name):
    for x in st.session_state.selection_proposals:
        if x.get("Compétition") == competition and x.get("Athlète") == athlete_name:
            return x
    return None

def get_convocation(competition, athlete_name):
    for x in st.session_state.convocations:
        if x.get("Compétition") == competition and x.get("Athlète") == athlete_name:
            return x
    return None

def upsert_proposal(competition, athlete_name, proposer, category, criteria_ok, criteria_notes=""):
    existing = get_proposal(competition, athlete_name)
    payload = {
        "Proposée par": proposer,
        "Catégorie": category,
        "Critères": criteria_ok,
        "Observations critères": criteria_notes,
        "Date proposition": str(date.today()),
        "Statut": "Éligible — à valider" if all(criteria_ok.values()) else "Non conforme aux critères",
    }
    if existing:
        existing.update(payload)
    else:
        st.session_state.selection_proposals.append({
            "Compétition": competition,
            "Athlète": athlete_name,
            **payload,
            "Décision": "", "Commission": "", "Date décision": "", "Motif": ""
        })

def create_direct_convocation(competition, athlete_name, manager="Manager / Sélectionneur"):
    existing = get_convocation(competition, athlete_name)
    athlete = get_athlete(athlete_name) or {}
    category = athlete.get("Catégorie poids", athlete.get("Catégorie", ""))

    if existing:
        existing["Catégorie"] = category
        existing["Signature manager"] = manager
        return existing

    convocation = {
        "Athlète": athlete_name,
        "Compétition": competition,
        "Catégorie": category,
        "Statut": "Brouillon",
        "Date création": str(date.today()),
        "Signature manager": manager,
    }
    st.session_state.convocations.append(convocation)
    return convocation

# ============================================================
# RENDU DU MODULE SÉLECTION & CONVOCATIONS
# ============================================================

def render_convocations_module(mode="manager"):
    is_manager = mode == "manager"
    st.markdown("""
    <div class="hero">
        <h1>📨 Sélection & convocations</h1>
        <p>Le manager choisit les lutteurs selon les critères applicables, valide la sélection puis édite les convocations PDF.</p>
    </div>
    """, unsafe_allow_html=True)

    logo = get_fflda_logo_bytes()
    if logo:
        st.image(logo, width=190)

    competitions = competition_names()
    if not competitions:
        st.warning("Aucune compétition enregistrée.")
        return

    selected_comp = st.selectbox("Compétition", competitions, key=f"convocation_competition_{mode}")

    proposals = get_proposals_for_competition(selected_comp)
    validated = [x for x in proposals if x.get("Statut") == "Validé"]
    pending = [x for x in proposals if x.get("Statut") == "Éligible — à valider"]
    rejected = [x for x in proposals if x.get("Statut") in ("Refusé", "Non conforme aux critères")]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lutteurs étudiés", len(proposals))
    c2.metric("À valider", len(pending))
    c3.metric("Validés", len(validated))
    c4.metric("Non retenus", len(rejected))

    if is_manager:
        st.subheader("1️⃣ Choisir les lutteurs à convoquer")
        names = athlete_names()
        selected_athletes = st.multiselect(
            "Lutteurs candidats",
            names,
            default=[x["Athlète"] for x in proposals],
            help="Le manager peut sélectionner plusieurs lutteurs puis vérifier les critères individuellement.",
        )
        manager_name = st.text_input("Nom du manager", value="Manager / Sélectionneur", key="manager_name")

        for idx, name in enumerate(selected_athletes):
            athlete = get_athlete(name) or {}
            existing = get_proposal(selected_comp, name) or {}
            with st.expander(f"🤼 {name} — {athlete.get('Style', '')} — {athlete.get('Catégorie poids', '')}", expanded=True):
                criteria = existing.get("Critères", {})
                checks = {}
                cols = st.columns(2)
                for cidx, criterion in enumerate(st.session_state.selection_criteria):
                    default = bool(criteria.get(criterion, False))
                    with cols[cidx % 2]:
                        checks[criterion] = st.checkbox(criterion, value=default, key=f"crit_{selected_comp}_{name}_{cidx}")
                notes = st.text_area(
                    "Observations du manager",
                    value=existing.get("Observations critères", ""),
                    key=f"criteria_notes_{idx}_{name}",
                )
                if st.button("💾 Enregistrer l'étude de ce lutteur", key=f"save_candidate_{idx}_{name}"):
                    upsert_proposal(
                        selected_comp,
                        name,
                        manager_name,
                        athlete.get("Catégorie poids", athlete.get("Catégorie", "")),
                        checks,
                        notes,
                    )
                    st.success(f"Étude enregistrée pour {name}.")
                    st.rerun()

# Lancement de l'application
if __name__ == "__main__":
    render_convocations_module(mode="manager")
