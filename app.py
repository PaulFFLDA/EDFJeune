import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(
    page_title="France Lutte Jeunes",
    page_icon="🇫🇷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# DONNÉES DE DÉMO
# -----------------------------
if "competitions" not in st.session_state:
    st.session_state.competitions = pd.DataFrame([
        {"Date": "2026-10-04", "Athlète": "Lucas Martin", "Compétition": "Tournoi National U17", "Catégorie": "71 kg", "Style": "Libre", "Résultat": "2e", "Victoires": 4, "Défaites": 1},
        {"Date": "2026-10-18", "Athlète": "Hugo Dupont", "Compétition": "Tournoi National U17", "Catégorie": "65 kg", "Style": "Libre", "Résultat": "1er", "Victoires": 5, "Défaites": 0},
        {"Date": "2026-11-08", "Athlète": "Lucas Martin", "Compétition": "Championnat Régional", "Catégorie": "71 kg", "Style": "Libre", "Résultat": "1er", "Victoires": 3, "Défaites": 0},
    ])

if "stages" not in st.session_state:
    st.session_state.stages = pd.DataFrame([
        {"Début": "2026-10-25", "Fin": "2026-10-29", "Stage": "Stage National U17", "Lieu": "Houlgate", "Collectif": "U17 Libre", "Statut": "Planifié"},
        {"Début": "2026-12-14", "Fin": "2026-12-18", "Stage": "Stage Préparation", "Lieu": "INSEP", "Collectif": "U17/U20", "Statut": "Planifié"},
    ])

if "planning" not in st.session_state:
    st.session_state.planning = pd.DataFrame([
        {"Date": "2026-10-05", "Type": "Préparation physique", "Intitulé": "Force / puissance", "Collectif": "U17", "Objectif": "Développement"},
        {"Date": "2026-10-10", "Type": "Compétition", "Intitulé": "Tournoi National", "Collectif": "U17", "Objectif": "Évaluation"},
        {"Date": "2026-10-25", "Type": "Stage", "Intitulé": "Stage National U17", "Collectif": "U17", "Objectif": "Technique + opposition"},
        {"Date": "2026-11-12", "Type": "Test", "Intitulé": "Tests physiques nationaux", "Collectif": "U17", "Objectif": "Évaluation"},
    ])

if "tests" not in st.session_state:
    st.session_state.tests = pd.DataFrame([
        {"Athlète": "Lucas Martin", "Test": "Saut horizontal", "Date": "2026-09-15", "Résultat": "2.24 m", "Précédent": "2.18 m"},
        {"Athlète": "Lucas Martin", "Test": "Tractions", "Date": "2026-09-15", "Résultat": "15", "Précédent": "13"},
        {"Athlète": "Lucas Martin", "Test": "Sprint 30 m", "Date": "2026-09-15", "Résultat": "4.41 s", "Précédent": "4.48 s"},
        {"Athlète": "Hugo Dupont", "Test": "Saut horizontal", "Date": "2026-09-15", "Résultat": "2.31 m", "Précédent": "2.25 m"},
    ])

if "personal_calendar" not in st.session_state:
    st.session_state.personal_calendar = pd.DataFrame([
        {"Athlète": "Lucas Martin", "Date": "2026-10-04", "Type": "Compétition", "Intitulé": "Tournoi National U17", "Objectif": "Évaluation"},
        {"Athlète": "Lucas Martin", "Date": "2026-10-25", "Type": "Stage", "Intitulé": "Stage National U17", "Objectif": "Technique + opposition"},
        {"Athlète": "Lucas Martin", "Date": "2026-11-12", "Type": "Test", "Intitulé": "Tests physiques", "Objectif": "Évaluation"},
    ])

if "weight_log" not in st.session_state:
    st.session_state.weight_log = pd.DataFrame([
        {"Athlète": "Lucas Martin", "Date": "2026-09-01", "Poids": 70.8},
        {"Athlète": "Lucas Martin", "Date": "2026-09-15", "Poids": 70.4},
        {"Athlète": "Lucas Martin", "Date": "2026-10-01", "Poids": 69.9},
        {"Athlète": "Hugo Dupont", "Date": "2026-09-01", "Poids": 65.4},
        {"Athlète": "Hugo Dupont", "Date": "2026-10-01", "Poids": 65.0},
    ])

if "athletes" not in st.session_state:
    st.session_state.athletes = pd.DataFrame([
        {"Nom": "Lucas Martin", "Collectif": "U17", "Style": "Libre", "Catégorie": "71 kg", "Club": "Club Démo"},
        {"Nom": "Hugo Dupont", "Collectif": "U17", "Style": "Libre", "Catégorie": "65 kg", "Club": "Club Démo"},
        {"Nom": "Thomas Bernard", "Collectif": "U17", "Style": "Gréco", "Catégorie": "67 kg", "Club": "Club Démo"},
        {"Nom": "Enzo Morel", "Collectif": "U20", "Style": "Libre", "Catégorie": "74 kg", "Club": "Club Démo"},
    ])

# -----------------------------
# STYLE
# -----------------------------
st.markdown("""
<style>
    .main-title {font-size: 2.4rem; font-weight: 800; margin-bottom: 0;}
    .subtitle {color: #6b7280; margin-top: 0;}
    .card {padding: 18px; border-radius: 14px; border: 1px solid #e5e7eb;
           background: rgba(255,255,255,.03); margin-bottom: 12px;}
    .small {font-size: .85rem; color: #6b7280;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("🇫🇷 France Lutte Jeunes")
profil = st.sidebar.selectbox(
    "Profil",
    ["Lutteur / Lutteuse", "Entraîneur / Club", "Sélectionneur / Staff", "Administration"]
)

pages = {
    "Lutteur / Lutteuse": [
        "🏠 Mon tableau de bord", "📅 Mon calendrier", "🏆 Mes compétitions",
        "🏕️ Mes stages", "🏋️ Ma préparation physique", "⚖️ Mon poids", "🧪 Mes tests"
    ],
    "Entraîneur / Club": [
        "🏠 Tableau de bord club", "👥 Mes athlètes", "🏆 Compétitions",
        "🧪 Tests physiques", "📅 Calendrier"
    ],
    "Sélectionneur / Staff": [
        "🏠 Tableau de bord national", "👥 Collectifs", "📅 Planification",
        "🏕️ Stages", "🏆 Compétitions", "🏋️ Préparation physique", "🧪 Tests"
    ],
    "Administration": [
        "🏠 Vue générale", "👥 Athlètes", "📅 Planning", "📊 Statistiques"
    ],
}
page = st.sidebar.radio("Navigation", pages[profil])

st.sidebar.divider()
st.sidebar.caption("Prototype V1 — données de démonstration")
st.sidebar.caption("⚠️ Ne pas utiliser avec de vraies données personnelles en production.")

# -----------------------------
# HELPERS
# -----------------------------
def kpi(label, value, help_text=""):
    st.metric(label, value, help=help_text)

def add_competition():
    st.subheader("Ajouter un résultat de compétition")
    with st.form("competition_form"):
        c1, c2 = st.columns(2)
        with c1:
            athlete = st.text_input("Athlète", value="Lucas Martin")
            comp = st.text_input("Compétition")
            comp_date = st.date_input("Date", date.today())
            category = st.text_input("Catégorie", "71 kg")
        with c2:
            style = st.selectbox("Style", ["Libre", "Gréco", "Féminine"])
            result = st.text_input("Classement / résultat")
            wins = st.number_input("Victoires", min_value=0, step=1)
            losses = st.number_input("Défaites", min_value=0, step=1)
        submitted = st.form_submit_button("💾 Enregistrer")
    if submitted:
        new_row = pd.DataFrame([{
            "Date": str(comp_date), "Athlète": athlete, "Compétition": comp,
            "Catégorie": category, "Style": style, "Résultat": result,
            "Victoires": int(wins), "Défaites": int(losses)
        }])
        st.session_state.competitions = pd.concat(
            [st.session_state.competitions, new_row], ignore_index=True
        )
        st.success("Résultat enregistré.")

# -----------------------------
# LUTTEUR
# -----------------------------
if profil == "Lutteur / Lutteuse":

    athlete = st.sidebar.selectbox("Mon profil", st.session_state.athletes["Nom"].tolist())
    athlete_data = st.session_state.athletes[st.session_state.athletes["Nom"] == athlete].iloc[0]

    if page == "🏠 Mon tableau de bord":
        st.markdown('<div class="main-title">🇫🇷 Mon parcours sportif</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="subtitle">{athlete} — {athlete_data["Collectif"]} · {athlete_data["Style"]} · {athlete_data["Catégorie"]}</div>', unsafe_allow_html=True)
        st.write("")

        c1, c2, c3, c4 = st.columns(4)
        hist = st.session_state.competitions[st.session_state.competitions["Athlète"] == athlete]
        tests = st.session_state.tests[st.session_state.tests["Athlète"] == athlete]
        c1.metric("Compétitions", len(hist))
        c2.metric("Stages planifiés", len(st.session_state.stages))
        c3.metric("Tests enregistrés", len(tests))
        c4.metric("Collectif", athlete_data["Collectif"])

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔔 À faire")
            st.info("Renseigner le bilan de ta dernière compétition")
            st.warning("Test physique national prévu le 12/11/2026")
            st.success("Convocation au Stage National U17 disponible")
        with col2:
            st.subheader("🎯 Prochaines échéances")
            st.write("🏕️ **25–29 octobre** — Stage National U17")
            st.write("🏆 **8 novembre** — Championnat Régional")
            st.write("🧪 **12 novembre** — Tests physiques")

        st.subheader("📈 Mes derniers résultats")
        st.dataframe(hist.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)

    elif page == "📅 Mon calendrier":
        st.title("📅 Mon calendrier")
        st.caption("Tu peux ajouter tes propres compétitions, stages et autres échéances.")

        mine = st.session_state.personal_calendar[
            st.session_state.personal_calendar["Athlète"] == athlete
        ].sort_values("Date")
        st.dataframe(mine, use_container_width=True, hide_index=True)

        with st.form("personal_calendar_form"):
            st.subheader("➕ Ajouter une échéance")
            d = st.date_input("Date", date.today())
            typ = st.selectbox("Type", ["Compétition", "Stage", "Entraînement", "Préparation physique", "Test", "Récupération"])
            title = st.text_input("Intitulé")
            objective = st.text_input("Objectif", "")
            submitted = st.form_submit_button("Ajouter à mon calendrier")
        if submitted:
            row = pd.DataFrame([{
                "Athlète": athlete, "Date": str(d), "Type": typ,
                "Intitulé": title, "Objectif": objective
            }])
            st.session_state.personal_calendar = pd.concat(
                [st.session_state.personal_calendar, row], ignore_index=True
            )
            st.success("Échéance ajoutée à ton calendrier.")

    elif page == "🏆 Mes compétitions":
        st.title("🏆 Mes compétitions")
        hist = st.session_state.competitions[st.session_state.competitions["Athlète"] == athlete]
        st.dataframe(hist.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("📝 Bilan rapide de compétition")
        st.caption("Le bilan est volontairement simple : quelques chiffres et un court commentaire.")

        with st.form("quick_competition_bilan"):
            c1, c2 = st.columns(2)
            with c1:
                d = st.date_input("Date de compétition", date.today())
                name = st.text_input("Compétition", "")
                category = st.text_input("Catégorie", athlete_data["Catégorie"])
            with c2:
                matches = st.number_input("Nombre de matchs", min_value=0, step=1, value=1)
                wins = st.number_input("Victoires", min_value=0, step=1, value=0)
                losses = st.number_input("Défaites", min_value=0, step=1, value=0)

            result = st.text_input("Résultat / classement", "Ex. 2e, 1/4 finale, vainqueur…")
            feeling = st.select_slider("Bilan de la compétition", options=["Difficile", "Moyen", "Bien", "Très bien"], value="Bien")
            comment = st.text_area("Petit bilan", placeholder="2 ou 3 phrases : ce qui a bien fonctionné, ce qui est à améliorer…")
            submitted = st.form_submit_button("💾 Enregistrer le bilan")

        if submitted:
            row = pd.DataFrame([{
                "Date": str(d), "Athlète": athlete, "Compétition": name,
                "Catégorie": category, "Style": athlete_data["Style"],
                "Résultat": result, "Victoires": int(wins), "Défaites": int(losses),
                "Matchs": int(matches), "Bilan": feeling, "Commentaire": comment
            }])
            st.session_state.competitions = pd.concat(
                [st.session_state.competitions, row], ignore_index=True
            )
            st.success("Bilan de compétition enregistré.")

        st.subheader("📌 Résumé")
        if len(hist):
            last = hist.sort_values("Date", ascending=False).iloc[0]
            total = int(last.get("Victoires", 0)) + int(last.get("Défaites", 0))
            st.metric("Dernier résultat", last["Résultat"])
            c1, c2, c3 = st.columns(3)
            c1.metric("Matchs", total)
            c2.metric("Victoires", int(last["Victoires"]))
            c3.metric("Défaites", int(last["Défaites"]))

    elif page == "🏕️ Mes stages":
        st.title("🏕️ Mes stages")
        st.dataframe(st.session_state.stages, use_container_width=True, hide_index=True)
        st.subheader("Bilan de stage")
        with st.form("stage_bilan"):
            stage = st.selectbox("Stage", st.session_state.stages["Stage"].tolist())
            feeling = st.slider("État de forme", 1, 10, 7)
            learning = st.text_area("Ce que j'ai appris")
            improvement = st.text_area("Point à améliorer")
            submitted = st.form_submit_button("Enregistrer mon bilan")
        if submitted:
            st.success(f"Bilan du {stage} enregistré. Forme : {feeling}/10.")

    elif page == "🏋️ Ma préparation physique":
        st.title("🏋️ Ma préparation physique")
        st.info("Cycle actuel : Force / Puissance — 4 semaines")
        sessions = pd.DataFrame([
            {"Jour": "Lundi", "Séance": "Force", "Contenu": "Squat 4×5 · Tractions 4×6", "RPE cible": 7},
            {"Jour": "Mercredi", "Séance": "Puissance", "Contenu": "Sauts 5×5 · Lancers medecine-ball", "RPE cible": 8},
            {"Jour": "Vendredi", "Séance": "Spécifique lutte", "Contenu": "Circuit 3×4 min", "RPE cible": 8},
        ])
        st.dataframe(sessions, use_container_width=True, hide_index=True)
        st.subheader("📈 Évolution des tests physiques")
        mytests = st.session_state.tests[st.session_state.tests["Athlète"] == athlete].copy()
        if len(mytests):
            st.caption("Les tests sont affichés par exercice lorsque les résultats sont numériques.")
            numeric_tests = []
            for _, r in mytests.iterrows():
                try:
                    value = float(str(r["Résultat"]).replace(",", ".").split()[0])
                    numeric_tests.append({"Date": pd.to_datetime(r["Date"]), "Test": r["Test"], "Valeur": value})
                except (ValueError, TypeError):
                    pass
            if numeric_tests:
                nt = pd.DataFrame(numeric_tests)
                selected_test = st.selectbox("Test à suivre", sorted(nt["Test"].unique()))
                series = nt[nt["Test"] == selected_test].sort_values("Date").set_index("Date")[["Valeur"]]
                st.line_chart(series, y="Valeur", height=280)
            else:
                st.info("Ajoute des résultats numériques pour afficher une courbe d'évolution.")
        else:
            st.info("Aucun test enregistré.")

        st.subheader("Retour séance")
        with st.form("training_feedback"):
            session = st.selectbox("Séance", sessions["Séance"].tolist())
            done = st.checkbox("Séance réalisée")
            rpe = st.slider("RPE", 1, 10, 7)
            comment = st.text_area("Commentaire")
            submitted = st.form_submit_button("Enregistrer")
        if submitted:
            st.success(f"{session} — RPE {rpe}/10 enregistré.")

    elif page == "⚖️ Mon poids":
        st.title("⚖️ Suivi du poids")
        st.caption("Historique personnel du poids. Les données servent au suivi de l'évolution, pas à une recommandation médicale.")

        mine = st.session_state.weight_log[
            st.session_state.weight_log["Athlète"] == athlete
        ].copy()
        mine["Date"] = pd.to_datetime(mine["Date"])
        mine = mine.sort_values("Date")

        if len(mine):
            current = float(mine.iloc[-1]["Poids"])
            first = float(mine.iloc[0]["Poids"])
            delta = current - first
            c1, c2 = st.columns(2)
            c1.metric("Dernier poids", f"{current:.1f} kg")
            c2.metric("Évolution depuis le premier relevé", f"{delta:+.1f} kg")

            chart = mine.set_index("Date")[["Poids"]]
            st.line_chart(chart, y="Poids", height=320)

            st.subheader("Ajouter un relevé")
            with st.form("weight_form"):
                d = st.date_input("Date", date.today())
                weight = st.number_input("Poids (kg)", min_value=30.0, max_value=200.0, value=current, step=0.1)
                submitted = st.form_submit_button("💾 Enregistrer le poids")
            if submitted:
                row = pd.DataFrame([{"Athlète": athlete, "Date": str(d), "Poids": float(weight)}])
                st.session_state.weight_log = pd.concat(
                    [st.session_state.weight_log, row], ignore_index=True
                )
                st.success("Relevé de poids enregistré.")
                st.rerun()
        else:
            st.info("Aucun relevé de poids pour cet athlète.")
            with st.form("first_weight_form"):
                d = st.date_input("Date", date.today())
                weight = st.number_input("Poids (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
                submitted = st.form_submit_button("Enregistrer")
            if submitted:
                row = pd.DataFrame([{"Athlète": athlete, "Date": str(d), "Poids": float(weight)}])
                st.session_state.weight_log = pd.concat([st.session_state.weight_log, row], ignore_index=True)
                st.rerun()

    elif page == "🧪 Mes tests":
        st.title("🧪 Mes tests physiques")
        mytests = st.session_state.tests[st.session_state.tests["Athlète"] == athlete]
        st.dataframe(mytests.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
        st.subheader("Renseigner un test")
        with st.form("test_form"):
            test = st.selectbox("Test", ["Saut horizontal", "Tractions", "Sprint 30 m", "Test spécifique lutte", "Gainage"])
            result = st.text_input("Résultat")
            test_date = st.date_input("Date", date.today())
            submitted = st.form_submit_button("💾 Enregistrer le test")
        if submitted:
            row = pd.DataFrame([{
                "Athlète": athlete, "Test": test, "Date": str(test_date),
                "Résultat": result, "Précédent": "-"
            }])
            st.session_state.tests = pd.concat([st.session_state.tests, row], ignore_index=True)
            st.success("Test enregistré.")

# -----------------------------
# ENTRAÎNEUR
# -----------------------------
elif profil == "Entraîneur / Club":

    if page == "🏠 Tableau de bord club":
        st.title("🏠 Tableau de bord club")
        c1, c2, c3 = st.columns(3)
        c1.metric("Athlètes", len(st.session_state.athletes))
        c2.metric("Résultats", len(st.session_state.competitions))
        c3.metric("Tests", len(st.session_state.tests))
        st.subheader("👥 Mes athlètes")
        st.dataframe(st.session_state.athletes, use_container_width=True, hide_index=True)

    elif page == "👥 Mes athlètes":
        st.title("👥 Mes athlètes")
        st.dataframe(st.session_state.athletes, use_container_width=True, hide_index=True)

    elif page == "🏆 Compétitions":
        st.title("🏆 Résultats des compétitions")
        st.dataframe(st.session_state.competitions.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)

    elif page == "🧪 Tests physiques":
        st.title("🧪 Tests physiques")
        st.dataframe(st.session_state.tests.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)

    elif page == "📅 Calendrier":
        st.title("📅 Calendrier")
        st.dataframe(st.session_state.planning.sort_values("Date"), use_container_width=True, hide_index=True)

# -----------------------------
# STAFF NATIONAL
# -----------------------------
elif profil == "Sélectionneur / Staff":

    if page == "🏠 Tableau de bord national":
        st.title("🇫🇷 Tableau de bord national")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Athlètes suivis", len(st.session_state.athletes))
        c2.metric("Compétitions", len(st.session_state.competitions))
        c3.metric("Stages", len(st.session_state.stages))
        c4.metric("Tests", len(st.session_state.tests))

        st.subheader("👥 Collectifs")
        summary = st.session_state.athletes.groupby("Collectif").size().reset_index(name="Nombre")
        st.dataframe(summary, use_container_width=True, hide_index=True)

        st.subheader("⚠️ Suivi à compléter")
        st.warning("4 athlètes doivent encore renseigner leur dernier résultat.")
        st.info("3 athlètes doivent renseigner leur prochain test physique.")

    elif page == "👥 Collectifs":
        st.title("👥 Gestion des collectifs")
        collectif = st.selectbox("Collectif", sorted(st.session_state.athletes["Collectif"].unique()))
        df = st.session_state.athletes[st.session_state.athletes["Collectif"] == collectif]
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif page == "📅 Planification":
        st.title("📅 Planification nationale")
        st.dataframe(st.session_state.planning.sort_values("Date"), use_container_width=True, hide_index=True)
        st.subheader("➕ Ajouter une échéance")
        with st.form("planning_form"):
            d = st.date_input("Date", date.today())
            typ = st.selectbox("Type", ["Compétition", "Stage", "Préparation physique", "Test", "Récupération"])
            name = st.text_input("Intitulé")
            collective = st.text_input("Collectif", "U17")
            objective = st.text_input("Objectif")
            submitted = st.form_submit_button("Ajouter")
        if submitted:
            row = pd.DataFrame([{"Date": str(d), "Type": typ, "Intitulé": name, "Collectif": collective, "Objectif": objective}])
            st.session_state.planning = pd.concat([st.session_state.planning, row], ignore_index=True)
            st.success("Échéance ajoutée.")

    elif page == "🏕️ Stages":
        st.title("🏕️ Stages")
        st.dataframe(st.session_state.stages.sort_values("Début"), use_container_width=True, hide_index=True)
        with st.form("stage_form"):
            start = st.date_input("Début", date.today())
            end = st.date_input("Fin", date.today() + timedelta(days=4))
            name = st.text_input("Nom du stage")
            place = st.text_input("Lieu")
            collective = st.text_input("Collectif", "U17")
            submitted = st.form_submit_button("Créer le stage")
        if submitted:
            row = pd.DataFrame([{"Début": str(start), "Fin": str(end), "Stage": name, "Lieu": place, "Collectif": collective, "Statut": "Planifié"}])
            st.session_state.stages = pd.concat([st.session_state.stages, row], ignore_index=True)
            st.success("Stage créé.")

    elif page == "🏆 Compétitions":
        st.title("🏆 Suivi des compétitions")
        st.dataframe(st.session_state.competitions.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)

    elif page == "🏋️ Préparation physique":
        st.title("🏋️ Planification de la préparation physique")
        st.info("Cette V1 permet de visualiser les cycles. La V2 pourra gérer les séances individuelles, exercices, séries, charges et RPE.")
        cycles = pd.DataFrame([
            {"Cycle": "S1", "Objectif": "Adaptation", "Durée": "1 semaine", "Intensité": "Modérée"},
            {"Cycle": "S2", "Objectif": "Développement force", "Durée": "1 semaine", "Intensité": "Élevée"},
            {"Cycle": "S3", "Objectif": "Puissance", "Durée": "1 semaine", "Intensité": "Élevée"},
            {"Cycle": "S4", "Objectif": "Récupération", "Durée": "1 semaine", "Intensité": "Faible"},
        ])
        st.dataframe(cycles, use_container_width=True, hide_index=True)

    elif page == "🧪 Tests":
        st.title("🧪 Tests physiques")
        st.dataframe(st.session_state.tests.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
        athlete_filter = st.selectbox("Athlète", ["Tous"] + st.session_state.athletes["Nom"].tolist())
        if athlete_filter != "Tous":
            st.dataframe(
                st.session_state.tests[st.session_state.tests["Athlète"] == athlete_filter],
                use_container_width=True,
                hide_index=True,
            )

# -----------------------------
# ADMIN
# -----------------------------
else:

    if page == "🏠 Vue générale":
        st.title("🏠 Administration")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Athlètes", len(st.session_state.athletes))
        c2.metric("Compétitions", len(st.session_state.competitions))
        c3.metric("Stages", len(st.session_state.stages))
        c4.metric("Tests", len(st.session_state.tests))
        st.subheader("État du système")
        st.success("Prototype opérationnel")
        st.info("La prochaine étape est de connecter une base de données persistante et une authentification.")

    elif page == "👥 Athlètes":
        st.title("👥 Athlètes")
        st.dataframe(st.session_state.athletes, use_container_width=True, hide_index=True)

    elif page == "📅 Planning":
        st.title("📅 Planning")
        st.dataframe(st.session_state.planning.sort_values("Date"), use_container_width=True, hide_index=True)

    elif page == "📊 Statistiques":
        st.title("📊 Statistiques")
        st.subheader("Athlètes par collectif")
        st.bar_chart(st.session_state.athletes["Collectif"].value_counts())
        st.subheader("Compétitions par athlète")
        st.bar_chart(st.session_state.competitions["Athlète"].value_counts())

st.divider()
st.caption("France Lutte Jeunes — prototype Streamlit")
