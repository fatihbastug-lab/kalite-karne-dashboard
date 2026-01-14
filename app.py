import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="Pro Kalite Analiz", layout="wide")

# --- VERİ YÜKLEME ---
uploaded_file = st.sidebar.file_uploader("Dosyayı Yükleyin", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Okuma motoru
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    
    # Veri Temizleme (Tarih formatı)
    df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce')

    # --- FİLTRELEME ---
    st.sidebar.header("🔍 Gelişmiş Filtreler")
    selected_loc = st.sidebar.multiselect("Lokasyon Seçin", options=df["Grup Adı"].unique(), default=df["Grup Adı"].unique())
    
    mask = df["Grup Adı"].isin(selected_loc)
    df_filtered = df[mask]
    
    selected_person = st.sidebar.selectbox("Personel Seçin", df_filtered["Personel"].unique())
    user_data = df_filtered[df_filtered["Personel"] == selected_person]

    # --- 1. LOKASYON BAZLI KIYASLAMA ---
    st.subheader("📍 Lokasyon Bazlı Performans Kıyaslaması")
    loc_comparison = df.groupby("Grup Adı")["Form Puan"].mean().reset_index()
    fig_loc = px.bar(loc_comparison, x="Grup Adı", y="Form Puan", color="Form Puan",
                     title="Hangi Lokasyon Daha Başarılı?", color_continuous_scale="Viridis")
    st.plotly_chart(fig_loc, use_container_width=True)

    # --- 2. TREND ANALİZİ (Zaman İçindeki Değişim) ---
    st.divider()
    st.subheader(f"📈 {selected_person} - Performans Trendi")
    trend_data = user_data.sort_values("Tarih")
    fig_trend = px.line(trend_data, x="Tarih", y="Form Puan", markers=True, 
                        title="Zaman İçinde Puan Değişimi", line_shape="spline")
    st.plotly_chart(fig_trend, use_container_width=True)

    # --- 3. METİN ANALİZİ (Açıklamaları Okuma) ---
    st.divider()
    col_text, col_radar = st.columns(2)
    
    with col_text:
        st.subheader("📝 Koçluk Notları Analizi (Yapay Zeka)")
        # Açıklamaları birleştirip en çok geçen kelimeleri bulma
        text = " ".join(str(note) for note in user_data["Açıklama Detay"] if str(note) != 'nan')
        
        if len(text) > 10:
            wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='Reds').generate(text)
            fig_wc, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig_wc)
            st.caption("Notlarda en sık geçen kelimeler (Büyük kelimeler en çok hata yapılan konuları işaret eder).")
        else:
            st.write("Analiz için yeterli koçluk notu bulunamadı.")

    with col_radar:
        st.subheader("🎯 Yetkinlik Karnesi")
        kriterler = ["Karşılama/Bitirme", "Ses tonu/ Ses enerjisi - Kurumsal Görüşme Standartları", "Bekletme", "Etkin Dinleme- Çözüm Odaklı Yaklaşım", "Doğru Bilgilendirme", "Süreç Yönetimi"]
        mevcut = [k for k in kriterler if k in df.columns]
        
        # Personel vs Genel Ortalama
        personel_avg = user_data[mevcut].mean().values
        genel_avg = df[mevcut].mean().values
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=personel_avg, theta=mevcut, fill='toself', name='Personel'))
        fig_radar.add_trace(go.Scatterpolar(r=genel_avg, theta=mevcut, fill='toself', name='Genel Ortalama'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
        st.plotly_chart(fig_radar, use_container_width=True)

    # --- DETAY LİSTE ---
    st.divider()
    with st.expander("Tüm Kayıtları Gör"):
        st.dataframe(user_data)

else:
    st.info("Lütfen bir Excel/CSV dosyası yükleyerek başlayın.")
