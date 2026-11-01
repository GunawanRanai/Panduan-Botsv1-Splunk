#!/usr/bin/env python3
import os
import sys
import subprocess
import urllib.request
import tarfile
import getpass
import shutil

# --- KONFIGURASI ---
SPLUNK_BIN = "/opt/splunk/bin/splunk"
WORK_DIR = "/tmp/botsv1"
INDEX_NAME = "botsv1"
SPLUNK_DOWNLOAD_URL = "<https://download.splunk.com/products/splunk/releases/9.4.0/linux/splunk-9.4.0-6b4ebe426f7c-Linux-x86_64.tgz>"
SPLUNK_TGZ = "/tmp/splunk.tgz"

# Mapping Kelompok Soal ke File Dataset
DATASETS = {
    "1": {
        "desc": "Soal 1-10: Reconnaissance & Web Defacement",
        "files": [
            {"url": "<https://s3.amazonaws.com/botsdataset/botsv1/json-by-sourcetype/botsv1.stream-http.json.gz>",
             "stype": "stream:http",
             "fname": "botsv1.stream-http.json.gz"}
        ]
    },
    "2": {
        "desc": "Soal 11-14: Malware Analysis & OSINT",
        "files": [
            {"url": "<https://s3.amazonaws.com/botsdataset/botsv1/json-by-sourcetype/botsv1.XmlWinEventLog-Microsoft-Windows-Sysmon-Operational.json.gz>",
             "stype": "XmlWinEventLog:Microsoft-Windows-Sysmon/Operational",
             "fname": "botsv1.Sysmon.json.gz"}
        ]
    },
    "3": {
        "desc": "Soal 15-20: Brute Force Attack",
        "files": [
            {"url": "<https://s3.amazonaws.com/botsdataset/botsv1/json-by-sourcetype/botsv1.stream-http.json.gz>",
             "stype": "stream:http",
             "fname": "botsv1.stream-http.json.gz"}
        ]
    },
    "4": {
        "desc": "Soal 21-24: Ransomware Initial Infection",
        "files": [
            {"url": "<https://s3.amazonaws.com/botsdataset/botsv1/json-by-sourcetype/botsv1.stream-dhcp.json.gz>",
             "stype": "stream:dhcp",
             "fname": "botsv1.stream-dhcp.json.gz"},
            {"url": "<https://s3.amazonaws.com/botsdataset/botsv1/json-by-sourcetype/botsv1.stream-dns.json.gz>",
             "stype": "stream:dns",
             "fname": "botsv1.stream-dns.json.gz"},
            {"url": "<https://s3.amazonaws.com/botsdataset/botsv1/json-by-sourcetype/botsv1.suricata.json.gz>",
             "stype": "suricata",
             "fname": "botsv1.suricata.json.gz"}
        ]
    },
    "5": {
        "desc": "Soal 25-26: Execution & Persistence",
        "files": [
            {"url": "<https://s3.amazonaws.com/botsdataset/botsv1/json-by-sourcetype/botsv1.XmlWinEventLog-Microsoft-Windows-Sysmon-Operational.json.gz>",
             "stype": "XmlWinEventLog:Microsoft-Windows-Sysmon/Operational",
             "fname": "botsv1.Sysmon.json.gz"},
            {"url": "<https://s3.amazonaws.com/botsdataset/botsv1/json-by-sourcetype/botsv1.winregistry.json.gz>",
             "stype": "winregistry",
             "fname": "botsv1.winregistry.json.gz"}
        ]
    },
    "6": {
        "desc": "Soal 27-32: Lateral Movement & Encryption",
        "files": [
            {"url": "<https://s3.amazonaws.com/botsdataset/botsv1/json-by-sourcetype/botsv1.stream-smb.json.gz>",
             "stype": "stream:smb",
             "fname": "botsv1.stream-smb.json.gz"},
            {"url": "<https://s3.amazonaws.com/botsdataset/botsv1/json-by-sourcetype/botsv1.XmlWinEventLog-Microsoft-Windows-Sysmon-Operational.json.gz>",
             "stype": "XmlWinEventLog:Microsoft-Windows-Sysmon/Operational",
             "fname": "botsv1.Sysmon.json.gz"},
            {"url": "<https://s3.amazonaws.com/botsdataset/botsv1/json-by-sourcetype/botsv1.stream-http.json.gz>",
             "stype": "stream:http",
             "fname": "botsv1.stream-http.json.gz"}
        ]
    }
}

