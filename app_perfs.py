import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 📌 Nom du fichier de sauvegarde principal
SAVE_FILE = "perfs.xlsx"

# Titre de l'application
st.title("🏋️Performances Sportives🏋️")

# Zones d'affichage
status_file = st.empty()

# Vérifier si le fichier sauvegardé existe déjà
if os.path.exists(SAVE_FILE):
    status_file.info(f"📂 Chargement du fichier de sauvegarde : `{SAVE_FILE}`")

# Barre latérale pour les fichiers supplémentaires
st.sidebar.header("🛠️ Outils supplémentaires")

# 📂 Téléchargement du fichier Excel Performances
uploaded_file = st.sidebar.file_uploader("📥 Performances (.xlsx)", type=["xlsx"])

# 📂 Téléchargement du fichier blessures
uploaded_injuries = False
break_button = st.sidebar.checkbox("🤕 Périodes de coupures")
if break_button:
    uploaded_injuries = st.sidebar.file_uploader("📥 Coupures (.xlsx)", type=["xlsx"])
    if uploaded_injuries and st.sidebar.button("📑 Données coupures"):
        injuries_df = pd.read_excel(uploaded_injuries, header=0)
        st.subheader("📑 Données coupures")
        st.table(injuries_df)

# 📌 Si un fichier est importé, on l’enregistre localement
if uploaded_file:
    # Utiliser le même nom de fichier que celui importé
    SAVE_FILE = uploaded_file.name
    # Sauvegarde du fichier importé pour éviter d’avoir à le réimporter la prochaine fois (mémoire de l'application temporaire)
    with open(SAVE_FILE, "wb") as f:
         f.write(uploaded_file.getbuffer())  # Écrasement du fichier existant
    status_file.success(f"💾 Le fichier {SAVE_FILE} a été chargé et sauvegardé.")

