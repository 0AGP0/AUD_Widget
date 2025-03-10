import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QDesktopWidget
)
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtGui import QPainter, QPixmap, QColor, QTransform, QPen, QBrush, QFont
import random

# Debug modunu aktif et
DEBUG = True

# Debug fonksiyonu
def debug_print(*args, **kwargs):
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)

print("=== Oyun Başlatılıyor ===")
print(f"Python versiyonu: {sys.version}")
print(f"Çalışma dizini: {os.getcwd()}")
print(f"Dosya yolu: {os.path.abspath(__file__)}")
print("=========================")

# Diğer importlar
try:
    from src.controllers.game_controller import GameController
    from src.models.villager import Villager
    from src.views.main_window import MainWindow
    debug_print("GameController import edildi")
except ImportError as e:
    print(f"HATA: GameController import edilemedi: {e}")
    sys.exit(1)

# Çalışma dizinini kontrol et
print(f"Çalışma dizini: {os.getcwd()}")
print(f"Assets dizini var mı: {os.path.exists('assets')}")
if os.path.exists('assets'):
    print(f"Assets içeriği: {os.listdir('assets')}")

# Yüksek DPI desteğini etkinleştir (QApplication oluşturulmadan önce)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

def main():
    """Ana fonksiyon"""
    try:
        # Uygulama dizinini ayarla
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(app_dir)
        
        print(f"Çalışma dizini: {os.getcwd()}")
        print(f"Python sürümü: {sys.version}")
        
        # QApplication oluştur
        app = QApplication(sys.argv)
        
        # GameController oluştur
        game_controller = GameController()
        
        # Oyunu kur
        game_controller.setup_game()
        
        # Ana pencereyi oluştur
        main_window = MainWindow(game_controller)
        
        # GameController'a pencereyi ata
        game_controller.window = main_window
        
        # Pencereyi göster
        main_window.show()
        
        # Uygulamayı başlat
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"HATA: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 