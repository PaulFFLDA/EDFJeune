# 🇫🇷 France Lutte Jeunes

Prototype Streamlit pour le suivi des jeunes lutteurs :
- profils lutteurs / entraîneurs / sélectionneurs / administration
- compétitions et résultats
- stages
- planification nationale
- préparation physique
- tests physiques
- tableaux de bord
- calendrier personnel du lutteur
- bilan rapide de compétition (matchs, victoires, défaites, résultat, ressenti, commentaire)
- suivi de progression des tests physiques avec courbes
- courbe d'évolution du poids

## Lancer localement

```bash
pip install -r requirements.txt
streamlit run app.py
```

> Cette version utilise des données de démonstration stockées dans `st.session_state`.
> Pour une utilisation réelle, il faudra connecter une base de données persistante et mettre en place une authentification.
