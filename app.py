import streamlit as st
import pandas as pd
from datetime import date, datetime
import io
import zipfile
import html
import urllib.request

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable
from reportlab.lib.units import mm

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="France Lutte Jeunes",
    page_icon="🤼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# IDENTITÉ VISUELLE FFLDA / FRANCE LUTTE
# ============================================================

# Image officielle publiée par la FFLDA lors du déploiement de son
# identité visuelle. Le visuel contient plusieurs déclinaisons du logo ;
# le code recadre automatiquement la déclinaison claire sur fond blanc.
FFLDA_LOGO_SOURCE_URL = (
    "https://www.fflutte.com/content/uploads/2021/10/3-1-1024x576.jpg"
)


@st.cache_data(ttl=86400, show_spinner=False)
def get_fflda_logo_bytes():
    """Télécharge et recadre le logo officiel pour l'application/PDF."""
    try:
        from PIL import Image

        with urllib.request.urlopen(FFLDA_LOGO_SOURCE_URL, timeout=10) as response:
            raw = response.read()
        image = Image.open(io.BytesIO(raw)).convert("RGB")
        width, height = image.size
        # Le logo France Lutte sur fond blanc est dans le quart supérieur gauche.
        crop = image.crop((0, 0, width // 2, height // 2))
        out = io.BytesIO()
        crop.save(out, format="PNG", optimize=True)
        return out.getvalue()
    except Exception:
        return None


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f6f8fb;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 1.6rem 2rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #172033, #263957);
        color: white;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        margin-bottom: 0.3rem;
    }

    .hero p {
        opacity: 0.85;
        margin-bottom: 0;
    }

    .section-card {
        background: white;
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid #e6eaf0;
        margin-bottom: 1rem;
    }

    .criterion-card {
        background: white;
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid #e6eaf0;
        min-height: 130px;
    }

    .status-green {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        padding: 0.8rem;
        border-radius: 12px;
    }

    .status-orange {
        background: #fffbeb;
        border: 1px solid #fde68a;
        padding: 0.8rem;
        border-radius: 12px;
    }

    .status-blue {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 0.8rem;
        border-radius: 12px;
    }

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
# DONNÉES DE BASE
# ============================================================

if "athletes" not in st.session_state:
    st.session_state.athletes = [
        {
            "Nom": "Martin",
            "Prénom": "Lucas",
            "Club": "Club de Caen",
            "Style": "Lutte libre",
            "Catégorie": "U17 - 65 kg",
            "Catégorie poids": "65 kg",
            "Date de naissance": "2009-04-12",
            "Collectif": "France U17",
            "Entraîneur": "Thomas Dupont",
            "Objectif": "Championnats d'Europe U17",
            "Points forts": "Explosivité, lutte debout, rythme",
            "Axes progression": "Défense au sol, gestion des fins de combat",
            "Observation": "Très bonne progression depuis le début de saison.",
        },
        {
            "Nom": "Durand",
            "Prénom": "Hugo",
            "Club": "Lutte Dijon",
            "Style": "Lutte libre",
            "Catégorie": "U20 - 74 kg",
            "Catégorie poids": "74 kg",
            "Date de naissance": "2007-08-21",
            "Collectif": "France U20",
            "Entraîneur": "Pierre Bernard",
            "Objectif": "Sélection internationale",
            "Points forts": "Technique, contrôle, endurance",
            "Axes progression": "Puissance et attaque première intention",
            "Observation": "Profil intéressant pour le collectif national.",
        },
        {
            "Nom": "Leroy",
            "Prénom": "Nathan",
            "Club": "Lutte Rouen",
            "Style": "Lutte gréco-romaine",
            "Catégorie": "U15 - 57 kg",
            "Catégorie poids": "57 kg",
            "Date de naissance": "2011-02-17",
            "Collectif": "France U15",
            "Entraîneur": "Marc Petit",
            "Objectif": "Championnat de France",
            "Points forts": "Mobilité, vitesse",
            "Axes progression": "Défense et force générale",
            "Observation": "Jeune lutteur en progression.",
        },
    ]

# ============================================================
# COMPÉTITIONS
# ============================================================

if "competitions" not in st.session_state:
    st.session_state.competitions = [
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-09-12",
            "Compétition": "TNR Paris",
            "Type": "TNR / Ranking national",
            "Catégorie": "65 kg",
            "Combats": 4,
            "Victoires": 3,
            "Défaites": 1,
            "Classement": "2e",
            "Bilan": "Très bien",
            "Résumé": "Bonne compétition. Très bon comportement dans les phases debout.",
            "Opposition": "Opposition nationale importante",
        },
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-09-20",
            "Compétition": "Championnat de France",
            "Type": "Championnat de France",
            "Catégorie": "65 kg",
            "Combats": 5,
            "Victoires": 4,
            "Défaites": 1,
            "Classement": "3e",
            "Bilan": "Très bien",
            "Résumé": "Bonne maîtrise de la compétition.",
            "Opposition": "Niveau national",
        },
        {
            "Athlète": "Hugo Durand",
            "Date": "2026-09-20",
            "Compétition": "TNR Paris",
            "Type": "TNR / Ranking national",
            "Catégorie": "74 kg",
            "Combats": 5,
            "Victoires": 3,
            "Défaites": 2,
            "Classement": "5e",
            "Bilan": "Bien",
            "Résumé": "Bonne intensité mais manque de régularité sur les fins de combat.",
            "Opposition": "Opposition nationale",
        },
    ]

# ============================================================
# POIDS
# ============================================================

if "weight_log" not in st.session_state:
    st.session_state.weight_log = [
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-08-20",
            "Poids": 66.2,
        },
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-09-01",
            "Poids": 65.7,
        },
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-09-12",
            "Poids": 65.1,
        },
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-09-20",
            "Poids": 65.0,
        },
        {
            "Athlète": "Hugo Durand",
            "Date": "2026-08-20",
            "Poids": 75.3,
        },
        {
            "Athlète": "Hugo Durand",
            "Date": "2026-09-20",
            "Poids": 74.4,
        },
    ]

# ============================================================
# TESTS PHYSIQUES
# ============================================================

if "tests" not in st.session_state:
    st.session_state.tests = [
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-08-20",
            "Test": "Saut vertical",
            "Valeur": 48,
            "Unité": "cm",
        },
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-09-15",
            "Test": "Saut vertical",
            "Valeur": 51,
            "Unité": "cm",
        },
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-08-20",
            "Test": "Pompes 1 min",
            "Valeur": 42,
            "Unité": "rép.",
        },
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-09-15",
            "Test": "Pompes 1 min",
            "Valeur": 48,
            "Unité": "rép.",
        },
    ]

# ============================================================
# CALENDRIER
# ============================================================

if "calendar" not in st.session_state:
    st.session_state.calendar = [
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-10-05",
            "Type": "Préparation physique",
            "Intitulé": "Force / puissance",
            "Objectif": "Développer l'explosivité",
        },
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-10-12",
            "Type": "Stage national",
            "Intitulé": "Stage national U17",
            "Objectif": "Préparation internationale",
        },
        {
            "Athlète": "Hugo Durand",
            "Date": "2026-10-08",
            "Type": "Compétition",
            "Intitulé": "Tournoi international",
            "Objectif": "Évaluation internationale",
        },
    ]

# ============================================================
# ÉVALUATIONS DES RÉFÉRENTS
# ============================================================

if "evaluations_selection" not in st.session_state:
    st.session_state.evaluations_selection = [
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-09-21",
            "Référent": "Référent U17",
            "Période": "Après TNR / Championnat de France",
            "Résultats": "3e au Championnat de France et 2e au TNR.",
            "Opposition": "Opposition nationale significative.",
            "Stabilité catégorie": "65 kg sur les principales compétitions.",
            "Expérience": "Expérience régulière sur les compétitions nationales.",
            "Progression": "Progression intéressante depuis le début de saison.",
            "Attitude": "Très bonne attitude.",
            "Engagement": "Engagement régulier dans les stages.",
            "Investissement": "Investissement satisfaisant dans le projet.",
            "Observation": "À suivre sur les prochaines échéances internationales.",
        }
    ]

