import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd

API_KEY = "d5a175d200msh7597c677f3cf9d5p12898ejsn804510a4ece6"
HEADERS = {
    "x-rapidapi-host": "aerodatabox.p.rapidapi.com",
    "x-rapidapi-key": API_KEY
}

ICAO = "SBNF"  # Aeroporto de Navegantes

st.set_page_config(page_title="Voos Navegantes", layout="wide")

st.title("Dashboard Voos Aeroporto de Navegantes (SBNF)")

# Interface do usuário
col1, col2 = st.columns(2)
with col1:
    filtro_voo = st.selectbox("Tipo de voo:", ["Chegadas", "Partidas"])
with col2:
    mostrar_json = st.checkbox("Mostrar dados brutos (JSON) para debug")

# Datas ampliadas para 3 dias (hoje -1 a hoje +1)
hoje = datetime.utcnow()
start_date = (hoje - timedelta(days=1)).strftime("%Y-%m-%dT00:00")
end_date = (hoje + timedelta(days=1)).strftime("%Y-%m-%dT23:59")

url = f"https://aerodatabox.p.rapidapi.com/airports/icao/{ICAO}/flights/{start_date}/{end_date}"

response = requests.get(url, headers=HEADERS)

if response.status_code != 200:
    st.error(f"Erro na API: {response.status_code}")
    st.stop()

data = response.json()

if mostrar_json:
    st.subheader("Dados brutos da API")
    st.write(data)

voos = data.get("arrivals") if filtro_voo == "Chegadas" else data.get("departures")

if not voos:
    st.warning(f"Nenhum voo encontrado para '{filtro_voo}' no período selecionado.")
    st.stop()

# Construir dataframe
rows = []
for voo in voos:
    try:
        rows.append({
            "Número": voo.get("flight", {}).get("number", "N/A"),
            "Origem" if filtro_voo == "Chegadas" else "Destino": voo.get("departure", {}).get("iataCode", "N/A") if filtro_voo == "Chegadas" else voo.get("arrival", {}).get("iataCode", "N/A"),
            "Companhia": voo.get("flight", {}).get("iataNumber", "N/A")[:2],
            "Status": voo.get("status", "N/A"),
            "Horário Previsto": voo.get("arrival", {}).get("scheduledTimeLocal", "N/A") if filtro_voo == "Chegadas" else voo.get("departure", {}).get("scheduledTimeLocal", "N/A")
        })
    except Exception as e:
        pass

df = pd.DataFrame(rows)

if df.empty:
    st.warning("Nenhum dado estruturado disponível para exibir.")
    st.stop()

# Exibir dataframe
st.dataframe(df)

# Mostrar logos simples das companhias
st.subheader("Logotipos das companhias aéreas")

# URLs básicas para logotipos (exemplo)
logos = {
    "AZ": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Azul_Airlines_logo.svg/120px-Azul_Airlines_logo.svg.png",
    "G3": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Gol_Logotipo.svg/120px-Gol_Logotipo.svg.png",
    "JJ": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Airlines_Brasil_Jet.svg/120px-Airlines_Brasil_Jet.svg.png",
    "AD": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Air_Asia_Logo.svg/120px-Air_Asia_Logo.svg.png",
}

comp_ativos = df["Companhia"].unique()
cols = st.columns(len(comp_ativos))

for idx, comp in enumerate(comp_ativos):
    url_logo = logos.get(comp, None)
    with cols[idx]:
        st.write(f"**{comp}**")
        if url_logo:
            st.image(url_logo, width=80)
        else:
            st.write("Logo não disponível")