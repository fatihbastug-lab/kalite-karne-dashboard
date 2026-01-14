import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa Ayarları
st.set_page_config(page_title="Kalite Karne Dashboard", layout="wide")

# CSS ile Görsel İyileştirme (Opsiyonel)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_all_headers=True)

st.title("📊 Kalite Karne Analiz Sistemi")

# --- 1. DOSYA YÜKLEME ALANI ---
uploaded_file = st.sidebar.file_uploader("Güncel CSV dosyasını buraya bırakın", type=["csv"])

if uploaded_file is not None:
    # Veriyi oku
    df = pd.read_csv(uploaded_file)
    
    # --- 2. FİLTRELER ---
    st.sidebar.divider()
    personel_listesi = sorted(df["Personel"].unique())
    selected_person = st.sidebar.selectbox("Analiz Edilecek Personeli Seçin", personel_listesi)
    
    # Veriyi filtrele
    user_data = df[df["Personel"] == selected_person]
    
    # --- 3. ÜST KPI KARTLARI ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ortalama Puan", f"{user_data['Form Puan'].mean():.1f}")
    with col2:
        st.metric("Değerlendirilen Çağrı", len(user_data))
    with col3:
        st.metric("Proje", user_data["Proje Adı"].iloc[0])
    with col4:
        st.metric("Dönem", user_data["Period Adı"].iloc[0])

    st.divider()

    # --- 4. KRİTER BAZLI BAŞARI (Görseldeki Bar Chart) ---
    st.subheader("🎯 Kriter Performans Analizi")
    kriterler = [
        "Karşılama/Bitirme", "Ses tonu/ Ses enerjisi - Kurumsal Görüşme Standartları",
        "Bekletme", "Etkin Dinleme- Çözüm Odaklı Yaklaşım", "Doğru Bilgilendirme", "Süreç Yönetimi"
    ]
    
    kriter_puanlari = user_data[kriterler].mean().reset_index()
    kriter_puanlari.columns = ["Kriter", "Başarı %"]
    
    fig = px.bar(kriter_puanlari, x="Başarı %", y="Kriter", orientation='h', 
                 text_auto='.1f', color="Başarı %", 
                 color_continuous_scale="RdYlGn", range_x=[0,100])
    
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. KRİTİK HATALAR ---
    st.subheader("🚨 Kritik Hata Kontrol Paneli")
    kritik_kolonlar = ["Can ve Mal Güvenliği", "Uygun Olmayan Davranışlar", "Kurum itibarını olumsuz etkileme"]
    
    ck1, ck2, ck3 = st.columns(3)
    for i, col_name in enumerate(kritik_kolonlar):
        hata_sayisi = (user_data[col_name] == 0).sum()
        with [ck1, ck2, ck3][i]:
            if hata_sayisi > 0:
                st.error(f"**{col_name}**\n\n{hata_sayisi} Adet Hata!")
            else:
                st.success(f"**{col_name}**\n\nKritik Hata Yok")

    # --- 6. ÇAĞRI DETAYLARI ---
    st.divider()
    st.subheader("📋 Detaylı Görüşme Listesi")
    st.dataframe(user_data[["Tarih", "Süre", "Arama Tipi", "Form Puan", "Açıklama Detay"]], 
                 use_container_width=True)

else:
    # Dosya yüklenmediyse uyarı ver
    st.info("💡 Başlamak için lütfen sol taraftaki alandan güncel 'Detay Liste' CSV dosyasını yükleyin.")
    st.image("https://img.icons8.com/clouds/500/upload.png", width=200)