# ============================================================
# PROJETS DE PERFORMANCE
# ============================================================

if "projets_performance" not in st.session_state:
    st.session_state.projets_performance = [
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-09-01",
            "Objectif principal": "Championnats d'Europe U17",
            "Objectifs intermédiaires": "Progresser sur la défense au sol et stabiliser la catégorie 65 kg.",
            "Objectif technique": "Défense et contre-attaque",
            "Objectif physique": "Développer explosivité et puissance",
            "Objectif tactique": "Mieux gérer les fins de combat",
            "Compétitions prioritaires": "TNR + Championnat de France + tournoi international",
            "Engagement lutteur": "Participation régulière et suivi du travail individuel",
            "Bilan": "Projet en cours de construction.",
        }
    ]

# ============================================================
# STAGES
# ============================================================

if "stages" not in st.session_state:
    st.session_state.stages = [
        {
            "Nom": "Stage national U17",
            "Date début": "2026-10-12",
            "Date fin": "2026-10-16",
            "Style": "Lutte libre",
            "Catégorie âge": "U17",
            "Lieu": "INSEP",
            "Objectif": "Préparation internationale",
        }
    ]


# ============================================================
# CONVOCATIONS / SÉLECTION MANAGER
# ============================================================

if "selection_proposals" not in st.session_state:
    st.session_state.selection_proposals = []

if "selection_commissions" not in st.session_state:
    st.session_state.selection_commissions = []

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
# FONCTIONS SÉLECTION / CONVOCATION
# ============================================================


def competition_names():
    return sorted(set(
        str(x.get("Compétition", "")).strip()
        for x in st.session_state.competitions
        if str(x.get("Compétition", "")).strip()
    ))


def get_proposals_for_competition(competition):
    return [
        x for x in st.session_state.selection_proposals
        if x.get("Compétition") == competition
    ]


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
            "Décision": "",
            "Commission": "",
            "Date décision": "",
            "Motif": "",
        })


def validate_proposal(competition, athlete_name, decision, manager, motif=""):
    proposal = get_proposal(competition, athlete_name)
    if not proposal:
        return

    proposal["Décision"] = decision
    proposal["Commission"] = manager
    proposal["Date décision"] = str(date.today())
    proposal["Motif"] = motif
    proposal["Statut"] = "Validé" if decision == "Validé" else "Refusé"

    if decision == "Validé":
        athlete = get_athlete(athlete_name) or {}
        existing = get_convocation(competition, athlete_name)
        if existing:
            existing["Catégorie"] = proposal.get("Catégorie", athlete.get("Catégorie poids", ""))
        else:
            st.session_state.convocations.append({
                "Athlète": athlete_name,
                "Compétition": competition,
                "Catégorie": proposal.get("Catégorie", athlete.get("Catégorie poids", "")),
                "Statut": "Brouillon",
                "Date création": str(date.today()),
                "Date envoi": "",
                "Réponse": "",
                "Date réponse": "",
                "Motif réponse": "",
                "Lieu": "",
                "Date début": "",
                "Date fin": "",
                "Heure rendez-vous": "",
                "Lieu rendez-vous": "",
                "Transport": "",
                "Hébergement": "",
                "Accompagnateur": "",
                "Informations": "",
                "Signature manager": manager,
            })


