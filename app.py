import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import date
from supabase import create_client


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="France Lutte Jeunes",
    page_icon="🇫🇷",
    layout="wide",
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
    }

    .hero {
        padding: 2rem;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            #111827,
            #1f2937
        );
        color: white;
        margin-bottom: 2rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.5rem;
    }

    .hero p {
        opacity: .75;
    }

    .card {
        padding: 1.3rem;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        background: white;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# CLIENT SUPABASE
# =========================================================

@st.cache_resource
def get_supabase():

    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )


@st.cache_resource
def get_admin_client():

    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_SERVICE_KEY"],
    )


supabase = get_supabase()


# =========================================================
# SESSION
# =========================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "profile" not in st.session_state:
    st.session_state.profile = None


# =========================================================
# AUTH
# =========================================================

def load_profile(user_id):

    response = (
        supabase
        .table("profiles")
        .select("*")
        .eq("id", user_id)
        .single()
        .execute()
    )

    return response.data


def login():

    st.markdown(
        """
        <div class="hero">
            <h1>🇫🇷 France Lutte Jeunes</h1>
            <p>
                Athlete Management System · V5
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col2:

        st.subheader("Connexion")

        email = st.text_input(
            "Email"
        )

        password = st.text_input(
            "Mot de passe",
            type="password",
        )

        if st.button(
            "Se connecter",
            use_container_width=True,
        ):

            try:

                response = (
                    supabase
                    .auth
                    .sign_in_with_password(
                        {
                            "email": email,
                            "password": password,
                        }
                    )
                )

                profile = load_profile(
                    response.user.id
                )

                if not profile["active"]:

                    st.error(
                        "Compte désactivé."
                    )

                    return

                st.session_state.user = (
                    response.user
                )

                st.session_state.profile = (
                    profile
                )

                st.rerun()

            except Exception:

                st.error(
                    "Email ou mot de passe incorrect."
                )


def logout():

    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.user = None
    st.session_state.profile = None

    st.rerun()


# =========================================================
# HELPERS
# =========================================================

def is_manager():

    return (
        st.session_state.profile
        and
        st.session_state.profile["role"]
        == "manager"
    )


def role_name(role):

    labels = {

        "lutteur":
            "🤼 Lutteur",

        "entraineur":
            "🏋️ Entraîneur / Club",

        "selectionneur":
            "👁️ Sélectionneur / Référent",

        "staff":
            "🇫🇷 Staff national",

        "manager":
            "👑 Manager",

    }

    return labels.get(
        role,
        role,
    )


def audit(
    action,
    object_type=None,
    object_id=None,
    details=None,
):

    try:

        supabase.table(
            "audit_logs"
        ).insert(
            {
                "user_id":
                    st.session_state.user.id,

                "action":
                    action,

                "object_type":
                    object_type,

                "object_id":
                    object_id,

                "details":
                    details or {},
            }
        ).execute()

    except Exception:
        pass


# =========================================================
# SIDEBAR
# =========================================================

def sidebar():

    profile = st.session_state.profile

    st.sidebar.title(
        "🇫🇷 France Lutte"
    )

    st.sidebar.write(
        f"**{profile['full_name']}**"
    )

    st.sidebar.caption(
        role_name(
            profile["role"]
        )
    )

    st.sidebar.divider()

    role = profile["role"]

    if role == "lutteur":

        pages = [
            "🏠 Accueil",
            "👤 Ma fiche",
            "🏆 Mes compétitions",
            "⚖️ Mon poids",
            "📈 Mes tests",
            "📅 Mon calendrier",
            "🎯 Mon projet",
            "🇫🇷 Mon suivi EDF",
        ]

    elif role == "entraineur":

        pages = [
            "🏠 Tableau de bord",
            "🤼 Mes athlètes",
            "🏆 Compétitions",
            "⚖️ Poids",
            "📈 Tests",
            "📅 Calendrier",
            "🎯 Projets",
            "🇫🇷 Suivi sélection",
        ]

    elif role == "selectionneur":

        pages = [
            "🏠 Mon périmètre",
            "🤼 Athlètes",
            "🏆 Compétitions",
            "🏕️ Stages",
            "📈 Progression",
            "🇫🇷 Évaluations",
            "🎯 Projets",
        ]

    elif role == "staff":

        pages = [
            "🏠 Tableau de bord",
            "🤼 Athlètes",
            "🏆 Compétitions",
            "🏕️ Stages",
            "📈 Tests",
            "🇫🇷 Suivi EDF",
        ]

    else:

        pages = [
            "🏠 Vue globale",
            "🤼 Athlètes",
            "👥 Utilisateurs",
            "🔐 Gestion des accès",
            "🏆 Compétitions",
            "🏕️ Stages",
            "🇫🇷 Sélection EDF",
            "📊 Statistiques",
            "📝 Audit",
        ]

    page = st.sidebar.radio(
        "Navigation",
        pages,
    )

    st.sidebar.divider()

    if st.sidebar.button(
        "🚪 Déconnexion",
        use_container_width=True,
    ):

        logout()

    return page


# =========================================================
# MANAGER DASHBOARD
# =========================================================

def manager_dashboard():

    st.title(
        "👑 Vue globale"
    )

    athletes = (
        supabase
        .table("athletes")
        .select("*")
        .eq("active", True)
        .execute()
        .data
    )

    users = (
        supabase
        .table("profiles")
        .select("*")
        .execute()
        .data
    )

    competitions = (
        supabase
        .table("competitions")
        .select("*")
        .execute()
        .data
    )

    stages = (
        supabase
        .table("stages")
        .select("*")
        .execute()
        .data
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Athlètes",
        len(athletes),
    )

    c2.metric(
        "Utilisateurs",
        len(users),
    )

    c3.metric(
        "Compétitions",
        len(competitions),
    )

    c4.metric(
        "Stages",
        len(stages),
    )

    st.divider()

    if athletes:

        df = pd.DataFrame(
            athletes
        )

        st.subheader(
            "Effectif national"
        )

        st.dataframe(
            df[
                [
                    "first_name",
                    "last_name",
                    "style",
                    "age_group",
                    "weight_class",
                    "collective",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# ATHLETES
# =========================================================

def athletes_page():

    st.title(
        "🤼 Athlètes"
    )

    athletes = (
        supabase
        .table("athletes")
        .select("*")
        .eq("active", True)
        .order("last_name")
        .execute()
        .data
    )

    if not athletes:

        st.info(
            "Aucun athlète accessible."
        )

        return

    df = pd.DataFrame(
        athletes
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        styles = [
            "Tous"
        ] + sorted(
            df["style"]
            .dropna()
            .unique()
            .tolist()
        )

        style = st.selectbox(
            "Style",
            styles,
        )

    with col2:

        ages = [
            "Tous"
        ] + sorted(
            df["age_group"]
            .dropna()
            .unique()
            .tolist()
        )

        age = st.selectbox(
            "Catégorie",
            ages,
        )

    with col3:

        weights = [
            "Tous"
        ] + sorted(
            df["weight_class"]
            .dropna()
            .unique()
            .tolist()
        )

        weight = st.selectbox(
            "Poids",
            weights,
        )

    if style != "Tous":

        df = df[
            df["style"] == style
        ]

    if age != "Tous":

        df = df[
            df["age_group"] == age
        ]

    if weight != "Tous":

        df = df[
            df["weight_class"] == weight
        ]

    st.dataframe(
        df[
            [
                "first_name",
                "last_name",
                "style",
                "age_group",
                "weight_class",
                "collective",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    athlete_ids = df["id"].tolist()

    if not athlete_ids:
        return

    selected = st.selectbox(
        "Ouvrir la fiche",
        athlete_ids,
        format_func=lambda x:
            next(
                (
                    f"{a['first_name']} "
                    f"{a['last_name']}"
                    for a in athletes
                    if a["id"] == x
                ),
                x,
            ),
    )

    athlete_page(
        selected
    )


# =========================================================
# ATHLETE PROFILE
# =========================================================

def athlete_page(
    athlete_id
):

    athlete = (
        supabase
        .table("athletes")
        .select("*")
        .eq("id", athlete_id)
        .single()
        .execute()
        .data
    )

    st.title(
        f"{athlete['first_name']} "
        f"{athlete['last_name']}"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Style",
        athlete.get("style") or "-"
    )

    c2.metric(
        "Âge",
        athlete.get("age_group") or "-"
    )

    c3.metric(
        "Poids",
        athlete.get("weight_class") or "-"
    )

    c4.metric(
        "Collectif",
        athlete.get("collective") or "-"
    )

    tabs = st.tabs(
        [
            "📋 Profil",
            "🏆 Résultats",
            "⚖️ Poids",
            "📈 Tests",
            "📅 Calendrier",
            "🎯 Projet",
            "🇫🇷 Sélection",
        ]
    )

    with tabs[0]:

        st.write(
            "**Club :**",
            athlete.get("club_id") or "-"
        )

        st.write(
            "**Entraîneur :**",
            athlete.get("coach_name") or "-"
        )

        st.text_area(
            "Points forts",
            athlete.get(
                "strengths"
            ) or "",
            disabled=True,
        )

        st.text_area(
            "Axes d'amélioration",
            athlete.get(
                "improvement_areas"
            ) or "",
            disabled=True,
        )

        st.text_area(
            "Objectif",
            athlete.get(
                "objective"
            ) or "",
            disabled=True,
        )

    with tabs[1]:

        results = (
            supabase
            .table("competition_results")
            .select(
                "*, competitions(name,competition_date)"
            )
            .eq(
                "athlete_id",
                athlete_id,
            )
            .execute()
            .data
        )

        if results:

            rows = []

            for result in results:

                competition = (
                    result.get(
                        "competitions"
                    ) or {}
                )

                rows.append(
                    {
                        "Date":
                            competition.get(
                                "competition_date"
                            ),

                        "Compétition":
                            competition.get(
                                "name"
                            ),

                        "Matchs":
                            result.get(
                                "matches"
                            ),

                        "Victoires":
                            result.get(
                                "wins"
                            ),

                        "Défaites":
                            result.get(
                                "losses"
                            ),

                        "Classement":
                            result.get(
                                "ranking"
                            ),

                        "Résultat":
                            result.get(
                                "result"
                            ),
                    }
                )

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "Aucun résultat."
            )

    with tabs[2]:

        weights = (
            supabase
            .table("weight_logs")
            .select("*")
            .eq(
                "athlete_id",
                athlete_id,
            )
            .order("measured_at")
            .execute()
            .data
        )

        if weights:

            df = pd.DataFrame(
                weights
            )

            df["measured_at"] = pd.to_datetime(
                df["measured_at"]
            )

            fig = px.line(
                df,
                x="measured_at",
                y="weight",
                markers=True,
                title="Évolution du poids",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        else:

            st.info(
                "Aucune donnée."
            )

    with tabs[3]:

        tests = (
            supabase
            .table("physical_tests")
            .select("*")
            .eq(
                "athlete_id",
                athlete_id,
            )
            .order("test_date")
            .execute()
            .data
        )

        if tests:

            st.dataframe(
                pd.DataFrame(
                    tests
                ),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "Aucun test."
            )

    with tabs[4]:

        events = (
            supabase
            .table("calendar_events")
            .select("*")
            .eq(
                "athlete_id",
                athlete_id,
            )
            .order("event_date")
            .execute()
            .data
        )

        if events:

            st.dataframe(
                pd.DataFrame(
                    events
                ),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "Aucun événement."
            )

    with tabs[5]:

        projects = (
            supabase
            .table("performance_projects")
            .select("*")
            .eq(
                "athlete_id",
                athlete_id,
            )
            .order(
                "updated_at",
                desc=True,
            )
            .limit(1)
            .execute()
            .data
        )

        if projects:

            project = projects[0]

            st.subheader(
                project.get(
                    "objective"
                ) or "Objectif"
            )

            st.write(
                "**Points forts**"
            )

            st.write(
                project.get(
                    "strengths"
                ) or "-"
            )

            st.write(
                "**Axes d'amélioration**"
            )

            st.write(
                project.get(
                    "improvement_areas"
                ) or "-"
            )

            st.write(
                "**Plan d'action**"
            )

            st.write(
                project.get(
                    "action_plan"
                ) or "-"
            )

        else:

            st.info(
                "Aucun projet."
            )

    with tabs[6]:

        selection_history(
            athlete_id
        )


# =========================================================
# SELECTION HISTORY
# =========================================================

def selection_history(
    athlete_id
):

    evaluations = (
        supabase
        .table(
            "selection_evaluations"
        )
        .select("*")
        .eq(
            "athlete_id",
            athlete_id,
        )
        .order(
            "evaluation_date",
            desc=True,
        )
        .execute()
        .data
    )

    if not evaluations:

        st.info(
            "Aucune évaluation."
        )

        return

    for evaluation in evaluations:

        with st.expander(
            f"{evaluation['evaluation_date']} · "
            f"{evaluation['period']}"
        ):

            st.write(
                "**Résultats TNR :**",
                evaluation.get(
                    "national_ranking_results"
                ) or "-"
            )

            st.write(
                "**Résultats internationaux :**",
                evaluation.get(
                    "international_results"
                ) or "-"
            )

            st.write(
                "**Stabilité catégorie :**",
                evaluation.get(
                    "category_stability"
                ) or "-"
            )

            st.write(
                "**Opposition :**",
                evaluation.get(
                    "opposition"
                ) or "-"
            )

            st.write(
                "**Progression :**",
                evaluation.get(
                    "progression"
                ) or "-"
            )

            st.write(
                "**Attitude :**",
                evaluation.get(
                    "attitude"
                ) or "-"
            )

            st.write(
                "**Engagement :**",
                evaluation.get(
                    "engagement"
                ) or "-"
            )

            st.write(
                "**Investissement :**",
                evaluation.get(
                    "investment"
                ) or "-"
            )

            st.write(
                "**Observation :**",
                evaluation.get(
                    "observation"
                ) or "-"
            )


# =========================================================
# SELECTION EVALUATION
# =========================================================

def selection_page():

    st.title(
        "🇫🇷 Évaluation Équipe de France"
    )

    athletes = (
        supabase
        .table("athletes")
        .select("*")
        .eq("active", True)
        .order("last_name")
        .execute()
        .data
    )

    if not athletes:

        st.info(
            "Aucun athlète."
        )

        return

    names = {
        a["id"]:
            f"{a['first_name']} "
            f"{a['last_name']} — "
            f"{a.get('style') or '-'} / "
            f"{a.get('age_group') or '-'} / "
            f"{a.get('weight_class') or '-'}"
        for a in athletes
    }

    athlete_id = st.selectbox(
        "Athlète",
        list(names.keys()),
        format_func=lambda x:
            names[x],
    )

    period = st.selectbox(
        "Période d'évaluation",
        [
            "Stage national",
            "Tournoi international",
            "Stage international",
        ],
    )

    with st.form(
        "selection_form"
    ):

        championship = st.checkbox(
            "Participation au championnat de France"
        )

        national_results = st.text_area(
            "Résultats TNR / tournois nationaux"
        )

        stability = st.text_area(
            "Stabilité et pertinence dans la catégorie"
        )

        experience = st.text_area(
            "Expérience de compétition"
        )

        international_results = st.text_area(
            "Résultats internationaux"
        )

        opposition = st.text_area(
            "Opposition rencontrée"
        )

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
            "Investissement dans le projet"
        )

        observation = st.text_area(
            "Observation du référent"
        )

        submitted = st.form_submit_button(
            "Enregistrer",
            use_container_width=True,
        )

    if submitted:

        payload = {

            "athlete_id":
                athlete_id,

            "referent_id":
                st.session_state.user.id,

            "evaluation_date":
                date.today().isoformat(),

            "period":
                period,

            "france_championship":
                championship,

            "national_ranking_results":
                national_results,

            "category_stability":
                stability,

            "previous_competition_experience":
                experience,

            "international_results":
                international_results,

            "opposition":
                opposition,

            "progression":
                progression,

            "attitude":
                attitude,

            "engagement":
                engagement,

            "investment":
                investment,

            "observation":
                observation,
        }

        try:

            supabase.table(
                "selection_evaluations"
            ).insert(
                payload
            ).execute()

            audit(
                "CREATE_SELECTION_EVALUATION",
                "selection_evaluations",
            )

            st.success(
                "Évaluation enregistrée."
            )

        except Exception as error:

            st.error(
                str(error)
            )


# =========================================================
# ACCESS MANAGEMENT
# =========================================================

def access_page():

    st.title(
        "🔐 Gestion des accès"
    )

    if not is_manager():

        st.error(
            "Cette section est réservée au Manager."
        )

        return

    users = (
        supabase
        .table("profiles")
        .select("*")
        .order("full_name")
        .execute()
        .data
    )

    if not users:
        return

    labels = {
        u["id"]:
            f"{u['full_name']} "
            f"— {role_name(u['role'])}"
        for u in users
    }

    user_id = st.selectbox(
        "Utilisateur",
        list(labels.keys()),
        format_func=lambda x:
            labels[x],
    )

    user = next(
        u
        for u in users
        if u["id"] == user_id
    )

    st.divider()

    st.subheader(
        "Profil"
    )

    roles = [
        "lutteur",
        "entraineur",
        "selectionneur",
        "staff",
        "manager",
    ]

    role = st.selectbox(
        "Rôle",
        roles,
        index=roles.index(
            user["role"]
        ),
    )

    active = st.checkbox(
        "Compte actif",
        value=user["active"],
    )

    if st.button(
        "Enregistrer le profil"
    ):

        supabase.table(
            "profiles"
        ).update(
            {
                "role":
                    role,

                "active":
                    active,
            }
        ).eq(
            "id",
            user_id,
        ).execute()

        st.success(
            "Profil enregistré."
        )

    # -----------------------------------------------------
    # SCOPE
    # -----------------------------------------------------

    if role in [
        "selectionneur",
        "staff",
    ]:

        st.divider()

        st.subheader(
            "Périmètre"
        )

        style = st.selectbox(
            "Style",
            [
                "Tous",
                "Libre",
                "Gréco-Romaine",
                "Féminine",
            ],
        )

        age = st.selectbox(
            "Catégorie d'âge",
            [
                "Toutes",
                "U15",
                "U17",
                "U20",
            ],
        )

        weights = st.multiselect(
            "Catégories de poids",
            [
                "40",
                "45",
                "48",
                "50",
                "53",
                "55",
                "57",
                "60",
                "61",
                "62",
                "65",
                "67",
                "70",
                "72",
                "74",
                "77",
                "79",
                "82",
                "86",
                "87",
                "92",
                "97",
                "125",
            ],
        )

        if st.button(
            "Enregistrer le périmètre"
        ):

            supabase.table(
                "scopes"
            ).delete().eq(
                "user_id",
                user_id,
            ).execute()

            style_value = (
                None
                if style == "Tous"
                else style
            )

            age_value = (
                None
                if age == "Toutes"
                else age
            )

            if not weights:

                weights = [None]

            for weight in weights:

                supabase.table(
                    "scopes"
                ).insert(
                    {
                        "user_id":
                            user_id,

                        "style":
                            style_value,

                        "age_group":
                            age_value,

                        "weight_class":
                            weight,
                    }
                ).execute()

            st.success(
                "Périmètre enregistré."
            )

    # -----------------------------------------------------
    # PERMISSIONS
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "Droits"
    )

    permissions = [

        "view_athlete",

        "view_competition",

        "view_weight",

        "view_tests",

        "view_project",

        "view_selection",

        "add_evaluation",

        "edit_evaluation",

        "add_result",

        "edit_result",

    ]

    existing = (
        supabase
        .table("permissions")
        .select("*")
        .eq(
            "user_id",
            user_id,
        )
        .execute()
        .data
    )

    existing_names = {
        p["permission"]
        for p in existing
        if p["enabled"]
    }

    selected_permissions = []

    for permission in permissions:

        checked = st.checkbox(
            permission,
            value=permission in existing_names,
        )

        if checked:

            selected_permissions.append(
                permission
            )

    if st.button(
        "Enregistrer les droits"
    ):

        supabase.table(
            "permissions"
        ).delete().eq(
            "user_id",
            user_id,
        ).execute()

        for permission in selected_permissions:

            supabase.table(
                "permissions"
            ).insert(
                {
                    "user_id":
                        user_id,

                    "permission":
                        permission,

                    "enabled":
                        True,
                }
            ).execute()

        audit(
            "UPDATE_PERMISSIONS",
            "permissions",
            user_id,
        )

        st.success(
            "Droits enregistrés."
        )


# =========================================================
# USER MANAGEMENT
# =========================================================

def users_page():

    st.title(
        "👥 Utilisateurs"
    )

    if not is_manager():

        st.error(
            "Accès Manager uniquement."
        )

        return

    users = (
        supabase
        .table("profiles")
        .select("*")
        .order("full_name")
        .execute()
        .data
    )

    if users:

        df = pd.DataFrame(
            users
        )

        st.dataframe(
            df[
                [
                    "full_name",
                    "email",
                    "role",
                    "active",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    st.subheader(
        "Créer un utilisateur"
    )

    name = st.text_input(
        "Nom complet"
    )

    email = st.text_input(
        "Email"
    )

    password = st.text_input(
        "Mot de passe initial",
        type="password",
    )

    role = st.selectbox(
        "Rôle",
        [
            "lutteur",
            "entraineur",
            "selectionneur",
            "staff",
            "manager",
        ],
    )

    if st.button(
        "Créer le compte"
    ):

        if not email or not password:

            st.error(
                "Email et mot de passe obligatoires."
            )

            return

        try:

            admin = get_admin_client()

            response = (
                admin.auth.admin.create_user(
                    {
                        "email":
                            email,

                        "password":
                            password,

                        "email_confirm":
                            True,

                        "user_metadata":
                            {
                                "full_name":
                                    name
                            },
                    }
                )
            )

            new_user = response.user

            supabase.table(
                "profiles"
            ).update(
                {
                    "full_name":
                        name,

                    "role":
                        role,
                }
            ).eq(
                "id",
                new_user.id,
            ).execute()

            audit(
                "CREATE_USER",
                "profile",
                new_user.id,
            )

            st.success(
                "Utilisateur créé."
            )

            st.rerun()

        except Exception as error:

            st.error(
                str(error)
            )


# =========================================================
# AUDIT
# =========================================================

def audit_page():

    st.title(
        "📝 Journal des actions"
    )

    if not is_manager():
        return

    logs = (
        supabase
        .table("audit_logs")
        .select("*")
        .order(
            "created_at",
            desc=True,
        )
        .limit(300)
        .execute()
        .data
    )

    if logs:

        st.dataframe(
            pd.DataFrame(logs),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "Aucune action enregistrée."
        )


# =========================================================
# STAGES
# =========================================================

def stages_page():

    st.title(
        "🏕️ Stages"
    )

    stages = (
        supabase
        .table("stages")
        .select("*")
        .order("start_date")
        .execute()
        .data
    )

    if stages:

        st.dataframe(
            pd.DataFrame(stages),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "Aucun stage enregistré."
        )


# =========================================================
# STATISTICS
# =========================================================

def statistics_page():

    st.title(
        "📊 Statistiques"
    )

    athletes = (
        supabase
        .table("athletes")
        .select("*")
        .eq("active", True)
        .execute()
        .data
    )

    if not athletes:
        return

    df = pd.DataFrame(
        athletes
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            df["style"]
            .value_counts()
            .reset_index(),
            x="style",
            y="count",
            title="Athlètes par style",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with col2:

        fig = px.bar(
            df["age_group"]
            .value_counts()
            .reset_index(),
            x="age_group",
            y="count",
            title="Athlètes par catégorie",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


# =========================================================
# ROUTER
# =========================================================

def router(page):

    role = st.session_state.profile[
        "role"
    ]

    if page == "🏠 Vue globale":

        manager_dashboard()

    elif page == "🏠 Tableau de bord":

        manager_dashboard()

    elif page == "🏠 Accueil":

        st.title(
            "🏠 Mon espace"
        )

        st.success(
            f"Bienvenue "
            f"{st.session_state.profile['full_name']}"
        )

    elif page == "🏠 Mon périmètre":

        athletes_page()

    elif page in [
        "🤼 Athlètes",
        "🤼 Mes athlètes",
    ]:

        athletes_page()

    elif page == "👥 Utilisateurs":

        users_page()

    elif page == "🔐 Gestion des accès":

        access_page()

    elif page in [
        "🇫🇷 Évaluations",
        "🇫🇷 Sélection EDF",
        "🇫🇷 Suivi sélection",
        "🇫🇷 Mon suivi EDF",
    ]:

        selection_page()

    elif page in [
        "🏕️ Stages",
    ]:

        stages_page()

    elif page == "📊 Statistiques":

        statistics_page()

    elif page == "📝 Audit":

        audit_page()

    else:

        st.title(page)

        st.info(
            "Module en cours de connexion."
        )


# =========================================================
# APPLICATION
# =========================================================

if st.session_state.user is None:

    login()

else:

    page = sidebar()

    router(page)
