Automated workflow manager for Splunk BOTS v1 challenge - Install, Ingest, Solve, Clean
# 🛡️ Splunk BOTS v1 Workflow Manager

[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![Splunk](https://img.shields.io/badge/Splunk-9.x-green.svg)](https://www.splunk.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Tool otomatis untuk mengelola workflow **Splunk Boss of the SOC (BOTS) v1** challenge. Script ini mengotomatisasi proses instalasi Splunk, ingest dataset per soal, dan pembersihan data.

## 📋 Fitur

- ✅ **Instalasi Splunk Otomatis** - Download, extract, dan setup Splunk Enterprise
- ✅ **Service Management** - Start, stop, restart, dan status Splunk
- ✅ **Dataset Management** - Download dan ingest dataset per kelompok soal
- ✅ **Auto Cleanup** - Hapus data dan file setelah selesai mengerjakan soal
- ✅ **Interactive Menu** - Menu interaktif yang mudah digunakan
- ✅ **Progress Tracking** - Progress bar saat download dataset

## 🎯 Kelompok Soal

| Menu | Soal | Topik | Dataset |
|------|------|-------|---------|
| 6 | 1-10 | Reconnaissance & Web Defacement | `stream:http` |
| 7 | 11-14 | Malware Analysis & OSINT | `Sysmon` |
| 8 | 15-20 | Brute Force Attack | `stream:http` |
| 9 | 21-24 | Ransomware Initial Infection | `dhcp`, `dns`, `suricata` |
| 10 | 25-26 | Execution & Persistence | `Sysmon`, `winregistry` |
| 11 | 27-32 | Lateral Movement & Encryption | `smb`, `Sysmon`, `http` |

## 🚀 Quick Start

### Prerequisites

- Linux OS (Ubuntu/Debian/CentOS)
- Python 3.x
- Akses `sudo`
- Koneksi internet (untuk download Splunk & dataset)

### Instalasi

```bash
# Clone repository
git clone https://github.com/USERNAME/splunk-bots-v1-manager.git
cd splunk-bots-v1-manager

# Berikan izin eksekusi
chmod +x scripts/splunk_bots_manager.py

# Jalankan script (WAJIB dengan sudo)
sudo python3 scripts/splunk_bots_manager.py
