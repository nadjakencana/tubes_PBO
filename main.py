import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import Fullscreen

# ===== SETTING PAGE =====
st.set_page_config(page_title="Nongkrong Tembalang", layout="wide")

# ====== LOAD DATA SAFELY ======
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/nongkrong_tembalang.csv")
        df.dropna(subset=["Jam Buka", "Harga", "Latitude", "Longitude"], inplace=True)
        return df
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()  # empty fallback

df = load_data()

# ===== THEME MODE =====
st.title("📍 Tracker Nongkrong Mahasiswa Tembalang")
tileset = "cartodbpositron"  # Tetap pakai peta terang

# ====== FILTER SECTION ======
if not df.empty:
    jam_buka_opsi = df["Jam Buka"].dropna().unique().tolist()
    harga_opsi = df["Harga"].dropna().unique().tolist()

    st.sidebar.header("🔎 Filter Lokasi")
    jam_buka_filter = st.sidebar.multiselect("Jam Buka", jam_buka_opsi, default=jam_buka_opsi)
    harga_filter = st.sidebar.multiselect("Harga", harga_opsi, default=harga_opsi)

    filtered_df = df[
        (df["Jam Buka"].isin(jam_buka_filter)) &
        (df["Harga"].isin(harga_filter))
    ]

    def get_color(harga):
        if harga.lower() == "murah":
            return "green"
        elif harga.lower() == "mending mahal":
            return "orange"
        elif harga.lower() == "mahal":
            return "red"
        return "blue"

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
        st.warning("Tidak ada lokasi yang cocok dengan filter.")
else:
    st.error("CSV tidak bisa dimuat atau kosong 😢")