# --- FUNGSI HELPER ---
def run_cmd(cmd, show_output=True, check=True):
    """Menjalankan perintah shell."""
    print(f"\n[~] Menjalankan: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if show_output and result.stdout:
            print(result.stdout.strip())
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[!] Error: {e.stderr.strip()}")
        return False, e.stderr

def download_file(url, dest_path):
    """Mendownload file dengan progress bar."""
    if os.path.exists(dest_path):
        print(f"[*] File sudah ada: {dest_path}. Melewati download.")
        return True

    print(f"[*] Mendownload dari: {url}")
    print("[*] Ini bisa memakan waktu beberapa menit, harap tunggu...")

    def reporthook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size) if total_size > 0 else 0
        percent = min(percent, 100)
        sys.stdout.write(f"\rProgress: {percent}%")
        sys.stdout.flush()
    print()

    try:
        urllib.request.urlretrieve(url, dest_path, reporthook)
        print("\n[+] Download selesai!")
        return True
    except Exception as e:
        print(f"\n[!] Gagal download: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return False

def install_splunk():
    """Install Splunk Enterprise secara otomatis."""
    print("\n" + "="*60)
    print("  INSTALASI SPLUNK ENTERPRISE")
    print("="*60)

    # Cek apakah Splunk sudah terinstall
    if os.path.exists(SPLUNK_BIN):
        print("[*] Splunk sudah terinstall di /opt/splunk")
        choice = input("[?] Apakah Anda ingin install ulang? (y/n): ").strip().lower()
        if choice != 'y':
            return

    # Download Splunk
    print("\n[*] STEP 1: Download Splunk Enterprise (~500MB)")
    if not download_file(SPLUNK_DOWNLOAD_URL, SPLUNK_TGZ):
        print("[!] Download gagal. Instalasi dibatalkan.")
        return

    # Ekstrak ke /opt
    print("\n[*] STEP 2: Ekstrak ke /opt/...")
    try:
        with tarfile.open(SPLUNK_TGZ, "r:gz") as tar:
            tar.extractall(path="/opt/")
        print("[+] Ekstraksi selesai!")
    except Exception as e:
        print(f"[!] Gagal ekstraksi: {e}")
        return

    # Buat user splunk jika belum ada
    print("\n[*] STEP 3: Setup user splunk...")
    result = subprocess.run(["id", "splunk"], capture_output=True)
    if result.returncode != 0:
        print("[*] Membuat user 'splunk'...")
        subprocess.run(["useradd", "-r", "-m", "-s", "/bin/bash", "splunk"], check=False)
    else:
        print("[*] User 'splunk' sudah ada.")

    # Set permission
    print("[*] Mengatur permission /opt/splunk...")
    subprocess.run(["chown", "-R", "splunk:splunk", "/opt/splunk"], check=False)

    # Start Splunk dengan accept license
    print("\n[*] STEP 4: Start Splunk pertama kali (accept license)...")
    print("[*] Proses ini bisa memakan waktu 1-3 menit...")
    run_cmd([SPLUNK_BIN, "start", "--accept-license", "--answer-yes"], show_output=True, check=False)

    # Setup admin credentials
    print("\n[*] STEP 5: Setup Admin Credentials")
    username = input("[?] Username (default: admin): ").strip() or "admin"
    password = getpass.getpass("[?] Password (min 8 chars, input tidak akan tampil): ")

    if len(password) < 8:
        print("[!] Password minimal 8 karakter. Coba lagi.")
        return

    # Edit user via CLI
    print(f"[*] Mengubah password untuk user '{username}'...")
    run_cmd([SPLUNK_BIN, "edit", "user", username, "-password", password, "-role", "admin", "-auth", f"{username}:changeme"], check=False)

    # Enable boot-start
    print("\n[*] STEP 6: Enable boot-start...")
    run_cmd([SPLUNK_BIN, "enable", "boot-start", "-user", "splunk"], check=False)

    print("\n" + "="*60)
    print("[+] INSTALASI SPLUNK SELESAI!")
    print("="*60)
    print(f"[*] Akses Splunk Web: <http://localhost:8000>")
    print(f"[*] Login: {username} / [password yang Anda input]")
    print("[*] Note: Jika password tidak berubah, login dengan 'admin:changeme' lalu ubah manual via Web.")

def ensure_setup():
    """Memastikan direktori kerja dan index sudah ada."""
    os.makedirs(WORK_DIR, exist_ok=True)
    print(f"[*] Memastikan direktori {WORK_DIR} ada...")

    if not os.path.exists(SPLUNK_BIN):
        print("[!] Splunk belum terinstall. Pilih menu '1. Install Splunk' terlebih dahulu.")
        return

    success, output = run_cmd([SPLUNK_BIN, "list", "index", INDEX_NAME], show_output=False, check=False)
    if INDEX_NAME not in output:
        print(f"[*] Membuat index '{INDEX_NAME}'...")
        run_cmd([SPLUNK_BIN, "add", "index", INDEX_NAME])
    else:
        print(f"[*] Index '{INDEX_NAME}' sudah ada.")

def splunk_service(action):
    """Mengelola layanan Splunk."""
    if not os.path.exists(SPLUNK_BIN):
        print("[!] Splunk belum terinstall.")
        return

    print(f"\n--- Mengelola Layanan Splunk: {action.upper()} ---")
    if action == "status":
        run_cmd([SPLUNK_BIN, "status"], check=False)
    else:
        run_cmd([SPLUNK_BIN, action], check=False)

def ingest_data(group_key):
    """Mendownload dan mengingest data."""
    if not os.path.exists(SPLUNK_BIN):
        print("[!] Splunk belum terinstall. Pilih menu '1. Install Splunk' terlebih dahulu.")
        return

    ensure_setup()
    group = DATASETS[group_key]
    print(f"\n--- Ingest Data: {group['desc']} ---")

    for file_info in group["files"]:
        url = file_info["url"]
        fname = file_info["fname"]
        stype = file_info["stype"]
        dest_path = os.path.join(WORK_DIR, fname)

        if not download_file(url, dest_path):
            continue

        print(f"[*] Mengingest {fname} ke index {INDEX_NAME}...")
        run_cmd([
            SPLUNK_BIN, "add", "oneshot", dest_path,
            "-index", INDEX_NAME,
            "-sourcetype", stype
        ], check=False)

    print("\n[+] Selesai! Silakan kerjakan soal di Splunk Web.")
    print(f"[*] Query dasar: index={INDEX_NAME}")
    print("[*] PENTING: Ubah Time Picker ke 'All Time' di Splunk Web!")

def clean_data(group_key):
    """Membersihkan index dan menghapus file lokal."""
    if not os.path.exists(SPLUNK_BIN):
        print("[!] Splunk belum terinstall.")
        return

    group = DATASETS[group_key]
    print(f"\n--- Membersihkan Data: {group['desc']} ---")

    print("[*] Membersihkan isi index di Splunk...")
    run_cmd([SPLUNK_BIN, "clean", "index", INDEX_NAME, "-f"], check=False)

    print("[*] Menghapus file download lokal...")
    for file_info in group["files"]:
        fname = file_info["fname"]
        dest_path = os.path.join(WORK_DIR, fname)
        if os.path.exists(dest_path):
            os.remove(dest_path)
            print(f"    [-] Dihapus: {fname}")

    print("[+] Pembersihan selesai.")

def cleanup_all():
    """Menghapus index dan semua file sisa."""
    if not os.path.exists(SPLUNK_BIN):
        print("[!] Splunk belum terinstall.")
        return

    print("\n--- Pembersihan Total ---")
    run_cmd([SPLUNK_BIN, "clean", "index", INDEX_NAME, "-f"], check=False)
    run_cmd([SPLUNK_BIN, "remove", "index", INDEX_NAME], check=False)

    if os.path.exists(WORK_DIR):
        shutil.rmtree(WORK_DIR)
        print(f"[+] Folder {WORK_DIR} dihapus.")

    print("[+] Semua data BOTS v1 telah dihapus.")

def main():
    while True:
        print("\n" + "="*60)
        print("  SPLUNK BOTS v1 WORKFLOW MANAGER v2.0")
        print("="*60)
        print("  [SPLUNK SERVICE]")
        print("  1. Install Splunk Enterprise (Otomatis)")
        print("  2. Start Splunk")
        print("  3. Stop Splunk")
        print("  4. Restart Splunk")
        print("  5. Status Splunk")
        print("-" * 60)
        print("  [SETUP]")
        print("  0. Setup Awal (Buat Folder & Index)")
        print("-" * 60)
        print("  [ADD LOGSOURCE]")
        print("  6. Soal 1-10  (Recon & Defacement)")
        print("  7. Soal 11-14 (Malware Analysis)")
        print("  8. Soal 15-20 (Brute Force)")
        print("  9. Soal 21-24 (Ransomware Initial)")
        print(" 10. Soal 25-26 (Execution & Persistence)")
        print(" 11. Soal 27-32 (Lateral Movement)")
        print("-" * 60)
        print("  [CLEAN LOGSOURCE]")
        print(" 12. Hapus Data Soal 1-10")
        print(" 13. Hapus Data Soal 11-14")
        print(" 14. Hapus Data Soal 15-20")
        print(" 15. Hapus Data Soal 21-24")
        print(" 16. Hapus Data Soal 25-26")
        print(" 17. Hapus Data Soal 27-32")
        print("-" * 60)
        print(" 99. CLEAN ALL (Hapus Total & Hapus Index)")
        print("  0. Keluar")
        print("="*60)

        choice = input("\nPilih opsi: ").strip()

        if choice == "1":
            install_splunk()
        elif choice == "2":
            splunk_service("start")
        elif choice == "3":
            splunk_service("stop")
        elif choice == "4":
            splunk_service("restart")
        elif choice == "5":
            splunk_service("status")
        elif choice == "0":
            ensure_setup()
        elif choice in ["6", "7", "8", "9", "10", "11"]:
            group_key = str(int(choice) - 5)
            ingest_data(group_key)
        elif choice in ["12", "13", "14", "15", "16", "17"]:
            group_key = str(int(choice) - 11)
            clean_data(group_key)
        elif choice == "99":
            cleanup_all()
        elif choice == "00":
            print("Keluar dari program. Selamat mengerjakan!")
            sys.exit(0)
        else:
            print("[!] Pilihan tidak valid.")

        input("\nTekan Enter untuk kembali ke menu...")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("\n[PERINGATAN] Script ini WAJIB dijalankan dengan 'sudo'!")
        print("Contoh: sudo python3 ~/splunk_bots_manager.py\n")
        sys.exit(1)

    main()
