import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Sayfa Ayarları
st.set_page_config(page_title="Kalite Karne Dashboard", layout="wide")

# Görseldeki Tasarıma Yakın CSS
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .stMetric { border: 1px solid #E6E9EF; padding: 15px; border-radius: 8px; background-color: #F8F9FA; }
    .hata-vurgu { padding: 10px; border-left: 5px solid #E74C3C; background-color: #FDEDEC; color: #7B241C; font-weight: bold; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Personel Kalite Karnesi")

uploaded_file = st.sidebar.file_uploader("Excel (.xlsx) dosyasını yükleyin", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    # --- FİLTRELEME (Grup -> Takım -> Personel) ---
    st.sidebar.header("🔍 Filtreler")
    grup = st.sidebar.selectbox("Grup/Lokasyon", sorted(df["Grup Adı"].unique()))
    df_grup = df[df["Grup Adı"] == grup]
    
    takim = st.sidebar.selectbox("Takım", sorted(df_grup["Takım Adı"].unique()))
    df_takim = df_grup[df_grup["Takım Adı"] == takim]
    
    personel = st.sidebar.selectbox("Personel", sorted(df_takim["Personel"].unique()))
    user_data = df_takim[df_takim["Personel"] == personel]

    # --- ÜST ÖZET KARTLARI ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Dinlenen Çağrı", len(user_data))
    c2.metric("Kalite Ortalaması", f"{user_data['Form Puan'].mean():.1f}")
    c3.metric("Takım Ortalaması", f"{df_takim['Form Puan'].mean():.1f}")
    c4.metric("Dönem", user_data["Period Adı"].iloc[0])

    st.divider()

    # --- ÇAĞRI ETİKETİNE GÖRE ANALİZ (Şikayet, Teşekkür, Kalite) ---
    st.subheader("📋 Çağrı Etiketi Bazlı Analiz")
    # CSV'deki 'Çağrı Etiketi' sütununa göre gruplama yapar
    etiket_analiz = user_data.groupby("Çağrı Etiketi").agg(
        Adet=('Form Puan', 'count'),
        Ortalama=('Form Puan', 'mean')
    ).reset_index()
    
    ec1, ec2 = st.columns([1, 2])
    with ec1:
        st.dataframe(etiket_analiz, hide_index=True, use_container_width=True)
    with ec2:
        fig_etiket = px.bar(etiket_analiz, x="Çağrı Etiketi", y="Adet", text="Ortalama",
                            title="Etiketlere Göre Çağrı Sayıları (Üstteki sayılar ortalama puandır)",
                            color="Ortalama", color_continuous_scale="RdYlGn")
        st.plotly_chart(fig_etiket, use_container_width=True)

    # --- KRİTER VE EN ÇOK YAPILAN HATA ANALİZİ ---
    st.divider()
    col_ana, col_yan = st.columns([2, 1])

    with col_ana:
        st.subheader("🎯 Kriter Bazlı Başarı")
        kriterler = ["Karşılama/Bitirme", "Ses tonu/ Ses enerjisi - Kurumsal Görüşme Standartları", 
                     "Bekletme", "Etkin Dinleme- Çözüm Odaklı Yaklaşım", "Doğru Bilgilendirme", "Süreç Yönetimi"]
        mevcut = [k for k in kriterler if k in df.columns]
        puanlar = user_data[mevcut].mean().reset_index()
        puanlar.columns = ["Kriter", "Başarı %"]
        
        fig = px.bar(puanlar, x="Başarı %", y="Kriter", orientation='h', text_auto='.1f',
                     color="Başarı %", color_continuous_scale="RdYlGn", range_x=[0,105])
        st.plotly_chart(fig, use_container_width=True)

    with col_yan:
        st.subheader("❌ En Çok Hata Yapılan Kriterler")
        # Puanı 100'den düşük olan kriterleri bulup sıralar
        hatalar = user_data[mevcut].mean().sort_values().head(3)
        for k, v in hatalar.items():
            if v < 100:
                st.markdown(f'<div class="hata-vurgu">{k}: %{v:.1f} başarı</div>', unsafe_allow_html=True)
        
        st.subheader("🚨 Kritik Hatalar")
        kritik = ["Can ve Mal Güvenliği", "Uygun Olmayan Davranışlar", "Kurum itibarını olumsuz etkileme"]
        for h in kritik:
            if h in user_data.columns:
                hata_sayisi = (user_data[h] == 0).sum()
                if hata_sayisi > 0:
                    st.error(f"{h}: {hata_sayisi} Adet Kritik Hata!")

    # --- DETAY LİSTE ---
    st.divider()
    with st.expander("Çağrı Detaylarını ve Koçluk Notlarını Gör"):
        st.dataframe(user_data[["Tarih", "Çağrı Etiketi", "Form Puan", "Açıklama Detay"]], use_container_width=True)

else:
    st.info("Lütfen sol taraftan Excel dosyasını (.xlsx) yükleyerek başlayın.")
