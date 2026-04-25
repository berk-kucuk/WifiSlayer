import sys
import os
from PyQt6.QtWidgets import QApplication
from gui import WifiSlayerGUI

def main():
    # Bu araç donanıma doğrudan müdahale ettiği için root yetkisi şarttır
    if os.geteuid() != 0:
        print("[!] Hata: Bu programı sudo yetkisi ile çalıştırmalısınız!")
        print("Örnek kullanım: sudo -E python3 main.py")
        sys.exit(1)

    app = QApplication(sys.argv)

    # Modern bir Qt teması uygulayalım
    app.setStyle("Fusion")

    window = WifiSlayerGUI()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
