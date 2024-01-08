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
    ],
)

if action == "Tambah Data Baru":
    st.markdown("Tambah data responden baru pada formulir di bawah ini.")
    with st.form(key="responden_form", clear_on_submit=True):
        tanggal = st.date_input("Tanggal Data Diambil")
        nama_koordinator = st.selectbox("Koordinator:red[*]", options=list_koordinator, index=None, placeholder="Pilih koordinator...")
        nama_responden = st.text_input("Responden:red[*]", placeholder="Nama responden")
        nik = str(st.number_input("Nomor Induk Kependudukan (NIK):red[*]", min_value=1, value=None, placeholder="NIK/No. KTP"))
        dusun_jalan = st.text_input("Dusun/Jalan", placeholder="Alamat/dusun/jalan")
        rt = st.number_input("RT:red[*]", min_value=1, value=None, step=1, placeholder="RT", help="Tidak perlu menambahkan angka 0 (nol) di depan.")
        rw = st.number_input("RW:red[*]", min_value=1, value=None, step=1, placeholder="RW", help="Tidak perlu menambahkan angka 0 (nol) di depan.")
        desa = st.selectbox("Desa :red[*]", options=list_desa, index=None, placeholder="Pilih desa...")
        no_selular = st.number_input("Nomor HP", min_value=1, value=None, placeholder="No. HP Responden", help="Tidak perlu menambahkan angka 0 (nol) di depan")
        keterangan = st.text_area("Keterangan Tambahan", placeholder="Tambahkan keterangan")

        # Mark mandatory fields
        st.markdown(":red[*wajib diisi]")

        submit_button = st.form_submit_button(label="Tambah Data", type="primary")

        if submit_button:
            if not nama_koordinator or not nama_responden or not desa or not rt or not rw or not nik:
                st.toast("Nama responden sudah terdata di dalam database.", icon='💽')
            elif existing_data["NIK"].str.contains(nik).any():
                st.toast("Nama responden sudah terdata di dalam database.", icon='💽')
            else:
                # Create a new row of respondent data
                responden_data = pd.DataFrame(
                    [
                        {
                            "TANGGAL": tanggal.strftime("%d-%m-%Y"),
                            "NAMA_KOORDINATOR": nama_koordinator.upper(),
                            "NAMA_RESPONDEN": nama_responden.upper(),
                            "NIK": str(nik),
                            "DUSUN_JALAN": dusun_jalan.upper(),
                            "RT": rt,
                            "RW": rw,
                            "DESA": desa.upper(),
                            "NO_SELULAR": str(no_selular),
                            "KETERANGAN": keterangan.upper(),
                        }
                    ]
                )
                # Add the new responden to the existing data
                update_df = pd.concat([existing_data, responden_data], ignore_index=True)

                # Update Google Sheets with new respondent data
                conn.update(worksheet="DATA", data=update_df)

                st.toast("Data berhasil ditambahkan!", icon='🎉')

elif action == "Update Existing Vendor":
    st.markdown("Pilih data yang hendak diubah.")

    responden_to_update = st.selectbox(
        "Cari NIK responden yang hendak diubah", options=existing_data["NIK"].tolist()
    )

    responden_data = existing_data[existing_data["NIK"] == responden_to_update].iloc[0]

    st.dataframe(responden_data)

    # with st.form(key="update_responden_data"):
    #     tanggal = st.date_input("Tanggal Data Diambil", value=pd.to_datetime(responden_data["TANGGAL"]))