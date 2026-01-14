import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa Genişliği
st.set_page_config(page_title="Kalite Karne", layout="wide")

# Veriyi oku (Dosya isminizle aynı olmalı)
df = pd.read_csv("data.csv")

# Başlık
st.title("📊 Kalite Karne Dashboard")

# Filtreler
personel = st.sidebar.selectbox("Personel Seçin", df["Personel"].unique())
veri = df[df["Personel"] == personel]

# Üst KPI Kartları
c1, c2, c3 = st.columns(3)
c1.metric("Ortalama Puan", f"{veri['Form Puan'].mean():.1f}")
c2.metric("Toplam Çağrı", len(veri))
c3.metric("Proje", veri["Proje Adı"].iloc[0])

st.divider()

# Kriter Bazlı Analiz (Görseldeki tablo/grafik yapısı)
st.subheader("🎯 Kriter Performansları")
kriterler = ["Karşılama/Bitirme", "Ses tonu/ Ses enerjisi - Kurumsal Görüşme Standartları", 
             "Bekletme", "Etkin Dinleme- Çözüm Odaklı Yaklaşım", "Doğru Bilgilendirme", "Süreç Yönetimi"]

puanlar = veri[kriterler].mean().reset_index()
puanlar.columns = ["Kriter", "Başarı Yüzdesi"]

fig = px.bar(puanlar, x="Başarı Yüzdesi", y="Kriter", orientation='h', 
             text_auto=True, color="Başarı Yüzdesi", color_continuous_scale="RdYlGn")
st.plotly_chart(fig, use_container_width=True)

# Kritik Hatalar
st.subheader("🚫 Kritik Hata Kontrolü")
kritik_hata_listesi = ["Can ve Mal Güvenliği", "Uygun Olmayan Davranışlar", "Kurum itibarını olumsuz etkileme"]
for hata in kritik_hata_listesi:
    if (veri[hata] == 0).any():
        st.error(f"DİKKAT: {hata} kriterinden hata yapılmıştır!")
    else:
        st.success(f"Temiz: {hata} kriterinde sorun yok.")

# Detay Tablo
st.subheader("📋 Çağrı Detayları")
st.write(veri[["Tarih", "Süre", "Form Puan", "Açıklama Detay"]])
