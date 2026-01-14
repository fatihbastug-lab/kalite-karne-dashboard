import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Kalite Karne Dashboard", layout="wide")

st.title("📊 Kalite Karne Analiz Sistemi")

# --- DOSYA YÜKLEME ALANI (Artık XLSX de kabul ediyor) ---
st.sidebar.header("📁 Veri Kaynağı")
uploaded_file = st.sidebar.file_uploader("Güncel Excel (.xlsx) veya CSV dosyasını yükleyin", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Dosya uzantısına göre okuma yöntemi seçimi
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            # Excel dosyasını okur
            df = pd.read_excel(uploaded_file)
        
        # --- PERSONEL SEÇİMİ VE FİLTRELEME ---
        personel_listesi = sorted(df["Personel"].unique())
        selected_person = st.sidebar.selectbox("Personel Seçin", personel_listesi)
        user_data = df[df["Personel"] == selected_person]

        # --- KPI KARTLARI ---
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Ortalama Puan", f"{user_data['Form Puan'].mean():.1f}")
        with col2:
            st.metric("Toplam Değerlendirme", len(user_data))
        with col3:
            st.metric("Proje", str(user_data["Proje Adı"].iloc[0]))
        with col4:
            st.metric("Dönem", str(user_data["Period Adı"].iloc[0]))

        st.divider()

        # --- GRAFİK VE ANALİZ ---
        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.subheader("🎯 Kriter Bazlı Başarı Oranı")
            kriterler = [
                "Karşılama/Bitirme", 
                "Ses tonu/ Ses enerjisi - Kurumsal Görüşme Standartları",
                "Bekletme", 
                "Etkin Dinleme- Çözüm Odaklı Yaklaşım",
                "Doğru Bilgilendirme", 
                "Süreç Yönetimi"
            ]
            mevcut_kriterler = [k for k in kriterler if k in df.columns]
            puanlar = user_data[mevcut_kriterler].mean().reset_index()
            puanlar.columns = ["Kriter", "Başarı %"]
            
            fig = px.bar(puanlar, x="Başarı %", y="Kriter", orientation='h', 
                         text_auto='.1f', color="Başarı %", 
                         color_continuous_scale="RdYlGn", range_x=[0,105])
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.subheader("🚨 Kritik Hatalar")
            # Kritik hata sütunları
            kritik_hatalar = ["Can ve Mal Güvenliği", "Uygun Olmayan Davranışlar", "Kurum itibarını olumsuz etkileme"]
            for hata in kritik_hatalar:
                if hata in user_data.columns:
                    hata_sayisi = (user_data[hata] == 0).sum()
                    if hata_sayisi > 0:
                        st.error(f"**{hata}**: {hata_sayisi} Hata!")
                    else:
                        st.success(f"**{hata}**: Sorun Yok")

        st.subheader("📋 Detaylı Liste")
        st.dataframe(user_data[["Tarih", "Süre", "Form Puan", "Açıklama Detay"]], use_container_width=True)

    except Exception as e:
        st.error(f"Dosya okunurken bir hata oluştu: {e}")
        st.info("Lütfen Excel dosyasındaki sütun isimlerinin doğruluğundan emin olun.")

else:
    st.info("👋 Lütfen analiz için bir Excel veya CSV dosyası yükleyin.")
