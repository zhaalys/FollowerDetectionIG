from instagrapi import Client
import time
import random

import os

SESSION_FILE = "session.json"

def login_user(username, password):
    """
    Login to Instagram using instagrapi.
    Attempts to load session first. If fails or no session, logs in with credentials and saves session.
    """
    cl = Client()
    # Setting Locale ke Indonesia agar terlihat legit
    cl.set_locale("id_ID")
    cl.set_country("ID")
    cl.set_timezone_offset(7 * 3600) # UTC+7 (WIB)
    
    # 1. Coba load session jika ada
    if os.path.exists(SESSION_FILE):
        try:
            print("Mencoba login menggunakan sesi tersimpan...")
            cl.load_settings(SESSION_FILE)
            cl.login(username, password) # Re-login to verify session is still valid
            print("Login via sesi berhasil!")
            return cl
        except Exception as e:
            print(f"Sesi tidak valid atau kadaluarsa: {e}")
            # Lanjut ke login manual di bawah
    
    # 2. Login manual jika sesi gagal/tidak ada
    try:
        # Menambahkan delay acak sedikit untuk meniru perilaku manusia
        cl.login(username, password)
        
        # 3. Simpan sesi untuk penggunaan berikutnya
        cl.dump_settings(SESSION_FILE)
        
        return cl
    except Exception as e:
        error_msg = str(e)
        if "added to the blacklist" in error_msg or "challenge_required" in error_msg:
             raise Exception("IP Internet Anda diblokir sementara oleh Instagram atau akun butuh verifikasi. \n\nSOLUSI: \n1. Ganti koneksi internet (matikan WiFi, pakai Hotspot HP). \n2. Tunggu beberapa jam. \n3. Coba akun lain.")
        
        raise Exception(f"Gagal Login: {error_msg}")

def logout_user():
    """
    Menghapus file sesi untuk logout.
    """
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


def get_relations(cl, target_username):
    """
    Fetches followers and following for a given user.
    Returns two dictionaries: followers, following.
    Each dictionary maps user_id -> user_info (username, full_name, etc.)
    """
    try:
        user_id = cl.user_id_from_username(target_username)
        
        # Mengambil daftar following (orang yang kita ikuti)
        # amount=0 berarti mengambil semua
        print(f"Mengambil data following untuk {target_username}...")
        following = cl.user_following(user_id, amount=0)
        
        # Mengambil daftar followers (orang yang mengikuti kita)
        print(f"Mengambil data followers untuk {target_username}...")
        followers = cl.user_followers(user_id, amount=0)
        
        return followers, following
    except Exception as e:
        raise Exception(f"Gagal mengambil data: {str(e)}")

def process_data(followers, following):
    """
    Processes the raw dictionaries to find:
    1. Not Following Back (Kita follow dia, dia ga follow kita)
    2. Fans (Dia follow kita, kita ga follow dia)
    3. Mutual (Saling follow)
    
    Returns lists of dictionaries for display.
    """
    # Convert keys to sets for set operations
    following_ids = set(following.keys())
    followers_ids = set(followers.keys())
    
    # 1. Not Following Back: Ada di following, tapi TIDAK ada di followers
    not_following_back_ids = following_ids - followers_ids
    
    # 2. Fans: Ada di followers, tapi TIDAK ada di following
    fans_ids = followers_ids - following_ids
    
    # 3. Mutual: Ada di keduanya
    mutual_ids = following_ids.intersection(followers_ids)
    
    # Helper to format output
    def format_users(user_ids, source_dict):
        result = []
        for uid in user_ids:
            user = source_dict.get(uid)
            if user:
                result.append({
                    "Username": user.username,
                    "Nama Lengkap": user.full_name,
                    "User ID": user.pk
                })
        return result

    # Note: Untuk not_following_back, datanya ambil dari 'following' dict
    not_following_back_list = format_users(not_following_back_ids, following)
    
    # Untuk fans, datanya ambil dari 'followers' dict
    fans_list = format_users(fans_ids, followers)
    
    # Untuk mutual, bisa ambil dari mana saja (pilih 'following')
    mutual_list = format_users(mutual_ids, following)
    
    return not_following_back_list, fans_list, mutual_list
