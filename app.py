import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Kalite Karnesi Pro", layout="wide")

# Tasarım: İlk attığın görsele sadık kalınmıştır
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .stMetric { border: 1px solid #E6E9EF; padding: 20px; border-radius: 8px; background-color: #F8F9FA; }
    .hata-box { padding: 10px; border-radius: 5px; margin-bottom: 8px; color: white; font-weight: bold; text-align: center; font-size: 13px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📑 Kalite Karnesi")

uploaded_file = st.sidebar.file_uploader("Excel Dosyasını Yükleyin (DATA Sekmesini Seçin)", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # Veriyi Oku (DATA sekmesine odaklı)
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()

        # --- DİNAMİK FİLTRELEME ---
        st.sidebar.header("🔍 Filtre Paneli")
        
        # Sütun varlık kontrolü yaparak filtreleri oluştur
        def get_opt(col): return sorted(df[col].dropna().unique().tolist()) if col in df.columns else []

        f_ekip = st.sidebar.multiselect("Ekip Adı", get_opt("Ekip Adı"), default=get_opt("Ekip Adı")[:2])
        df_f = df[df["Ekip Adı"].isin(f_ekip)] if f_ekip else df
        
        f_lider = st.sidebar.multiselect("Takım Lideri", sorted(df_f["Takım Lideri"].unique().tolist()))
        if f_lider: df_f = df_f[df_f["Takım Lideri"].isin(f_lider)]
        
        f_temsilci = st.sidebar.selectbox("Temsilci Seçin", sorted(df_f["Temsilci"].unique().tolist()))
        # Temsilciye ait tüm satırlar
        user_rows = df_f[df_f["Temsilci"] == f_temsilci]

        # --- VERİ ANALİZİ (PİVOT MANTIĞI) ---
        # Her Değerlendirme No aslında tek bir çağrıdır.
        unique_calls = user_rows.drop_duplicates(subset=["Değerlendirme No"])
        
        # --- ÜST ÖZET KARTLARI ---
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("ORTALAMA PUAN", f"{unique_calls['Kalite Puanı'].mean():.1f}")
        with c2:
            st.metric("DİNLENEN ÇAĞRI", len(unique_calls))
        with c3:
            hata_adet = len(user_rows[user_rows["Puan"] == 0])
            st.metric("TOPLAM HATA", hata_adet)
        with c4:
            fcr_evet = len(unique_calls[unique_calls['Cevap'] == 'EVET']) if 'Cevap' in unique_calls.columns else 0
            fcr_oran = (fcr_evet / len(unique_calls) * 100) if len(unique_calls) > 0 else 0
            st.metric("FCR BAŞARI", f"%{fcr_oran:.1f}")

        st.divider()

        # --- ORTA ALAN: GRAFİK VE HATA LİSTESİ ---
        col_sol, col_sag = st.columns([2, 1])

        with col_sol:
            st.subheader("📊 Kriter Bazlı Performans (Pivot)")
            # Pivot Row Seçimi
            satir_bazli = st.selectbox("Tablo Kırılımı Seçin", ["KaliteGrup", "Çağrı Etiketi", "Arama Tipi"], index=0)
            
            pivot_df = user_rows.groupby(satir_bazli).agg(
                Hata_Sayısı=("Puan", lambda x: (x == 0).sum()),
                Başarı_Ortalaması=("Kalite Puanı", "mean")
            ).reset_index()
            
            st.dataframe(pivot_df, use_container_width=True, hide_index=True)
            
            fig = px.bar(pivot_df, x="Başarı_Ortalaması", y=satir_secimi if 'satir_secimi' in locals() else satir_bazli, 
                         orientation='h', color="Başarı_Ortalaması", color_continuous_scale="RdYlGn", text_auto='.1f')
            st.plotly_chart(fig, use_container_width=True)

        with col_sag:
            st.subheader("❌ En Sık Yapılan Hatalar")
            # Puanı 0 olan gerçek hata açıklamaları
            hatalar = user_rows[user_rows["Puan"] == 0]["Kalite Tip Açıklama"].value_counts().head(5)
            if not hatal.empty:
                for h_ad, h_sayi in hatal.items():
                    st.markdown(f'<div class="hata-box" style="background-color: #E74C3C;">{h_sayi} KEZ: {h_ad[:40]}...</div>', unsafe_allow_html=True)
            else:
                st.success("Bu filtrelerde hata bulunmadı.")

        # --- ALT TABLO ---
        st.divider()
        with st.expander("📝 Çağrı Bazlı Notlar ve Detaylar"):
            st.table(unique_calls[["Değerlendirme Tarihi", "Arama Tipi", "Kalite Puanı"]].tail(10))

    except Exception as e:
        st.error(f"Bir şeyler ters gitti: {e}")
else:
    st.info("👋 Hoş geldin! Lütfen DATA sekmesini içeren Excel dosyanı yükle.")