def create_convocation_pdf(convocation):
    """Produit un PDF A4 officiel avec logo et données personnalisées."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"Convocation - {convocation.get('Athlète', '')}",
        author="France Lutte / Athlete Management System",
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "ConvTitle", parent=styles["Title"], fontSize=21, leading=25,
        textColor=colors.HexColor("#172033"), alignment=TA_CENTER, spaceAfter=5,
    )
    subtitle = ParagraphStyle(
        "ConvSub", parent=styles["Normal"], fontSize=9.5, leading=12,
        textColor=colors.HexColor("#526174"), alignment=TA_CENTER, spaceAfter=12,
    )
    heading = ParagraphStyle(
        "ConvHeading", parent=styles["Heading2"], fontSize=12.5, leading=15,
        textColor=colors.HexColor("#172033"), spaceBefore=10, spaceAfter=6,
    )
    body = ParagraphStyle(
        "ConvBody", parent=styles["BodyText"], fontSize=9.5, leading=13,
        textColor=colors.HexColor("#172033"),
    )

    def ptext(value):
        return html.escape(str(value or "")).replace("\n", "<br/>")

    story = []
    logo = get_fflda_logo_bytes()
    if logo:
        story.append(RLImage(io.BytesIO(logo), width=45 * mm, height=28 * mm, kind="proportional"))
        story.append(Spacer(1, 2 * mm))
    else:
        story.append(Paragraph("FRANCE LUTTE — FFLDA", title))

    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#172033"), spaceAfter=10))
    story.append(Paragraph("CONVOCATION OFFICIELLE", title))
    story.append(Paragraph("Fédération Française de Lutte et Disciplines Associées", subtitle))

    athlete = get_athlete(convocation.get("Athlète", "")) or {}
    athlete_name = f"{athlete.get('Prénom', '')} {athlete.get('Nom', '')}".strip()

    story.append(Paragraph("ATHLÈTE CONVOQUÉ", heading))
    athlete_rows = [
        [Paragraph("Nom / prénom", body), Paragraph(ptext(athlete_name), body)],
        [Paragraph("Club", body), Paragraph(ptext(athlete.get("Club", "")), body)],
        [Paragraph("Style", body), Paragraph(ptext(athlete.get("Style", "")), body)],
        [Paragraph("Catégorie de poids", body), Paragraph(ptext(convocation.get("Catégorie", "")), body)],
    ]
    table = Table(athlete_rows, colWidths=[50 * mm, 118 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f4f8")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#d8dee8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e3e7ed")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)

    story.append(Paragraph("COMPÉTITION", heading))
    comp_rows = [
        [Paragraph("Compétition", body), Paragraph(ptext(convocation.get("Compétition", "")), body)],
        [Paragraph("Lieu", body), Paragraph(ptext(convocation.get("Lieu", "")), body)],
        [Paragraph("Période", body), Paragraph(ptext(f"Du {convocation.get('Date début', '')} au {convocation.get('Date fin', '')}"), body)],
        [Paragraph("Rendez-vous", body), Paragraph(ptext(f"{convocation.get('Heure rendez-vous', '')} — {convocation.get('Lieu rendez-vous', '')}"), body)],
    ]
    table = Table(comp_rows, colWidths=[50 * mm, 118 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f4f8")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#d8dee8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e3e7ed")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)

    story.append(Paragraph("ORGANISATION", heading))
    org_rows = [
        [Paragraph("Transport", body), Paragraph(ptext(convocation.get("Transport", "")), body)],
        [Paragraph("Hébergement", body), Paragraph(ptext(convocation.get("Hébergement", "")), body)],
        [Paragraph("Accompagnateur", body), Paragraph(ptext(convocation.get("Accompagnateur", "")), body)],
    ]
    table = Table(org_rows, colWidths=[50 * mm, 118 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f4f8")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#d8dee8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e3e7ed")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)

    story.append(Paragraph("INFORMATIONS PRATIQUES", heading))
    story.append(Paragraph(ptext(convocation.get("Informations", "")), body))
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(
        "La présente convocation est établie à la suite de la validation de la sélection par le manager.",
        subtitle,
    ))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(ptext(f"Manager : {convocation.get('Signature manager', '')}"), body))

    doc.build(story)
    return buffer.getvalue()


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

    # Configuration des critères : ils sont volontairement configurables car le fichier source
    # ne contient pas une liste officielle détaillée de critères par compétition.
    if is_manager:
        with st.expander("⚙️ Critères de sélection — configuration du manager", expanded=True):
            st.caption("Les critères ci-dessous sont configurables dans l'application. Ils doivent être alignés avec les critères fédéraux applicables à votre compétition.")
            criteria_text = st.text_area(
                "Un critère par ligne",
                value="\n".join(st.session_state.selection_criteria),
                key="criteria_editor",
                height=150,
            )
            if st.button("💾 Enregistrer les critères", key="save_criteria"):
                st.session_state.selection_criteria = [x.strip() for x in criteria_text.splitlines() if x.strip()]
                st.success("Critères mis à jour.")
                st.rerun()

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

        if selected_athletes:
            st.subheader("2️⃣ Validation du manager")
            for idx, proposal in enumerate(get_proposals_for_competition(selected_comp)):
                if proposal.get("Athlète") not in selected_athletes:
                    continue
                all_ok = all(proposal.get("Critères", {}).get(c, False) for c in st.session_state.selection_criteria)
                if all_ok and proposal.get("Statut") != "Validé":
                    st.success(f"{proposal['Athlète']} respecte tous les critères configurés.")
                    if st.button("✅ Valider et créer la convocation", key=f"manager_validate_{idx}"):
                        validate_proposal(selected_comp, proposal["Athlète"], "Validé", manager_name, proposal.get("Observations critères", ""))
                        st.rerun()
                elif not all_ok:
                    st.warning(f"{proposal['Athlète']} ne respecte pas encore tous les critères : la convocation est bloquée.")

    st.subheader("3️⃣ Édition des convocations PDF")
    comp_convocations = [
        x for x in st.session_state.convocations
        if x.get("Compétition") == selected_comp
    ]

    if comp_convocations:
        for idx, conv in enumerate(comp_convocations):
            with st.expander(f"{conv['Athlète']} — {conv.get('Statut','Brouillon')}", expanded=False):
                if is_manager:
                    with st.form(f"conv_form_{mode}_{idx}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            lieu = st.text_input("Lieu", value=conv.get("Lieu", ""))
                            debut = st.text_input("Date début", value=conv.get("Date début", ""))
                            fin = st.text_input("Date fin", value=conv.get("Date fin", ""))
                            heure = st.text_input("Heure de rendez-vous", value=conv.get("Heure rendez-vous", ""))
                            rdv = st.text_input("Lieu de rendez-vous", value=conv.get("Lieu rendez-vous", ""))
                        with c2:
                            transport = st.text_input("Transport", value=conv.get("Transport", ""))
                            hotel = st.text_input("Hébergement", value=conv.get("Hébergement", ""))
                            accompagnateur = st.text_input("Accompagnateur", value=conv.get("Accompagnateur", ""))
                            infos = st.text_area("Informations pratiques", value=conv.get("Informations", ""), height=140)
                        if st.form_submit_button("💾 Enregistrer la convocation", type="primary"):
                            conv.update({
                                "Lieu": lieu, "Date début": debut, "Date fin": fin,
                                "Heure rendez-vous": heure, "Lieu rendez-vous": rdv,
                                "Transport": transport, "Hébergement": hotel,
                                "Accompagnateur": accompagnateur, "Informations": infos,
                                "Signature manager": manager_name,
                            })
                            st.success("Convocation enregistrée.")
                            st.rerun()

                pdf_data = create_convocation_pdf(conv)
                st.download_button(
                    "📄 Télécharger la convocation PDF",
                    data=pdf_data,
                    file_name=f"convocation_{conv['Athlète'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    type="primary",
                    key=f"pdf_{mode}_{idx}",
                )

                if is_manager and conv.get("Statut") == "Brouillon":
                    if st.button("📤 Marquer comme envoyée", key=f"send_{mode}_{idx}"):
                        conv["Statut"] = "Envoyée"
                        conv["Date envoi"] = str(date.today())
                        st.rerun()
    else:
        st.info("Aucune convocation. Elle est créée uniquement après validation des critères par le manager.")

    if is_manager and comp_convocations:
        st.subheader("4️⃣ Publipostage PDF")
        ready = [x for x in comp_convocations if x.get("Statut") in ("Brouillon", "Envoyée")]
        if ready:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for conv in ready:
                    zf.writestr(
                        f"convocation_{conv['Athlète'].replace(' ', '_')}.pdf",
                        create_convocation_pdf(conv),
                    )
            st.download_button(
                "📦 Générer toutes les convocations PDF",
                data=zip_buffer.getvalue(),
                file_name=f"convocations_{selected_comp.replace(' ', '_')}.zip",
                mime="application/zip",
                type="primary",
            )

    if mode == "athlete":
        mine = [x for x in comp_convocations if x.get("Athlète") == st.session_state.get("athlete")]
        if not mine:
            st.info("Aucune convocation pour votre profil.")
        else:
            for idx, conv in enumerate(mine):
                st.info(f"Statut : {conv.get('Statut', '')}")
                if conv.get("Statut") == "Envoyée":
                    st.download_button(
                        "📄 Télécharger ma convocation PDF",
                        data=create_convocation_pdf(conv),
                        file_name=f"convocation_{conv['Athlète'].replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key=f"athlete_pdf_{idx}",
                    )
                    if st.button("✅ J'accepte la convocation", key=f"accept_{idx}"):
                        conv["Réponse"] = "Acceptée"
                        conv["Date réponse"] = str(date.today())
                        st.rerun()
                    if st.button("❌ Je refuse la convocation", key=f"decline_{idx}"):
                        conv["Réponse"] = "Refusée"
                        conv["Date réponse"] = str(date.today())
                        st.rerun()

def athlete_names():
    return [
        f"{a['Prénom']} {a['Nom']}"
        for a in st.session_state.athletes
    ]


def get_athlete(full_name):
    for athlete in st.session_state.athletes:
        if f"{athlete['Prénom']} {athlete['Nom']}" == full_name:
            return athlete

    return None


def stats_for(full_name):

    competitions = [
        x
        for x in st.session_state.competitions
        if x["Athlète"] == full_name
    ]

    matches = sum(
        int(x["Combats"])
        for x in competitions
    )

    wins = sum(
        int(x["Victoires"])
        for x in competitions
    )

    losses = sum(
        int(x["Défaites"])
        for x in competitions
    )

    podiums = 0

    for x in competitions:

        ranking = str(
            x["Classement"]
        ).lower()

        if ranking.startswith(
            ("1", "2", "3")
        ):
            podiums += 1

    return {
        "competitions": len(competitions),
        "matches": matches,
        "wins": wins,
        "losses": losses,
        "podiums": podiums,
    }


def competition_summary(full_name):

    competitions = [
        x
        for x in st.session_state.competitions
        if x["Athlète"] == full_name
    ]

    if not competitions:
        return {
            "tnr": 0,
            "france": 0,
            "international": 0,
        }

    return {
        "tnr": sum(
            1 for x in competitions
            if x["Type"] == "TNR / Ranking national"
        ),
        "france": sum(
            1 for x in competitions
            if x["Type"] == "Championnat de France"
        ),
        "international": sum(
            1 for x in competitions
            if x["Type"] == "Tournoi international"
        ),
    }


def selection_data_for(full_name):

    evaluations = [
        x
        for x in st.session_state.evaluations_selection
        if x["Athlète"] == full_name
    ]

    projects = [
        x
        for x in st.session_state.projets_performance
        if x["Athlète"] == full_name
    ]

    competitions = [
        x
        for x in st.session_state.competitions
        if x["Athlète"] == full_name
    ]

    stages_nationaux = [
        x
        for x in st.session_state.calendar
        if x["Athlète"] == full_name
        and x["Type"] == "Stage national"
    ]

    return {
        "evaluations": evaluations,
        "projects": projects,
        "competitions": competitions,
        "stages_nationaux": stages_nationaux,
    }


# ============================================================
# FICHE ATHLÈTE
# ============================================================

def render_athlete_sheet(
    full_name,
    editable=False,
    show_selection=True,
):

    athlete = get_athlete(full_name)

    if athlete is None:
        st.error("Lutteur introuvable.")
        return

    stats = stats_for(full_name)

    st.markdown(
        f"""
        <div class="hero">
            <h1>🤼 {athlete['Prénom']} {athlete['Nom']}</h1>
            <p>
                {athlete['Club']} ·
                {athlete['Style']} ·
                {athlete['Catégorie']} ·
                {athlete['Collectif']}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # INDICATEURS
    # --------------------------------------------------------

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Compétitions",
        stats["competitions"]
    )

    c2.metric(
        "Combats",
        stats["matches"]
    )

    c3.metric(
        "Victoires",
        stats["wins"]
    )

    c4.metric(
        "Défaites",
        stats["losses"]
    )

    c5.metric(
        "Podiums",
        stats["podiums"]
    )

    st.divider()

    # --------------------------------------------------------
    # INFORMATIONS
    # --------------------------------------------------------

    st.subheader("👤 Informations générales")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Club :** {athlete['Club']}"
        )

        st.write(
            f"**Style :** {athlete['Style']}"
        )

        st.write(
            f"**Catégorie :** {athlete['Catégorie']}"
        )

        st.write(
            f"**Date de naissance :** "
            f"{athlete['Date de naissance']}"
        )

    with col2:

        st.write(
            f"**Collectif :** {athlete['Collectif']}"
        )

        st.write(
            f"**Entraîneur :** {athlete['Entraîneur']}"
        )

        st.write(
            f"**Objectif :** {athlete['Objectif']}"
        )

    # --------------------------------------------------------
    # PROFIL SPORTIF
    # --------------------------------------------------------

    st.subheader("🎯 Profil sportif")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            '<div class="criterion-card">'
            '<b>Points forts</b><br><br>'
            f"{athlete['Points forts']}"
            "</div>",
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            '<div class="criterion-card">'
            '<b>Axes de progression</b><br><br>'
            f"{athlete['Axes progression']}"
            "</div>",
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            '<div class="criterion-card">'
            '<b>Observation</b><br><br>'
            f"{athlete['Observation']}"
            "</div>",
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # SÉLECTION ÉQUIPE DE FRANCE
    # --------------------------------------------------------

    if show_selection:

        render_selection_module(
            full_name,
            editable=editable,
        )

    # --------------------------------------------------------
    # COMPÉTITIONS
    # --------------------------------------------------------

    st.subheader("🏆 Résultats en compétition")

    competitions = [
        x
        for x in st.session_state.competitions
        if x["Athlète"] == full_name
    ]

    if competitions:

        df_comp = pd.DataFrame(
            competitions
        )

        st.dataframe(
            df_comp[
                [
                    "Date",
                    "Compétition",
                    "Type",
                    "Catégorie",
                    "Combats",
                    "Victoires",
                    "Défaites",
                    "Classement",
                    "Bilan",
                    "Opposition",
                    "Résumé",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "Aucun résultat enregistré."
        )

    # --------------------------------------------------------
    # POIDS
    # --------------------------------------------------------

    st.subheader("⚖️ Évolution du poids")

    weights = [
        x
        for x in st.session_state.weight_log
        if x["Athlète"] == full_name
    ]

    if weights:

        df_weight = pd.DataFrame(
            weights
        )

        df_weight["Date"] = pd.to_datetime(
            df_weight["Date"]
        )

        df_weight = df_weight.sort_values(
            "Date"
        )

        chart = df_weight.set_index(
            "Date"
        )

        st.line_chart(
            chart["Poids"],
            height=280,
        )

        last_weight = chart["Poids"].iloc[-1]
        first_weight = chart["Poids"].iloc[0]

        evolution = (
            last_weight - first_weight
        )

        c1, c2 = st.columns(2)

        c1.metric(
            "Poids actuel",
            f"{last_weight:.1f} kg"
        )

        c2.metric(
            "Évolution",
            f"{evolution:+.1f} kg"
        )

    else:

        st.info(
            "Aucune donnée de poids."
        )

    # --------------------------------------------------------
    # TESTS
    # --------------------------------------------------------

    st.subheader(
        "🧪 Évolution des tests physiques"
    )

    athlete_tests = [
        x
        for x in st.session_state.tests
        if x["Athlète"] == full_name
    ]

    if athlete_tests:

        test_names = sorted(
            list(
                set(
                    x["Test"]
                    for x in athlete_tests
                )
            )
        )

        selected_test = st.selectbox(
            "Test à afficher",
            test_names,
            key=f"test_{full_name}",
        )

        filtered_tests = [
            x
            for x in athlete_tests
            if x["Test"] == selected_test
        ]

        df_test = pd.DataFrame(
            filtered_tests
        )

        df_test["Date"] = pd.to_datetime(
            df_test["Date"]
        )

        df_test = df_test.sort_values(
            "Date"
        )

        st.line_chart(
            df_test.set_index("Date")["Valeur"],
            height=280,
        )

    else:

        st.info(
            "Aucun test physique enregistré."
        )

    # --------------------------------------------------------
    # CALENDRIER
    # --------------------------------------------------------

    st.subheader(
        "📅 Prochaines échéances"
    )

    calendar = [
        x
        for x in st.session_state.calendar
        if x["Athlète"] == full_name
    ]

    if calendar:

        df_calendar = pd.DataFrame(
            calendar
        )

        df_calendar["Date"] = pd.to_datetime(
            df_calendar["Date"]
        )

        st.dataframe(
            df_calendar.sort_values("Date"),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "Aucune échéance programmée."
        )

    # --------------------------------------------------------
    # ÉDITION FICHE
    # --------------------------------------------------------

    if editable:

        st.divider()

        st.subheader(
            "✏️ Modifier la fiche"
        )

        with st.form(
            f"edit_athlete_{full_name}"
        ):

            col1, col2 = st.columns(2)

            with col1:

                new_club = st.text_input(
                    "Club",
                    athlete["Club"],
                )

                new_style = st.selectbox(
                    "Style",
                    [
                        "Lutte libre",
                        "Lutte gréco-romaine",
                        "Lutte féminine",
                    ],
                    index=[
                        "Lutte libre",
                        "Lutte gréco-romaine",
                        "Lutte féminine",
                    ].index(
                        athlete["Style"]
                    ),
                )

                new_category = st.text_input(
                    "Catégorie",
                    athlete["Catégorie"],
                )

                new_weight_category = st.text_input(
                    "Catégorie de poids",
                    athlete["Catégorie poids"],
                )

                new_coach = st.text_input(
                    "Entraîneur",
                    athlete["Entraîneur"],
                )

            with col2:

                new_collective = st.text_input(
                    "Collectif",
                    athlete["Collectif"],
                )

                new_objective = st.text_input(
                    "Objectif",
                    athlete["Objectif"],
                )

                new_strengths = st.text_area(
                    "Points forts",
                    athlete["Points forts"],
                )

                new_progression = st.text_area(
                    "Axes de progression",
                    athlete["Axes progression"],
                )

                new_observation = st.text_area(
                    "Observation",
                    athlete["Observation"],
                )

            submitted = st.form_submit_button(
                "💾 Enregistrer",
                type="primary",
                use_container_width=True,
            )

            if submitted:

                athlete["Club"] = new_club
                athlete["Style"] = new_style
                athlete["Catégorie"] = new_category
                athlete["Catégorie poids"] = new_weight_category
                athlete["Entraîneur"] = new_coach
                athlete["Collectif"] = new_collective
                athlete["Objectif"] = new_objective
                athlete["Points forts"] = new_strengths
                athlete["Axes progression"] = new_progression
                athlete["Observation"] = new_observation

                st.success(
                    "Fiche mise à jour."
                )

                st.rerun()


# ============================================================
# MODULE SÉLECTION ÉQUIPE DE FRANCE
# ============================================================

def render_selection_module(
    full_name,
    editable=False,
):

    athlete = get_athlete(full_name)

    data = selection_data_for(
        full_name
    )

    competitions = data["competitions"]
    evaluations = data["evaluations"]
    projects = data["projects"]
    stages = data["stages_nationaux"]

    summary = competition_summary(
        full_name
    )

    st.divider()

    st.markdown(
        """
        <div class="hero">
            <h1>🇫🇷 Sélection Équipe de France</h1>
            <p>
            Synthèse des éléments d'évaluation du projet
            de performance
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Cette page rassemble les éléments prévus dans "
        "les critères d'évaluation. Elle ne produit pas "
        "automatiquement une décision de sélection."
    )

    # --------------------------------------------------------
    # SYNTHÈSE
    # --------------------------------------------------------

    st.subheader(
        "📊 Synthèse de la saison"
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "TNR",
        summary["tnr"]
    )

    c2.metric(
        "Championnats de France",
        summary["france"]
    )

    c3.metric(
        "International",
        summary["international"]
    )

    c4.metric(
        "Stages nationaux",
        len(stages)
    )

    c5.metric(
        "Évaluations référent",
        len(evaluations)
    )

    # --------------------------------------------------------
    # CRITÈRES
    # --------------------------------------------------------

    st.subheader(
        "📋 Critères d'évaluation"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"""
            <div class="criterion-card">
            <b>🏆 Résultats nationaux</b><br><br>
            TNR enregistrés : {summary['tnr']}<br>
            Championnat de France :
            {summary['france']}<br>
            Expérience compétitive :
            {len(competitions)} compétition(s)
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        st.markdown(
            f"""
            <div class="criterion-card">
            <b>⚖️ Stabilité de catégorie</b><br><br>
            Catégorie de référence :
            <b>{athlete['Catégorie poids']}</b><br><br>
            Les catégories utilisées en compétition
            sont consultables dans l'historique.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        st.markdown(
            f"""
            <div class="criterion-card">
            <b>🌍 Expérience internationale</b><br><br>
            Tournois internationaux enregistrés :
            <b>{summary['international']}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            f"""
            <div class="criterion-card">
            <b>📈 Dynamique de progression</b><br><br>
            Évaluations disponibles :
            <b>{len(evaluations)}</b><br><br>
            Les observations successives permettent
            de suivre l'évolution du lutteur.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        st.markdown(
            f"""
            <div class="criterion-card">
            <b>🤝 Attitude / engagement</b><br><br>
            Évaluations référent disponibles :
            <b>{len(evaluations)}</b><br><br>
            Les appréciations sont conservées dans
            l'historique.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        st.markdown(
            f"""
            <div class="criterion-card">
            <b>🎯 Projet de performance</b><br><br>
            Projet enregistré :
            <b>{"Oui" if projects else "Non"}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # HISTORIQUE DES COMPÉTITIONS NATIONALES
    # --------------------------------------------------------

    st.subheader(
        "🏆 Résultats TNR / Championnat de France"
    )

    national_competitions = [
        x
        for x in competitions
        if x["Type"] in [
            "TNR / Ranking national",
            "Championnat de France",
        ]
    ]

    if national_competitions:

        df = pd.DataFrame(
            national_competitions
        )

        st.dataframe(
            df[
                [
                    "Date",
                    "Compétition",
                    "Type",
                    "Catégorie",
                    "Combats",
                    "Victoires",
                    "Défaites",
                    "Classement",
                    "Opposition",
                    "Résumé",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "Aucun résultat national enregistré."
        )

    # --------------------------------------------------------
    # INTERNATIONAL
    # --------------------------------------------------------

    st.subheader(
        "🌍 Expérience internationale"
    )

    international = [
        x
        for x in competitions
        if x["Type"] == "Tournoi international"
    ]

    if international:

        st.dataframe(
            pd.DataFrame(
                international
            ),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "Aucun tournoi international enregistré."
        )

    # --------------------------------------------------------
    # ÉVALUATIONS RÉFÉRENTS
    # --------------------------------------------------------

    st.subheader(
        "👁️ Évaluations des référents"
    )

    if evaluations:

        for index, evaluation in enumerate(
            evaluations
        ):

            with st.expander(
                f"{evaluation['Date']} — "
                f"{evaluation['Référent']} — "
                f"{evaluation['Période']}"
            ):

                c1, c2 = st.columns(2)

                with c1:

                    st.markdown(
                        "**Résultats**"
                    )

                    st.write(
                        evaluation["Résultats"]
                    )

                    st.markdown(
                        "**Opposition rencontrée**"
                    )

                    st.write(
                        evaluation["Opposition"]
                    )

                    st.markdown(
                        "**Stabilité de catégorie**"
                    )

                    st.write(
                        evaluation[
                            "Stabilité catégorie"
                        ]
                    )

                    st.markdown(
                        "**Expérience**"
                    )

                    st.write(
                        evaluation["Expérience"]
                    )

                with c2:

                    st.markdown(
                        "**Dynamique de progression**"
                    )

                    st.write(
                        evaluation["Progression"]
                    )

                    st.markdown(
                        "**Attitude**"
                    )

                    st.write(
                        evaluation["Attitude"]
                    )

                    st.markdown(
                        "**Engagement**"
                    )

                    st.write(
                        evaluation["Engagement"]
                    )

                    st.markdown(
                        "**Investissement**"
                    )

                    st.write(
                        evaluation["Investissement"]
                    )

                st.markdown(
                    "**Observation du référent**"
                )

                st.info(
                    evaluation["Observation"]
                )

    else:

        st.info(
            "Aucune évaluation de référent enregistrée."
        )

    # --------------------------------------------------------
    # AJOUT ÉVALUATION
    # --------------------------------------------------------

    if editable:

        st.divider()

        st.subheader(
            "➕ Ajouter une évaluation"
        )

        with st.form(
            f"selection_evaluation_{full_name}"
        ):

            col1, col2 = st.columns(2)

            with col1:

                eval_date = st.date_input(
                    "Date",
                    value=date.today(),
                )

                referent = st.text_input(
                    "Référent"
                )

                period = st.selectbox(
                    "Période d'évaluation",
                    [
                        "Après stage national",
                        "Après TNR",
                        "Après Championnat de France",
                        "Après tournoi international",
                        "Après stage international",
                        "Bilan de saison",
                    ],
                )

                results = st.text_area(
                    "Résultats"
                )

                opposition = st.text_area(
                    "Opposition rencontrée"
                )

                category_stability = st.text_area(
                    "Stabilité et pertinence "
                    "de la catégorie"
                )

                experience = st.text_area(
                    "Expérience de compétition antérieure"
                )

            with col2:

                progression = st.text_area(
                    "Dynamique de progression"
                )

                attitude = st.text_area(
                    "Attitude"
                )

                engagement = st.text_area(
                    "Engagement"
                )

                investment = st.text_area(
                    "Investissement dans le projet "
                    "de performance individuel"
                )

                observation = st.text_area(
                    "Observation du référent"
                )

            submit = st.form_submit_button(
                "💾 Enregistrer l'évaluation",
                type="primary",
                use_container_width=True,
            )

            if submit:

                st.session_state.evaluations_selection.append(
                    {
                        "Athlète": full_name,
                        "Date": str(eval_date),
                        "Référent": referent,
                        "Période": period,
                        "Résultats": results,
                        "Opposition": opposition,
                        "Stabilité catégorie":
                            category_stability,
                        "Expérience": experience,
                        "Progression": progression,
                        "Attitude": attitude,
                        "Engagement": engagement,
                        "Investissement": investment,
                        "Observation": observation,
                    }
                )

                st.success(
                    "Évaluation enregistrée."
                )

                st.rerun()

    # --------------------------------------------------------
    # PROJET DE PERFORMANCE
    # --------------------------------------------------------

    st.subheader(
        "🎯 Projet de performance individuel"
    )

    if projects:

        latest_project = projects[-1]

        c1, c2 = st.columns(2)

        with c1:

            st.markdown(
                "**Objectif principal**"
            )

            st.info(
                latest_project[
                    "Objectif principal"
                ]
            )

            st.markdown(
                "**Objectifs intermédiaires**"
            )

            st.write(
                latest_project[
                    "Objectifs intermédiaires"
                ]
            )

            st.markdown(
                "**Compétitions prioritaires**"
            )

            st.write(
                latest_project[
                    "Compétitions prioritaires"
                ]
            )

        with c2:

            st.markdown(
                "**Objectif technique**"
            )

            st.write(
                latest_project[
                    "Objectif technique"
                ]
            )

            st.markdown(
                "**Objectif physique**"
            )

            st.write(
                latest_project[
                    "Objectif physique"
                ]
            )

            st.markdown(
                "**Objectif tactique**"
            )

            st.write(
                latest_project[
                    "Objectif tactique"
                ]
            )

        st.markdown(
            "**Engagement du lutteur**"
        )

        st.write(
            latest_project[
                "Engagement lutteur"
            ]
        )

        st.markdown(
            "**Bilan**"
        )

        st.info(
            latest_project["Bilan"]
        )

    else:

        st.info(
            "Aucun projet de performance enregistré."
        )

    # --------------------------------------------------------
    # AJOUT PROJET
    # --------------------------------------------------------

    if editable:

        with st.expander(
            "➕ Créer / mettre à jour le projet de performance"
        ):

            with st.form(
                f"project_{full_name}"
            ):

                project_date = st.date_input(
                    "Date",
                    value=date.today(),
                )

                objective_main = st.text_input(
                    "Objectif principal"
                )

                intermediate = st.text_area(
                    "Objectifs intermédiaires"
                )

                technical = st.text_area(
                    "Objectif technique"
                )

                physical = st.text_area(
                    "Objectif physique"
                )

                tactical = st.text_area(
                    "Objectif tactique"
                )

                priority_competitions = st.text_area(
                    "Compétitions prioritaires"
                )

                athlete_commitment = st.text_area(
                    "Engagement du lutteur"
                )

                project_review = st.text_area(
                    "Bilan / point d'étape"
                )

                submit = st.form_submit_button(
                    "💾 Enregistrer le projet",
                    type="primary",
                    use_container_width=True,
                )

                if submit:

                    st.session_state.projets_performance.append(
                        {
                            "Athlète": full_name,
                            "Date": str(project_date),
                            "Objectif principal":
                                objective_main,
                            "Objectifs intermédiaires":
                                intermediate,
                            "Objectif technique":
                                technical,
                            "Objectif physique":
                                physical,
                            "Objectif tactique":
                                tactical,
                            "Compétitions prioritaires":
                                priority_competitions,
                            "Engagement lutteur":
                                athlete_commitment,
                            "Bilan":
                                project_review,
                        }
                    )

                    st.success(
                        "Projet enregistré."
                    )

                    st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🤼 France Lutte Jeunes"
)

st.sidebar.caption(
    "Athlete Management System"
)

_sidebar_logo = get_fflda_logo_bytes()
if _sidebar_logo:
    st.sidebar.image(_sidebar_logo, width=150)

role = st.sidebar.selectbox(
    "Profil utilisateur",
    [
        "Lutteur / Lutteuse",
        "Entraîneur / Club",
        "Manager / Sélectionneur",
        "Sélectionneur / Référent",
        "Administration",
    ],
)

# ============================================================
# LUTTEUR
# ============================================================

if role == "Lutteur / Lutteuse":

    athlete = st.sidebar.selectbox(
        "Mon profil",
        athlete_names(),
    )

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Tableau de bord",
            "📋 Ma fiche récap",
            "🇫🇷 Mon suivi Équipe de France",
            "📅 Mon calendrier",
            "🏆 Mes compétitions",
            "📨 Mes convocations",
            "⚖️ Mon poids",
            "🧪 Mes tests",
        ],
    )

# ============================================================
# CLUB
# ============================================================

elif role == "Entraîneur / Club":

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Tableau de bord",
            "👥 Mes lutteurs",
            "📋 Fiches lutteurs",
            "🇫🇷 Suivi sélection",
            "🏆 Compétitions",
            "📨 Convocations",
            "🧪 Tests physiques",
            "📅 Calendrier",
        ],
    )

# ============================================================
# MANAGER
# ============================================================

elif role == "Manager / Sélectionneur":

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Tableau de bord",
            "🎯 Sélection & critères",
            "📨 Convocations & commission",
            "🏆 Compétitions",
            "📋 Fiches lutteurs",
        ],
    )

# ============================================================
# SÉLECTIONNEUR
# ============================================================

elif role == "Sélectionneur / Référent":

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Tableau national",
            "🇫🇷 Sélection Équipe de France",
            "👥 Collectifs",
            "📋 Fiches lutteurs",
            "👁️ Évaluations référents",
            "🎯 Projets de performance",
            "📅 Planning national",
            "🏕️ Stages",
            "🏆 Compétitions",
            "📨 Convocations & commission",
            "🧪 Tests physiques",
        ],
    )

# ============================================================
# ADMIN
# ============================================================

else:

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Administration",
            "👥 Lutteurs",
            "📋 Fiches",
            "🇫🇷 Sélection Équipe de France",
            "📊 Statistiques",
            "📅 Planning",
            "📨 Convocations & commission",
        ],
    )


# ============================================================
# DASHBOARD LUTTEUR
# ============================================================

if page == "🏠 Tableau de bord":

    if role == "Manager / Sélectionneur":
        st.markdown("""
        <div class="hero">
          <h1>🎯 Espace Manager</h1>
          <p>Sélection des lutteurs selon les critères et gestion des convocations.</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("Utilisez « Sélection & critères » pour étudier les lutteurs, valider la sélection et générer les convocations PDF.")

    elif role == "Lutteur / Lutteuse":

        st.markdown(
            """
            <div class="hero">
                <h1>🤼 Mon espace sportif</h1>
                <p>
                Suivi individuel de la saison
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        stats = stats_for(athlete)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Compétitions",
            stats["competitions"]
        )

        c2.metric(
            "Combats",
            stats["matches"]
        )

        c3.metric(
            "Victoires",
            stats["wins"]
        )

        c4.metric(
            "Podiums",
            stats["podiums"]
        )

        athlete_data = get_athlete(
            athlete
        )

        st.subheader(
            "🎯 Mon objectif"
        )

        st.info(
            athlete_data["Objectif"]
        )

        st.subheader(
            "🇫🇷 Suivi Équipe de France"
        )

        summary = competition_summary(
            athlete
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "TNR",
            summary["tnr"]
        )

        c2.metric(
            "Championnat de France",
            summary["france"]
        )

        c3.metric(
            "International",
            summary["international"]
        )


# ============================================================
# FICHE LUTTEUR
# ============================================================

elif page == "📋 Ma fiche récap":

    render_athlete_sheet(
        athlete,
        editable=True,
        show_selection=True,
    )


# ============================================================
# SUIVI EDF LUTTEUR
# ============================================================

elif page == "🇫🇷 Mon suivi Équipe de France":

    render_selection_module(
        athlete,
        editable=False,
    )


# ============================================================
# CALENDRIER LUTTEUR
# ============================================================

elif page == "📅 Mon calendrier":

    st.title(
        "📅 Mon calendrier"
    )

    with st.form(
        "new_calendar"
    ):

        event_date = st.date_input(
            "Date",
            value=date.today(),
        )

        event_type = st.selectbox(
            "Type",
            [
                "Compétition",
                "Stage national",
                "Stage international",
                "Entraînement",
                "Préparation physique",
                "Test",
                "Récupération",
            ],
        )

        title = st.text_input(
            "Intitulé"
        )

        objective = st.text_area(
            "Objectif"
        )

        submit = st.form_submit_button(
            "Ajouter",
            type="primary",
        )

        if submit:

            st.session_state.calendar.append(
                {
                    "Athlète": athlete,
                    "Date": str(event_date),
                    "Type": event_type,
                    "Intitulé": title,
                    "Objectif": objective,
                }
            )

            st.success(
                "Événement ajouté."
            )

            st.rerun()

    data = [
        x
        for x in st.session_state.calendar
        if x["Athlète"] == athlete
    ]

    if data:

        df = pd.DataFrame(data)

        df["Date"] = pd.to_datetime(
            df["Date"]
        )

        st.dataframe(
            df.sort_values("Date"),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# COMPÉTITIONS LUTTEUR
# ============================================================

elif page == "🏆 Mes compétitions":

    st.title(
        "🏆 Mes compétitions"
    )

    with st.form(
        "competition_report"
    ):

        competition_date = st.date_input(
            "Date",
            value=date.today(),
        )

        competition_name = st.text_input(
            "Compétition"
        )

        competition_type = st.selectbox(
            "Type",
            [
                "TNR / Ranking national",
                "Championnat de France",
                "Tournoi international",
                "Autre compétition",
            ],
        )

        category = st.text_input(
            "Catégorie"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            matches = st.number_input(
                "Nombre de combats",
                min_value=0,
                step=1,
            )

        with col2:

            wins = st.number_input(
                "Victoires",
                min_value=0,
                step=1,
            )

        with col3:

            losses = st.number_input(
                "Défaites",
                min_value=0,
                step=1,
            )

        ranking = st.text_input(
            "Résultat / classement"
        )

        opposition = st.text_area(
            "Opposition rencontrée"
        )

        assessment = st.selectbox(
            "Bilan général",
            [
                "Difficile",
                "Moyen",
                "Bien",
                "Très bien",
            ],
        )

        summary = st.text_area(
            "Résumé"
        )

        submit = st.form_submit_button(
            "💾 Enregistrer",
            type="primary",
            use_container_width=True,
        )

        if submit:

            st.session_state.competitions.append(
                {
                    "Athlète": athlete,
                    "Date": str(
                        competition_date
                    ),
                    "Compétition":
                        competition_name,
                    "Type":
                        competition_type,
                    "Catégorie":
                        category,
                    "Combats":
                        matches,
                    "Victoires":
                        wins,
                    "Défaites":
                        losses,
                    "Classement":
                        ranking,
                    "Bilan":
                        assessment,
                    "Résumé":
                        summary,
                    "Opposition":
                        opposition,
                }
            )

            st.success(
                "Compte-rendu enregistré."
            )

            st.rerun()


# ============================================================
# POIDS
# ============================================================

elif page == "⚖️ Mon poids":

    st.title(
        "⚖️ Mon suivi du poids"
    )

    with st.form(
        "weight_form"
    ):

        weight_date = st.date_input(
            "Date",
            value=date.today(),
        )

        weight = st.number_input(
            "Poids (kg)",
            min_value=0.0,
            max_value=200.0,
            value=65.0,
            step=0.1,
        )

        submit = st.form_submit_button(
            "Ajouter",
            type="primary",
        )

        if submit:

            st.session_state.weight_log.append(
                {
                    "Athlète": athlete,
                    "Date": str(
                        weight_date
                    ),
                    "Poids": weight,
                }
            )

            st.success(
                "Poids enregistré."
            )

            st.rerun()

    weights = [
        x
        for x in st.session_state.weight_log
        if x["Athlète"] == athlete
    ]

    if weights:

        df = pd.DataFrame(
            weights
        )

        df["Date"] = pd.to_datetime(
            df["Date"]
        )

        st.line_chart(
            df.sort_values(
                "Date"
            ).set_index("Date")[
                "Poids"
            ],
            height=350,
        )


# ============================================================
# TESTS
# ============================================================

elif page == "🧪 Mes tests":

    st.title(
        "🧪 Mes tests physiques"
    )

    with st.form(
        "test_form"
    ):

        test_date = st.date_input(
            "Date",
            value=date.today(),
        )

        test_name = st.text_input(
            "Test"
        )

        value = st.number_input(
            "Valeur",
            value=0.0,
        )

        unit = st.text_input(
            "Unité"
        )

        submit = st.form_submit_button(
            "Ajouter",
            type="primary",
        )

        if submit:

            st.session_state.tests.append(
                {
                    "Athlète": athlete,
                    "Date": str(
                        test_date
                    ),
                    "Test": test_name,
                    "Valeur": value,
                    "Unité": unit,
                }
            )

            st.success(
                "Test enregistré."
            )

            st.rerun()


# ============================================================
# CLUB
# ============================================================

elif page == "👥 Mes lutteurs":

    st.title(
        "👥 Mes lutteurs"
    )

    st.dataframe(
        pd.DataFrame(
            st.session_state.athletes
        ),
        use_container_width=True,
        hide_index=True,
    )


elif page == "📋 Fiches lutteurs":

    st.title(
        "📋 Fiches lutteurs"
    )

    selected = st.selectbox(
        "Lutteur",
        athlete_names(),
    )

    render_athlete_sheet(
        selected,
        editable=True,
        show_selection=True,
    )


elif page == "🇫🇷 Suivi sélection":

    st.title(
        "🇫🇷 Suivi Équipe de France"
    )

    selected = st.selectbox(
        "Lutteur",
        athlete_names(),
    )

    render_selection_module(
        selected,
        editable=True,
    )


elif page == "🏆 Compétitions":

    st.title(
        "🏆 Compétitions"
    )

    st.dataframe(
        pd.DataFrame(
            st.session_state.competitions
        ),
        use_container_width=True,
        hide_index=True,
    )


elif page == "🧪 Tests physiques":

    st.title(
        "🧪 Tests physiques"
    )

    st.dataframe(
        pd.DataFrame(
            st.session_state.tests
        ),
        use_container_width=True,
        hide_index=True,
    )


elif page == "📅 Calendrier":

    st.title(
        "📅 Calendrier"
    )

    st.dataframe(
        pd.DataFrame(
            st.session_state.calendar
        ),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# SÉLECTIONNEUR
# ============================================================

elif page == "🏠 Tableau national":

    st.markdown(
        """
        <div class="hero">
            <h1>🇫🇷 Tableau national</h1>
            <p>
            Suivi des collectifs jeunes
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Lutteurs",
        len(
            st.session_state.athletes
        )
    )

    c2.metric(
        "Compétitions",
        len(
            st.session_state.competitions
        )
    )

    c3.metric(
        "Évaluations",
        len(
            st.session_state.evaluations_selection
        )
    )

    c4.metric(
        "Projets",
        len(
            st.session_state.projets_performance
        )
    )

    st.subheader(
        "👥 Collectif national"
    )

    df = pd.DataFrame(
        st.session_state.athletes
    )

    st.dataframe(
        df[
            [
                "Prénom",
                "Nom",
                "Style",
                "Club",
                "Catégorie",
                "Collectif",
                "Objectif",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# SÉLECTION EDF
# ============================================================

elif page == "🇫🇷 Sélection Équipe de France":

    st.markdown(
        """
        <div class="hero">
            <h1>🇫🇷 Sélection Équipe de France</h1>
            <p>
            Suivi des éléments d'évaluation des collectifs
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Cette interface permet aux référents de consulter "
        "les résultats, les stages, la stabilité de catégorie, "
        "la progression et les évaluations."
    )

    selected_style = st.selectbox(
        "Style",
        [
            "Tous",
            "Lutte libre",
            "Lutte gréco-romaine",
            "Lutte féminine",
        ],
    )

    selected_age = st.selectbox(
        "Collectif / âge",
        [
            "Tous",
            "France U15",
            "France U17",
            "France U20",
        ],
    )

    filtered = []

    for athlete in st.session_state.athletes:

        if (
            selected_style != "Tous"
            and athlete["Style"]
            != selected_style
        ):
            continue

        if (
            selected_age != "Tous"
            and athlete["Collectif"]
            != selected_age
        ):
            continue

        filtered.append(
            athlete
        )

    if filtered:

        for athlete_data in filtered:

            name = (
                f"{athlete_data['Prénom']} "
                f"{athlete_data['Nom']}"
            )

            summary = competition_summary(
                name
            )

            evaluations = [
                x
                for x in
                st.session_state
                .evaluations_selection
                if x["Athlète"] == name
            ]

            with st.expander(
                f"🤼 {name} — "
                f"{athlete_data['Catégorie poids']}"
            ):

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "TNR",
                    summary["tnr"]
                )

                c2.metric(
                    "France",
                    summary["france"]
                )

                c3.metric(
                    "International",
                    summary["international"]
                )

                c4.metric(
                    "Évaluations",
                    len(evaluations)
                )

                if st.button(
                    "📋 Ouvrir la fiche",
                    key=f"open_{name}",
                ):

                    st.session_state[
                        "selected_athlete"
                    ] = name

                    st.session_state[
                        "force_selection_page"
                    ] = True

                    st.rerun()


# ============================================================
# COLLECTIFS
# ============================================================

elif page == "👥 Collectifs":

    st.title(
        "👥 Collectifs"
    )

    df = pd.DataFrame(
        st.session_state.athletes
    )

    for collective in df[
        "Collectif"
    ].unique():

        st.subheader(
            collective
        )

        st.dataframe(
            df[
                df["Collectif"]
                == collective
            ],
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# FICHES STAFF
# ============================================================

elif page == "📋 Fiches lutteurs":

    st.title(
        "📋 Fiches individuelles"
    )

    selected = st.selectbox(
        "Lutteur",
        athlete_names(),
    )

    render_athlete_sheet(
        selected,
        editable=True,
        show_selection=True,
    )


# ============================================================
# ÉVALUATIONS RÉFÉRENTS
# ============================================================

elif page == "👁️ Évaluations référents":

    st.title(
        "👁️ Évaluations des référents"
    )

    selected = st.selectbox(
        "Lutteur",
        athlete_names(),
    )

    render_selection_module(
        selected,
        editable=True,
    )


# ============================================================
# PROJETS PERFORMANCE
# ============================================================

elif page == "🎯 Projets de performance":

    st.title(
        "🎯 Projets de performance individuels"
    )

    selected = st.selectbox(
        "Lutteur",
        athlete_names(),
    )

    projects = [
        x
        for x in
        st.session_state
        .projets_performance
        if x["Athlète"] == selected
    ]

    if projects:

        for project in projects:

            st.markdown(
                f"""
                <div class="section-card">

                <b>Date :</b> {project['Date']}<br><br>

                <b>Objectif principal :</b><br>
                {project['Objectif principal']}<br><br>

                <b>Objectifs intermédiaires :</b><br>
                {project['Objectifs intermédiaires']}<br><br>

                <b>Objectif technique :</b><br>
                {project['Objectif technique']}<br><br>

                <b>Objectif physique :</b><br>
                {project['Objectif physique']}<br><br>

                <b>Objectif tactique :</b><br>
                {project['Objectif tactique']}<br><br>

                <b>Compétitions prioritaires :</b><br>
                {project['Compétitions prioritaires']}<br><br>

                <b>Engagement du lutteur :</b><br>
                {project['Engagement lutteur']}<br><br>

                <b>Bilan :</b><br>
                {project['Bilan']}

                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.info(
            "Aucun projet enregistré."
        )


# ============================================================
# PLANNING NATIONAL
# ============================================================

elif page == "📅 Planning national":

    st.title(
        "📅 Planning national"
    )

    st.dataframe(
        pd.DataFrame(
            st.session_state.calendar
        ),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# STAGES
# ============================================================

elif page == "🏕️ Stages":

    st.title(
        "🏕️ Stages"
    )

    st.dataframe(
        pd.DataFrame(
            st.session_state.stages
        ),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# ADMINISTRATION
# ============================================================

elif page == "🏠 Administration":

    st.markdown(
        """
        <div class="hero">
            <h1>⚙️ Administration</h1>
            <p>
            Administration de la plateforme
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Lutteurs",
        len(
            st.session_state.athletes
        )
    )

    c2.metric(
        "Compétitions",
        len(
            st.session_state.competitions
        )
    )

    c3.metric(
        "Évaluations",
        len(
            st.session_state.evaluations_selection
        )
    )

    c4.metric(
        "Projets",
        len(
            st.session_state.projets_performance
        )
    )


elif page == "👥 Lutteurs":

    st.title(
        "👥 Tous les lutteurs"
    )

    st.dataframe(
        pd.DataFrame(
            st.session_state.athletes
        ),
        use_container_width=True,
        hide_index=True,
    )


elif page == "📋 Fiches":

    st.title(
        "📋 Fiches récapitulatives"
    )

    selected = st.selectbox(
        "Lutteur",
        athlete_names(),
    )

    render_athlete_sheet(
        selected,
        editable=True,
        show_selection=True,
    )


elif page == "🇫🇷 Sélection Équipe de France":

    st.title(
        "🇫🇷 Sélection Équipe de France"
    )

    selected = st.selectbox(
        "Lutteur",
        athlete_names(),
    )

    render_selection_module(
        selected,
        editable=True,
    )


elif page == "📊 Statistiques":

    st.title(
        "📊 Statistiques"
    )

    df = pd.DataFrame(
        st.session_state.competitions
    )

    if not df.empty:

        total_matches = df[
            "Combats"
        ].sum()

        total_wins = df[
            "Victoires"
        ].sum()

        total_losses = df[
            "Défaites"
        ].sum()

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Combats",
            int(total_matches)
        )

        c2.metric(
            "Victoires",
            int(total_wins)
        )

        c3.metric(
            "Défaites",
            int(total_losses)
        )

        chart_data = pd.DataFrame(
            {
                "Résultat": [
                    "Victoires",
                    "Défaites",
                ],
                "Nombre": [
                    total_wins,
                    total_losses,
                ],
            }
        )

        st.bar_chart(
            chart_data.set_index(
                "Résultat"
            )
        )


elif page == "📅 Planning":

    st.title(
        "📅 Planning global"
    )

    st.dataframe(
        pd.DataFrame(
            st.session_state.calendar
        ),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "France Lutte Jeunes — V4"
)

st.sidebar.caption(
    "Athlete Management System spécialisé lutte"
)

st.sidebar.caption(
    "Prototype — données en session"
)

# ============================================================
# NOUVEAUX MODULES : CONVOCATIONS
# ============================================================

if page == "📨 Convocations & commission":
    render_convocations_module("manager" if role == "Manager / Sélectionneur" else "selection")

elif page == "🎯 Sélection & critères":
    render_convocations_module("manager")

elif page == "📨 Convocations":
    render_convocations_module("selection")

elif page == "📨 Mes convocations":
    render_convocations_module("athlete")
