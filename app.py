import streamlit as st
import pandas as pd
from datetime import date

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
        padding: 1.5rem 2rem;
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

    .card {
        background: white;
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid #e6eaf0;
        margin-bottom: 1rem;
    }

    .small-label {
        font-size: 0.8rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .big-number {
        font-size: 2rem;
        font-weight: 700;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e6eaf0;
        padding: 1rem;
        border-radius: 14px;
    }

    .success-box {
        padding: 1rem;
        border-radius: 12px;
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
    }

    .warning-box {
        padding: 1rem;
        border-radius: 12px;
        background: #fffbeb;
        border: 1px solid #fde68a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# DONNÉES DE DÉMONSTRATION
# ============================================================

if "athletes" not in st.session_state:
    st.session_state.athletes = [
        {
            "Nom": "Martin",
            "Prénom": "Lucas",
            "Club": "Club de Caen",
            "Catégorie": "U17 - 65 kg",
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
            "Catégorie": "U20 - 74 kg",
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
            "Catégorie": "U15 - 57 kg",
            "Date de naissance": "2011-02-17",
            "Collectif": "France U15",
            "Entraîneur": "Marc Petit",
            "Objectif": "Championnat de France",
            "Points forts": "Mobilité, vitesse",
            "Axes progression": "Défense et force générale",
            "Observation": "Jeune lutteur en progression.",
        },
    ]

if "competitions" not in st.session_state:
    st.session_state.competitions = [
        {
            "Athlète": "Lucas Martin",
            "Date": "2026-09-12",
            "Compétition": "Tournoi National",
            "Catégorie": "65 kg",
            "Combats": 4,
            "Victoires": 3,
            "Défaites": 1,
            "Classement": "2e",
            "Bilan": "Très bien",
            "Résumé": "Bonne compétition. Très bon comportement dans les phases debout.",
        },
        {
            "Athlète": "Hugo Durand",
            "Date": "2026-09-20",
            "Compétition": "Tournoi International",
            "Catégorie": "74 kg",
            "Combats": 5,
            "Victoires": 3,
            "Défaites": 2,
            "Classement": "5e",
            "Bilan": "Bien",
            "Résumé": "Bonne intensité mais manque de régularité sur les fins de combat.",
        },
    ]

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
            "Type": "Stage",
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
# FONCTIONS
# ============================================================

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
        x for x in st.session_state.competitions
        if x["Athlète"] == full_name
    ]

    matches = sum(x["Combats"] for x in competitions)
    wins = sum(x["Victoires"] for x in competitions)
    losses = sum(x["Défaites"] for x in competitions)

    podiums = 0

    for x in competitions:
        ranking = str(x["Classement"]).lower()
        if ranking.startswith(("1", "2", "3")):
            podiums += 1

    return {
        "competitions": len(competitions),
        "matches": matches,
        "wins": wins,
        "losses": losses,
        "podiums": podiums,
    }


# ============================================================
# FICHE RÉCAPITULATIVE
# ============================================================

def render_athlete_sheet(full_name, editable=False):

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
                {athlete['Club']} · {athlete['Catégorie']} ·
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
    # INFORMATIONS GÉNÉRALES
    # --------------------------------------------------------

    st.subheader("👤 Informations générales")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Club :** {athlete['Club']}")
        st.write(f"**Catégorie :** {athlete['Catégorie']}")
        st.write(f"**Date de naissance :** {athlete['Date de naissance']}")

    with col2:
        st.write(f"**Collectif :** {athlete['Collectif']}")
        st.write(f"**Entraîneur :** {athlete['Entraîneur']}")
        st.write(f"**Objectif :** {athlete['Objectif']}")

    # --------------------------------------------------------
    # PROFIL SPORTIF
    # --------------------------------------------------------

    st.subheader("🎯 Profil sportif")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Points forts**")
        st.info(athlete["Points forts"])

    with col2:
        st.markdown("**Axes de progression**")
        st.warning(athlete["Axes progression"])

    with col3:
        st.markdown("**Observation**")
        st.success(athlete["Observation"])

    # --------------------------------------------------------
    # RÉSULTATS COMPÉTITIONS
    # --------------------------------------------------------

    st.subheader("🏆 Résultats en compétition")

    competitions = [
        x for x in st.session_state.competitions
        if x["Athlète"] == full_name
    ]

    if competitions:

        df_comp = pd.DataFrame(competitions)

        st.dataframe(
            df_comp[
                [
                    "Date",
                    "Compétition",
                    "Catégorie",
                    "Combats",
                    "Victoires",
                    "Défaites",
                    "Classement",
                    "Bilan",
                    "Résumé",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("Aucun résultat enregistré.")

    # --------------------------------------------------------
    # COURBE DE POIDS
    # --------------------------------------------------------

    st.subheader("⚖️ Évolution du poids")

    weights = [
        x for x in st.session_state.weight_log
        if x["Athlète"] == full_name
    ]

    if weights:

        df_weight = pd.DataFrame(weights)
        df_weight["Date"] = pd.to_datetime(df_weight["Date"])

        df_weight = df_weight.sort_values("Date")
        df_weight = df_weight.set_index("Date")

        st.line_chart(
            df_weight["Poids"],
            height=280,
        )

        last_weight = df_weight["Poids"].iloc[-1]
        first_weight = df_weight["Poids"].iloc[0]

        evolution = last_weight - first_weight

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
        st.info("Aucune donnée de poids.")

    # --------------------------------------------------------
    # TESTS PHYSIQUES
    # --------------------------------------------------------

    st.subheader("🧪 Évolution des tests physiques")

    athlete_tests = [
        x for x in st.session_state.tests
        if x["Athlète"] == full_name
    ]

    if athlete_tests:

        test_names = sorted(
            list(set(x["Test"] for x in athlete_tests))
        )

        selected_test = st.selectbox(
            "Test à afficher",
            test_names,
            key=f"test_{full_name}",
        )

        filtered_tests = [
            x for x in athlete_tests
            if x["Test"] == selected_test
        ]

        df_test = pd.DataFrame(filtered_tests)

        df_test["Date"] = pd.to_datetime(df_test["Date"])

        df_test = df_test.sort_values("Date")
        df_test = df_test.set_index("Date")

        st.line_chart(
            df_test["Valeur"],
            height=280,
        )

        st.dataframe(
            pd.DataFrame(filtered_tests),
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("Aucun test physique enregistré.")

    # --------------------------------------------------------
    # CALENDRIER
    # --------------------------------------------------------

    st.subheader("📅 Prochaines échéances")

    calendar = [
        x for x in st.session_state.calendar
        if x["Athlète"] == full_name
    ]

    if calendar:

        df_calendar = pd.DataFrame(calendar)

        df_calendar["Date"] = pd.to_datetime(
            df_calendar["Date"]
        )

        df_calendar = df_calendar.sort_values("Date")

        st.dataframe(
            df_calendar,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("Aucune échéance programmée.")

    # --------------------------------------------------------
    # ÉDITION
    # --------------------------------------------------------

    if editable:

        st.divider()

        st.subheader("✏️ Modifier la fiche")

        with st.form(
            f"edit_athlete_{full_name}"
        ):

            col1, col2 = st.columns(2)

            with col1:

                new_club = st.text_input(
                    "Club",
                    athlete["Club"],
                )

                new_category = st.text_input(
                    "Catégorie",
                    athlete["Catégorie"],
                )

                new_coach = st.text_input(
                    "Entraîneur",
                    athlete["Entraîneur"],
                )

                new_birth = st.text_input(
                    "Date de naissance",
                    athlete["Date de naissance"],
                )

                new_collective = st.text_input(
                    "Collectif",
                    athlete["Collectif"],
                )

            with col2:

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
                "💾 Enregistrer la fiche",
                type="primary",
                use_container_width=True,
            )

            if submitted:

                athlete["Club"] = new_club
                athlete["Catégorie"] = new_category
                athlete["Entraîneur"] = new_coach
                athlete["Date de naissance"] = new_birth
                athlete["Collectif"] = new_collective
                athlete["Objectif"] = new_objective
                athlete["Points forts"] = new_strengths
                athlete["Axes progression"] = new_progression
                athlete["Observation"] = new_observation

                st.success(
                    "Fiche du lutteur mise à jour."
                )

                st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🤼 France Lutte Jeunes")

st.sidebar.caption(
    "Suivi sportif des collectifs nationaux"
)

role = st.sidebar.selectbox(
    "Profil utilisateur",
    [
        "Lutteur / Lutteuse",
        "Entraîneur / Club",
        "Sélectionneur / Staff",
        "Administration",
    ],
)

# ============================================================
# NAVIGATION LUTTEUR
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
            "📅 Mon calendrier",
            "🏆 Mes compétitions",
            "⚖️ Mon poids",
            "🧪 Mes tests",
        ],
    )

# ============================================================
# NAVIGATION STAFF
# ============================================================

elif role == "Entraîneur / Club":

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Tableau de bord",
            "👥 Mes lutteurs",
            "📋 Fiches lutteurs",
            "🏆 Compétitions",
            "🧪 Tests physiques",
            "📅 Calendrier",
        ],
    )

# ============================================================
# NAVIGATION SÉLECTIONNEUR
# ============================================================

elif role == "Sélectionneur / Staff":

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Tableau national",
            "👥 Collectifs",
            "📋 Fiches lutteurs",
            "📅 Planning national",
            "🏕️ Stages",
            "🏆 Compétitions",
            "🧪 Tests physiques",
        ],
    )

