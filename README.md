# -Dashboard-Immobilier-Paris ( Paris 20 Arrondissements ) - 2 METHODES ( HTTP - LOCAL ) ( Données 2024 )
🏙️ Dashboard Immobilier Paris - ℹ️ Données réelles DVF 2024 pour l'arrondissement de Paris 1er Arrondissement (INSEE 75101), provenant de data.gouv.fr
<img width="662" height="465" alt="Screenshot_2025-10-15_17-03-02" src="https://github.com/user-attachments/assets/91f77272-c666-457f-b3f8-f53cc18071da" />

# EXAMPLE
<img width="1280" height="1024" alt="Screenshot_2025-10-15_17-01-36" src="https://github.com/user-attachments/assets/068c3b00-f5a6-41df-977a-2d9d1fc00f51" />
<img width="1280" height="1024" alt="Screenshot_2025-10-15_17-02-27" src="https://github.com/user-attachments/assets/0daf23ba-cfb1-4a5f-a3d6-7dd60077e7bd" />

# INSTALL DEPENDENCIES 

    pip install beautifulsoup4 streamlit pandas requests plotly

# RUN PROGRAM

    streamlit run Dashboard.py

# METHODE LOCAL ( FICHIER LOCAL )


# TÉLÉCHARGEMENT " dvf_2024.csv " avec CURL 

    curl -L -o dvf_2024.csv.gz "https://files.data.gouv.fr/geo-dvf/latest/csv/2024/full.csv.gz"

# RUN PROGRAM ( PARIS - 20 Arrondissements ) METHODE LOCAL

    streamlit run Dash.py

PS : pour la methode local s'assurer d'avoir le fichier : dvf_2024.csv dans le meme dossier que Dash.py 



By Gleaphe 2025 .
