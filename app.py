import streamlit as st
from fsm import ChatbotFSM

# Inisialisasi FSM Bot
fsm_bot = ChatbotFSM()

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(
    page_title="Sinar Express - Logistik Cerdas",  
    layout="wide",
    initial_sidebar_state="expanded" # Sidebar dibuka default
)

# ================= INJECT CUSTOM CSS (DARK MODE UPGRADED) =================
st.markdown("""
<style>
    /* Warna Background Utama */
    .stApp, [data-testid="stSidebar"] {
        background-color: #121212;
        color: #e0e0e0;
    }
    /* Garis pemisah sidebar */
    [data-testid="stSidebar"] > div:first-child {
        border-right: 1px solid #2a2a3c;
    }
    /* Warna Input Box */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #1e1e2f;
        color: white;
        border-color: #2a2a3c;
    }
    /* Warna Tombol Utama (Cyan) */
    .stButton>button[kind="primary"] {
        background-color: #00bcd4;
        color: #121212;
        border-radius: 8px;
        font-weight: bold;
        border: none;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #00e5ff;
        color: #121212;
    }
    /* Warna Tombol Sekunder (Quick Replies) */
    .stButton>button:not([kind="primary"]) {
        background-color: #1e1e2f;
        color: #00bcd4;
        border: 1px solid #2a2a3c;
        border-radius: 20px;
    }
    .stButton>button:not([kind="primary"]):hover {
        background-color: #272740;
        border-color: #00bcd4;
    }
    /* Warna Chat Input */
    .stChatInput>div>div>textarea {
        background-color: #1e1e2f;
        color: white;
        border-color: #2a2a3c;
    }
    /* Warna Chat Bubble Bot */
    .stChatMessage[data-testid="stChatMessageAvatar-Assistant"] + div {
        background-color: #1e1e2f;
        border: 1px solid #2a2a3c;
        border-radius: 12px;
        color: #e0e0e0;
    }
    /* Warna Chat Bubble User */
    .stChatMessage[data-testid="stChatMessageAvatar-User"] + div {
        background-color: #00bcd4;
        border-radius: 12px;
        color: #121212;
        font-weight: 500;
    }
    /* Warna Judul Metric */
    [data-testid="stMetricValue"] {
        color: #00bcd4;
        font-size: 1.8rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #a0a0b0;
        font-size: 0.9rem !important;
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #a0a0b0 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #00bcd4 !important;
        border-bottom-color: #00bcd4 !important;
    }
    hr { border-color: #2a2a3c !important; }
</style>
""", unsafe_allow_html=True)


# ================= SIDEBAR INFO =================
with st.sidebar:
    st.markdown("<h2 style='color: #00bcd4;'> Sinar Express</h2>", unsafe_allow_html=True)
    st.caption("Jasa Pengiriman Cepat & Terpercaya")
    st.divider()
    
    st.markdown("#### 📞 Kontak Kami")
    st.markdown("- **Call Center:** 0813-4890-0013")
    st.markdown("- **Email:** cs@sinarexpress.id")
    st.markdown("- **Kantor Pusat:** Jl. Plewan No. 1, Semarang")
    st.divider()
    
    st.markdown("#### ⏰ Jam Operasional")
    st.markdown("- **Senin - Sabtu:** 08.00 - 20.00 WIB")
    st.markdown("- **Minggu:** 09.00 - 16.00 WIB")
    st.divider()
    
    # Tombol Reset Chat yang sangat penting untuk demo
    if st.button("🗑️ Reset Percakapan", use_container_width=True):
        if "messages" in st.session_state:
            del st.session_state.messages
            del st.session_state.fsm_state
        st.rerun()

    st.markdown("---")
    st.caption("© 2024 Sinar Express. All Rights Reserved.")


# ================= MAIN PAGE =================

# Tab Navigasi Utama
tab_home, tab_services = st.tabs([" Home & Chatbot", " Layanan Kami"])

