import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Titre de l'application
st.title("Suivi des Performances Sportives")

# Barre latérale pour les fichiers supplémentaires
st.sidebar.header("Ajouter des fichiers supplémentaires")

# Téléchargement du fichier Excel Performances
uploaded_file = st.sidebar.file_uploader("Téléchargez votre fichier Excel de performances", type=["xlsx"])

# Téléchargement d'un fichier supplémentaire (ex: blessures)
uploaded_injuries = False
break_button = st.sidebar.checkbox("Ajouter coupures")
if break_button :
    uploaded_injuries = st.sidebar.file_uploader("Téléchargez un fichier Excel avec les dates de blessures", type=["xlsx"])

    # Bouton pour afficher le fichier des blessures
    if uploaded_injuries:
        if st.sidebar.button("📄 Data break"):
            injuries_df = pd.read_excel(uploaded_injuries, header=0)
            st.subheader("Données des coupures")
            st.table(injuries_df)

if uploaded_file:
    # Chargement des feuilles de l'Excel dans un dictionnaire de DataFrames
    sheets = pd.read_excel(uploaded_file, sheet_name=None, header=0)

    # Sélection d'une feuille spécifique
    selected_sheet = st.selectbox("Sélectionnez un exercice", list(sheets.keys()))

    # Récupération des données de la feuille sélectionnée
    df = sheets[selected_sheet]

    # Bouton pour afficher le fichier des performances
    if st.sidebar.button(f"📄 Data {selected_sheet}"):
        st.subheader(f"Données de l'exercice : {selected_sheet}")
        st.table(df)  # Utilisation de st.table() pour une meilleure lisibilité sur mobile

    # Création du bouton à cocher pour afficher les répétitions
    rep_button = st.sidebar.checkbox("Ajouter répétitions")

    # Création des onglets
    tab1, tab2 = st.tabs(["A venir...", "Suivi des perfs"])

    with tab1:
        st.subheader("A venir...")

    with tab2:
        # Vérification et conversion en datetime si une colonne Date existe
        if "Date" in df.columns and "Kg" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date", "Kg"])

            if rep_button :
                nb_lignes = df.shape[0]

                # Choix du coeff
                coeff = st.sidebar.number_input("coeff", min_value=0.1, format="%.2f")

                for i_ligne in range(nb_lignes):
                    rep_sum = df.iloc[i_ligne, 2:].sum()  # somme des dernières colonnes de la ième ligne

                    # Ajout du coeff de l'importance des répétitions
                    rep_sum = rep_sum * coeff

                    # Ajout des kg soulevés
                    perf_final = rep_sum + df["Kg"][i_ligne]

                    # Remplacer les valeurs de la colonne Kg par perf_final
                    df["Kg"][i_ligne] = perf_final

            # Déterminer les couleurs des segments en fonction de l'évolution
            df["Diff"] = df["Kg"].diff()
            colors = ["grey"] + ["green" if x > 0 else "red" if x < 0 else "orange" for x in df["Diff"].iloc[1:]]

            # Création du graphique avec des couleurs dynamiques
            fig = go.Figure()
            for i in range(len(df) - 1):
                fig.add_trace(go.Scatter(
                    x=df["Date"].iloc[i:i + 2],
                    y=df["Kg"].iloc[i:i + 2],
                    mode='lines',
                    line=dict(color=colors[i + 1], width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=[df["Date"].iloc[i + 1]],
                    y=[df["Kg"].iloc[i + 1]],
                    mode='markers',
                    marker=dict(size=8, color=colors[i + 1])
                ))

            fig.update_layout(title=f"Evolution des perfs (charge seulement): {selected_sheet}")
            if rep_button:
                fig.update_layout(title=f"Evolution des perfs (avec nb répétitions) : {selected_sheet}")

            # Si un fichier de blessures est ajouté, afficher des zones pour chaque période de coupure
            if uploaded_injuries:
                injuries_df = pd.read_excel(uploaded_injuries, header=0)
                injuries_df["Date_debut"] = pd.to_datetime(injuries_df["Date_debut"], errors="coerce")
                injuries_df["Date_fin"] = pd.to_datetime(injuries_df["Date_fin"], errors="coerce")

                for _, row in injuries_df.iterrows():
                    fig.add_vrect(
                        x0=row["Date_debut"], x1=row["Date_fin"],
                        fillcolor="blue", opacity=0.3, line_width=1,
                        annotation_text=row["Motif"], annotation_position="top left"
                    )
                st.warning("Les zones bleu indiquent les périodes de blessure avec leur motif.")

            # Ajout de la légende pour les couleurs
            legend_colors = {"Augmentation": "green", "Diminution": "red", "Stagnation": "orange"}
            legend_traces = [go.Scatter(
                x=[None], y=[None], mode='lines',
                line=dict(color=color, width=4),
                name=label
            ) for label, color in legend_colors.items()]

            fig.add_traces(legend_traces)
            st.plotly_chart(fig, use_container_width=True)


# A FAIRE :
# - supprimer la légende trace x du graphique
# - ajouter les répétitions dans le calcul avec une cache à cocher + un coeff modifiable
# - ajouter un moyen d'ajouter une nouvelle valeur dans le df