import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import time
from openpyxl import Workbook


# Titre de l'application
st.title("🏋️Performances Sportives🏋️")

# 🎯 Saisie du nom de l'utilisateur
user_name = st.text_input("👤 Entre ton nom :", value="", placeholder="exemple : Alexis")

# Vérification que le nom est bien renseigné
if user_name.strip() == "":
    st.warning("⚠️ Entre ton nom pour continuer.")
    st.stop()  # Stoppe l'exécution tant qu'un nom n'est pas fourni

# 📌 Création du fichier personnalisé de sauvegarde
SAVE_FILE = f"perfs_{user_name}.xlsx"

# Zones d'affichage
status_file = st.empty()

# Barre latérale pour les fichiers supplémentaires
st.sidebar.header("🛠️ Outils supplémentaires")

# 📂 Téléchargement du fichier Excel Performances
uploaded_file = st.sidebar.file_uploader("📥 Télécharge ton fichier (.xlsx)", type=["xlsx"])

# ✅ Ajouter un bouton pour réinitialiser la sauvegarde et permettre l'importation d'un nouveau fichier
if st.sidebar.button("📥 Clique si fichier chargé non importé"):
    st.session_state.file_saved = False
    st.rerun()

# Initialisation de l'état
if "show_exercise_form" not in st.session_state:
    st.session_state.show_exercise_form = False

# 📦 Bouton pour créer un fichier vide
if st.sidebar.button("📝 Créé/Réinitialise ton fichier"):
    # Créer un fichier Excel avec une feuille temporaire
    wb = Workbook()
    ws = wb.active
    ws.title = "..."
    ws.append(["..."])  # Ligne fictive pour éviter les problèmes
    wb.save(SAVE_FILE)

    st.session_state.show_exercise_form = True
    st.sidebar.success("📝 Fichier réinitialisé. Ajoutez vos exercices.")

