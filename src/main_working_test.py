import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPixmap, QColor
import random

class Villager:
    """Basit köylü sınıfı"""
    def __init__(self, x, y, name, gender, profession):
        self.x = x
        self.y = y
        self.name = name
        self.gender = gender
        self.profession = profession
        print(f"{self.name} oluşturuldu: ({self.x}, {self.y}), cinsiyet: {self.gender}")

class Building:
    """Basit yapı sınıfı"""
    def __init__(self, x, y, width, height, building_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.building_type = building_type
        print(f"{self.building_type} oluşturuldu: ({self.x}, {self.y}), {self.width}x{self.height}")

class GameWidget(QWidget):
    """Oyun alanı widget'ı"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Oyun nesneleri
        self.buildings = []
        self.trees = []
        self.villagers = []
        
        # Resimleri yükle
        self.load_images()
        
        # Oyunu hazırla
        self.setup_game()
    
    def load_images(self):
        """Resimleri yükle"""
        try:
            # Tam dosya yollarını oluştur
            assets_dir = "assets"
            
            # Dosya varlığını kontrol et
            zemin_path = os.path.join(assets_dir, "zemin.png")
            kale_path = os.path.join(assets_dir, "kale.png")
            agac_path = os.path.join(assets_dir, "agac.png")
            
            print(f"Zemin dosyası var mı: {os.path.exists(zemin_path)}")
            print(f"Kale dosyası var mı: {os.path.exists(kale_path)}")
            print(f"Ağaç dosyası var mı: {os.path.exists(agac_path)}")
            
            # Temel resimleri yükle
            self.ground_tile = QPixmap(zemin_path).scaled(64, 64)
            self.castle_img = QPixmap(kale_path)
            self.tree_img = QPixmap(agac_path)
            
            # Erkek köylü resimleri
            self.villager_male_img = None
            male_path = os.path.join(assets_dir, "koylu1.png")
            if os.path.exists(male_path):
                self.villager_male_img = QPixmap(male_path).scaled(50, 50)
                print(f"Erkek köylü resmi yüklendi: {male_path}")
            
            # Kadın köylü resimleri
            self.villager_female_img = None
            female_path = os.path.join(assets_dir, "kadin_koylu1.png")
            if os.path.exists(female_path):
                self.villager_female_img = QPixmap(female_path).scaled(50, 50)
                print(f"Kadın köylü resmi yüklendi: {female_path}")
            
            print("Resimler başarıyla yüklendi")
            
        except Exception as e:
            print(f"Resim yükleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_game(self):
        """Oyunu hazırla"""
        # Kaleyi yerleştir
        castle = Building(
            x=100,
            y=500,
            width=150,
            height=150,
            building_type="castle"
        )
        self.buildings.append(castle)
        
        # Ağaçları yerleştir
        tree_positions = [
            (300, 500),
            (400, 500),
            (500, 500),
            (600, 500),
            (700, 500)
        ]
        
        for x, y in tree_positions:
            tree = Building(
                x=x,
                y=y,
                width=50,
                height=80,
                building_type="tree"
            )
            self.trees.append(tree)
        
        # Köylüleri yerleştir
        villager_data = [
            (150, 450, "Ahmet", "Erkek", "Oduncu"),
            (200, 450, "Ayşe", "Kadın", "Madenci"),
            (250, 450, "Mehmet", "Erkek", "İnşaatçı"),
            (300, 450, "Fatma", "Kadın", "Sanatçı")
        ]
        
        for x, y, name, gender, profession in villager_data:
            villager = Villager(
                x=x,
                y=y,
                name=name,
                gender=gender,
                profession=profession
            )
            self.villagers.append(villager)
    
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
            
            # Kaleyi çiz
            if self.castle_img:
                for building in self.buildings:
                    if building.building_type == "castle":
                        painter.drawPixmap(
                            int(building.x),
                            int(building.y - building.height),
                            self.castle_img
                        )
            
            # Ağaçları çiz
            if self.tree_img:
                for tree in self.trees:
                    painter.drawPixmap(
                        int(tree.x),
                        int(tree.y - tree.height),
                        self.tree_img
                    )
            
            # Köylüleri çiz
            for villager in self.villagers:
                # Köylü resmini seç
                if villager.gender == "Erkek" and self.villager_male_img:
                    img = self.villager_male_img
                elif villager.gender == "Kadın" and self.villager_female_img:
                    img = self.villager_female_img
                else:
                    # Varsayılan resim
                    img = QPixmap(50, 50)
                    img.fill(Qt.red)
                
                # Köylüyü çiz
                painter.drawPixmap(int(villager.x), int(villager.y), img)
                
                # Mesleğini üstüne yaz
                painter.setPen(Qt.black)
                profession_text = villager.profession if villager.profession else "İşsiz"
                painter.drawText(int(villager.x), int(villager.y - 10), profession_text)
            
        except Exception as e:
            print(f"Çizim hatası: {e}")
            import traceback
            traceback.print_exc()
        finally:
            painter.end()
    
    def mousePressEvent(self, event):
        """Mouse tıklamasını işle"""
        if event.button() == Qt.LeftButton:
            x = event.x()
            y = event.y()
            
            # Tıklanan konumda bir şey var mı kontrol et
            for building in self.buildings:
                if building.x <= x <= building.x + building.width and building.y - building.height <= y <= building.y:
                    print(f"Yapıya tıklandı: {building.building_type}")
                    return
                    
            for villager in self.villagers:
                if villager.x <= x <= villager.x + 50 and villager.y <= y <= villager.y + 50:
                    print(f"Köylüye tıklandı: {villager.name}")
                    return
                    
            # Boş bir alana tıklandı
            print(f"Boş alana tıklandı: ({x}, {y})")

class GameWindow(QMainWindow):
    """Oyun penceresi"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Çağlar Boyu Savaş")
        self.setGeometry(100, 100, 800, 600)
        
        # Oyun widget'ını ekle
        self.game_widget = GameWidget(self)
        self.setCentralWidget(self.game_widget)
        
        # Timer'ı başlat
        self.timer = QTimer()
        self.timer.setInterval(1000)  # 1000ms
        self.timer.timeout.connect(self.update_game)
        self.timer.start()
    
    def update_game(self):
        """Oyunu güncelle"""
        # Sadece ekranı yenile
        self.game_widget.update()
    
    def keyPressEvent(self, event):
        """Tuş basma olayı"""
        # ESC tuşuna basılınca oyundan çık
        if event.key() == Qt.Key_Escape:
            self.close()

def main():
    """Oyunu başlat"""
    try:
        # QApplication oluştur
        app = QApplication(sys.argv)
        print("QApplication oluşturuldu")
        
        # Oyun penceresini oluştur
        window = GameWindow()
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