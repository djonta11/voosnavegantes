
import streamlit as st
import requests
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh

API_KEY = "d5a175d200msh7597c677f3cf9d5p12898ejsn804510a4ece6"
HEADERS = {
    "x-rapidapi-host": "aerodatabox.p.rapidapi.com",
    "x-rapidapi-key": API_KEY
}

ICAO = "SBNF"  # Aeroporto de Navegantes

st.set_page_config(page_title="Voos Navegantes - Partidas", layout="wide")

st.title("Dashboard Voos Partidas Aeroporto de Navegantes (SBNF)")

mostrar_json = st.checkbox("Mostrar dados brutos (JSON) para debug")

# Atualiza a página a cada 5 minutos (300 segundos)
count = st_autorefresh(interval=300 * 1000, limit=None, key="auto_refresh")

data_hoje = datetime.utcnow().strftime("%Y-%m-%d")
start = f"{data_hoje}T00:00"
end = f"{data_hoje}T23:59"
tipo_voo = "departures"

url = f"https://aerodatabox.p.rapidapi.com/flights/airports/icao/{ICAO}/{tipo_voo}/{start}/{end}"
st.write("📡 URL da API:", url)

response = requests.get(url, headers=HEADERS)

if response.status_code != 200:
    st.error(f"Erro na API: {response.status_code} - {response.text}")
    st.stop()

data = response.json()
st.write("🔍 JSON retornado:")
st.json(data)

voos = data.get("departures") or data.get("items") or []

if not isinstance(voos, list):
    st.warning("Resposta da API não está no formato esperado. Nenhum voo listado.")
    st.stop()

rows = []
for voo in voos:
    flight = voo.get("flight") or {}
    arrival = voo.get("arrival") or {}
    departure = voo.get("departure") or {}

    rows.append({
        "Número": flight.get("number", "N/A"),
        "Destino": arrival.get("iataCode", "N/A"),
        "Companhia": flight.get("iataNumber", "N/A")[:2] if flight.get("iataNumber") else "N/A",
        "Status": voo.get("status", "N/A"),
        "Horário Previsto": departure.get("scheduledTimeLocal", "N/A")
    })

df = pd.DataFrame(rows)

if df.empty:
    st.warning("Nenhum dado estruturado disponível para exibir.")
    st.stop()

st.dataframe(df)

st.subheader("Logotipos das companhias aéreas")

logos = {
    "AZ": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Azul_Airlines_logo.svg/120px-Azul_Airlines_logo.svg.png",
    "G3": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Gol_Logotipo.svg/120px-Gol_Logotipo.svg.png",
    "JJ": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Airlines_Brasil_Jet.svg/120px-Airlines_Brasil_Jet.svg.png",
    "AD": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Air_Asia_Logo.svg/120px-Air_Asia_Logo.svg.png",
}

comp_ativos = df["Companhia"].unique()
cols = st.columns(len(comp_ativos))

for idx, comp in enumerate(comp_ativos):
    with cols[idx]:
        st.write(f"**{comp}**")
        url_logo = logos.get(comp)
        if url_logo:
            st.image(url_logo, width=80)
        else:
            st.write("Logo não disponível")
