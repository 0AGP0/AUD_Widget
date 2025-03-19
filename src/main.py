import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QDesktopWidget
)
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtGui import QPainter, QPixmap, QColor, QTransform, QPen, QBrush, QFont
import random

# PYTHON_PATH düzeltmesi
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

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
    print(f"HATA: {e}")
    print("Import hatası. Python yolu: ", sys.path)
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
    """Ana uygulama"""
    try:
        print("=== Oyun Başlatılıyor ===")
        print(f"Python versiyonu: {sys.version}")
        print(f"Çalışma dizini: {os.getcwd()}")
        print(f"Dosya yolu: {os.path.abspath(__file__)}")
        print("=========================")
        
        print("[DEBUG] GameController import edildi")
        
        # Çalışma dizinini kontrol et
        print(f"Çalışma dizini: {os.getcwd()}")
        
        # Assets dizinini kontrol et
        print(f"Assets dizini var mı: {os.path.exists('assets')}")
        
        # Çalışma dizinini tekrar yazdır
        print(f"Çalışma dizini: {os.getcwd()}")
        
        print(f"Python sürümü: {sys.version}")
        
        # Ana uygulamayı oluştur
        app = QApplication(sys.argv)
        
        # Oyun kontrolcüsünü oluştur
        controller = GameController()
        print("GameController başarıyla oluşturuldu!")
        
        # Ana pencereyi oluştur
        main_window = MainWindow(controller)
        controller.window = main_window
        
        # Davranış ağaçlarını oluştur (oyun kurulumundan sonra)
        controller.setup_game()
        
        # Davranış ağaçlarını oluştur
        create_behavior_trees(controller)
        print("Davranış ağaçları oluşturuldu!")
        
        # Pencereyi göster
        controller.window.show()
        
        # Uygulamayı başlat
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"HATA: {e}")
        import traceback
        traceback.print_exc()

def create_behavior_trees(game_controller):
    """Tüm köylüler için davranış ağaçlarını oluşturur"""
    try:
        from src.models.ai.villager_behaviors import create_villager_behavior_tree
        
        # Köylüler için davranış ağaçlarını oluştur
        for villager in game_controller.villagers:
            behavior_tree = create_villager_behavior_tree(villager)
            villager.behavior_tree = behavior_tree
            print(f"{villager.name} için davranış ağacı oluşturuldu.")
            
    except Exception as e:
        print(f"HATA: Davranış ağaçları oluşturulurken hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 