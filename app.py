import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Sayfa Genişliği
st.set_page_config(page_title="Kalite Karne Dashboard", layout="wide")

# Görseldeki Temiz Tasarım İçin CSS
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .stMetric { border: 1px solid #E6E9EF; padding: 20px; border-radius: 5px; background-color: #F8F9FA; }
    .kritik-kutu { padding: 15px; border-radius: 5px; margin-bottom: 10px; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("📑 Kalite Değerlendirme Karnesi")

uploaded_file = st.sidebar.file_uploader("Excel Dosyasını Yükleyin", type=["xlsx", "csv"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    
    # --- HIYERARŞİK FİLTRELER (LOKASYON -> TAKIM -> PERSONEL) ---
    st.sidebar.header("🔍 Filtreleme Paneli")
    
    # 1. Lokasyon (Grup Adı)
    lokasyonlar = sorted(df["Grup Adı"].unique())
    secili_lokasyon = st.sidebar.selectbox("Lokasyon Seçin", lokasyonlar)
    df_lok = df[df["Grup Adı"] == secili_lokasyon]
    
    # 2. Takım
    takimlar = sorted(df_lok["Takım Adı"].unique())
    secili_takim = st.sidebar.selectbox("Takım Seçin", takimlar)
    df_takim = df_lok[df_lok["Takım Adı"] == secili_takim]
    
    # 3. Personel
    personeller = sorted(df_takim["Personel"].unique())
    secili_personel = st.sidebar.selectbox("Personel Seçin", personeller)
    user_data = df_takim[df_takim["Personel"] == secili_personel]

    # --- ÜST BİLGİ VE KPI (Görseldeki Sol Üst Kısım) ---
    col_kpi, col_kritik = st.columns([2, 1])

    with col_kpi:
        c1, c2, c3 = st.columns(3)
        c1.metric("KALİTE PUANI", f"{user_data['Form Puan'].mean():.1f}")
        c2.metric("ÇAĞRI ADEDİ", len(user_data))
        c3.metric("LOKASYON", secili_lokasyon)
        
        # --- ORTA KISIM: KRİTER BAZLI ANALİZ (Görseldeki Bar Grafik) ---
        st.subheader("🎯 Kriter Bazlı Başarı Oranı")
        kriterler = ["Karşılama/Bitirme", "Ses tonu/ Ses enerjisi - Kurumsal Görüşme Standartları", 
                     "Bekletme", "Etkin Dinleme- Çözüm Odaklı Yaklaşım", "Doğru Bilgilendirme", "Süreç Yönetimi"]
        mevcut = [k for k in kriterler if k in df.columns]
        puanlar = user_data[mevcut].mean().reset_index()
        puanlar.columns = ["Kriter", "Başarı %"]
        
        fig = px.bar(puanlar, x="Başarı %", y="Kriter", orientation='h', text_auto='.1f',
                     color="Başarı %", color_continuous_scale="RdYlGn", range_x=[0,105])
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_kritik:
        st.subheader("🚨 Kritik Hatalar")
        # Görseldeki gibi kırmızı kutular
        kritik_listesi = ["Can ve Mal Güvenliği", "Uygun Olmayan Davranışlar", "Kurum itibarını olumsuz etkileme"]
        for k_hata in kritik_listesi:
            if k_hata in user_data.columns:
                hata_var = (user_data[k_hata] == 0).any()
                if hata_var:
                    st.markdown(f'<div class="kritik-kutu" style="background-color: #E74C3C;">⚠️ {k_hata}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="kritik-kutu" style="background-color: #27AE60;">✅ {k_hata} Sorun Yok</div>', unsafe_allow_html=True)
        
        # ANALİZ: KELİME BULUTU (Açıklamaları Okuma)
        st.divider()
        st.subheader("🗨️ Not Analizi")
        notlar = " ".join(str(n) for n in user_data["Açıklama Detay"] if str(n).lower() != 'nan')
        if len(notlar) > 5:
            wc = WordCloud(width=300, height=200, background_color='white').generate(notlar)
            fig_wc, ax = plt.subplots()
            ax.imshow(wc)
            ax.axis("off")
            st.pyplot(fig_wc)

    # --- ALT KISIM: ÇAĞRI LİSTESİ (Görseldeki Tablo) ---
    st.divider()
    st.subheader("📋 Görüşme Detayları")
    st.dataframe(user_data[["Tarih", "Süre", "Arama Tipi", "Form Puan", "Açıklama Detay"]], use_container_width=True)

else:
    st.info("Lütfen sol taraftan Excel dosyasını yükleyin.")
