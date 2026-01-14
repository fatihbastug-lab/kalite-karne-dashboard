import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dinamik Pivot Analiz", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .metric-card { border: 1px solid #dee2e6; padding: 15px; border-radius: 8px; background-color: #F8F9FA; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧩 Esnek Pivot Analiz Paneli")

uploaded_file = st.sidebar.file_uploader("Dosyayı Yükleyin (DATA Sekmesi Önerilir)", type=["xlsx", "csv"])

if uploaded_file is not None:
    # Veri Okuma
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip() # Sütun isimlerindeki boşlukları temizle
    
    # --- 1. DİNAMİK FİLTRE SEÇİMİ (Sidebar) ---
    st.sidebar.header("⚙️ 1. Filtre Alanlarını Seç")
    filtre_sutunlari = st.sidebar.multiselect(
        "Hangi alanlara göre filtreleme yapmak istersiniz?",
        options=df.columns.tolist(),
        default=["Ekip Adı", "Yönetici", "Takım Lideri"]
    )

    # Seçilen her filtre alanı için dinamik selectbox oluştur
    filtered_df = df.copy()
    for col in filtre_sutunlari:
        secenekler = sorted(filtered_df[col].unique().tolist())
        secim = st.sidebar.multiselect(f"{col} Seçin", options=secenekler, default=secenekler)
        filtered_df = filtered_df[filtered_df[col].isin(secim)]

    # --- 2. SATIR (KIRILIM) SEÇİMİ ---
    st.subheader("📊 Pivot Kırılım Ayarları")
    col_k1, col_k2 = st.columns(2)
    
    with col_k1:
        satir_kirilimi = st.multiselect(
            "Satırlar (Pivot Rows):",
            options=df.columns.tolist(),
            default=["Temsilci"]
        )
    
    with col_k2:
        deger_sutunu = st.selectbox("Hesaplanacak Değer (Value):", options=["Kalite Puanı", "Puan"], index=0)

    # --- 3. PİVOT HESAPLAMA (Say ve Ortala) ---
    if satir_kirilimi:
        pivot_table = filtered_df.groupby(satir_kirilimi).agg(
            Adet=(deger_sutunu, 'count'),
            Ortalama=(deger_sutunu, 'mean')
        ).reset_index()

        # KPI Özetleri
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Kayıt", len(filtered_df))
        c2.metric("Genel Ortalama", f"%{filtered_df[deger_sutunu].mean():.1f}")
        c3.metric("Filtrelenmiş Grup Sayısı", len(pivot_table))

        # Pivot Tabloyu Göster
        st.write("### 📋 Pivot Tablo Sonucu")
        st.dataframe(pivot_table.sort_values(by="Ortalama", ascending=False), use_container_width=True)

        # Dinamik Grafik
        st.divider()
        st.subheader("📈 Görsel Analiz")
        # Grafik için ilk satır kırılımını x ekseni olarak alalım
        fig = px.bar(pivot_table, x=satir_kirilimi[0], y="Ortalama", color="Ortalama",
                     text_auto='.1f', title=f"{satir_kirilimi[0]} Bazlı Başarı Sıralaması",
                     color_continuous_scale="RdYlGn")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Lütfen analiz için en az bir 'Satır' alanı seçin.")

    # Ham Veri Çıktısı
    with st.expander("📥 Filtrelenmiş Ham Veriyi İndir / İncele"):
        st.dataframe(filtered_df)

else:
    st.info("Lütfen bir dosya yükleyerek 'Pivot Özelliklerini' kullanmaya başlayın.")
