import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa Yapılandırması
st.set_page_config(page_title="Kalite Karnesi", layout="wide")

# Görseldeki Tasarım İçin Stil (CSS)
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .stMetric { border: 1px solid #E6E9EF; padding: 20px; border-radius: 5px; background-color: #F8F9FA; }
    .pivot-container { border: 1px solid #dee2e6; padding: 15px; border-radius: 10px; background-color: #FFFFFF; }
    .hata-box { padding: 10px; border-radius: 5px; margin-bottom: 8px; color: white; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("📑 Kalite Karnesi")

uploaded_file = st.sidebar.file_uploader("Excel Dosyasını Yükleyin (DATA Sekmesi Önerilir)", type=["xlsx", "csv"])

if uploaded_file is not None:
    # Veriyi Oku
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # Sayısal veri dönüşümü
    puan_col = "Kalite Puanı" if "Kalite Puanı" in df.columns else "Form Puan"
    df[puan_col] = pd.to_numeric(df[puan_col], errors='coerce')

    # --- 1. DİNAMİK FİLTRE PANELİ (Sidebar - Kontrol Sende) ---
    st.sidebar.header("⚙️ Filtre Ayarları")
    filtre_alanlari = st.sidebar.multiselect(
        "Kullanılacak Filtreleri Seçin:",
        options=df.columns.tolist(),
        default=["Ekip Adı", "Yönetici", "Takım Lideri", "Temsilci"]
    )

    filtered_df = df.copy()
    for col in filtre_alanlari:
        secenekler = sorted(filtered_df[col].unique().tolist())
        secim = st.sidebar.multiselect(f"{col} Seçin", options=secenekler, default=secenekler)
        filtered_df = filtered_df[filtered_df[col].isin(secim)]

    # --- 2. ÜST ÖZET (Görseldeki Karne Tasarımı) ---
    st.subheader("📌 Genel Performans Özeti")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.metric("ORTALAMA PUAN", f"{filtered_df[puan_col].mean():.1f}")
    with c2:
        st.metric("ÇAĞRI ADEDİ", len(filtered_df.drop_duplicates(subset=['Değerlendirme No' if 'Değerlendirme No' in df.columns else 'Call ID'])))
    with c3:
        st.metric("HATA ADEDİ", len(filtered_df[filtered_df["Puan"] == 0]))
    with c4:
        st.metric("FCR ORANI", f"%{(len(filtered_df[filtered_df['Cevap'] == 'EVET']) / len(filtered_df) * 100):.1f}" if 'Cevap' in df.columns else "N/A")

    st.divider()

    # --- 3. PİVOT KIRILIM VE GRAFİK (Orta Kısım) ---
    col_pivot, col_kritik = st.columns([2, 1])

    with col_pivot:
        st.subheader("📊 Dinamik Pivot Analizi")
        satir_secimi = st.multiselect(
            "Satırlar (Kırılım Seçin):",
            options=df.columns.tolist(),
            default=["KaliteGrup"]
        )
        
        if satir_secimi:
            pivot_data = filtered_df.groupby(satir_secimi).agg(
                Çağrı_Adedi=(puan_col, 'count'),
                Başarı_Ortalaması=(puan_col, 'mean')
            ).reset_index()
            
            st.dataframe(pivot_data.sort_values(by="Başarı_Ortalaması", ascending=False), use_container_width=True)
            
            # Görseldeki Bar Grafik
            fig = px.bar(pivot_data, x="Başarı_Ortalaması", y=satir_secimi[0], orientation='h',
                         text_auto='.1f', color="Başarı_Ortalaması", color_continuous_scale="RdYlGn")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col_kritik:
        st.subheader("🚨 Kritik Durum")
        # En çok hata yapılan parametreler
        hata_ozeti = filtered_df[filtered_df["Puan"] == 0]["Kalite Tip Açıklama"].value_counts().head(5)
        
        if not hata_ozeti.empty:
            for hata, count in hata_ozeti.items():
                st.markdown(f'<div class="hata-box" style="background-color: #E74C3C;">{count} Kez: {hata}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="hata-box" style="background-color: #27AE60;">✅ Kritik Hata Tespit Edilmedi</div>', unsafe_allow_html=True)
        
        st.info("💡 İpucu: Sol taraftan farklı filtreler seçerek bu hataları asistan bazlı daraltabilirsiniz.")

    # --- 4. DETAY LİSTE ---
    st.divider()
    with st.expander("📋 Detaylı Veri Satırlarını İncele"):
        st.write(filtered_df)

else:
    st.info("👋 Hoş Geldiniz! Analize başlamak için lütfen 'Kalite Kırılım Raporu' dosyanızı yükleyin.")
