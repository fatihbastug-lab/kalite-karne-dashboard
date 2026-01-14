import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Kalite Karnesi", layout="wide")

# Görsel Stil Ayarları
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .stMetric { border: 1px solid #E6E9EF; padding: 20px; border-radius: 8px; background-color: #F8F9FA; }
    .hata-box { padding: 10px; border-radius: 5px; margin-bottom: 8px; color: white; font-weight: bold; text-align: center; font-size: 13px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📑 Dinamik Kalite Karnesi")

uploaded_file = st.sidebar.file_uploader("Excel veya CSV Dosyasını Yükleyin", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # Veri Okuma
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip() # Sütun isimlerini temizle

        # --- AKILLI SÜTUN EŞLEŞTİRME ---
        # Sistem otomatik olarak puan, kişi ve ID sütunlarını tahmin eder
        def find_col(possible_names):
            for name in possible_names:
                for col in df.columns:
                    if name.lower() in col.lower(): return col
            return df.columns[0]

        id_col = find_col(["No", "ID", "Numarası", "Call ID"])
        puan_col = find_col(["Kalite Puanı", "Form Puan", "Toplam Puan", "Puan"])
        temsilci_col = find_col(["Temsilci", "Personel", "Adı Soyadı", "Sicil"])
        hata_col = find_col(["Kalite Tip Açıklama", "Hata Nedeni", "Açıklama Detay"])

        # Sayısal dönüşüm
        df[puan_col] = pd.to_numeric(df[puan_col], errors='coerce')

        # --- DİNAMİK FİLTRELEME (Kontrol Sende) ---
        st.sidebar.header("⚙️ Filtreleri Yönet")
        secili_filtreler = st.sidebar.multiselect("Kullanılacak Filtre Başlıkları:", df.columns.tolist(), 
                                                 default=[c for c in ["Ekip Adı", "Yönetici", "Takım Lideri", temsilci_col] if c in df.columns])

        filtered_df = df.copy()
        for col in secili_filtreler:
            opt = sorted(filtered_df[col].dropna().unique().tolist())
            sel = st.sidebar.multiselect(f"{col} Seçin", options=opt, default=opt)
            filtered_df = filtered_df[filtered_df[col].isin(sel)]

        # --- ÜST ÖZET (KARNE METRİKLERİ) ---
        # Aynı çağrıya ait mükerrer satırları temizleyerek ana özeti çıkar
        unique_calls = filtered_df.drop_duplicates(subset=[id_col])
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ORTALAMA PUAN", f"{unique_calls[puan_col].mean():.1f}")
        c2.metric("TOPLAM ÇAĞRI", len(unique_calls))
        c3.metric("FİLTRELİ SATIR", len(filtered_df))
        c4.metric("MAX PUAN", f"{unique_calls[puan_col].max()}")

        st.divider()

        # --- PİVOT VE GRAFİK ALANI ---
        col_piv, col_hata = st.columns([2, 1])

        with col_piv:
            st.subheader("📊 Pivot Kırılım Analizi")
            pivot_row = st.selectbox("Satırlar (Kırılım Seçin):", df.columns.tolist(), index=df.columns.get_loc(find_col(["KaliteGrup", "Kategori"])))
            
            pivot_table = filtered_df.groupby(pivot_row).agg(
                Adet=(id_col, 'nunique'),
                Ortalama=(puan_col, 'mean')
            ).reset_index().sort_values("Ortalama", ascending=False)
            
            st.dataframe(pivot_table, use_container_width=True, hide_index=True)
            
            # Dinamik Grafik
            fig = px.bar(pivot_table, x="Ortalama", y=pivot_row, orientation='h',
                         color="Ortalama", color_continuous_scale="RdYlGn", text_auto='.1f')
            st.plotly_chart(fig, use_container_width=True)

        with col_hata:
            st.subheader("🚨 En Çok Tekrarlanan Durumlar")
            hata_ozeti = filtered_df[hata_col].value_counts().head(6)
            
            if not hata_ozeti.empty:
                for txt, count in hata_ozeti.items():
                    color = "#E74C3C" if count > 5 else "#F39C12"
                    st.markdown(f'<div class="hata-box" style="background-color: {color};">{count} Kez: {str(txt)[:45]}...</div>', unsafe_allow_html=True)
            else:
                st.success("Analiz edilecek veri bulunamadı.")

        # --- DETAY LİSTE ---
        with st.expander("📥 Ham Veri ve Detay Tablo"):
            st.write(filtered_df)

    except Exception as e:
        st.error(f"Sistem dosyayı okurken zorlanıyor: {e}")
        st.info("İpucu: Dosyanızda sütun başlıklarının ilk satırda olduğundan emin olun.")
else:
    st.info("👋 Kalite Karnesi hazır! Lütfen herhangi bir Excel veya CSV dosyasını yükleyin.")
