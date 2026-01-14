import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Kalite Karne Dashboard", layout="wide")

st.title("📊 Hiyerarşik Kalite Karne Paneli")

# --- DOSYA YÜKLEME ---
uploaded_file = st.sidebar.file_uploader("Excel (.xlsx) veya CSV dosyasını yükleyin", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Dosyayı oku
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)

        # --- DİNAMİK FİLTRELEME BÖLÜMÜ ---
        st.sidebar.header("🔍 Filtreleme Seçenekleri")

        # 1. Filtre: Takım Seçimi
        takimlar = sorted(df["Takım Adı"].unique().tolist())
        selected_takim = st.sidebar.selectbox("1. Takım Seçin", ["Hepsi"] + takimlar)

        # Takıma göre veri filtreleme
        if selected_takim != "Hepsi":
            df_filtered_takim = df[df["Takım Adı"] == selected_takim]
        else:
            df_filtered_takim = df

        # 2. Filtre: Personel Seçimi (Seçilen takıma göre güncellenir)
        personel_listesi = sorted(df_filtered_takim["Personel"].unique().tolist())
        selected_person = st.sidebar.selectbox("2. Personel Seçin", personel_listesi)

        # Nihai veri seti
        user_data = df_filtered_takim[df_filtered_takim["Personel"] == selected_person]

        # --- DASHBOARD GÖRÜNÜMÜ ---
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Ortalama Puan", f"{user_data['Form Puan'].mean():.1f}")
        with col2:
            st.metric("Değerlendirme Sayısı", len(user_data))
        with col3:
            st.metric("Takım", user_data["Takım Adı"].iloc[0])
        with col4:
            st.metric("Dönem", user_data["Period Adı"].iloc[0])

        st.divider()

        # Grafik ve Kritik Hatalar (Önceki yapıyla aynı)
        c_left, c_right = st.columns([2, 1])
        with c_left:
            st.subheader("🎯 Kriter Başarı Oranları")
            kriterler = ["Karşılama/Bitirme", "Ses tonu/ Ses enerjisi - Kurumsal Görüşme Standartları", 
                         "Bekletme", "Etkin Dinleme- Çözüm Odaklı Yaklaşım", "Doğru Bilgilendirme", "Süreç Yönetimi"]
            mevcut = [k for k in kriterler if k in df.columns]
            puanlar = user_data[mevcut].mean().reset_index()
            puanlar.columns = ["Kriter", "Başarı %"]
            fig = px.bar(puanlar, x="Başarı %", y="Kriter", orientation='h', text_auto='.1f',
                         color="Başarı %", color_continuous_scale="RdYlGn", range_x=[0,105])
            st.plotly_chart(fig, use_container_width=True)

        with c_right:
            st.subheader("🚨 Kritik Hata Durumu")
            kritik = ["Can ve Mal Güvenliği", "Uygun Olmayan Davranışlar", "Kurum itibarını olumsuz etkileme"]
            for h in kritik:
                if h in user_data.columns:
                    hata_sayisi = (user_data[h] == 0).sum()
                    if hata_sayisi > 0:
                        st.error(f"{h}: {hata_sayisi} Hata")
                    else:
                        st.success(f"{h}: Sorun Yok")

        st.subheader("📋 Seçili Personel Çağrı Detayları")
        st.dataframe(user_data[["Tarih", "Süre", "Arama Tipi", "Form Puan", "Açıklama Detay"]], use_container_width=True)

    except Exception as e:
        st.error(f"Hata: {e}")
else:
    st.info("Lütfen bir dosya yükleyerek başlayın.")
