import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap, QColor
import random

# Çalışma dizinini kontrol et
print(f"Çalışma dizini: {os.getcwd()}")
print(f"Assets dizini var mı: {os.path.exists('assets')}")
if os.path.exists('assets'):
    print(f"Assets içeriği: {os.listdir('assets')}")

# Yüksek DPI desteğini etkinleştir (QApplication oluşturulmadan önce)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

class Villager:
    """Basit köylü sınıfı"""
    def __init__(self, x, y, name, gender, profession):
        self.x = x
        self.y = y
        self.name = name
        self.gender = gender
        self.profession = profession

class SimpleGroundWidget(QWidget):
    """Basit zemin widget'ı"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ground_tile = None
        self.castle_img = None
        self.tree_img = None
        self.villager_male_img = None
        self.villager_female_img = None
        self.load_images()
        
        # Ağaç konumları
        self.tree_positions = []
        for i in range(10):
            x = 300 + i * 100 + random.randint(-20, 20)
            self.tree_positions.append(x)
        
        # Köylüler
        self.villagers = []
        
        # Erkek köylüler
        self.villagers.append(Villager(150, 0, "Ahmet", "Erkek", "Oduncu"))
        self.villagers.append(Villager(250, 0, "Mehmet", "Erkek", "Madenci"))
        
        # Kadın köylüler
        self.villagers.append(Villager(350, 0, "Ayşe", "Kadın", "İnşaatçı"))
        self.villagers.append(Villager(450, 0, "Fatma", "Kadın", "Sanatçı"))
    
    def load_images(self):
        """Resimleri yükle"""
        try:
            # Resimleri yükle
            assets_dir = "assets"
            zemin_path = os.path.join(assets_dir, "zemin.png")
            kale_path = os.path.join(assets_dir, "kale.png")
            agac_path = os.path.join(assets_dir, "agac.png")
            koylu_path = os.path.join(assets_dir, "koylu1.png")
            kadin_koylu_path = os.path.join(assets_dir, "kadin_koylu1.png")
            
            if os.path.exists(zemin_path):
                self.ground_tile = QPixmap(zemin_path).scaled(64, 64)
                print(f"Zemin resmi yüklendi: {zemin_path}")
            else:
                print(f"Zemin resmi bulunamadı: {zemin_path}")
            
            if os.path.exists(kale_path):
                self.castle_img = QPixmap(kale_path)
                print(f"Kale resmi yüklendi: {kale_path}")
            else:
                print(f"Kale resmi bulunamadı: {kale_path}")
            
            if os.path.exists(agac_path):
                self.tree_img = QPixmap(agac_path)
                print(f"Ağaç resmi yüklendi: {agac_path}")
            else:
                print(f"Ağaç resmi bulunamadı: {agac_path}")
            
            if os.path.exists(koylu_path):
                self.villager_male_img = QPixmap(koylu_path).scaled(50, 50)
                print(f"Erkek köylü resmi yüklendi: {koylu_path}")
            else:
                print(f"Erkek köylü resmi bulunamadı: {koylu_path}")
            
            if os.path.exists(kadin_koylu_path):
                self.villager_female_img = QPixmap(kadin_koylu_path).scaled(50, 50)
                print(f"Kadın köylü resmi yüklendi: {kadin_koylu_path}")
            else:
                print(f"Kadın köylü resmi bulunamadı: {kadin_koylu_path}")
                
        except Exception as e:
            print(f"Resim yükleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def paintEvent(self, event):
        """Çizim olayı"""
        try:
            painter = QPainter(self)
            
            # Arkaplanı beyaz yap
            painter.fillRect(self.rect(), QColor(255, 255, 255))
            
            # Zemini çiz
            if self.ground_tile:
                tile_width = self.ground_tile.width()
                tile_count = int(self.width() / tile_width) + 1
                
                for x in range(tile_count):
                    painter.drawPixmap(
                        int(x * tile_width),
                        self.height() - self.ground_tile.height(),
                        self.ground_tile
                    )
            
            # Ağaçları çiz
            if self.tree_img:
                for x in self.tree_positions:
                    tree_y = self.height() - self.tree_img.height()
                    painter.drawPixmap(x, tree_y, self.tree_img)
            
            # Kaleyi çiz
            if self.castle_img:
                castle_x = 100
                castle_y = self.height() - self.castle_img.height()
                painter.drawPixmap(castle_x, castle_y, self.castle_img)
            
            # Köylüleri çiz
            if self.villager_male_img and self.villager_female_img:
                for villager in self.villagers:
                    # Y pozisyonunu ayarla (zeminin üstünde)
                    villager_y = self.height() - 50 - 10
                    
                    # Köylü resmini seç
                    if villager.gender == "Erkek":
                        img = self.villager_male_img
                    else:
                        img = self.villager_female_img
                    
                    # Köylüyü çiz
                    painter.drawPixmap(int(villager.x), int(villager_y), img)
                    
                    # Mesleğini üstüne yaz
                    painter.setPen(Qt.black)
                    profession_text = f"{villager.name} ({villager.profession})"
                    painter.drawText(int(villager.x), int(villager_y - 10), profession_text)
            
        except Exception as e:
            print(f"Çizim hatası: {e}")
            import traceback
            traceback.print_exc()
        finally:
            painter.end()

def main():
    """Basit bir pencere aç"""
    try:
        # QApplication oluştur
        app = QApplication(sys.argv)
        print("QApplication oluşturuldu")
        
        # Basit bir pencere oluştur
        window = QMainWindow()
        window.setWindowTitle("Çağlar Boyu Savaş - Test")
        window.setGeometry(100, 100, 800, 600)
        
        # Zemin widget'ını ekle
        ground_widget = SimpleGroundWidget(window)
        ground_widget.setGeometry(0, 0, 800, 600)
        
        # Pencereyi göster
        window.show()
        print("Pencere gösterildi")
        
        # Uygulamayı çalıştır
        return app.exec_()
    except Exception as e:
        print(f"Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("Oyun başlatılıyor...")
    exit_code = main()
    print(f"Oyun sonlandı. Çıkış kodu: {exit_code}")
    sys.exit(exit_code) 