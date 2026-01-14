import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa ayarları
st.set_page_config(page_title="Kalite Karne Dashboard", layout="wide")

# Veriyi oku
df = pd.read_csv("data.csv")

# Sol menü - Filtreler
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
st.sidebar.header("Personel Seçimi")
selected_person = st.sidebar.selectbox("Lütfen bir isim seçin:", df["Personel"].unique())

# Veriyi seçilen kişiye göre filtrele
user_data = df[df["Personel"] == selected_person]

# Üst Başlık ve Özet Bilgiler
st.title(f"📊 Kalite Karne: {selected_person}")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Ortalama Puan", f"{user_data['Form Puan'].mean():.1f}")
with col2:
    st.metric("Toplam Çağrı", len(user_data))
with col3:
    st.metric("Proje", user_data["Proje Adı"].iloc[0])
with col4:
    st.metric("Dönem", user_data["Period Adı"].iloc[0])

st.markdown("---")

# Orta Bölüm: Kriter Performansı (Görseldeki Bar Chart)
st.subheader("🎯 Kriter Bazlı Başarı Analizi")
kriterler = [
    "Karşılama/Bitirme", "Ses tonu/ Ses enerjisi - Kurumsal Görüşme Standartları",
    "Bekletme", "Etkin Dinleme- Çözüm Odaklı Yaklaşım", "Doğru Bilgilendirme", "Süreç Yönetimi"
]

# Kriter puanlarını hesapla
kriter_puanlari = user_data[kriterler].mean().reset_index()
kriter_puanlari.columns = ["Kriter", "Başarı %"]

fig = px.bar(kriter_puanlari, x="Başarı %", y="Kriter", orientation='h', 
             text_auto='.1f', color="Başarı %", color_continuous_scale="RdYlGn", range_x=[0,100])
st.plotly_chart(fig, use_container_width=True)

# Kritik Hatalar Paneli
st.subheader("🚨 Kritik Hata Kontrolü")
kritik_kolonlar = ["Can ve Mal Güvenliği", "Uygun Olmayan Davranışlar", "Kurum itibarını olumsuz etkileme"]

c1, c2, c3 = st.columns(3)
for idx, col in enumerate([c1, c2, c3]):
    hata_var_mi = (user_data[kritik_kolonlar[idx]] == 0).any()
    if hata_var_mi:
        col.error(f"❌ {kritik_kolonlar[idx]}")
    else:
        col.success(f"✅ {kritik_kolonlar[idx]}")

# Alt Bölüm: Çağrı Listesi
st.markdown("---")
st.subheader("📋 Çağrı Kayıtları ve Koçluk Notları")
st.dataframe(user_data[["Tarih", "Süre", "Arama Tipi", "Form Puan", "Açıklama Detay"]], use_container_width=True)