# ➕ Formulaire d'ajout d'exercices
if st.session_state.show_exercise_form:
    st.subheader("➕ Ajoute tes exercices")

    with st.form("form_exos"):
        liste_exos = st.text_area(
            "Entre tes exercices (un par ligne)",
            placeholder="Développé couché\nSquat\nTractions"
        )
        submit = st.form_submit_button("✅ OK")

    if submit:
        exos = [e.strip() for e in liste_exos.splitlines() if e.strip()]
        with pd.ExcelWriter(SAVE_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            workbook = writer.book

            # Supprimer la feuille temporaire si elle existe
            if "..." in workbook.sheetnames:
                std = workbook["..."]
                workbook.remove(std)

            for exo in exos:
                # Nettoyage du nom d'onglet (max 31 caractères, pas de / \ etc.)
                safe_name = exo.replace("/", "-").replace("\\", "-")[:31]
                df_empty = pd.DataFrame(columns=["Date", "Kg", "S1", "S2", "S3", "S4"])
                df_empty.to_excel(writer, index=False, sheet_name=safe_name)

        st.success("✅ Exercice(s) ajouté(s)")
        st.session_state.show_exercise_form = False
        time.sleep(2)
        st.rerun()

# 📌 Vérifie si un fichier a déjà été sauvegardé
if "file_saved" not in st.session_state:
    st.session_state.file_saved = False  # Par défaut, pas encore sauvegardé

# 📌 Si un fichier est importé et pas encore sauvegardé, on l’enregistre
if uploaded_file and not st.session_state.file_saved:
    UPLOADED_FILE_NAME = uploaded_file.name

    # Sauvegarde du fichier importé en SAVE_FILE
    with open(SAVE_FILE, "wb") as f:
        f.write(uploaded_file.getbuffer())  # Écrasement du fichier existant
    status_file.success(f"💾 {UPLOADED_FILE_NAME} a été chargé et sauvegardé comme {SAVE_FILE}.")
    time.sleep(5)
    # ✅ Marquer que le fichier a été sauvegardé pour éviter une nouvelle sauvegarde après `st.rerun()`
    st.session_state.file_saved = True
    st.rerun()  # Recharge l'application pour appliquer les changements


# 📂 Téléchargement du fichier blessures
uploaded_injuries = False
break_button = st.sidebar.checkbox("🤕 Périodes de coupures")
if break_button:
    uploaded_injuries = st.sidebar.file_uploader("📥 Télécharge ton fichier (.xlsx)", type=["xlsx"])
    if uploaded_injuries and st.sidebar.button("📑 Données coupures"):
        injuries_df = pd.read_excel(uploaded_injuries, header=0)
        st.subheader("📑 Données coupures")
        st.table(injuries_df)

# 📂 Charger les données de SAVE_FILE (déjà sauvegardé ou copie du fichier importé)
if os.path.exists(SAVE_FILE):
    if not uploaded_file :
        status_file.info(f"📂 Fichier de sauvegarde `{SAVE_FILE}` importé automatiquement")

    ## Récupération des feuilles
    sheets = pd.read_excel(SAVE_FILE, sheet_name=None, header=0)
    sheet_names = list(sheets.keys())

    # ➕ Ajouter une option pour créer un nouvel exercice
    sheet_names.append("➕ Ajoute un exercice")

    # 🎯 Menu déroulant
    selected_sheet = st.selectbox("🎯 Sélectionne un exercice", sheet_names)

    # 🔧 Si l'utilisateur veut ajouter un exercice
    if selected_sheet == "➕ Ajoute un exercice":
        new_exercise = st.text_input("🆕 Nom de ton exercice")

        if new_exercise:
            if new_exercise in sheets:
                st.warning("⚠️ Cet exercice existe déjà")
            else:
                # 🔨 Créer une nouvelle feuille avec les bonnes colonnes
                df_empty = pd.DataFrame(columns=["Date", "Kg", "S1", "S2", "S3", "S4"])
                with pd.ExcelWriter(SAVE_FILE, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
                    df_empty.to_excel(writer, index=False, sheet_name=new_exercise)
                st.success(f"✅ Exercice '{new_exercise}' ajouté.")
                selected_sheet = new_exercise
                st.rerun()  # Recharge l’application pour afficher la nouvelle feuille

    if selected_sheet != "➕ Ajoute un exercice" :
        df = sheets[selected_sheet]

        # Création du bouton à cocher pour afficher les répétitions
        rep_button = st.sidebar.checkbox("➕ répétitions")

        # 🔄 Onglets pour saisie & suivi des performances**
        tab1, tab2 = st.tabs(["💾 Enregistre tes performances", "📈 Visualise tes performances"])

        with tab1:
            # 🔄 Charger les performances sauvegardées
            xls = pd.ExcelFile(SAVE_FILE)
            if selected_sheet in xls.sheet_names:
                df_saved = pd.read_excel(SAVE_FILE, sheet_name=selected_sheet)
            else:
                df_saved = pd.DataFrame(columns=["Date", "Kg", "S1", "S2", "S3", "S4"])

            # 📝 Formulaire pour entrer les performances
            with st.form(key="new_perf"): # intérêt de key ???
                col1, col2 = st.columns(2)
                with col1:
                    new_date = st.date_input("🗓️ Date de la séance")
                    new_kg = st.number_input("🏋️‍♂️ Poids (Kg)", min_value=0.0, step=0.5)

                with col2:
                    new_s1 = st.number_input("1️⃣ Série | Répétitions", min_value=0.0, step=0.5)
                    new_s2 = st.number_input("2️⃣ Série | Répétitions", min_value=0.0, step=0.5)
                    new_s3 = st.number_input("3️⃣ Série | Répétitions", min_value=0.0, step=0.5)
                    new_s4 = st.number_input("4️⃣ Série | Répétitions", min_value=0.0, step=0.5)

                submit_button = st.form_submit_button("💾 Sauvegarder")

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
                    with pd.ExcelWriter(SAVE_FILE, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
                        df_saved.to_excel(writer, sheet_name=selected_sheet, index=False)

                    st.success("✅ Tes performances sont enregistrées !")
                    # st.rerun()  # 🚀 Recharge l'application pour afficher la mise à jour

            # Bouton de téléchargement
            with open(SAVE_FILE, "rb") as file:
                st.download_button(
                    label=f"📥 Télécharge ton fichier sous {SAVE_FILE}",
                    data=file, # indique que le fichier ouvert (SAVE_FILE) est la données à télécharger
                    file_name=SAVE_FILE, # nom du fichier téléchargé
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" # Permet au navigateur de reconnaître qu’il s’agit d’un fichier Excel
                )

            # # 📊 Affichage des performances mises à jour
            # Vérifier si les colonnes existent dans df_saved avant de les convertir en numeric
            if "Kg" in df_saved.columns:
                df_saved["Kg"] = pd.to_numeric(df_saved["Kg"], errors="coerce").round(1)

            series_columns = ["S1", "S2", "S3", "S4"]
            for col in series_columns:
                if col in df_saved.columns:
                    df_saved[col] = pd.to_numeric(df_saved[col], errors="coerce").round(1)

            # Convertir les valeurs en string avec formatage pour garantir l'affichage correct
            #df_saved = df_saved.astype(str)

            # Affichage du tableau mis à jour
            st.subheader("📊 Historique des performances")

            # Trier les performances de la plus récente à la plus ancienne
            df_saved = df_saved.sort_values(by="Date", ascending=False)

            # ✅ Convertir la colonne "Date" en datetime
            #df_saved["Date"] = pd.to_datetime(df_saved["Date"], errors="coerce")
            #df_saved["Kg"] = pd.to_numeric(df["Kg"], errors="coerce")

            # Afficher le tableau interactif
            for index, row in df_saved.iterrows():
                col1, col2, col3, col4 = st.columns([2, 2, 3, 1])

                col1.write(row["Date"].strftime("%d-%m-%Y") if pd.notna(row["Date"]) else "N/A")
                col2.write(f"{row['Kg']:.1f} Kg" if pd.notna(row["Kg"]) else "N/A")
                # ✅ Séries affichées sous format condensé
                col3.write(f"1️⃣ {row['S1']}  2️⃣ {row['S2']}  3️⃣ {row['S3']}  4️⃣ {row['S4']}")

                # Bouton de suppression
                if col4.button("❌", key=f"delete_{index}"):
                    # 🔄 Charger à nouveau les anciennes performances pour éviter d'écraser des données
                    xls = pd.ExcelFile(SAVE_FILE)
                    if selected_sheet in xls.sheet_names:
                        df_saved = pd.read_excel(SAVE_FILE, sheet_name=selected_sheet)
                    else:
                        df_saved = pd.DataFrame(columns=["Date", "Kg", "S1", "S2", "S3", "S4"])

                    # 🚮 Supprimer la ligne
                    df_saved = df_saved.drop(index)
                    st.success(f"Performance du {row['Date'].strftime('%d-%m-%Y')} supprimée.")

                    # 📂 Sauvegarder la mise à jour
                    with pd.ExcelWriter(SAVE_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                        df_saved.to_excel(writer, sheet_name=selected_sheet, index=False)

                    # 🚀 Forcer l'actualisation de la page pour voir la modification
                    st.rerun()  # 🚀 Recharge l'application pour afficher la mise à jour

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
                    # coeff = st.sidebar.number_input("coeff", min_value=0.1, format="%.2f")

                    for i_ligne in range(nb_lignes):
                        rep_moy = df.iloc[i_ligne, 2:].mean()  # moyenne des dernières colonnes de la ième ligne

                        # Ajout du coeff de l'importance des répétitions
                        # rep_moy = rep_moy * coeff

                        # Ajout des kg soulevés
                        perf_final = rep_moy * df["Kg"][i_ligne] * 4 # formule de calcul du tonage

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

                fig.update_layout(title=f"📊 Évolution des performances : {selected_sheet}")

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
    st.warning(f"⚠️ Aucun fichier {SAVE_FILE} trouvé. Télécharge ton fichier Excel ou créé en un.")

# trouver comment faire pour pouvoir partir de zéro
# changer le delta poids en 0.9+1,2, quand une case gilet leste est actionné
# ajouter une option pour ajouter des dates (injections)
# solution pour ajouter des nv exercices
# ajouter une zone pour entrer le poids (utile pour exo sans poids) et le mémoriser dans le excel afin de ne pas avoir besoin de le rentrer à chaque fois
# ajouter un bouton pour ajouter une série (ne pas être fixé à 4)
