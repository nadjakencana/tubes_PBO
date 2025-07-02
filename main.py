# main.py
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import Fullscreen
from models.models import DataManager, TempatNongkrong

st.set_page_config(page_title="Nongkrong Tembalang", layout="wide")

# ====== SESSION LOGIN ======
if "username" not in st.session_state:
    st.session_state.username = None
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# ====== LOGIN PANEL ======
st.sidebar.title("🔐 Login Pengguna")
if st.session_state.username is None:
    username_input = st.sidebar.text_input("Masukkan Username")
    if st.sidebar.button("Login"):
        if username_input.strip():
            st.session_state.username = username_input.strip()
            st.rerun()
else:
    st.sidebar.success(f"Login sebagai {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.username = None
        st.rerun()

# ===== INIT DATABASE MANAGER =====
dm = DataManager()
data = dm.get_all_tempat()

# ===== FILTER =====
st.sidebar.title("🔍 Filter")
jam_opsi = list(set([d.jam_buka for d in data]))
harga_opsi = list(set([d.harga for d in data]))

jam_filter = st.sidebar.multiselect("Jam Buka", jam_opsi, default=jam_opsi)
harga_filter = st.sidebar.multiselect("Harga", harga_opsi, default=harga_opsi)

filtered = [d for d in data if d.jam_buka in jam_filter and d.harga in harga_filter]

# ====== TAMPILKAN PETA ======
st.title("📍 Info Nongkrong Mahasiswa Tembalang")

def get_color(h):
    h = h.lower()
    return "green" if h == "murah" else "orange" if h == "mending mahal" else "red"

if filtered:
    m = folium.Map(location=[filtered[0].latitude, filtered[0].longitude], zoom_start=15)
    Fullscreen().add_to(m)

    for row in filtered:
        popup = f"""
        <b>{row.nama}</b><br>
        Jam Buka: {row.jam_buka}<br>
        Harga: {row.harga}<br>
        ⭐ {row.rating}<br>
        <i>{row.komentar}</i><br>
        <img src="{row.foto}" width="200"><br>
        <a href="https://www.google.com/maps/search/?api=1&query={row.latitude},{row.longitude}" target="_blank">📍 Lihat di Google Maps</a>
        """
        folium.Marker(
            location=[row.latitude, row.longitude],
            tooltip=row.nama,
            popup=popup,
            icon=folium.Icon(color=get_color(row.harga))
        ).add_to(m)
    folium_static(m, width=950, height=600)
else:
    st.warning("Tidak ada lokasi yang cocok!")

# ===== FORM TAMBAH/EDIT =====
if st.session_state.username:
    st.subheader("➕ Tambah / ✏️ Edit Tempat Nongkrong")
    if st.session_state.edit_id:
        tempat = next((x for x in data if x.id == st.session_state.edit_id), None)
        st.info(f"Edit tempat: {tempat.nama}")
    else:
        tempat = TempatNongkrong(0, "", "", "", 0.0, 0.0, "", 4.0, "")

    with st.form("form_tambah"):
        nama = st.text_input("Nama", tempat.nama)
        jam_buka = st.selectbox("Jam Buka", ["24 Jam", "Nggak 24 Jam"], index=0 if tempat.jam_buka == "24 Jam" else 1)
        harga = st.selectbox("Harga", ["Murah", "Mending Mahal", "Mahal"], index=["Murah", "Mending Mahal", "Mahal"].index(tempat.harga or "Murah"))
        lat = st.number_input("Latitude", value=tempat.latitude, step=0.0000000001, format="%.10f")
        lon = st.number_input("Longitude", value=tempat.longitude, step=0.0000000001, format="%.10f")
        foto = st.text_input("Link Foto", value=tempat.foto)
        rating = st.slider("Rating", 1.0, 5.0, value=tempat.rating, step=0.1)
        komentar = st.text_input("Komentar", value=tempat.komentar)
        submit = st.form_submit_button("Simpan")

        if submit:
            new_tempat = TempatNongkrong(
                id=tempat.id,
                nama=nama,
                jam_buka=jam_buka,
                harga=harga,
                latitude=lat,
                longitude=lon,
                foto=foto,
                rating=rating,
                komentar=komentar
            )
            if st.session_state.edit_id:
                dm.edit_tempat(new_tempat)
                st.success("Data berhasil diupdate!")
                st.session_state.edit_id = None
            else:
                dm.tambah_tempat(new_tempat, st.session_state.username)
                st.success("Data berhasil ditambahkan!")
            st.rerun()

# ===== DAFTAR TEMPAT + AKSI =====
if st.session_state.username:
    st.subheader("📄 Daftar Lokasi")
    for row in data:
        with st.expander(f"{row.nama} ({row.harga})"):
            st.write(f"Jam: {row.jam_buka} | Rating: {row.rating}")
            st.image(row.foto, width=300)
            if st.session_state.username == "nadjakencana":
                st.caption(f"🧑‍💻 Ditambahkan oleh: `{row.creator}`")
            st.write(row.komentar)
            if st.session_state.username == "nadjakencana":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ Edit - {row.id}"):
                        st.session_state.edit_id = row.id
                        st.rerun()
                with col2:
                    if st.button(f"🗑️ Hapus - {row.id}"):
                        dm.hapus_tempat(row.id)
                        st.success("Data berhasil dihapus!")
                        st.rerun()
