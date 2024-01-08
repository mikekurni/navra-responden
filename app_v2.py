import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(
    page_title="Entri Data Konstituen",
    page_icon="🛡️",
    layout="centered"
)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden !important;}
            header {visibility: hidden;}
            a.viewerBadge_container__r5tak styles_viewerBadge__CvC9N {visibility: hidden;}
            </style>
            """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Display Title and Description
st.title("Entri Data Konstituen")
st.image(".statics/navra_1.jpeg", caption="Mbak Navra", width=250)
st.subheader("Mbak Navra Bersama Masyarakat")
st.markdown("""
Aplikasi entri data konstituen Tim Sukses Mbak Navra.  **Dapil 5. Kecamatan Taman - Sukodono**.
""")

# Establishing a Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing constituent data
existing_data = conn.read(worksheet="DATA", usecols=list(range(11)), ttl=5)
existing_data = existing_data.dropna(how="all")
existing_data["NIK"] = existing_data["NIK"].astype(str).replace('.', '')
existing_data["NO_SELULAR"] = existing_data["NO_SELULAR"].astype(str).replace('.', '')

# Fetching Koordinator data
koordinator_data = conn.read(worksheet="KOORDINATOR", usecols=list[2], ttl=5)

# Fetching Desa
desa_data = conn.read(worksheet="DESA", usecols=list[1], ttl=5)

# Metrics
total_responden = existing_data.NAMA_RESPONDEN.count()
total_koordinator = koordinator_data.NAMA.count()
total_koordinator_aktif = existing_data.NAMA_KOORDINATOR.nunique()
total_desa = desa_data.DESA.count()
total_desa_terdata = existing_data.DESA.nunique()
# total_phone = existing_data.NO_SELULAR.nunique()
list_koordinator = koordinator_data.NAMA.dropna()
list_desa = desa_data.DESA.dropna()

col1, col2, col3 = st.columns(3)
col1.metric(label="Total Responden", value=total_responden)
col2.metric(label="Total Koordinator", value=total_koordinator, delta=(f'{total_koordinator_aktif} Aktif'), delta_color="off")
col3.metric(label="Total Desa", value=total_desa, delta=(f"{total_desa_terdata} Terdata"), delta_color="off")

# Choosing Actions
action = st.selectbox(
    "Choose an Action",
    [
        "Tambah Data Baru",
        "Edit Data",
        "Lihat Data",
    ],
)
