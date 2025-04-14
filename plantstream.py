import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials

# === Google Sheet Config ===
spreadsheet_id = '1XdXlgTWxEDfU0uHK1Z3mM885JQuM0EH16DrDaIHP3zc'

st.set_page_config(page_title="🌿 Plant Monitoring Dashboard", layout="wide")
st.title("🌿 Real-time Plant Monitoring Dashboard")


# === Function to Load Sheet ===
@st.cache_data
def load_sheet_data(sheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file"
    ]

    creds_info = dict(st.secrets["google_service_account"])
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df.columns = df.columns.str.strip().str.lower()  # Clean headers
    return df

# === Load and plot Sheet1 (Numeric Monitoring Data) ===
try:
    df = load_sheet_data("Sheet1")
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])

    st.subheader("📈 Environmental Sensor Trends")

    col1, col2 = st.columns(2)

    with col1:
        fig_temp = px.line(df, x='datetime', y='temperature',
                           title='🌡️ Temperature Over Time',
                           markers=True,
                           line_shape='linear',
                           color_discrete_sequence=['#FF5733'])
        st.plotly_chart(fig_temp, use_container_width=True)

        fig_soil = px.line(df, x='datetime', y='soil moisture',
                           title='🌱 Soil Moisture Over Time',
                           markers=True,
                           line_shape='linear',
                           color_discrete_sequence=['#3D9970'])
        st.plotly_chart(fig_soil, use_container_width=True)

    with col2:
        fig_humidity = px.line(df, x='datetime', y='humidity',
                               title='💧 Humidity Over Time',
                               markers=True,
                               line_shape='linear',
                               color_discrete_sequence=['#0074D9'])
        st.plotly_chart(fig_humidity, use_container_width=True)

        fig_ph = px.line(df, x='datetime', y='ph',
                         title='🧪 pH Level Over Time',
                         markers=True,
                         line_shape='linear',
                         color_discrete_sequence=['#B10DC9'])
        st.plotly_chart(fig_ph, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error loading Sheet1: {e}")

# === Load and plot CAT (Categorical Monitoring Data) ===
st.divider()
st.subheader("🔍 Qualitative Monitoring Insights (CAT)")

try:
    df_cat = load_sheet_data("cat")

    # Melt data to long format
    df_melted = df_cat.melt(var_name='parameter', value_name='level')

    # Custom color map for categories
    category_colors = {
        'High': '#FF4136',
        'Normal': '#2ECC40',
        'Low': '#0074D9'
    }

    fig_cat = px.histogram(
        df_melted,
        x='parameter',
        color='level',
        barmode='group',
        title="⚠️ Frequency of Qualitative Readings",
        color_discrete_map=category_colors,
        text_auto=True
    )
    st.plotly_chart(fig_cat, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error loading cat: {e}")

# === Raw Data Section ===
st.divider()
st.subheader("📋 Raw Data Tables")

with st.expander("🔎 View Raw Sheet1 Data"):
    try:
        st.dataframe(df, use_container_width=True)
    except:
        st.warning("Sheet1 data not available.")

with st.expander("🔎 View Raw cat Data"):
    try:
        st.dataframe(df_cat, use_container_width=True)
    except:
        st.warning("cat data not available.")

# === Footer ===
st.caption("Last updated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))


if st.button("🔄 Refresh Sheet1 Data"):
    st.cache_data.clear()
    df = load_sheet_data("Sheet1")
    st.success("Data refreshed!")
else:
    df_cat = load_sheet_data("cat")
