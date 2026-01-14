import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Kalite Karne Dashboard", layout="wide")

# Boş ekran yerine rehber bir mesaj gösterelim
st.title("📊 Personel Kalite Karnesi")

uploaded_file = st.sidebar.file_uploader("Lütfen Excel dosyanızı buraya sürükleyin", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # Dosyayı oku
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
            
        # SÜTUN İSİMLERİNİ TEMİZLE (En sık yapılan hata budur)
        df.columns = df.columns.str.strip()

        # FİLTRE PANELİ
        st.sidebar.success("Dosya başarıyla yüklendi!")
        grup = st.sidebar.selectbox("Grup Seçin", sorted(df["Grup Adı"].unique()))
        df_grup = df[df["Grup Adı"] == grup]
        
        personel = st.sidebar.selectbox("Personel Seçin", sorted(df_grup["Personel"].unique()))
        user_data = df_grup[df_grup["Personel"] == personel]

        # --- ANA EKRAN VERİLERİ ---
        st.subheader(f"👤 {personel} - Performans Detayları")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Toplam Dinlenen Çağrı", len(user_data))
        m2.metric("Kalite Puan Ortalaması", f"{user_data['Form Puan'].mean():.1f}")
        m3.metric("Grup Ortalaması", f"{df_grup['Form Puan'].mean():.1f}")

        # --- ETİKET ANALİZİ (Şikayet/Teşekkür/Kalite) ---
        st.divider()
        st.subheader("📋 Çağrı Etiket Analizi (Adet ve Puan)")
        # Sütun ismini kontrol ederek grupla
        etiket_col = "Çağrı Etiketi" if "Çağrı Etiketi" in df.columns else "Arama Tipi"
        
        etiket_analiz = user_data.groupby(etiket_col).agg(
            Adet=('Form Puan', 'count'),
            Ortalama_Puan=('Form Puan', 'mean')
        ).reset_index()
        
        st.table(etiket_analiz)

        # --- EN ÇOK YAPILAN HATA ---
        st.divider()
        col_bar, col_hata = st.columns([2, 1])
        
        with col_bar:
            st.subheader("🎯 Kriter Başarı Oranları")
            kriterler = ["Karşılama/Bitirme", "Ses tonu/ Ses enerjisi - Kurumsal Görüşme Standartları", 
                         "Bekletme", "Etkin Dinleme- Çözüm Odaklı Yaklaşım", "Doğru Bilgilendirme", "Süreç Yönetimi"]
            mevcut = [k for k in kriterler if k in df.columns]
            puanlar = user_data[mevcut].mean().reset_index()
            puanlar.columns = ["Kriter", "Puan"]
            fig = px.bar(puanlar, x="Puan", y="Kriter", orientation='h', text_auto='.1f', color="Puan", color_continuous_scale="RdYlGn")
            st.plotly_chart(fig, use_container_width=True)

        with col_hata:
            st.subheader("❌ En Çok Yapılan Hata")
            en_kotu = puanlar.sort_values("Puan").iloc[0]
            st.error(f"Dikkat: En düşük kriteriniz: **{en_kotu['Kriter']}** (%{en_kotu['Puan']:.1f})")

    except Exception as e:
        st.error(f"Sistem dosyayı işleyemedi: {e}")
        st.info("Lütfen Excel dosyanızdaki sütun başlıklarını kontrol edin.")
else:
    # DOSYA YÜKLENMEDİĞİNDE GÖRÜNEN EKRAN
    st.warning("⚠️ Dashboard şu an boş çünkü veri yüklenmedi.")
    st.markdown("""
    ### Başlamak için:
    1. Sol taraftaki menüden **'Browse files'** butonuna basın.
    2. Excel dosyanızı seçin.
    3. Veriler otomatik olarak buraya dolacaktır.
    """)
