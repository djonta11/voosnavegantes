
import requests
import pandas as pd
import streamlit as st
from datetime import datetime

API_KEY = "d5a175d200msh7597c677f3cf9d5p12898ejsn804510a4ece6"
HEADERS = {
    "x-rapidapi-host": "aerodatabox.p.rapidapi.com",
    "x-rapidapi-key": API_KEY
}
ICAO = "SBNF"
today = datetime.utcnow()
start = today.strftime("%Y-%m-%dT00:00")
end = today.strftime("%Y-%m-%dT23:59")
url = f"https://aerodatabox.p.rapidapi.com/airports/icao/{ICAO}/flights/{start}/{end}"

@st.cache_data
def get_flight_data():
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    def normalize_flights(flight_list, tipo):
        if not flight_list:
            return pd.DataFrame()
        df = pd.json_normalize(flight_list)
        df["tipo"] = tipo
        return df

    df_arr = normalize_flights(data.get("arrivals", []), "Chegada")
    df_dep = normalize_flights(data.get("departures", []), "Partida")

    return pd.concat([df_arr, df_dep], ignore_index=True)

@st.cache_data
def get_logo_url(airline_name):
    try:
        domain = airline_name.lower().replace(" ", "") + ".com"
        return f"https://logo.clearbit.com/{domain}"
    except:
        return ""

st.set_page_config(layout="wide", page_title="Dashboard Aeroporto Navegantes")
st.title("✈️ Dashboard de Voos – Aeroporto de Navegantes (SBNF)")

try:
    df = get_flight_data()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

if df.empty:
    st.warning("Nenhum dado de voo encontrado para hoje.")
    st.stop()

required_columns = ["flight.number", "airline.name", "status", "departure.scheduledTimeUtc"]
for col in required_columns:
    if col not in df.columns:
        df[col] = None

df["flight.number"] = df["flight.number"].fillna("Desconhecido")
df["airline.name"] = df["airline.name"].fillna("Indefinida")
df["status"] = df["status"].fillna("Desconhecido")

df["departure.scheduledTimeUtc"] = pd.to_datetime(df["departure.scheduledTimeUtc"], errors="coerce")
df["local_time"] = df["departure.scheduledTimeUtc"].dt.tz_localize("UTC").dt.tz_convert("America/Sao_Paulo")
df["logo_url"] = df["airline.name"].apply(get_logo_url)

tipo = st.selectbox("Selecionar tipo de voo:", ["Todos", "Chegada", "Partida"])
companhia = st.multiselect("Filtrar por companhia aérea:", sorted(df["airline.name"].unique()))

df_filtered = df.copy()
if tipo != "Todos":
    df_filtered = df_filtered[df_filtered["tipo"] == tipo]
if companhia:
    df_filtered = df_filtered[df_filtered["airline.name"].isin(companhia)]

st.subheader("📋 Tabela de voos com logotipo")
for _, row in df_filtered.iterrows():
    cols = st.columns([1, 2, 2, 2, 2])
    with cols[0]:
        st.image(row["logo_url"], width=40)
    with cols[1]:
        st.markdown(f"**{row['airline.name']}**")
    with cols[2]:
        st.markdown(f"Voo: `{row['flight.number']}`")
    with cols[3]:
        st.markdown(f"Status: `{row['status']}`")
    with cols[4]:
        hora = row["local_time"].strftime('%H:%M') if pd.notnull(row["local_time"]) else "N/A"
        st.markdown(f"🕒 {hora}")

st.subheader("📈 Distribuição de status dos voos")
st.bar_chart(df_filtered["status"].value_counts())

st.subheader("🏢 Voos por companhia aérea")
st.bar_chart(df_filtered["airline.name"].value_counts())
