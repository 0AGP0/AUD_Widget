from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QDesktopWidget
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QPixmap, QColor
import os
import sys
import random

class Koylu:
    """Köylü sınıfı"""
    def __init__(self, x, y, cinsiyet, isim, meslek=None):
        self.x = x
        self.y = y
        self.cinsiyet = cinsiyet  # "erkek" veya "kadın"
        self.isim = isim
        self.meslek = meslek  # "Oduncu", "Madenci", "İnşaatcı", "İşsiz", "Sanatçı"
        
        # Köylü özellikleri
        self.saglik = 100
        self.para = 0
        self.mutluluk = 50
        self.karizma = 50
        self.egitim = 0
        self.yas = random.randint(18, 50)
        
        # Mesleğe göre özellikler
        if self.meslek:
            self.meslek_ozellikleri_ayarla()
        
        # Hareket için
        self.hedef_x = None
        self.hedef_y = None
        self.hareket_hizi = 2
    
    def meslek_ozellikleri_ayarla(self):
        """Mesleğe göre özellikleri ayarla"""
        if self.meslek == "Oduncu":
            self.hareket_hizi = 3
            self.para = 10
        elif self.meslek == "Madenci":
            self.hareket_hizi = 2
            self.para = 20
        elif self.meslek == "İnşaatcı":
            self.hareket_hizi = 2
            self.para = 15
        elif self.meslek == "İşsiz":
            self.hareket_hizi = 1
            self.para = 0
            self.mutluluk = 30
        elif self.meslek == "Sanatçı":
            self.hareket_hizi = 2
            self.para = 5
            self.karizma = 70
            self.mutluluk = 70

