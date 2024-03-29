import base64
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
            # MainMenu {visibility: hidden;}
            footer {visibility: hidden !important;}
            # header {visibility: hidden;}
            </style>
            """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Hide stepper in st.number_input globally
st.markdown("""
<style>
    button.step-up {display: none;}
    button.step-down {display: none;}
    div[data-baseweb] {border-radius: 4px;}
</style>""",
unsafe_allow_html=True)

# Display Title and Description
st.title("Mbak Navra Bersama Masyarakat", anchor=False)
st.image(".statics/navra_1.jpeg", caption="Mbak Navra", width=250)
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

# st.dataframe(
#     existing_data,
#     hide_index=True
#     )

# def total_responden():
#     total_responden = len(existing_data)
#     return total_responden

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
        "Data per Koordinator",
        "Cek dan Tambah Data"
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
                st.toast("Pastikan formulir dengan tanda wajib untuk diisi.", icon='💽')
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

    responden = st.selectbox("Cari Nama Responden yang hendak diubah:red[*]", options=koor_data["NAMA_RESPONDEN"].tolist())
    responden_data = existing_data[existing_data["NAMA_RESPONDEN"] == responden].iloc[0]

    st.divider()

    # st.dataframe(responden_data,use_container_width=True)

    with st.form(key="update_responden_data"):
        tanggal = st.date_input("Tanggal Data Diambil", value=pd.to_datetime(responden_data["TANGGAL"]), disabled=True)
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

    @st.cache
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    csv = convert_df(koor_data)

    koor_data["TANGGAL"] = pd.to_datetime(koor_data["TANGGAL"]).dt.date

    date_range = koor_data["TANGGAL"].unique()

    # # start_date = mask_date.min()
    # # end_date = mask_date.max()

    st.write("\n")

    # select_all = st.multiselect("Pilih tanggal", date_range)

    # st.write(select_all)

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

    # st.subheader("")

    col4, col5 = st.columns(2, gap="medium")
    col4.metric(f"Total Responden per Tanggal", value=total_per_date)
    col5.metric("Total Perolehan\nResponden Koordinator", value=total_perolehan)

    st.dataframe(
        koor_data, 
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

    # Add a download button
    # csv = df.to_csv(index=False)
    # b64 = base64.b64encode(csv.encode()).decode()  # Convert DataFrame to CSV string
    # href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download CSV File</a>'
    # st.markdown(href, unsafe_allow_html=True)

    st.download_button(
        label="Unduh data Koordinator",
        data=csv,
        file_name=f'{koor}_data.csv',
        mime='text/csv',
        type='primary',
    )

elif action == "Cek dan Tambah Data":
    st.header("Cari Data DPT Kecamatan Sukodono")

    sukodono = """
    Khusus untuk Kelurahan:
    - BANGSRI
    - CANGKIRSARI
    - JOGOSATRU
    - KEBON AGUNG
    - MASANGAN KULON
    - NGARESREJO
    - PADEMONEGORO
    - PLUMBUNGAN
    - SAMBUNGREJO
    - SURUH

    Koordinator bisa cek data DPT dengan memasukkan NIK.
    """
    with st.expander("Informasi"):
        st.markdown(sukodono)
    

    @st.cache_data
    def get_data(sheet_name):
        data = conn.read(worksheet=sheet_name, usecols=list(range(8)), ttl=600)
        return data
    
    # kecamatan = st.selectbox("Pilih Kecamatan", ["SUKODONO"],index=0,disabled=True)
    kelurahan = st.selectbox("Pilih Kelurahan", ("BANGSRI","CANGKIRSARI","JOGOSATRU","KEBONAGUNG","MASANGANKULON","NGARESREJO","PADEMONEGORO","PLUMBUNGAN","SAMBUNGREJO","SURUH"),index=None,placeholder="Pilih Kelurahan/Desa")

    # search_nik = st.text_input(f"Cari NIK DPT {kelurahan}")
    search_nik = str(st.number_input("Cari NIK DPT",min_value=0,value=0,placeholder="NIK Responden"))

    st.write("")
    
    if st.button("Cari DPT", type="primary"):
        # # Check if the search box is not empty
        if search_nik != "0":
            df_cari_data = get_data(kelurahan)

            # Use boolean masking to filter the DataFrame
            search_mask = df_cari_data['NIK'].astype(str).str.contains(search_nik)
            search_results = df_cari_data[search_mask]

            # Convert search_results DataFrame to a dictionary
            search_results_dict = search_results.to_dict(orient='records')

            # Display the search results
            if not search_results.empty:
                # st.write("Hasil pencarian:")
                with st.container(border=True):
                    tps = search_results_dict[0]['TPS']
                    st.subheader(f"☑️ TPS/DPT 00{tps}", divider="grey")
                    
                    nama = search_results_dict[0]['NAMA']
                    st.markdown(":grey[Nama Pemilih]")
                    st.markdown(f"**{nama}**")
                
                    kelamin = search_results_dict[0]['KELAMIN']
                    # st.markdown(f"**JENIS KELAMIN:** {kelamin}")
                    st.markdown(":grey[JENIS KELAMIN]")
                    st.markdown(f"**{kelamin}**")

                    nik = int(search_results_dict[0]['NIK'])
                    st.markdown(":grey[NIK]")
                    st.markdown(f"**{nik}**")

                    alamat = search_results_dict[0]['ALAMAT']
                    st.markdown(":grey[ALAMAT]")
                    st.markdown(f"**{alamat}**")

                    rt = search_results_dict[0]['RT']
                    st.markdown(":grey[RT]")
                    st.markdown(f"**{rt}**")

                    rw = search_results_dict[0]['RW']
                    st.markdown(":grey[RW]")
                    st.markdown(f"**{rw}**")

                    if st.button("Mendukung", type='primary'):
                        with st.form(key="responden_form_1", clear_on_submit=True, border=True):
                            tanggal = st.date_input("Tanggal Data Diambil")
                            nama_koordinator = st.selectbox("Koordinator:red[*]", options=list_koordinator, index=None, placeholder="Pilih koordinator...")
                            nama_responden = st.text_input("Responden:red[*]", placeholder="Nama responden", value=nama)
                            nik = str(st.number_input("Nomor Induk Kependudukan (NIK):red[*]", value=nik, placeholder="NIK/No. KTP",disabled=True))
                            dusun_jalan = st.text_input("Dusun/Jalan", value=alamat,placeholder="Alamat/dusun/jalan")
                            rt = st.number_input("RT:red[*]", value=rt, placeholder="RT", help="Tidak perlu menambahkan angka 0 (nol) di depan.")
                            rw = st.number_input("RW:red[*]",value=rw, placeholder="RW", help="Tidak perlu menambahkan angka 0 (nol) di depan.")
                            desa = st.selectbox("Desa :red[*]", [kelurahan])
                            no_selular = st.number_input("Nomor HP", min_value=0, value=0, placeholder="No. HP Responden", help="Tidak perlu menambahkan angka 0 (nol) di depan")
                            keterangan = st.text_area("Keterangan Tambahan", value="None", placeholder="Tambahkan keterangan")

                            # Mark mandatory fields
                            st.markdown(":red[*wajib diisi]")

                            submit_button = st.form_submit_button(label="Tambah Data", type="primary")

                            if submit_button:
                                if not nama_koordinator or not nama_responden or not desa or not rt or not rw or not nik:
                                    st.toast("Pastikan formulir dengan tanda wajib untuk diisi.", icon='💽')
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
            else:
                st.warning("Data NIK tidak ditemukan")
        else:
            st.warning("Silahkan masukkan NIK yang valid untuk melakukan pencarian.")