import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="Pro Kalite Dashboard", layout="wide")

# Tasarım İyileştirmeleri
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Gelişmiş Kalite Analiz ve Koçluk Sistemi")

uploaded_file = st.sidebar.file_uploader("Excel veya CSV Yükleyin", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Veri Okuma
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        df['Tarih'] = pd.to_datetime(df['Tarih'], errors='coerce')

        # --- HIYERARŞİK FİLTRELER ---
        st.sidebar.header("🔍 Dinamik Filtreler")
        
        # 1. Lokasyon (Grup Adı)
        loc_list = sorted(df["Grup Adı"].unique().tolist())
        selected_loc = st.sidebar.multiselect("Lokasyon(lar) Seçin", loc_list, default=loc_list)
        df_loc = df[df["Grup Adı"].isin(selected_loc)]

        # 2. Takım
        team_list = sorted(df_loc["Takım Adı"].unique().tolist())
        selected_team = st.sidebar.selectbox("Takım Seçin", ["Hepsi"] + team_list)
        df_team = df_loc if selected_team == "Hepsi" else df_loc[df_loc["Takım Adı"] == selected_team]

        # 3. Personel
        person_list = sorted(df_team["Personel"].unique().tolist())
        selected_person = st.sidebar.selectbox("Personel Seçin", person_list)
        
        user_data = df_team[df_team["Personel"] == selected_person].sort_values("Tarih")

        # --- KPI ÖZET ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Personel Puanı", f"{user_data['Form Puan'].mean():.1f}")
        c2.metric("Ekip Ortalaması", f"{df_team['Form Puan'].mean():.1f}")
        c3.metric("Değerlendirme", len(user_data))
        c4.metric("Son Puan", f"{user_data['Form Puan'].iloc[-1]}")

        # --- TREND VE LOKASYON ANALİZİ ---
        st.divider()
        col_trend, col_loc = st.columns(2)

        with col_trend:
            st.subheader("📈 Performans Trendi")
            fig_trend = px.line(user_data, x="Tarih", y="Form Puan", markers=True, 
                                line_shape="spline", title="Zaman İçindeki Puan Değişimi")
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_loc:
            st.subheader("🌍 Lokasyon Kıyaslaması")
            loc_avg = df.groupby("Grup Adı")["Form Puan"].mean().reset_index()
            fig_loc = px.bar(loc_avg, x="Grup Adı", y="Form Puan", color="Form Puan", 
                             color_continuous_scale="RdYlGn")
            st.plotly_chart(fig_loc, use_container_width=True)

        # --- METİN ANALİZİ VE RADAR ---
        st.divider()
        col_text, col_radar = st.columns(2)

        with col_text:
            st.subheader("🗣️ Koçluk Notları Analizi (Yapay Zeka)")
            # Açıklamaları okuma ve analiz etme
            all_notes = " ".join(str(n) for n in user_data["Açıklama Detay"] if str(n).lower() != 'nan')
            
            if len(all_notes) > 10:
                # WordCloud oluşturma
                wc = WordCloud(width=600, height=300, background_color='white', colormap='tab10').generate(all_notes)
                fig_wc, ax = plt.subplots()
                ax.imshow(wc, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig_wc)
                st.info("Büyük görünen kelimeler koçluk notlarında en çok geçen konulardır.")
            else:
                st.warning("Bu personel için yeterli not bulunamadı.")

        with col_radar:
            st.subheader("🎯 Yetkinlik Kıyaslama (Radar)")
            kriterler = ["Karşılama/Bitirme", "Ses tonu/ Ses enerjisi - Kurumsal Görüşme Standartları", 
                         "Bekletme", "Etkin Dinleme- Çözüm Odaklı Yaklaşım", "Doğru Bilgilendirme", "Süreç Yönetimi"]
            mevcut = [k for k in kriterler if k in df.columns]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=user_data[mevcut].mean().values, theta=mevcut, fill='toself', name='Personel'))
            fig_radar.add_trace(go.Scatterpolar(r=df_team[mevcut].mean().values, theta=mevcut, fill='toself', name='Takım Ort.'))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True)
            st.plotly_chart(fig_radar, use_container_width=True)

        # Detaylı Liste
        with st.expander("Görüşme Detaylarını ve Ham Veriyi Gör"):
            st.write(user_data)

    except Exception as e:
        st.error(f"Sistem bir hata ile karşılaştı: {e}")
else:
    st.info("Lütfen sol menüden bir Excel veya CSV dosyası yükleyerek başlayın.")
