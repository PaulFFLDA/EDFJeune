import streamlit as st
import pandas as pd
from datetime import date, datetime
import io
import zipfile
import html
import urllib.request

try:
    from streamlit_sortables import sort_items
except ImportError:
    sort_items = None

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


def create_direct_convocation(competition, athlete_name, manager="Manager / Sélectionneur"):
    """Crée une convocation directement depuis une compétition, sans passer par la proposition de sélection."""
    existing = get_convocation(competition, athlete_name)
    athlete = get_athlete(athlete_name) or {}
    competition_rows = [
        x for x in st.session_state.competitions
        if x.get("Compétition") == competition and x.get("Athlète") == athlete_name
    ]
    source = competition_rows[0] if competition_rows else {}
    category = source.get("Catégorie", "") or athlete.get("Catégorie poids", "") or athlete.get("Catégorie", "")

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
        "Date envoi": "",
        "Réponse": "",
        "Date réponse": "",
        "Motif réponse": "",
        "Lieu": "",
        "Date début": source.get("Date", ""),
        "Date fin": source.get("Date", ""),
        "Heure rendez-vous": "",
        "Lieu rendez-vous": "",
        "Transport": "",
        "Hébergement": "",
        "Accompagnateur": "",
        "Informations": "",
        "Signature manager": manager,
        "Origine": "Création directe depuis une compétition",
    }
    st.session_state.convocations.append(convocation)
    return convocation


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



