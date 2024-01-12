import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from os import listdir
from datetime import date, datetime, timedelta


pd.options.mode.chained_assignment = None

# Page configuration
st.set_page_config(
    page_title="Entri Data Konstituen",
    page_icon="🛡️",
    layout="centered"
)

# Hide streamlit
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden !important;}
            header {visibility: hidden;}
            </style>
            """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# img_dir = r"./static/"
# files = listdir(img_dir)

# Display Title and Description
st.title("Mbak Navra Bersama Masyarakat", anchor=False)
st.image("static/navra_1.jpeg", width=250, use_column_width="auto")
st.subheader("Entri Data Konstituen")
st.markdown("""
Aplikasi entri data konstituen Tim Sukses Mbak Navra.
            
**Dapil 5. Kecamatan Taman - Sukodono**.
""")

# Establishing a Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing constituent data
existing_data = conn.read(worksheet="DATA", usecols=list(range(10)), ttl=5)
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
list_koordinator = koordinator_data.NAMA.dropna().values.tolist()
list_desa = desa_data.DESA.dropna().values.tolist()

st.header("")
col1, col2, col3 = st.columns(3)
col1.metric(label="Total Responden", value=total_responden)
col2.metric(label="Total Koordinator", value=total_koordinator, delta=(f'{total_koordinator_aktif} Aktif'), delta_color="off")
col3.metric(label="Total Desa", value=total_desa, delta=(f"{total_desa_terdata} Terdata"), delta_color="off")

st.header("")

# Choosing Actions
action = st.selectbox(
    "Pilih Aksi",
    [
        "Tambah Data Baru",
        "Ubah Data Responden",
        "Data per Koordinator"
    ],
)

st.divider()

if action == "Tambah Data Baru":
    st.header("Tambah data responden baru pada formulir di bawah ini", divider="green", anchor=False)
    st.header("")
    with st.form(key="responden_form", clear_on_submit=True):
        tanggal = st.date_input("Tanggal Data Diambil")
        nama_koordinator = st.selectbox("Koordinator:red[*]", options=list_koordinator, index=None, placeholder="Pilih koordinator...")
        nama_responden = st.text_input("Responden:red[*]", placeholder="Nama responden")
        nik = str(st.number_input("Nomor Induk Kependudukan (NIK):red[*]", min_value=0, value=0, placeholder="NIK/No. KTP"))
        dusun_jalan = st.text_input("Dusun/Jalan", placeholder="Alamat/dusun/jalan")
        rt = st.number_input("RT:red[*]", min_value=1, value=1, placeholder="RT", help="Tidak perlu menambahkan angka 0 (nol) di depan.")
        rw = st.number_input("RW:red[*]", min_value=1, value=1, placeholder="RW", help="Tidak perlu menambahkan angka 0 (nol) di depan.")
        desa = st.selectbox("Desa :red[*]", options=list_desa, index=None, placeholder="Pilih desa...")
        no_selular = st.number_input("Nomor HP", min_value=0, value=0, placeholder="No. HP Responden", help="Tidak perlu menambahkan angka 0 (nol) di depan")
        keterangan = st.text_area("Keterangan Tambahan", value="None", placeholder="Tambahkan keterangan")

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
                            "TANGGAL": tanggal.strftime("%Y/%m/%d"),
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

                st.toast(f"Data responden {nama_responden} berhasil ditambahkan!", icon='🎉')

elif action == "Ubah Data Responden":
    st.header("Pilih data responden yang hendak diubah", divider="orange", anchor=False)
    st.header("")

    list_koordinator = existing_data["NAMA_KOORDINATOR"].unique()

    with st.expander("Cara ubah data:"):
        st.write(
            """
            Untuk mengubah data ikuti langkah berikut ini:
            1. Pilih Nama Koordinator
            2. Aplikasi menampilkan data Nama Responden menurut Nama Koordinator
            3. Lakukan perubahan data seperlunya.
            4. Setelah selesai melakukan perubahan. Tekan tombol **:red[Ubah Data Responden]**
            """
        )

    st.markdown("")

    koor = st.selectbox("Pilih Koordinator:red[*]", options=list_koordinator)
    mask_koor = existing_data["NAMA_KOORDINATOR"].values == koor
    koor_data = existing_data.iloc[mask_koor]

    st.write(koor_data)

    responden = st.selectbox("Cari Nama Responden yang hendak diubah:red[*]", options=koor_data["NAMA_RESPONDEN"].tolist())
    responden_data = existing_data[existing_data["NAMA_RESPONDEN"] == responden].iloc[0]

    st.divider()

    # st.dataframe(responden_data,use_container_width=True)

    with st.form(key="update_responden_data"):
        tanggal = st.date_input("Tanggal Data Diambil", value=pd.to_datetime(responden_data["TANGGAL"]), disabled=True))
        nama_koordinator = st.selectbox("Koordinator:red[*]", options=koor_data["NAMA_KOORDINATOR"].unique(), disabled=True)
        nama_responden = st.text_input("Responden:red[*]", value=responden_data["NAMA_RESPONDEN"])
        nik = st.number_input("Nomor Induk Kependudukan (NIK):red[*]", value=int(float(responden_data["NIK"])))
        dusun_jalan = st.text_input("Dusun/Jalan", value=responden_data["DUSUN_JALAN"])
        rt = st.number_input("RT:red[*]", value=int(float(responden_data["RT"])), format="%d")
        rw = st.number_input("RW:red[*]", value=int(float(responden_data["RW"])), format="%d")
        desa = st.selectbox("Desa:red[*]", options=list_desa, index=list_desa.index(responden_data["DESA"]))
        no_selular = st.number_input("No. HP", value=int(float(responden_data["NO_SELULAR"])), format="%d")
        keterangan = st.text_area("Keterangan Tambahan", value=responden_data["KETERANGAN"])

        # Mark mandatory fields
        st.markdown(":red[*wajib diisi]")

        update_button = st.form_submit_button(label="Ubah Data Responden", type="primary")

        if update_button:
            if not nama_responden or not desa or not rt or not rw or not nik:
                st.toast("Pastikan isian yang diwajibkan sudah terisi.", icon='✳️')
            else:
                # Removing old entry
                existing_data.drop(
                    existing_data[
                        existing_data["NAMA_RESPONDEN"] == responden
                    ].index,
                    inplace=True
                )

                # Create updated data entry
                updated_responden_data = pd.DataFrame(
                    [
                        {
                            "TANGGAL": tanggal.strftime("%Y/%m/%d"),
                            "NAMA_KOORDINATOR": nama_koordinator,
                            "NAMA_RESPONDEN": nama_responden.upper(),
                            "NIK": str(nik),
                            "RT": rt,
                            "RW": rw,
                            "DESA": desa.upper(),
                            "NO_SELULAR": str(no_selular),
                            "KETERANGAN": keterangan.upper(),
                        }
                    ]
                )

                # Adding updated data to the dataframe
                updated_df = pd.concat(
                    [existing_data, updated_responden_data], ignore_index=True
                )

                # Updated Google Sheets with edited responden data
                conn.update(worksheet="DATA", data=updated_df)

                st.toast(f"Data responden {nama_responden} berhasil diubah!", icon='🎉')
        
elif action == "Data per Koordinator":
    st.header("Tampilkan Data Responden Berdasar Koordinator", divider="blue", anchor=False)
    st.header("")

    list_koordinator = existing_data["NAMA_KOORDINATOR"].unique()

    koor = st.selectbox("Pilih Koordinator:red[*]", options=list_koordinator)
    mask_koor = existing_data["NAMA_KOORDINATOR"].values == koor
    koor_data = existing_data.iloc[mask_koor]

    koor_data["TANGGAL"] = pd.to_datetime(koor_data["TANGGAL"]).dt.date

    date_range = koor_data["TANGGAL"]

    # start_date = mask_date.min()
    # end_date = mask_date.max()

    st.write("\n")

    date_slider = st.select_slider(
        'Tampilkan data responden berdasar tanggal input',
        options=date_range,
    )

    mask_date = koor_data["TANGGAL"].values == date_slider
    responden_date = koor_data.iloc[mask_date]
    # st.write(responden_date)

    st.subheader("")
    st.markdown(f"### Data Responden Koordinator :blue[{koor}]")

    st.markdown("")

    total_per_date = responden_date["NAMA_RESPONDEN"].count()
    total_perolehan = koor_data["NAMA_RESPONDEN"].count()
    # today = date.today()

    st.subheader("")

    col4, col5 = st.columns(2, gap="medium")
    col4.metric(f"Total Responden per Tanggal", value=total_per_date)
    col5.metric("Total Perolehan\nResponden Koordinator", value=total_perolehan)

    st.dataframe(
        responden_date, 
        column_config={
        "NAMA_KOORDINATOR": st.column_config.TextColumn(
                "NAMA KOORDINATOR",
                width="small",
            ),
        "NAMA_RESPONDEN": st.column_config.TextColumn(
                "NAMA RESPONDEN",
            ),
        "DUSUN_JALAN": st.column_config.TextColumn(
                "DUSUN/JALAN",
            ),
        "NIK": st.column_config.NumberColumn(
                width="medium",
                format="%d",
            ),
        "NO_SELULAR": st.column_config.NumberColumn(
                "NO. HP",
                format="%d",
            ),
        },
        hide_index=True,
        use_container_width=True,
    )