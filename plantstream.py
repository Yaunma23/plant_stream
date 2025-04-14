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
    df.columns = df.columns.str.strip().str.lower()
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

# === Classify ALL data rows into High, Low, Normal and write to 'cat' sheet ===
try:
    def classify(value, low, high):
        if value < low:
            return "Low"
        elif value > high:
            return "High"
        else:
            return "Normal"

    cat_data = []
    for _, row in df.iterrows():
        cat_data.append({
            'temperature': classify(row['temperature'], 27, 31),
            'humidity': classify(row['humidity'], 70, 95),
            'soil moisture': classify(row['soil moisture'], 200, 410),
            'ph': classify(row['ph'], 6.2, 7.8)
        })

    cat_df = pd.DataFrame(cat_data)

    # Upload full cat_df to the "cat" sheet
    creds_info = dict(st.secrets["google_service_account"])
    creds = Credentials.from_service_account_info(creds_info, scopes=[
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file"
    ])
    client = gspread.authorize(creds)
    cat_sheet = client.open_by_key(spreadsheet_id).worksheet("cat")
    cat_sheet.clear()
    cat_sheet.update([cat_df.columns.values.tolist()] + cat_df.values.tolist())

except Exception as e:
    st.error(f"❌ Failed to update 'cat' sheet: {e}")

# === Load and plot CAT (Categorical Monitoring Data) ===
st.divider()
st.subheader("🔍 Qualitative Monitoring Insights ")

try:
    df_cat = load_sheet_data("cat")

    df_melted = df_cat.melt(var_name='parameter', value_name='level')

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

with st.expander("🔎 View Raw Data"):
    try:
        st.dataframe(df, use_container_width=True)
    except:
        st.warning("Sheet1 data not available.")


# === Footer ===
st.caption("Last updated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))

if st.button("🔄 Refresh Sheet1 Data"):
    st.cache_data.clear()
    df = load_sheet_data("Sheet1")
    st.success("Data refreshed!")
else:
    df_cat = load_sheet_data("cat")
