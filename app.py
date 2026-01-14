import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Pro Kalite Pivot Dashboard", layout="wide")

# Görseldeki Karne Tasarımı İçin Stil
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .metric-card { border: 1px solid #E6E9EF; padding: 15px; border-radius: 10px; background-color: #F8F9FA; text-align: center; }
    .hata-vurgu { padding: 10px; border-left: 5px solid #E74C3C; background-color: #FDEDEC; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Dinamik Kalite Kırılım ve Pivot Analizi")

uploaded_file = st.sidebar.file_uploader("Excel veya CSV dosyasını yükleyin", type=["xlsx", "csv"])

if uploaded_file is not None:
    # Veriyi Yükle
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # Sütun isimlerini temizle
    df.columns = df.columns.str.strip()
    
    # Puan sütununu sayısal yap (Hata almamak için)
    puan_col = "Kalite Puanı" if "Kalite Puanı" in df.columns else "Form Puan"
    df[puan_col] = pd.to_numeric(df[puan_col], errors='coerce')

    # --- 5 KATMANLI GELİŞMİŞ FİLTRELEME ---
    st.sidebar.header("🔍 Pivot Filtreleri")
    
    ekip = st.sidebar.multiselect("1. Ekip / Lokasyon", options=sorted(df["Ekip Adı"].unique()), default=df["Ekip Adı"].unique())
    df_f1 = df[df["Ekip Adı"].isin(ekip)]
    
    yonetici = st.sidebar.multiselect("2. Yönetici", options=sorted(df_f1["Yönetici"].unique()), default=df_f1["Yönetici"].unique())
    df_f2 = df_f1[df_f1["Yönetici"].isin(yonetici)]
    
    t_lideri = st.sidebar.multiselect("3. Takım Lideri", options=sorted(df_f2["Takım Lideri"].unique()), default=df_f2["Takım Lideri"].unique())
    df_f3 = df_f2[df_f2["Takım Lideri"].isin(t_lideri)]
    
    etiket = st.sidebar.multiselect("4. Çağrı Etiketi", options=sorted(df_f3["Çağrı Etiketi"].unique()), default=df_f3["Çağrı Etiketi"].unique())
    df_f4 = df_f3[df_f3["Çağrı Etiketi"].isin(etiket)]
    
    temsilci = st.sidebar.selectbox("5. Temsilci (Karne Görünümü)", sorted(df_f4["Temsilci"].unique()))
    user_data = df_f4[df_f4["Temsilci"] == temsilci]

    # --- PİVOT ÖZET METRİKLER (Say/Ortalama) ---
    st.subheader(f"📈 {temsilci} - Yönetici Özeti")
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown(f'<div class="metric-card"><b>Toplam Çağrı (Count)</b><br><span style="font-size:24px;">{len(user_data)}</span></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><b>Kalite Ort. (Average)</b><br><span style="font-size:24px;">%{user_data[puan_col].mean():.1f}</span></div>', unsafe_allow_html=True)
    with m3:
        # Şikayet/Teşekkür saydırma (Pivot gibi)
        sikayet_sayisi = len(user_data[user_data["Çağrı Etiketi"].str.contains("Şikayet", na=False)])
        st.markdown(f'<div class="metric-card"><b>Şikayet Adedi</b><br><span style="font-size:24px;">{sikayet_sayisi}</span></div>', unsafe_allow_html=True)
    with m4:
        # En çok hata yapılan grup
        en_cok_hata = user_data[user_data["Puan"] == 0]["KaliteGrup"].mode()
        hata_metni = en_cok_hata[0] if not en_cok_hata.empty else "Hata Yok"
        st.markdown(f'<div class="metric-card"><b>En Çok Hata:</b><br><span style="font-size:16px;">{hata_metni}</span></div>', unsafe_allow_html=True)

    st.divider()

    # --- PİVOT TABLO GÖRÜNÜMÜ (Etiket Bazlı Say ve Ortalamalar) ---
    st.subheader("📋 Çağrı Etiketlerine Göre Pivot Kırılım")
    pivot_df = user_data.groupby("Çağrı Etiketi").agg(
        Adet=(puan_col, 'count'),
        Ortalama_Puan=(puan_col, 'mean')
    ).reset_index()
    st.dataframe(pivot_df, use_container_width=True, hide_index=True)

    # --- KRİTER ANALİZİ (Görseldeki Bar Grafik) ---
    st.divider()
    col_graph, col_list = st.columns([2, 1])
    
    with col_graph:
        st.subheader("🎯 Kırılım Bazlı Başarı Oranları")
        # KaliteGrup bazında puan ortalamaları
        kırılım_puan = user_data.groupby("KaliteGrup")["Puan"].mean().reset_index()
        fig = px.bar(kırılım_puan, x="Puan", y="KaliteGrup", orientation='h', 
                     color="Puan", color_continuous_scale="RdYlGn", text_auto='.1f')
        st.plotly_chart(fig, use_container_width=True)

    with col_list:
        st.subheader("❌ Hatalı Parametreler")
        # Puanı 0 olan satırları bul
        hatalar = user_data[user_data["Puan"] == 0]["Kalite Tip Açıklama"].value_counts().head(5)
        if not hatal.empty:
            for txt, count in hatal.items():
                st.markdown(f'<div class="hata-vurgu"><b>{count} Kez:</b> {txt}</div>', unsafe_allow_html=True)
        else:
            st.success("Temsilcinin bu filtrelerde hatalı parametresi bulunmuyor.")

    # --- HAM VERİ ---
    with st.expander("Tüm Veri Satırlarını İncele"):
        st.write(user_data)

else:
    st.info("💡 Lütfen yeni 'Kalite Kırılım Raporu' dosyasını yükleyin. Filtreler otomatik olarak güncellenecektir.")