# ============================================================
# NAVIGATION ADMIN
# ============================================================

else:

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Administration",
            "👥 Lutteurs",
            "📋 Fiches",
            "📊 Statistiques",
            "📅 Planning",
        ],
    )


# ============================================================
# TABLEAU DE BORD LUTTEUR
# ============================================================

if page == "🏠 Tableau de bord":

    st.markdown(
        """
        <div class="hero">
            <h1>🤼 Mon espace sportif</h1>
            <p>Suivi individuel de la saison</p>
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

    st.subheader("🎯 Mon objectif")

    athlete_data = get_athlete(athlete)

    st.info(
        athlete_data["Objectif"]
    )

    st.subheader("📅 Mes prochaines échéances")

    upcoming = [
        x for x in st.session_state.calendar
        if x["Athlète"] == athlete
    ]

    if upcoming:

        df = pd.DataFrame(upcoming)

        df["Date"] = pd.to_datetime(
            df["Date"]
        )

        df = df.sort_values("Date")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# FICHE LUTTEUR
# ============================================================

elif page == "📋 Ma fiche récap":

    render_athlete_sheet(
        athlete,
        editable=True,
    )


# ============================================================
# MON CALENDRIER
# ============================================================

elif page == "📅 Mon calendrier":

    st.title("📅 Mon calendrier")

    st.info(
        "Le lutteur peut renseigner ici ses compétitions, "
        "entraînements, stages et objectifs."
    )

    with st.form("new_calendar"):

        event_date = st.date_input(
            "Date",
            value=date.today(),
        )

        event_type = st.selectbox(
            "Type",
            [
                "Compétition",
                "Stage",
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
            "Ajouter au calendrier",
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

    st.divider()

    data = [
        x for x in st.session_state.calendar
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
# COMPÉTITION
# ============================================================

elif page == "🏆 Mes compétitions":

    st.title("🏆 Mes compétitions")

    st.subheader(
        "Compte-rendu rapide"
    )

    with st.form("competition_report"):

        competition_date = st.date_input(
            "Date",
            value=date.today(),
        )

        competition_name = st.text_input(
            "Compétition"
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
            "Résultat / classement",
            placeholder="Ex : 2e, 5e, éliminé en 1/4...",
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
            "Petit bilan",
            placeholder="Quelques lignes sur la compétition...",
        )

        submit = st.form_submit_button(
            "💾 Enregistrer le compte-rendu",
            type="primary",
            use_container_width=True,
        )

        if submit:

            st.session_state.competitions.append(
                {
                    "Athlète": athlete,
                    "Date": str(competition_date),
                    "Compétition": competition_name,
                    "Catégorie": category,
                    "Combats": matches,
                    "Victoires": wins,
                    "Défaites": losses,
                    "Classement": ranking,
                    "Bilan": assessment,
                    "Résumé": summary,
                }
            )

            st.success(
                "Compte-rendu enregistré."
            )

            st.rerun()

    st.divider()

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
        "Défaites",
        stats["losses"]
    )

    athlete_competitions = [
        x for x in st.session_state.competitions
        if x["Athlète"] == athlete
    ]

    if athlete_competitions:

        st.dataframe(
            pd.DataFrame(athlete_competitions),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# POIDS
# ============================================================

elif page == "⚖️ Mon poids":

    st.title("⚖️ Mon suivi du poids")

    with st.form("weight_form"):

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
            "Ajouter le poids",
            type="primary",
        )

        if submit:

            st.session_state.weight_log.append(
                {
                    "Athlète": athlete,
                    "Date": str(weight_date),
                    "Poids": weight,
                }
            )

            st.success(
                "Poids enregistré."
            )

            st.rerun()

    weights = [
        x for x in st.session_state.weight_log
        if x["Athlète"] == athlete
    ]

    if weights:

        df = pd.DataFrame(weights)

        df["Date"] = pd.to_datetime(
            df["Date"]
        )

        df = df.sort_values("Date")
        df = df.set_index("Date")

        st.line_chart(
            df["Poids"],
            height=350,
        )


# ============================================================
# TESTS
# ============================================================

elif page == "🧪 Mes tests":

    st.title("🧪 Mes tests physiques")

    with st.form("test_form"):

        test_date = st.date_input(
            "Date",
            value=date.today(),
        )

        test_name = st.text_input(
            "Nom du test",
            placeholder="Ex : Saut vertical",
        )

        value = st.number_input(
            "Valeur",
            value=0.0,
        )

        unit = st.text_input(
            "Unité",
            placeholder="cm, kg, secondes, répétitions...",
        )

        submit = st.form_submit_button(
            "Ajouter le test",
            type="primary",
        )

        if submit:

            st.session_state.tests.append(
                {
                    "Athlète": athlete,
                    "Date": str(test_date),
                    "Test": test_name,
                    "Valeur": value,
                    "Unité": unit,
                }
            )

            st.success(
                "Test enregistré."
            )

            st.rerun()

    athlete_tests = [
        x for x in st.session_state.tests
        if x["Athlète"] == athlete
    ]

    if athlete_tests:

        df = pd.DataFrame(athlete_tests)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# STAFF / CLUB
# ============================================================

elif page == "👥 Mes lutteurs":

    st.title("👥 Mes lutteurs")

    df = pd.DataFrame(
        st.session_state.athletes
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


elif page == "📋 Fiches lutteurs":

    st.title("📋 Fiches récapitulatives")

    selected = st.selectbox(
        "Choisir un lutteur",
        athlete_names(),
    )

    render_athlete_sheet(
        selected,
        editable=True,
    )


elif page == "🏆 Compétitions":

    st.title("🏆 Suivi des compétitions")

    st.dataframe(
        pd.DataFrame(
            st.session_state.competitions
        ),
        use_container_width=True,
        hide_index=True,
    )


elif page == "🧪 Tests physiques":

    st.title("🧪 Tests physiques")

    st.dataframe(
        pd.DataFrame(
            st.session_state.tests
        ),
        use_container_width=True,
        hide_index=True,
    )


elif page == "📅 Calendrier":

    st.title("📅 Calendrier")

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
            <p>Suivi des collectifs jeunes</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    athletes_count = len(
        st.session_state.athletes
    )

    competitions_count = len(
        st.session_state.competitions
    )

    tests_count = len(
        st.session_state.tests
    )

    calendar_count = len(
        st.session_state.calendar
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Lutteurs",
        athletes_count
    )

    c2.metric(
        "Compétitions renseignées",
        competitions_count
    )

    c3.metric(
        "Tests physiques",
        tests_count
    )

    c4.metric(
        "Échéances",
        calendar_count
    )

    st.subheader(
        "📊 Vue des collectifs"
    )

    df = pd.DataFrame(
        st.session_state.athletes
    )

    st.dataframe(
        df[
            [
                "Prénom",
                "Nom",
                "Club",
                "Catégorie",
                "Collectif",
                "Objectif",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


elif page == "👥 Collectifs":

    st.title("👥 Collectifs")

    df = pd.DataFrame(
        st.session_state.athletes
    )

    for collective in df["Collectif"].unique():

        st.subheader(
            collective
        )

        st.dataframe(
            df[
                df["Collectif"] == collective
            ],
            use_container_width=True,
            hide_index=True,
        )


elif page == "📋 Fiches lutteurs":

    st.title(
        "📋 Fiches individuelles"
    )

    selected = st.selectbox(
        "Sélectionner un lutteur",
        athlete_names(),
    )

    render_athlete_sheet(
        selected,
        editable=True,
    )


elif page == "📅 Planning national":

    st.title(
        "📅 Planning national"
    )

    st.info(
        "Cette section pourra accueillir le planning "
        "national partagé par les sélectionneurs."
    )

    st.dataframe(
        pd.DataFrame(
            st.session_state.calendar
        ),
        use_container_width=True,
        hide_index=True,
    )


elif page == "🏕️ Stages":

    st.title("🏕️ Stages")

    st.info(
        "Les stages nationaux pourront être créés "
        "et attribués aux collectifs."
    )


# ============================================================
# ADMINISTRATION
# ============================================================

elif page == "🏠 Administration":

    st.markdown(
        """
        <div class="hero">
            <h1>⚙️ Administration</h1>
            <p>Vue globale de la plateforme</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Lutteurs",
        len(st.session_state.athletes)
    )

    c2.metric(
        "Compétitions",
        len(st.session_state.competitions)
    )

    c3.metric(
        "Tests",
        len(st.session_state.tests)
    )


elif page == "👥 Lutteurs":

    st.title("👥 Tous les lutteurs")

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
    )


elif page == "📊 Statistiques":

    st.title("📊 Statistiques")

    df = pd.DataFrame(
        st.session_state.competitions
    )

    if not df.empty:

        total_matches = df["Combats"].sum()
        total_wins = df["Victoires"].sum()
        total_losses = df["Défaites"].sum()

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

        st.subheader(
            "Victoires / défaites"
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

    st.title("📅 Planning global")

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
    "France Lutte Jeunes — Prototype V3"
)

st.sidebar.caption(
    "Données actuellement stockées en session."
)