with tab_home:
    # --- Fitur Cepat: Cek Resi di Atas ---
    st.markdown("<h1 style='color: #00bcd4; margin-bottom: 0px;'>Lacak Paket Anda</h1>", unsafe_allow_html=True)
    st.caption("Masukkan nomor resi untuk melihat status terkini")
    
    col_track1, col_track2 = st.columns([4, 1])
    with col_track1:
        resi_input = st.text_input("Masukkan nomor resi:", label_visibility="collapsed", placeholder="Contoh: JNE12345678, SPX99001122...")
    with col_track2:
        st.markdown("<br>", unsafe_allow_html=True)
        track_clicked = st.button(" Lacak", type="primary", use_container_width=True)

    if track_clicked:
        if resi_input:
            st.session_state.quick_track = resi_input
            st.session_state.trigger_chat = True
        else:
            st.warning("Silakan masukkan nomor resi terlebih dahulu!")

    # --- Statistik ---
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(" Paket Terkirim", "10K+")
    col2.metric(" Kota Jateng", "35+")
    col3.metric(" Pelanggan", "50K+")
    col4.metric(" Support Bot", "24/7")
    st.divider()

    # ================= UI CHATBOT =================
    st.markdown("### 💬 Sinar Bot - Asisten Virtual")

    # Inisialisasi state history chatbot
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.fsm_state = "GREETING"
        
        reply, next_state = fsm_bot.process("", "GREETING")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.fsm_state = next_state

    # Cek jika ada trigger dari tombol Lacak Resi
    if "trigger_chat" in st.session_state and st.session_state.trigger_chat:
        user_msg = st.session_state.quick_track
        st.session_state.messages.append({"role": "user", "content": user_msg})
        
        reply, next_state = fsm_bot.process(user_msg, st.session_state.fsm_state)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.fsm_state = next_state
        
        st.session_state.trigger_chat = False
        st.rerun()

    # Quick Replies (Tombol Cepat)
    st.markdown("**Pilih topik cepat:**")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
    
    if qcol1.button(" Cek Resi", use_container_width=True):
        st.session_state.quick_msg = "1"
    if qcol2.button(" Cek Tarif", use_container_width=True):
        st.session_state.quick_msg = "2"
    if qcol3.button(" Pengaduan", use_container_width=True):
        st.session_state.quick_msg = "3"
    if qcol4.button(" Jemput Paket", use_container_width=True):
        st.session_state.quick_msg = "6"

    # Proses pesan dari Quick Replies
    if "quick_msg" in st.session_state and st.session_state.quick_msg:
        prompt = st.session_state.quick_msg
        st.session_state.messages.append({"role": "user", "content": prompt})
        reply, next_state = fsm_bot.process(prompt, st.session_state.fsm_state)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.fsm_state = next_state
        del st.session_state.quick_msg
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True) # Jarak aesthetic

    # Tampilkan history chat di layar
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input chat di bawah layar
    if prompt := st.chat_input("Ketik pesan Anda di sini..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        reply, next_state = fsm_bot.process(prompt, st.session_state.fsm_state)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.fsm_state = next_state
        
        with st.chat_message("assistant"):
            st.markdown(reply)


# ================= TAB LAYANAN =================
with tab_services:
    st.markdown("<h1 style='color: #00bcd4;'>Layanan Unggulan Kami</h1>", unsafe_allow_html=True)
    st.caption("Solusi pengiriman terbaik untuk kebutuhan individu dan bisnis Anda di Jawa Tengah.")
    
    st.divider()
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.markdown("#### 🚛 Reguler (Jawa Tengah)")
        st.info("Layanan pengiriman paket antar kota di Jawa Tengah dengan estimasi tiba 2-3 hari. Harga terjangkau dan aman.")
        st.markdown("**Estimasi Tarif:** Rp 15.000 (1Kg pertama)")
        
    with col_s2:
        st.markdown("#### ⚡ Express (Same Day)")
        st.info("Butuh paket tiba hari ini juga? Layanan Same Day kami siap mengantar paket Anda sebelum jam 5 sore.")
        st.markdown("**Estimasi Tarif:** Mulai Rp 30.000")
        
    with col_s3:
        st.markdown("#### 📦 Kargo Berat")
        st.info("Pengiriman barang besar dan berat dengan tarif kompetitif. Cocok untuk kebutuhan bisnis dan pindahan.")
        st.markdown("**Estimasi Tarif:** Hubungi CS")

    st.divider()
    
    st.markdown("### 🚫 Daftar Barang Terlarang")
    st.warning("Untuk keamanan bersama, kami **TIDAK** menerima pengiriman barang-barang berikut:")
    st.markdown("""
    - Cairan mudah terbakar (Bensin, Minyak Tanah, dll)
    - Baterai / Lithium secara mandiri (tanpa terpasang di alat)
    - Uang tunai, Logam mulia, & Perhiasan berharga
    - Obat-obatan terlarang & Benda tajam tanpa pengamanan
    - Hewan hidup & Makanan mudah busuk
    """)