class ZeminPenceresi(QMainWindow):
    """Zemin penceresi sınıfı"""
    def __init__(self):
        print("ZeminPenceresi.__init__ başladı")
        super().__init__(None)
        self.setWindowTitle("Çağlar Boyu Savaş")
        
        try:
            # Tüm ekranları al
            desktop = QDesktopWidget()
            print(f"QDesktopWidget oluşturuldu, ekran sayısı: {desktop.screenCount()}")
            
            # Ekranların toplam genişliğini ve yüksekliğini hesapla
            self.total_width = 0
            self.max_height = 0
            self.min_x = float('inf')
            self.min_y = float('inf')
            self.max_y = float('-inf')
            
            # Her ekranın bilgilerini topla
            for i in range(desktop.screenCount()):
                screen = desktop.screenGeometry(i)
                self.total_width += screen.width()
                self.max_height = max(self.max_height, screen.height())
                self.min_x = min(self.min_x, screen.x())
                self.min_y = min(self.min_y, screen.y())
                self.max_y = max(self.max_y, screen.y() + screen.height())
                print(f"Ekran {i+1}: ({screen.x()}, {screen.y()}, {screen.width()}x{screen.height()})")
            
            # Zemin yüksekliği
            self.zemin_height = 100
            
            # Kale resmini yükle ve boyutunu küçült
            original_kale = QPixmap("assets/kale.png")
            self.kale_img = original_kale.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Köylü resimlerini yükle - daha küçük boyutlarda
            self.erkek_koylu_img = QPixmap("assets/koylu1.png").scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.kadin_koylu_img = QPixmap("assets/kadin_koylu1.png").scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Pencere yüksekliğini hesapla (zemin + kale yüksekliği)
            self.window_height = self.zemin_height + self.kale_img.height()
            print("Ekran bilgileri toplandı")
            
            # Pencere özelliklerini ayarla
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
            self.setAttribute(Qt.WA_TranslucentBackground)
            print("Pencere özellikleri ayarlandı")
            
            # Pencereyi tüm ekranları kapsayacak şekilde ayarla
            # Tüm ekranların en alt noktasını kullan
            window_y = self.max_y - self.window_height
            self.setGeometry(self.min_x, window_y, self.total_width, self.window_height)
            print(f"Pencere geometrisi ayarlandı: ({self.min_x}, {window_y}, {self.total_width}, {self.window_height})")
            
            # Resimlerin yollarını kontrol et
            self.check_assets()
            
            # Zemin resmini yükle
            self.zemin_tile = QPixmap("assets/zemin.png").scaled(64, 64)  # 64x64 boyutunda
            print("Zemin resmi yüklendi")
            print("Kale resmi yüklendi")
            print("Köylü resimleri yüklendi")
            
            # Zemin y pozisyonu (zeminin üst kenarı)
            self.zemin_y = self.height() - self.zemin_tile.height()
            
            # Kale konumunu hesapla
            self.castle_x = 100
            self.castle_y = self.zemin_y - self.kale_img.height() + 30  # 30 piksel zeminin içinde
            
            # Köylüleri oluştur
            self.create_villagers()
            
            # Debug bilgisi
            print(f"Toplam genişlik: {self.total_width}")
            print(f"Başlangıç X: {self.min_x}")
            print(f"Başlangıç Y: {window_y}")
            print(f"Ekran sayısı: {desktop.screenCount()}")
            print(f"Kale boyutu: {self.kale_img.width()}x{self.kale_img.height()}")
            print(f"Köylü boyutu: {self.erkek_koylu_img.width()}x{self.erkek_koylu_img.height()}")
            print(f"Pencere yüksekliği: {self.window_height}")
            print(f"Zemin Y pozisyonu: {self.zemin_y}")
            
            print("ZeminPenceresi.__init__ tamamlandı")
        except Exception as e:
            print(f"ZeminPenceresi.__init__ hata: {e}")
            import traceback
            traceback.print_exc()
    
    def create_villagers(self):
        """Köylüleri oluştur"""
        try:
            # Köylü listesi
            self.koyluler = []
            
            # Köylü isimleri
            erkek_isimleri = ["Ahmet", "Mehmet", "Ali", "Mustafa", "Hasan"]
            kadin_isimleri = ["Ayşe", "Fatma", "Zeynep", "Emine", "Hatice"]
            
            # Meslekler
            meslekler = ["Oduncu", "Madenci", "İnşaatcı", "İşsiz", "Sanatçı"]
            
            # En az 1 erkek ve 1 kadın olacak şekilde
            cinsiyetler = ["erkek", "kadın", "erkek", "kadın"]
            
            # Köylüleri oluştur - kalenin etrafında ve zeminin üzerinde
            # Köylü y pozisyonu (zeminin üzerinde)
            koylu_y = self.zemin_y - self.erkek_koylu_img.height()
            
            # Köylü x pozisyonları (kalenin etrafında)
            koylu_x_positions = [
                self.castle_x - 50,  # Sol
                self.castle_x + self.kale_img.width() + 10,  # Sağ
                self.castle_x + self.kale_img.width() // 2 - 20,  # Orta sol
                self.castle_x + self.kale_img.width() // 2 + 20   # Orta sağ
            ]
            
            # Köylüleri oluştur
            for i, x in enumerate(koylu_x_positions):
                cinsiyet = cinsiyetler[i]
                if cinsiyet == "erkek":
                    isim = random.choice(erkek_isimleri)
                else:
                    isim = random.choice(kadin_isimleri)
                
                # Her köylüye farklı bir meslek ata
                meslek = meslekler[i]
                
                koylu = Koylu(x, koylu_y, cinsiyet, isim, meslek)
                self.koyluler.append(koylu)
            
            print(f"Toplam {len(self.koyluler)} köylü oluşturuldu")
            for koylu in self.koyluler:
                print(f"Köylü: {koylu.isim} ({koylu.cinsiyet}), Meslek: {koylu.meslek}, Konum: ({koylu.x}, {koylu.y})")
        except Exception as e:
            print(f"create_villagers hata: {e}")
            import traceback
            traceback.print_exc()
    
    def check_assets(self):
        """Asset dosyalarının varlığını kontrol et"""
        required_assets = ["zemin.png", "kale.png", "koylu1.png", "kadin_koylu1.png","koylu2.png","kadin_koylu2.png","koylu3.png","kadin_koylu3.png","koylu4.png","kadin_koylu4.png"]
        for asset in required_assets:
            asset_path = os.path.join("assets", asset)
            if not os.path.exists(asset_path):
                print(f"UYARI: {asset_path} dosyası bulunamadı!")
            else:
                print(f"Dosya bulundu: {asset_path}")
    
    def paintEvent(self, event):
        """Pencereyi çiz"""
        try:
            print("paintEvent başladı")
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Arkaplanı saydam yap
            painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
            
            # Zemini çiz
            self.draw_ground(painter)
            
            # Kaleyi çiz
            self.draw_castle(painter)
            
            # Köylüleri çiz
            self.draw_villagers(painter)
            
            print("paintEvent tamamlandı")
        except Exception as e:
            print(f"paintEvent hata: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_ground(self, painter: QPainter):
        """Zemini çiz"""
        try:
            # Yatayda kaç adet zemin.png gerekiyor hesapla
            tile_width = self.zemin_tile.width()  # 64 piksel
            tile_count = int(self.total_width / tile_width) + 1
            
            # Debug bilgisi
            print(f"Zemin parçası sayısı: {tile_count}")
            print(f"Zemin parçası genişliği: {tile_width}")
            
            # Zemini yatayda tekrarla
            for x in range(tile_count):
                painter.drawPixmap(
                    int(x * tile_width),
                    self.zemin_y,  # Zeminin y pozisyonu
                    self.zemin_tile
                )
            print("Zemin çizildi")
        except Exception as e:
            print(f"draw_ground hata: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_castle(self, painter: QPainter):
        """Kaleyi çiz"""
        try:
            painter.drawPixmap(self.castle_x, self.castle_y, self.kale_img)
            print(f"Kale çizildi: ({self.castle_x}, {self.castle_y})")
        except Exception as e:
            print(f"draw_castle hata: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_villagers(self, painter: QPainter):
        """Köylüleri çiz"""
        try:
            for koylu in self.koyluler:
                # Köylünün cinsiyetine göre resmi seç
                img = self.erkek_koylu_img if koylu.cinsiyet == "erkek" else self.kadin_koylu_img
                
                # Köylüyü çiz
                painter.drawPixmap(
                    int(koylu.x),
                    int(koylu.y),
                    img
                )
                
                # Köylünün mesleğini üstüne yaz
                painter.setPen(Qt.white)  # Beyaz renk
                painter.drawText(
                    int(koylu.x),
                    int(koylu.y - 5),  # Köylünün biraz üstüne
                    koylu.meslek
                )
            print(f"{len(self.koyluler)} köylü çizildi")
        except Exception as e:
            print(f"draw_villagers hata: {e}")
            import traceback
            traceback.print_exc()
    
    def keyPressEvent(self, event):
        """Tuş basma olayı"""
        # ESC tuşuna basılınca oyundan çık
        if event.key() == Qt.Key_Escape:
            print("ESC tuşuna basıldı, uygulama kapatılıyor")
            self.close() 