def render_drag_drop_convocations(selected_comp, manager_name="Manager / Sélectionneur"):
    """Interface drag-and-drop pour affecter les lutteurs aux convocations."""
    st.subheader("🖱️ Glisser-déposer des lutteurs")
    st.caption("Fais glisser un lutteur depuis « Lutteurs disponibles » vers une compétition. Le déplacement crée ou met à jour automatiquement sa convocation.")

    if sort_items is None:
        st.warning("Le module de glisser-déposer n'est pas installé. Ajoute `streamlit-sortables` dans requirements.txt puis redéploie l'application.")
        return

    all_competitions = competition_names()
    containers = [{"header": "🤼 Lutteurs disponibles", "items": []}]
    for comp in all_competitions:
        containers.append({"header": f"📨 {comp}", "items": []})

    # Un lutteur déjà affecté à une compétition apparaît dans cette compétition.
    assigned = {}
    for conv in st.session_state.convocations:
        comp = conv.get("Compétition")
        athlete = conv.get("Athlète")
        if comp in all_competitions and athlete:
            assigned[athlete] = comp

    available = []
    for name in athlete_names():
        if name not in assigned:
            available.append(name)

    containers[0]["items"] = available
    for idx, comp in enumerate(all_competitions, start=1):
        containers[idx]["items"] = [name for name, assigned_comp in assigned.items() if assigned_comp == comp]

    custom_style = """
    .sortable-component { border: 0 !important; background: transparent !important; font-family: inherit; }
    .sortable-container { border: 1px solid #dfe5ed; border-radius: 14px; background: #f7f9fc; min-height: 150px; }
    .sortable-container-header { font-weight: 700; padding: 12px; background: #172033; color: white; border-radius: 12px 12px 0 0; }
    .sortable-container-body { padding: 8px; min-height: 100px; }
    .sortable-item { border-radius: 10px; margin: 6px 0; padding: 10px; background: white; border: 1px solid #dfe5ed; color: #172033; font-weight: 600; cursor: grab; }
    .sortable-item:hover { background: #eef4ff; }
    """

    result = sort_items(containers, multi_containers=True, custom_style=custom_style, key=f"drag_convocations_{selected_comp}")
    if not result:
        return

    # Détecter la destination de chaque lutteur après le déplacement.
    destination = {}
    for container in result:
        header = str(container.get("header", ""))
        items = container.get("items", []) or []
        if header == "🤼 Lutteurs disponibles":
            for name in items:
                destination[name] = None
        elif header.startswith("📨 "):
            comp = header[2:].strip()
            for name in items:
                destination[name] = comp

    changed = False
    for name in athlete_names():
        old_comp = assigned.get(name)
        new_comp = destination.get(name)
        if old_comp == new_comp:
            continue
        if new_comp:
            create_direct_convocation(new_comp, name, manager_name)
            changed = True
        elif old_comp:
            # Retour vers « disponibles » : suppression de la convocation uniquement si elle
            # est encore un brouillon créé par le drag-and-drop/direct.
            st.session_state.convocations = [
                c for c in st.session_state.convocations
                if not (c.get("Athlète") == name and c.get("Compétition") == old_comp and c.get("Statut") == "Brouillon")
            ]
            changed = True

    if changed:
        st.success("Convocations mises à jour à partir du glisser-déposer.")
        st.rerun()

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

    if is_manager:
        manager_name_drag = st.text_input("Responsable des convocations", value="Manager / Sélectionneur", key="drag_manager_name")
        render_drag_drop_convocations(selected_comp, manager_name_drag)
        st.divider()

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
            "🗂️ Base & cercles de performance",
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
            "🗂️ Base & cercles de performance",
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

    # Création directe d'une convocation depuis une compétition.
    # Disponible au manager et à l'administrateur ; le circuit de validation
    # par critères reste disponible dans « Sélection & critères ».
    if role in ("Manager / Sélectionneur", "Administration"):
        st.divider()
        st.subheader("📨 Créer une convocation directement depuis la compétition")
        st.caption(
            "Ce raccourci permet de créer immédiatement un brouillon de convocation. "
            "La convocation pourra ensuite être complétée, téléchargée en PDF et envoyée. "
            "La validation des critères reste disponible dans le module de sélection."
        )

        direct_competition = st.selectbox(
            "Compétition concernée",
            competition_names(),
            key="direct_convocation_competition",
        )
        direct_athletes = st.multiselect(
            "Lutteurs à convoquer",
            athlete_names(),
            key="direct_convocation_athletes",
            help="Tu peux sélectionner plusieurs lutteurs pour générer plusieurs convocations d'un coup.",
        )
        direct_manager = st.text_input(
            "Responsable de la convocation",
            value="Manager / Sélectionneur",
            key="direct_convocation_manager",
        )

        if st.button(
            "📨 Créer les convocations",
            type="primary",
            disabled=not direct_athletes,
            key="create_direct_convocations",
        ):
            created = []
            for athlete_name in direct_athletes:
                conv = create_direct_convocation(direct_competition, athlete_name, direct_manager)
                created.append(conv["Athlète"])
            st.session_state.direct_convocation_competition_result = direct_competition
            st.success(f"{len(created)} convocation(s) créée(s) en brouillon : {', '.join(created)}")

        direct_created = [
            x for x in st.session_state.convocations
            if x.get("Compétition") == direct_competition
        ]
        if direct_created:
            st.markdown("### 📄 Convocations de cette compétition")
            for idx, conv in enumerate(direct_created):
                c1, c2, c3 = st.columns([3, 2, 2])
                c1.write(f"**{conv.get('Athlète', '')}** — {conv.get('Statut', 'Brouillon')}")
                if c2.button("✏️ Ouvrir / modifier", key=f"direct_edit_{idx}"):
                    st.session_state["convocation_competition_preselect"] = direct_competition
                    st.session_state["page"] = "📨 Convocations & commission"
                    st.rerun()
                c3.download_button(
                    "📄 PDF",
                    data=create_convocation_pdf(conv),
                    file_name=f"convocation_{conv['Athlète'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key=f"direct_pdf_{idx}",
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



# ============================================================
# BASE ATHLETES, COLLECTIFS ET CERCLES DE PERFORMANCE
# ============================================================

if page == "🗂️ Base & cercles de performance":
    if role not in ("Administration", "Manager / Sélectionneur"):
        st.error("Accès réservé à l'administration et au manager.")
        st.stop()

    st.markdown("""
    <div class="hero">
      <h1>🗂️ Base athlètes & cercles de performance</h1>
      <p>Gestion des fiches, des collectifs et du suivi individualisé des lutteurs.</p>
    </div>
    """, unsafe_allow_html=True)

    # Champs ajoutés sans écraser les données existantes.
    for athlete in st.session_state.athletes:
        athlete.setdefault("Collectifs", athlete.get("Collectif", ""))
        athlete.setdefault("Cercle performance", "À évaluer")
        athlete.setdefault("Statut sportif", "Actif")
        athlete.setdefault("Région", "")
        athlete.setdefault("Licence", "")
        athlete.setdefault("Objectif saison", athlete.get("Objectif", ""))
        athlete.setdefault("Commentaire performance", "")

    CIRCLES = [
        "Cercle haute performance",
        "Cellule performance",
        "Sélectionnable / potentiel",
        "Relève / développement",
        "Suivi territorial",
        "À évaluer",
    ]

    tab_base, tab_collectifs, tab_cercles, tab_import = st.tabs([
        "👥 Base des lutteurs",
        "🔄 Collectifs",
        "🏅 Cercles de performance",
        "📥 Import / export",
    ])

    with tab_base:
        st.subheader("Effectif")
        f1, f2, f3 = st.columns(3)
        query = f1.text_input("Rechercher un lutteur", key="base_search").strip().lower()
        style_filter = f2.selectbox(
            "Style",
            ["Tous"] + sorted({str(a.get("Style", "")) for a in st.session_state.athletes if a.get("Style")}),
            key="base_style_filter",
        )
        status_filter = f3.selectbox(
            "Statut",
            ["Tous", "Actif", "En pause", "Sorti"],
            key="base_status_filter",
        )

        filtered = []
        for a in st.session_state.athletes:
            full_name = f"{a.get('Prénom', '')} {a.get('Nom', '')}".strip()
            searchable = " ".join([
                full_name, str(a.get("Club", "")), str(a.get("Collectif", "")),
                str(a.get("Collectifs", "")), str(a.get("Catégorie", "")),
                str(a.get("Catégorie poids", "")), str(a.get("Région", "")),
            ]).lower()
            if query and query not in searchable:
                continue
            if style_filter != "Tous" and a.get("Style", "") != style_filter:
                continue
            if status_filter != "Tous" and a.get("Statut sportif", "Actif") != status_filter:
                continue
            filtered.append(a)

        st.metric("Lutteurs correspondant aux filtres", len(filtered))
        if filtered:
            display_columns = [
                "Prénom", "Nom", "Club", "Style", "Catégorie", "Catégorie poids",
                "Collectif", "Cercle performance", "Statut sportif", "Région"
            ]
            st.dataframe(
                pd.DataFrame([{k: a.get(k, "") for k in display_columns} for a in filtered]),
                use_container_width=True, hide_index=True
            )

        st.divider()
        st.subheader("➕ Ajouter un lutteur")
        with st.form("add_athlete_extended", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            prenom = c1.text_input("Prénom *")
            nom = c2.text_input("Nom *")
            club = c3.text_input("Club")
            c4, c5, c6 = st.columns(3)
            style = c4.selectbox("Style de lutte", ["Lutte libre", "Lutte gréco-romaine", "Lutte féminine"])
            categorie = c5.text_input("Catégorie d'âge")
            poids = c6.text_input("Catégorie de poids")
            c7, c8, c9 = st.columns(3)
            collectif = c7.text_input("Collectif principal")
            cercle = c8.selectbox("Cercle de performance", CIRCLES, index=len(CIRCLES)-1)
            region = c9.text_input("Région")
            c10, c11 = st.columns(2)
            coach = c10.text_input("Entraîneur")
            objectif = c11.text_input("Objectif sportif")
            add = st.form_submit_button("Ajouter le lutteur", type="primary")
            if add:
                if not prenom.strip() or not nom.strip():
                    st.error("Le prénom et le nom sont obligatoires.")
                elif any(
                    a.get("Prénom", "").strip().casefold() == prenom.strip().casefold()
                    and a.get("Nom", "").strip().casefold() == nom.strip().casefold()
                    for a in st.session_state.athletes
                ):
                    st.error("Un lutteur portant ce prénom et ce nom existe déjà.")
                else:
                    st.session_state.athletes.append({
                        "Prénom": prenom.strip(), "Nom": nom.strip(), "Club": club.strip(),
                        "Style": style, "Catégorie": categorie.strip(), "Catégorie poids": poids.strip(),
                        "Date de naissance": "", "Collectif": collectif.strip(), "Collectifs": collectif.strip(),
                        "Entraîneur": coach.strip(), "Objectif": objectif.strip(),
                        "Objectif saison": objectif.strip(), "Points forts": "", "Axes progression": "",
                        "Observation": "", "Cercle performance": cercle, "Statut sportif": "Actif",
                        "Région": region.strip(), "Licence": "", "Commentaire performance": "",
                    })
                    st.success(f"{prenom.strip()} {nom.strip()} a été ajouté.")
                    st.rerun()

        st.divider()
        st.subheader("✏️ Modifier ou retirer un lutteur")
        athlete_labels = [
            f"{a.get('Prénom', '')} {a.get('Nom', '')}".strip()
            for a in st.session_state.athletes
        ]
        if athlete_labels:
            chosen = st.selectbox("Lutteur à modifier", athlete_labels, key="edit_athlete_extended")
            selected = next(
                a for a in st.session_state.athletes
                if f"{a.get('Prénom', '')} {a.get('Nom', '')}".strip() == chosen
            )
            with st.form("edit_athlete_extended_form"):
                c1, c2, c3 = st.columns(3)
                new_club = c1.text_input("Club", value=selected.get("Club", ""))
                new_collectif = c2.text_input("Collectif principal", value=selected.get("Collectif", ""))
                current_circle = selected.get("Cercle performance", "À évaluer")
                new_circle = c3.selectbox(
                    "Cercle de performance", CIRCLES,
                    index=CIRCLES.index(current_circle) if current_circle in CIRCLES else len(CIRCLES)-1
                )
                c4, c5, c6 = st.columns(3)
                new_category = c4.text_input("Catégorie", value=selected.get("Catégorie", ""))
                new_weight = c5.text_input("Catégorie de poids", value=selected.get("Catégorie poids", ""))
                new_region = c6.text_input("Région", value=selected.get("Région", ""))
                c7, c8 = st.columns(2)
                new_coach = c7.text_input("Entraîneur", value=selected.get("Entraîneur", ""))
                new_status = c8.selectbox(
                    "Statut sportif", ["Actif", "En pause", "Sorti"],
                    index=["Actif", "En pause", "Sorti"].index(
                        selected.get("Statut sportif", "Actif")
                        if selected.get("Statut sportif", "Actif") in ["Actif", "En pause", "Sorti"]
                        else "Actif"
                    )
                )
                new_objective = st.text_input(
                    "Objectif saison", value=selected.get("Objectif saison", selected.get("Objectif", ""))
                )
                new_notes = st.text_area(
                    "Commentaire performance", value=selected.get("Commentaire performance", "")
                )
                save = st.form_submit_button("Enregistrer les modifications", type="primary")
                if save:
                    selected.update({
                        "Club": new_club.strip(), "Collectif": new_collectif.strip(),
                        "Collectifs": new_collectif.strip(), "Cercle performance": new_circle,
                        "Catégorie": new_category.strip(), "Catégorie poids": new_weight.strip(),
                        "Région": new_region.strip(), "Entraîneur": new_coach.strip(),
                        "Statut sportif": new_status, "Objectif saison": new_objective.strip(),
                        "Objectif": new_objective.strip(), "Commentaire performance": new_notes.strip(),
                    })
                    st.success("Fiche mise à jour.")
                    st.rerun()

            with st.expander("⚠️ Retirer un lutteur de la base"):
                st.warning("Cette action supprime aussi ses données liées (résultats, poids, tests, évaluations, projets et calendrier).")
                confirm = st.checkbox(f"Je confirme le retrait de {chosen}", key="confirm_delete_athlete")
                if st.button("Retirer définitivement ce lutteur", type="secondary", disabled=not confirm):
                    st.session_state.athletes = [
                        a for a in st.session_state.athletes
                        if f"{a.get('Prénom', '')} {a.get('Nom', '')}".strip() != chosen
                    ]
                    for key in [
                        "competitions", "weight_log", "tests", "calendar",
                        "evaluations_selection", "projets_performance"
                    ]:
                        if key in st.session_state:
                            st.session_state[key] = [
                                row for row in st.session_state[key]
                                if row.get("Athlète") != chosen
                            ]
                    st.session_state.selection_proposals = [
                        row for row in st.session_state.selection_proposals if row.get("Athlète") != chosen
                    ]
                    st.session_state.convocations = [
                        row for row in st.session_state.convocations if row.get("Athlète") != chosen
                    ]
                    st.success(f"{chosen} a été retiré de la base.")
                    st.rerun()

    with tab_collectifs:
        st.subheader("Affecter ou retirer un lutteur d'un collectif")
        st.caption("Un changement d'affectation met à jour le collectif principal de la fiche.")
        athlete_labels = [
            f"{a.get('Prénom', '')} {a.get('Nom', '')}".strip()
            for a in st.session_state.athletes
        ]
        collective_names = sorted({
            str(a.get("Collectif", "")).strip()
            for a in st.session_state.athletes if str(a.get("Collectif", "")).strip()
        })
        collective_names += [x for x in ["France U15", "France U17", "France U20", "France Senior", "Groupe relève", "Groupe détection"] if x not in collective_names]
        if athlete_labels:
            selected_names = st.multiselect("Lutteurs concernés", athlete_labels, key="collective_bulk_names")
            target_collective = st.selectbox("Collectif cible", collective_names + ["Créer un nouveau collectif"], key="collective_target")
            custom_collective = ""
            if target_collective == "Créer un nouveau collectif":
                custom_collective = st.text_input("Nom du nouveau collectif", key="new_collective_name")
            effective_collective = custom_collective.strip() if target_collective == "Créer un nouveau collectif" else target_collective
            ca, cb = st.columns(2)
            if ca.button("➕ Ajouter / affecter au collectif", disabled=not selected_names):
                if not effective_collective:
                    st.error("Indique un nom de collectif.")
                else:
                    for a in st.session_state.athletes:
                        name = f"{a.get('Prénom', '')} {a.get('Nom', '')}".strip()
                        if name in selected_names:
                            memberships = [x.strip() for x in str(a.get("Collectifs", a.get("Collectif", ""))).split(";") if x.strip()]
                            if effective_collective not in memberships:
                                memberships.append(effective_collective)
                            a["Collectifs"] = "; ".join(memberships)
                            if not a.get("Collectif"):
                                a["Collectif"] = effective_collective
                    st.success(f"{len(selected_names)} affectation(s) ajoutée(s) au collectif.")
                    st.rerun()
            if cb.button("➖ Retirer du collectif sélectionné", disabled=not selected_names):
                for a in st.session_state.athletes:
                    name = f"{a.get('Prénom', '')} {a.get('Nom', '')}".strip()
                    if name in selected_names:
                        memberships = [x.strip() for x in str(a.get("Collectifs", a.get("Collectif", ""))).split(";") if x.strip()]
                        memberships = [x for x in memberships if x != effective_collective]
                        a["Collectifs"] = "; ".join(memberships)
                        if a.get("Collectif") == effective_collective:
                            a["Collectif"] = memberships[0] if memberships else ""
                st.success("Retrait effectué pour le collectif sélectionné.")
                st.rerun()

        st.divider()
        st.subheader("Composition actuelle des collectifs")
        by_collective = {}
        for a in st.session_state.athletes:
            memberships = [x.strip() for x in str(a.get("Collectifs", a.get("Collectif", ""))).split(";") if x.strip()]
            if not memberships:
                memberships = ["Sans collectif"]
            for group in memberships:
                by_collective.setdefault(group, []).append(a)
        for group, members in sorted(by_collective.items()):
            with st.expander(f"{group} — {len(members)} lutteur(s)"):
                st.dataframe(pd.DataFrame([{
                    "Lutteur": f"{a.get('Prénom', '')} {a.get('Nom', '')}".strip(),
                    "Club": a.get("Club", ""), "Catégorie": a.get("Catégorie", ""),
                    "Poids": a.get("Catégorie poids", ""), "Cercle": a.get("Cercle performance", "À évaluer")
                } for a in members]), use_container_width=True, hide_index=True)

    with tab_cercles:
        st.subheader("Répartition des cercles")
        st.caption("Ces cercles sont une proposition de suivi interne. Ils ne valent pas inscription officielle sur une liste ministérielle ou attribution d'une aide ANS.")
        counts = {circle: 0 for circle in CIRCLES}
        for a in st.session_state.athletes:
            circle = a.get("Cercle performance", "À évaluer")
            counts[circle] = counts.get(circle, 0) + 1
        cols = st.columns(3)
        for i, circle in enumerate(CIRCLES):
            cols[i % 3].metric(circle, counts.get(circle, 0))
        for circle in CIRCLES:
            members = [a for a in st.session_state.athletes if a.get("Cercle performance", "À évaluer") == circle]
            if members:
                with st.expander(f"{circle} — {len(members)}"):
                    st.dataframe(pd.DataFrame([{
                        "Lutteur": f"{a.get('Prénom', '')} {a.get('Nom', '')}".strip(),
                        "Club": a.get("Club", ""), "Collectif": a.get("Collectif", ""),
                        "Style": a.get("Style", ""), "Catégorie": a.get("Catégorie", ""),
                        "Objectif": a.get("Objectif saison", a.get("Objectif", "")),
                    } for a in members]), use_container_width=True, hide_index=True)

    with tab_import:
        st.subheader("Importer une base existante")
        st.write("Importe un fichier CSV ou Excel avec au minimum les colonnes **Prénom** et **Nom**. Les colonnes reconnues sont ajoutées aux fiches.")
        st.caption("Colonnes utiles : Prénom, Nom, Club, Style, Catégorie, Catégorie poids, Collectif, Entraîneur, Région, Licence, Cercle performance, Statut sportif, Objectif.")
        uploaded = st.file_uploader("Choisir un fichier CSV ou Excel", type=["csv", "xlsx"], key="athlete_bulk_upload")
        import_mode = st.radio("Mode d'import", ["Ajouter les nouveaux lutteurs", "Mettre à jour les fiches existantes et ajouter les nouveaux"], horizontal=True)
        if uploaded is not None:
            try:
                if uploaded.name.lower().endswith(".csv"):
                    imported_df = pd.read_csv(uploaded, dtype=str).fillna("")
                else:
                    imported_df = pd.read_excel(uploaded, dtype=str).fillna("")
                st.dataframe(imported_df.head(10), use_container_width=True, hide_index=True)
                if st.button("Importer les lignes", type="primary", key="confirm_athlete_import"):
                    if not {"Prénom", "Nom"}.issubset(set(imported_df.columns)):
                        st.error("Le fichier doit contenir les colonnes 'Prénom' et 'Nom'.")
                    else:
                        existing_map = {
                            (a.get("Prénom", "").strip().casefold(), a.get("Nom", "").strip().casefold()): a
                            for a in st.session_state.athletes
                        }
                        added = updated = skipped = 0
                        allowed = {
                            "Prénom", "Nom", "Club", "Style", "Catégorie", "Catégorie poids",
                            "Date de naissance", "Collectif", "Entraîneur", "Objectif", "Points forts",
                            "Axes progression", "Observation", "Région", "Licence", "Cercle performance",
                            "Statut sportif", "Objectif saison", "Commentaire performance"
                        }
                        for _, row in imported_df.iterrows():
                            first = str(row.get("Prénom", "")).strip()
                            last = str(row.get("Nom", "")).strip()
                            if not first or not last:
                                skipped += 1
                                continue
                            key = (first.casefold(), last.casefold())
                            payload = {k: str(row.get(k, "")).strip() for k in allowed if k in imported_df.columns}
                            payload.setdefault("Collectif", "")
                            payload.setdefault("Style", "")
                            payload.setdefault("Catégorie", "")
                            payload.setdefault("Catégorie poids", "")
                            payload.setdefault("Objectif", "")
                            payload.setdefault("Date de naissance", "")
                            payload.setdefault("Points forts", "")
                            payload.setdefault("Axes progression", "")
                            payload.setdefault("Observation", "")
                            payload.setdefault("Entraîneur", "")
                            payload.setdefault("Club", "")
                            payload["Collectifs"] = payload.get("Collectif", "")
                            payload.setdefault("Cercle performance", "À évaluer")
                            payload.setdefault("Statut sportif", "Actif")
                            if key in existing_map:
                                if import_mode.startswith("Mettre à jour"):
                                    existing_map[key].update(payload)
                                    updated += 1
                                else:
                                    skipped += 1
                            else:
                                st.session_state.athletes.append(payload)
                                existing_map[key] = payload
                                added += 1
                        st.success(f"Import terminé : {added} ajouté(s), {updated} mis à jour, {skipped} ignoré(s).")
                        st.rerun()
            except Exception as exc:
                st.error(f"Impossible de lire ce fichier : {exc}")

        st.divider()
        st.subheader("Exporter la base")
        export_df = pd.DataFrame(st.session_state.athletes)
        st.download_button(
            "⬇️ Télécharger la base des lutteurs (CSV)",
            data=export_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="base_lutteurs.csv",
            mime="text/csv",
            type="primary",
        )

    st.info(
        "Important : cette version conserve encore les modifications dans la session Streamlit. "
        "Pour une base durable et partagée entre plusieurs utilisateurs, il faudra connecter une base persistante "
        "(par exemple PostgreSQL/Supabase) ; le fichier local seul n'est pas une garantie de conservation sur Streamlit Cloud."
    )