# 📂 Charger les données depuis le fichier de sauvegarde
if os.path.exists(SAVE_FILE):
    sheets = pd.read_excel(SAVE_FILE, sheet_name=None, header=0)
    selected_sheet = st.selectbox("🎯 Sélectionnez un exercice", list(sheets.keys()))
    df = sheets[selected_sheet]

    # Création du bouton à cocher pour afficher les répétitions
    rep_button = st.sidebar.checkbox("➕ répétitions")

    # 🔄 **Onglets pour saisie & suivi des performances**
    tab1, tab2 = st.tabs(["💾 Enregistre tes performances", "📈 Visualise tes performances"])

    with tab1:

        # 🔄 Charger les performances sauvegardées
        xls = pd.ExcelFile(SAVE_FILE)
        if selected_sheet in xls.sheet_names:
            df_saved = pd.read_excel(SAVE_FILE, sheet_name=selected_sheet)
        else:
            df_saved = pd.DataFrame(columns=["Date", "Kg", "S1", "S2", "S3", "S4"])

        # 📝 Formulaire pour entrer les performances
        with st.form(key="new_perf"):
            col1, col2 = st.columns(2)
            with col1:
                new_date = st.date_input("🗓️ Date de la séance")
                new_kg = st.number_input("🏋️‍♂️ Poids (Kg)", min_value=0.0, step=0.5)

            with col2:
                new_s1 = st.number_input("Série 1️⃣", min_value=0, step=1)
                new_s2 = st.number_input("Série 2️⃣", min_value=0, step=1)
                new_s3 = st.number_input("Série 3️⃣", min_value=0, step=1)
                new_s4 = st.number_input("Série 4️⃣", min_value=0, step=1)

            submit_button = st.form_submit_button("➕ Enregistrer cette performance")

            if submit_button:
                # Ajouter la nouvelle performance au DataFrame
                new_data = pd.DataFrame({
                    "Date": [new_date],
                    "Kg": [new_kg],
                    "S1": [new_s1],
                    "S2": [new_s2],
                    "S3": [new_s3],
                    "S4": [new_s4]
                })
                df_saved = pd.concat([df_saved, new_data], ignore_index=True)

                # ✅ Convertir la colonne Date
                df_saved["Date"] = pd.to_datetime(df_saved["Date"])

                # 📂 Sauvegarde du fichier mis à jour
                with pd.ExcelWriter(SAVE_FILE, engine="openpyxl", mode="w") as writer:
                    for sheet_name, sheet_df in sheets.items():
                        if sheet_name == selected_sheet:
                            sheet_df = df_saved
                        sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)

                st.success("✅ Performance enregistrée avec succès !")

        # Vérifier si le fichier existe avant d'afficher le bouton de téléchargement
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "rb") as file:
                st.download_button(
                    label="📥 Télécharger le fichier Excel",
                    data=file,
                    file_name=SAVE_FILE,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        # # 📊 Affichage des performances mises à jour
        # Vérifier si les colonnes existent dans df_saved avant d'appliquer les modifications
        if "Kg" in df_saved.columns:
            df_saved["Kg"] = pd.to_numeric(df_saved["Kg"], errors="coerce").round(1)

        series_columns = ["S1", "S2", "S3", "S4"]
        for col in series_columns:
            if col in df_saved.columns:
                df_saved[col] = pd.to_numeric(df_saved[col], errors="coerce").round(1)

        # Convertir les valeurs en string avec formatage pour garantir l'affichage correct
        df_saved = df_saved.astype(str)

        # Trier les performances de la plus récente à la plus ancienne
        df_saved = df_saved.sort_values(by="Date", ascending=False)

        # Affichage du tableau mis à jour
        st.subheader("📊 Historique des performances")

        # ✅ Convertir la colonne "Date" en datetime
        df_saved["Date"] = pd.to_datetime(df_saved["Date"], errors="coerce")
        df_saved["Kg"] = pd.to_numeric(df["Kg"], errors="coerce")

        # Trier pour afficher les plus récentes en haut
        df_saved = df_saved.sort_values(by="Date", ascending=False)

        # Afficher le tableau interactif
        for index, row in df_saved.iterrows():
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 2, 2, 2, 2, 1])

            col1.write(row["Date"].strftime("%Y-%m-%d") if pd.notna(row["Date"]) else "N/A")
            col2.write(f"{row['Kg']:.1f} Kg")
            col3.write(float(row["S1"]))
            col4.write(float(row["S2"]))
            col5.write(float(row["S3"]))
            col6.write(float(row["S4"]))

            # Bouton de suppression
            if col7.button("❌", key=f"delete_{index}"):
                df_saved = df_saved.drop(index)
                st.success(f"Performance du {row['Date'].strftime('%Y-%m-%d')} supprimée.")

                # Sauvegarde du fichier Excel mis à jour
                with pd.ExcelWriter(SAVE_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                    df_saved.to_excel(writer, sheet_name=selected_sheet, index=False)

                st.rerun()  # 🚀 Recharge l'application pour afficher la mise à jour
        # st.table(df_saved)

    with tab2:

        # 🔄 Charger les données mises à jour
        df = pd.read_excel(SAVE_FILE, sheet_name=selected_sheet, header=0)

        ## Conversion en datetime (date) et en numeric (kg)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Kg"] = pd.to_numeric(df["Kg"], errors="coerce")

        if "Date" in df.columns and "Kg" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date", "Kg"]).sort_values("Date") # ?? utilité

            ## Paramétrage du bouton des répétitions
            if rep_button :
                nb_lignes = df.shape[0]

                # Choix du coeff
                coeff = st.sidebar.number_input("coeff", min_value=0.1, format="%.2f")

                for i_ligne in range(nb_lignes):
                    rep_moy = df.iloc[i_ligne, 2:].mean()  # moyenne des dernières colonnes de la ième ligne

                    # Ajout du coeff de l'importance des répétitions
                    rep_moy = rep_moy * coeff

                    # Ajout des kg soulevés
                    perf_final = rep_moy + df["Kg"][i_ligne]

                    # Remplacer les valeurs de la colonne Kg par perf_final
                    df["Kg"][i_ligne] = perf_final

            # 🔄 Déterminer les couleurs des segments
            df["Diff"] = df["Kg"].diff()
            colors = ["grey"] + ["green" if x > 0 else "red" if x < 0 else "orange" for x in df["Diff"].iloc[1:]]

            # 📊 Création du graphique
            fig = go.Figure()
            for i in range(len(df) - 1):
                fig.add_trace(go.Scatter(
                    x=df["Date"].iloc[i:i + 2],
                    y=df["Kg"].iloc[i:i + 2],
                    mode='lines',
                    line=dict(color=colors[i + 1], width=2),
                    showlegend=False
                ))
                fig.add_trace(go.Scatter(
                    x=[df["Date"].iloc[i + 1]],
                    y=[df["Kg"].iloc[i + 1]],
                    mode='markers',
                    marker=dict(size=8, color=colors[i + 1]),
                    showlegend=False
                ))

            fig.update_layout(title=f"📊 Évolution des perfs : {selected_sheet}")

            # 📍 Affichage des blessures sous forme de zones colorées
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

            # 🔄 Ajout de la légende personnalisée
            legend_colors = {"Augmentation": "green", "Diminution": "red", "Stagnation": "orange"}
            legend_traces = [go.Scatter(
                x=[None], y=[None], mode='lines',
                line=dict(color=color, width=4),
                name=label
            ) for label, color in legend_colors.items()]

            fig.add_traces(legend_traces)
            st.plotly_chart(fig, use_container_width=True)

else:
    st.warning(f"⚠️ Aucun fichier {SAVE_FILE} trouvé. Télécharge ton fichier Excel.")

# supprimer/modifier un exercice
#
