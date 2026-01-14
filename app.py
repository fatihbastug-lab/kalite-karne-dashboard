import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Sayfa Yapılandırması
st.set_page_config(page_title="Akıllı Kalite Asistanı", layout="wide")

# Görsel Stil (Daha Sade ve Modern)
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #2E86C1; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 Akıllı Kalite Analiz ve Koçluk Paneli")

uploaded_file = st.sidebar.file_uploader("Excel veya CSV Yükleyin", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Veri Okuma
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce')
    
    # --- FİLTRE PANELİ ---
    st.sidebar.subheader("📍 Hiyerarşik Seçim")
    grup = st.sidebar.selectbox("Lokasyon / Grup", sorted(df["Grup Adı"].unique()))
    df_grup = df[df["Grup Adı"] == grup]
    
    takim = st.sidebar.selectbox("Takım", sorted(df_grup["Takım Adı"].unique()))
    df_takim = df_grup[df_grup["Takım Adı"] == takim]
    
    personel = st.sidebar.selectbox("Personel", sorted(df_takim["Personel"].unique()))
    user_data = df_takim[df_takim["Personel"] == personel].sort_values("Tarih")

    # --- ÜST ÖZET KARTLARI ---
    st.subheader(f"👤 Personel Özeti: {personel}")
    k1, k2, k3, k4 = st.columns(4)
    avg_puan = user_data['Form Puan'].mean()
    k1.metric("Genel Puan Ort.", f"{avg_puan:.1f}")
    k2.metric("Değerlendirme Sayısı", len(user_data))
    k3.metric("Takım Ortalaması", f"{df_takim['Form Puan'].mean():.1f}")
    
    # Gelişim Durumu (Son puan vs Ortalama)
    diff = user_data['Form Puan'].iloc[-1] - avg_puan
    k4.metric("Son Çağrı Performansı", f"{user_data['Form Puan'].iloc[-1]}", delta=f"{diff:.1f}")

    st.divider()

    # --- ANALİZ BÖLÜMÜ ---
    col_ana, col_yan = st.columns([2, 1])

    with col_ana:
        st.subheader("📊 Performans Gelişim Grafiği")
        fig_trend = px.area(user_data, x="Tarih", y="Form Puan", title="Zaman İçindeki Puan Seyri",
                            color_discrete_sequence=['#3498DB'])
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # OTOMATİK TAVSİYE SİSTEMİ
        st.subheader("💡 Yapay Zeka Koçluk Tavsiyesi")
        kriterler = ["Karşılama/Bitirme", "Ses tonu/ Ses enerjisi - Kurumsal Görüşme Standartları", 
                     "Bekletme", "Etkin Dinleme- Çözüm Odaklı Yaklaşım", "Doğru Bilgilendirme", "Süreç Yönetimi"]
        mevcut = [k for k in kriterler if k in df.columns]
        en_dusuk_kriter = user_data[mevcut].mean().idxmin()
        st.info(f"🚀 **Odaklanılması Gereken Alan:** Bu personelin en çok zorlandığı konu **'{en_dusuk_kriter}'**. Bir sonraki koçluk seansında bu kriter üzerine pratik yapılması önerilir.")

    with col_yan:
        st.subheader("🏷️ Notlardaki Anahtar Kelimeler")
        notlar = " ".join(str(n) for n in user_data["Açıklama Detay"] if str(n).lower() != 'nan')
        if len(notlar) > 5:
            wc = WordCloud(width=400, height=400, background_color='white', colormap='Set2').generate(notlar)
            fig_wc, ax = plt.subplots()
            ax.imshow(wc)
            ax.axis("off")
            st.pyplot(fig_wc)
        else:
            st.write("Analiz için not bulunamadı.")

    # --- LOKASYON KIYASLAMA ---
    st.divider()
    st.subheader("🏢 Lokasyon Bazlı Genel Durum")
    fig_loc = px.box(df, x="Grup Adı", y="Form Puan", color="Grup Adı", title="Lokasyonların Puan Dağılımı (Yayılım)")
    st.plotly_chart(fig_loc, use_container_width=True)

    # DETAY LİSTE
    with st.expander("Görüşme Kayıtlarını ve Özel Notları İncele"):
        st.table(user_data[["Tarih", "Form Puan", "Açıklama Detay"]].tail(5))

else:
    st.info("Lütfen bir dosya yükleyerek analiz sistemini başlatın.")
