import streamlit as st
import pandas as pd
from utils import login_user, get_relations, process_data
import time

st.set_page_config(page_title="Cek Unfollowers Instagram", page_icon="📸", layout="wide")

st.title("📸 Analisa Pengikut Instagram")
st.markdown("""
Aplikasi ini membantu Anda melihat siapa yang **tidak follback**, siapa **fans** Anda, dan siapa teman **mutual**.
**Note:** Proses pengambilan data bisa memakan waktu tergantung jumlah followers/following Anda.
""")

# Sidebar untuk Login/Logout
with st.sidebar:
    st.header("Pengaturan Akun")
    
    # Cek apakah sudah ada session state untuk client
    if 'cl' not in st.session_state:
        st.session_state.cl = None

    if st.session_state.cl is None:
        # Tampilan Belum Login
        username = st.text_input("Username Instagram")
        password = st.text_input("Password Instagram", type="password")
        login_btn = st.button("Login & Simpan Sesi")
        
        if login_btn and username and password:
            try:
                st.info(f"Sedang login sebagai {username}...")
                cl = login_user(username, password)
                st.session_state.cl = cl
                st.session_state.username = username
                st.success("Login Berhasil!")
                st.rerun()
            except Exception as e:
                st.error(f"Login Gagal: {e}")
    else:
        # Tampilan Sudah Login
        st.success(f"✅ Login sebagai: {st.session_state.username}")
        if st.button("Logout"):
            from utils import logout_user
            logout_user()
            st.session_state.cl = None
            if 'username' in st.session_state:
                del st.session_state.username
            st.rerun()

# Main Area
st.subheader("Cek Pengikut")

if st.session_state.cl:
    target_username = st.text_input("Masukkan Username Target", value=st.session_state.username, help="Username yang ingin dicek (harus publik atau difollow akun login).")
    analyze_btn = st.button("🔍 Analisa Sekarang")

    if analyze_btn:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Fetch Data
            status_text.info(f"Sedang mengambil data followers & following dari {target_username}...")
            progress_bar.progress(20)
            
            followers, following = get_relations(st.session_state.cl, target_username)
            st.write(f"📊 **Statistik {target_username}:**")
            
            col1, col2 = st.columns(2)
            col1.metric("Followers", len(followers))
            col2.metric("Following", len(following))
            progress_bar.progress(60)
            
            # Process Data
            status_text.info("Sedang memproses data...")
            not_follback, fans, mutual = process_data(followers, following)
            progress_bar.progress(100)
            status_text.empty()
            
            # Display Results
            st.divider()
            
            tab1, tab2, tab3 = st.tabs(["❌ Tidak Follback", "🌟 Fans", "🤝 Mutual"])
            
            with tab1:
                st.warning(f"Mereka yang Anda follow, tapi TIDAK follow balik ({len(not_follback)})")
                if not_follback:
                    df = pd.DataFrame(not_follback)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Wah, semua orang yang Anda follow juga follow Anda balik!")
                    
            with tab2:
                st.success(f"Mereka yang follow Anda, tapi TIDAK Anda follow balik ({len(fans)})")
                if fans:
                    df = pd.DataFrame(fans)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Tidak ada fans saat ini.")
                    
            with tab3:
                st.info(f"Saling Follow ({len(mutual)})")
                if mutual:
                    df = pd.DataFrame(mutual)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Tidak ada teman mutual.")

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
            st.info("Tips: Jika error berlanjut, coba Logout dan Login kembali.")
else:
    st.info("👈 Silakan login di panel sebelah kiri untuk memulai.")

