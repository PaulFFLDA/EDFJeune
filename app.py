import io
import zipfile
import pandas as pd
import streamlit as st
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ---------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="AMS France Lutte",
    page_icon="🤼",
    layout="wide"
)

# Initialisation du st.session_state
if "proposals" not in st.session_state:
    st.session_state.proposals = {}

if "convocations" not in st.session_state:
    st.session_state.convocations = []

# Données d'exemple (Athlètes et Compétitions)
ATHLETES_DATA = [
    {"Nom": "GADIROV Said", "Catégorie poids": "74 kg", "Club": "Paris Lutte", "Statut": "Titulaire"},
    {"Nom": "LUKASZEWSKI Adam", "Catégorie poids": "86 kg", "Club": "Lyon Wrestling", "Statut": "Remplaçant"},
    {"Nom": "MOUSTAPHA Kouyaté", "Catégorie poids": "97 kg", "Club": "Nice Lutte", "Statut": "Titulaire"},
]

COMPETITIONS = [
    "Championnat d'Europe U23 - Zagreb 2026",
    "Grand Prix de France - Henri Deglane 2026",
    "Tournoi de Qualification Olympique 2026"
]

SELECTION_CRITERIA = [
    "Test physique validé",
    "Poids dans la catégorie cible",
    "Bilan médical conforme",
    "Règlement intérieur signé"
]

# ---------------------------------------------------------
# 2. LOGIQUE MÉTIER & FONCTIONS UTILITAIRES
# ---------------------------------------------------------
def create_convocation_pdf(conv_data):
    """Génère un document PDF de convocation en mémoire."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    styles = getSampleStyleSheet()
    story = []

    # En-tête
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=1,
        spaceAfter=20
    )
    story.append(Paragraph("<b>OFFICIEL — CONVOCATION EQUIPE DE FRANCE</b>", title_style))
    story.append(Spacer(1, 15))

    # Tableau des détails
    data = [
        ["Compétition :", conv_data.get("Compétition", "")],
        ["Athlète :", conv_data.get("Athlète", "")],
        ["Catégorie :", conv_data.get("Catégorie", "")],
        ["Statut :", conv_data.get("Statut", "")],
        ["Manager / Référent :", conv_data.get("Manager", "")],
        ["Remarques :", conv_data.get("Notes", "Aucune remarque spécifique.")],
    ]

    t = Table(data, colWidths=[150, 350])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F3F4F6")),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    
    story.append(t)
    doc.build(story)
    return buffer.getvalue()


def generate_all_convocations_zip(competition_name):
    """Génère une archive ZIP contenant tous les PDF des convocations pour une compétition."""
    zip_buffer = io.BytesIO()
    convocations = [c for c in st.session_state.convocations if c.get("Compétition") == competition_name]

    if not convocations:
        return None

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for conv in convocations:
            pdf_data = create_convocation_pdf(conv)
            filename = f"Convocation_{conv.get('Athlète', 'Lutteur').replace(' ', '_')}.pdf"
            zip_file.writestr(filename, pdf_data)

    return zip_buffer.getvalue()


def upsert_proposal(comp, athlete_name, manager, category, checks, notes):
    """Enregistre ou met à jour une étude de sélection."""
    key = f"{comp}___{athlete_name}"
    st.session_state.proposals[key] = {
        "Compétition": comp,
        "Athlète": athlete_name,
        "Manager": manager,
        "Catégorie": category,
        "Critères": checks,
        "Notes": notes,
        "Statut": "En étude"
    }


def validate_proposal(comp, athlete_name, status, manager, notes):
    """Valide ou refuse un athlète et génère la convocation si validé."""
    key = f"{comp}___{athlete_name}"
    if key in st.session_state.proposals:
        st.session_state.proposals[key]["Statut"] = status

    # Mise à jour ou ajout dans la liste globale des convocations
    st.session_state.convocations = [
        c for c in st.session_state.convocations
        if not (c["Compétition"] == comp and c["Athlète"] == athlete_name)
    ]

    st.session_state.convocations.append({
        "Compétition": comp,
        "Athlète": athlete_name,
        "Statut": status,
        "Manager": manager,
        "Notes": notes,
        "Catégorie": "Sélectionné"
    })

# ---------------------------------------------------------
# 3. INTERFACE UTILISATEUR STREAMLIT
# ---------------------------------------------------------
st.title("🤼 AMS France Lutte — Sélection & Convocations")

selected_comp = st.selectbox("🎯 Sélectionner une compétition :", COMPETITIONS)
manager_name = st.text_input("👤 Nom du Référent / Manager :", value="Entraîneur National")

st.divider()

st.subheader("1️⃣ Étude des candidatures")

for idx, athlete in enumerate(ATHLETES_DATA):
    name = athlete["Nom"]
    with st.expander(f"🤼 {name} ({athlete['Catégorie poids']}) — {athlete['Club']}"):
        
        checks = {}
        st.write("**Critères de sélection :**")
        for crit in SELECTION_CRITERIA:
            checks[crit] = st.checkbox(crit, key=f"chk_{selected_comp}_{name}_{crit}")

        notes = st.text_area(f"Remarques / Notes pour {name} :", key=f"notes_{selected_comp}_{name}")

        col_save, col_v1, col_v2 = st.columns([2, 1, 1])

        with col_save:
            if st.button("💾 Enregistrer l'étude", key=f"save_{idx}_{name}"):
                upsert_proposal(
                    selected_comp,
                    name,
                    manager_name,
                    athlete.get("Catégorie poids", ""),
                    checks,
                    notes
                )
                st.success(f"Étude enregistrée pour {name}.")
                st.rerun()

        with col_v1:
            if st.button("✅ Valider", key=f"val_{idx}_{name}"):
                validate_proposal(selected_comp, name, "Validé", manager_name, notes)
                st.success(f"{name} validé !")
                st.rerun()

        with col_v2:
            if st.button("❌ Refuser", key=f"ref_{idx}_{name}"):
                validate_proposal(selected_comp, name, "Refusé", manager_name, notes)
                st.warning(f"{name} refusé.")
                st.rerun()

# ---------------------------------------------------------
# 4. RÉCAPITULATIF & TÉLÉCHARGEMENT DES CONVOCATIONS
# ---------------------------------------------------------
st.divider()
st.subheader("2️⃣ Convocations générées")

comp_convocations = [c for c in st.session_state.convocations if c.get("Compétition") == selected_comp]

if not comp_convocations:
    st.info("Aucune convocation validée pour le moment pour cette compétition.")
else:
    # Exportation ZIP global
    zip_data = generate_all_convocations_zip(selected_comp)
    if zip_data:
        st.download_button(
            label="📦 Télécharger TOUTES les convocations de cette compétition (.ZIP)",
            data=zip_data,
            file_name=f"Convocations_{selected_comp.replace(' ', '_')}.zip",
            mime="application/zip",
            use_container_width=True
        )
        st.write("")

    # Téléchargement individuel
    for conv in comp_convocations:
        with st.expander(f"📄 Convocation PDF — {conv.get('Athlète')} ({conv.get('Statut')})"):
            pdf_bytes = create_convocation_pdf(conv)
            st.download_button(
                label=f"📥 Télécharger la convocation de {conv.get('Athlète')} (PDF)",
                data=pdf_bytes,
                file_name=f"Convocation_{conv.get('Athlète').replace(' ', '_')}.pdf",
                mime="application/pdf",
                key=f"dl_pdf_{conv.get('Athlète')}_{selected_comp}"
            )
