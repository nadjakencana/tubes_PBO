# tracker_nongkrong_streamlit/main.py

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import Fullscreen

# ===== SETTING PAGE =====
st.set_page_config(page_title="Nongkrong Tembalang", layout="wide")

# ====== LOAD DATA SAFELY ======
CSV_PATH = "data/nongkrong_tembalang.csv"
@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(CSV_PATH)
        df.dropna(subset=["Jam Buka", "Harga", "Latitude", "Longitude"], inplace=True)
        return df
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

df = load_data()

st.title("📍 Tracker Nongkrong Mahasiswa Tembalang")

# ====== SEARCH BOX ======
st.sidebar.subheader("🔍 Cari Tempat Nongkrong")
search_query = st.sidebar.text_input("Cari berdasarkan nama")

# ====== FILTER ======
st.sidebar.subheader("🎯 Filter")
jam_buka_opsi = df["Jam Buka"].dropna().unique().tolist()
harga_opsi = df["Harga"].dropna().unique().tolist()

jam_buka_filter = st.sidebar.multiselect("Jam Buka", jam_buka_opsi, default=jam_buka_opsi)
harga_filter = st.sidebar.multiselect("Harga", harga_opsi, default=harga_opsi)

# ====== FILTER DATA ======
filtered_df = df[
    (df["Jam Buka"].isin(jam_buka_filter)) &
    (df["Harga"].isin(harga_filter))
]

if search_query:
    filtered_df = filtered_df[filtered_df["Nama"].str.contains(search_query, case=False)]

# ====== FUNGSI WARNA ======
def get_color(harga):
    if harga.lower() == "murah":
        return "green"
    elif harga.lower() == "mending mahal":
        return "orange"
    elif harga.lower() == "mahal":
        return "red"
    return "blue"

# ====== TAMPILKAN PETA ======
if not filtered_df.empty:
    m = folium.Map(
        location=[filtered_df["Latitude"].mean(), filtered_df["Longitude"].mean()],
        zoom_start=15,
        tiles="cartodbpositron"
    )
    Fullscreen().add_to(m)

    for _, row in filtered_df.iterrows():
        foto = f"<img src='{row['Foto']}' width='200'><br>" if row['Foto'] else ""
        rating = f"⭐ Rating: {row['Rating']}<br>" if 'Rating' in row and pd.notna(row['Rating']) else ""
        komentar = f"<i>{row['Komentar']}</i><br>" if 'Komentar' in row and pd.notna(row['Komentar']) else ""
        gmaps = f"<a href='https://www.google.com/maps/search/?api=1&query={row['Latitude']},{row['Longitude']}' target='_blank'>🗺️ Buka di Google Maps</a>"

        popup_html = f"""
            <b>{row['Nama']}</b><br>
            Jam Buka: {row['Jam Buka']}<br>
            Harga: {row['Harga']}<br>
            {rating}{foto}{komentar}{gmaps}
        """

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['Nama'],
            icon=folium.Icon(color=get_color(row["Harga"]))
        ).add_to(m)

    folium_static(m, width=950, height=600)
    st.success(f"✅ {len(filtered_df)} lokasi ditemukan.")
else:
    st.warning("Tidak ada lokasi yang cocok dengan filter atau pencarian.")

# ====== FORM TAMBAH LOKASI ======
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Tambah Tempat Baru")
with st.sidebar.form("form_tambah"):
    nama_baru = st.text_input("Nama Tempat")
    st.caption("🛈 Nama harus bener")

    lat_baru = st.number_input("Latitude", format="%f")
    lon_baru = st.number_input("Longitude", format="%f")
    st.caption("🛈 Temukan Lokasi di Google Maps lalu klik kanan untuk salin koordinat")

    jam24 = st.checkbox("Buka 24 Jam")
    harga_baru = st.selectbox("Harga", ["Murah", "Mending Mahal", "Mahal"])
    rating_baru = st.slider("Rating (Dummy)", 1.0, 5.0, 4.0, 0.1)
    komentar_baru = st.text_input("Komentar (Dummy)", "Tempat baru nih guys!")
    link_foto = st.text_input("Link Foto")

    submit = st.form_submit_button("Tambah Lokasi")

    if submit:
        jam_buka_val = "24 Jam" if jam24 else "Nggak 24 Jam"
        new_row = pd.DataFrame([{
            "Nama": nama_baru,
            "Jam Buka": jam_buka_val,
            "Harga": harga_baru,
            "Latitude": lat_baru,
            "Longitude": lon_baru,
            "Foto": link_foto,
            "Rating": rating_baru,
            "Komentar": komentar_baru
        }])

        try:
            existing_df = pd.read_csv(CSV_PATH)
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            updated_df.to_csv(CSV_PATH, index=False)
            st.sidebar.success("✅ Lokasi berhasil ditambahkan!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Gagal menambahkan data: {e}")
