import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa Genişliği ve Tasarımı
st.set_page_config(page_title="Kalite Karne Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { border: 1px solid #d1d5db; padding: 15px; border-radius: 10px; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Kalite Karne Analiz Sistemi")

# --- DOSYA YÜKLEME ALANI ---
st.sidebar.header("📁 Veri Kaynağı")
uploaded_file = st.sidebar.file_uploader("Güncel CSV dosyasını buraya yükleyin", type=["csv"])

if uploaded_file is not None:
    # CSV dosyasını oku (Virgül veya Noktalı virgül ayrımını otomatik çözer)
    df = pd.read_csv(uploaded_file, sep=None, engine='python')
    
    # --- FİLTRELER ---
    st.sidebar.divider()
    personel_listesi = sorted(df["Personel"].unique())
    selected_person = st.sidebar.selectbox("Personel Seçin", personel_listesi)
    
    # Seçilen personelin verileri
    user_data = df[df["Personel"] == selected_person]
    
    # --- ÜST KPI KARTLARI ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ortalama Puan", f"{user_data['Form Puan'].mean():.1f}")
    with col2:
        st.metric("Toplam Değerlendirme", len(user_data))
    with col3:
        st.metric("Proje", user_data["Proje Adı"].iloc[0])
    with col4:
        st.metric("Dönem", user_data["Period Adı"].iloc[0])

    st.divider()

    # --- KRİTER ANALİZİ (Görseldeki Bar Grafik) ---
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
        
        # Sütun isimlerini kontrol ederek ortalamaları al
        mevcut_kriterler = [k for k in kriterler if k in df.columns]
        puanlar = user_data[mevcut_kriterler].mean().reset_index()
        puanlar.columns = ["Kriter", "Başarı %"]
        
        fig = px.bar(puanlar, x="Başarı %", y="Kriter", orientation='h', 
                     text_auto='.1f', color="Başarı %", 
                     color_continuous_scale="RdYlGn", range_x=[0,105])
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("🚨 Kritik Hatalar")
        # Kritik hata kolonları (Dosyadaki isimlerle eşleşmeli)
        kritik_hatalar = [
            "Can ve Mal Güvenliği", 
            "Müşteriye ait bilgilerin 3. Şahıslar ile paylaşılması",
            "Kurum itibarını olumsuz etkileme",
            "Uygun Olmayan Davranışlar"
        ]
        
        for hata in kritik_hatalar:
            if hata in user_data.columns:
                hata_sayisi = (user_data[hata] == 0).sum()
                if hata_sayisi > 0:
                    st.error(f"**{hata}**\n\n{hata_sayisi} Adet Kritik Hata!")
                else:
                    st.success(f"**{hata}**\n\nSorun Yok")

    # --- ALT TABLO: ÇAĞRI DETAYLARI ---
    st.divider()
    st.subheader("📋 Çağrı Kayıtları ve Notlar")
    st.dataframe(
        user_data[["Tarih", "Süre", "Arama Tipi", "Form Puan", "Açıklama Detay"]],
        use_container_width=True,
        hide_index=True
    )

else:
    # Dosya yüklenmediyse gösterilecek mesaj
    st.info("👋 Başlamak için lütfen sol paneldeki 'Browse files' butonuna tıklayarak CSV dosyasını yükleyin.")
