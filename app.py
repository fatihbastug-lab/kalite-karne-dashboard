import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Sayfa Genişliği ve Başlık
st.set_page_config(page_title="Kalite Karne Dashboard", layout="wide")

# Görsel Stil Ayarları
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { border: 1px solid #dee2e6; padding: 10px; border-radius: 10px; background-color: white; }
    </style>
    """, unsafe_allow_all_headers=True)

st.title("📊 Kalite Karne Analiz Sistemi")

# --- 1. DOSYA YÜKLEME ALANI ---
st.sidebar.header("📁 Veri Kaynağı")
uploaded_file = st.sidebar.file_uploader("Güncel CSV dosyasını seçin veya sürükleyin", type=["csv"])

if uploaded_file is not None:
    # Veriyi oku (Noktalı virgül veya virgül ayrımını otomatik çözer)
    df = pd.read_csv(uploaded_file, sep=None, engine='python')
    
    # --- 2. FİLTRELER ---
    st.sidebar.divider()
    personel_listesi = sorted(df["Personel"].unique())
    selected_person = st.sidebar.selectbox("Personel Seçin", personel_listesi)
    
    # Seçilen personelin verileri
    user_data = df[df["Personel"] == selected_person]
    
    # --- 3. ÜST ÖZET BİLGİLER (KPI) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ortalama Puan", f"{user_data['Form Puan'].mean():.1f}")
    with col2:
        st.metric("Toplam Değerlendirme", len(user_data))
    with col3:
        st.metric("Proje", user_data["Proje Adı"].iloc[0])
    with col4:
        st.metric("Son Değerlendirme", user_data["Tarih"].iloc[0])

    st.divider()

    # --- 4. KRİTER ANALİZİ (Bar Chart) ---
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
        
        # Mevcut kriterleri dataframe içinde kontrol et ve ortalamalarını al
        mevcut_kriterler = [k for k in kriterler if k in df.columns]
        puanlar = user_data[mevcut_kriterler].mean().reset_index()
        puanlar.columns = ["Kriter", "Başarı %"]
        
        fig = px.bar(puanlar, x="Başarı %", y="Kriter", orientation='h', 
                     text_auto='.1f', color="Başarı %", 
                     color_continuous_scale="RdYlGn", range_x=[0,105])
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("🚨 Kritik Hatalar")
        # Kritik hata kolonlarını kontrol et
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
                    st.error(f"**{hata}**\n\n{hata_sayisi} Kez Hata Yapıldı!")
                else:
                    st.success(f"**{hata}**\n\nSorun Yok")

    # --- 5. LİSTE VE NOTLAR ---
    st.divider()
    st.subheader("📋 Görüşme Detayları ve Koçluk Notları")
    st.dataframe(
        user_data[["Tarih", "Süre", "Arama Tipi", "Form Puan", "Açıklama Detay"]],
        use_container_width=True,
        hide_index=True
    )

else:
    # Henüz dosya yüklenmediyse gösterilecek ekran
    st.info("👋 Hoş Geldiniz! Dashboard'u oluşturmak için lütfen sol taraftaki menüden CSV dosyanızı yükleyin.")
