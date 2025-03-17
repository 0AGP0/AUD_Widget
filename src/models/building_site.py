from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QRectF
import random
import time
import os

class BuildingSite(QObject):
    """İnşaat alanı sınıfı"""
    construction_finished = pyqtSignal(object)  # İnşaat tamamlandığında sinyal gönder
    construction_progress_updated = pyqtSignal(object, float)  # İnşaat ilerlemesi güncellendiğinde sinyal gönder
    
    def __init__(self, x: float, y: float, width: int, height: int):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_active = True
        self.progress = 0.0  # 0.0 - 1.0 arası ilerleme
        self.construction_time = 10.0  # 10 saniye
        self.start_time = None
        self.builder = None
        self.house_type = None  # Ev tipi (rastgele seçilecek)
        self.id = id(self)
        self.rect = QRectF(self.x, self.y - self.height, self.width, self.height)
        
        # Rastgele ev tipi seç
        self.select_random_house_type()
        
        print(f"İnşaat alanı oluşturuldu: ({self.x}, {self.y}), {self.width}x{self.height}, Ev tipi: {self.house_type}")
    
    def select_random_house_type(self):
        """Rastgele ev tipi seç"""
        house_types = ["ev1", "ev2", "ev3", "ev4"]  # Farklı ev tipleri
        self.house_type = random.choice(house_types)
    
    def start_construction(self, builder):
        """İnşaat sürecini başlat"""
        if not self.is_active:
            print(f"İnşaat alanı ID: {self.id} aktif değil, inşaat başlatılamaz!")
            return False
            
        if self.builder:
            print(f"İnşaat alanı ID: {self.id} zaten inşa ediliyor! İnşaatçı: {self.builder.name}")
            return False
            
        # Kale envanterinde yeterli odun var mı kontrol et
        if hasattr(builder, 'game_controller') and builder.game_controller:
            game_controller = builder.game_controller
            if hasattr(game_controller, 'castle') and game_controller.castle:
                castle = game_controller.castle
                if not castle.remove_from_inventory("odun", 20):
                    print(f"İnşaat başlatılamadı: Kale envanterinde yeterli odun yok!")
                    return False
                print(f"İnşaat için 20 odun kullanıldı!")
            else:
                print("UYARI: Kale bulunamadı, odun kontrolü yapılamadı!")
                return False
        else:
            print("UYARI: Oyun kontrolcüsü bulunamadı, odun kontrolü yapılamadı!")
            return False
            
        self.builder = builder
        self.start_time = time.time()
        self.progress = 0.0
        
        # İnşaat sürecini başlat
        self.update_progress()
        
        print(f"İnşaat başlatıldı! İnşaatçı: {builder.name}, Süre: {self.construction_time} saniye")
        return True
    
    def update_progress(self):
        """İnşaat ilerlemesini güncelle"""
        if not self.is_active or not self.builder or self.progress >= 1.0:
            return
            
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        # İlerlemeyi hesapla (0.0 - 1.0 arası)
        self.progress = min(elapsed_time / self.construction_time, 1.0)
        
        # İlerleme sinyali gönder
        self.construction_progress_updated.emit(self, self.progress)
        
        # İnşaat tamamlandı mı kontrol et
        if self.progress >= 1.0:
            self.finish_construction()
        else:
            # 100ms sonra tekrar güncelle
            QTimer.singleShot(100, self.update_progress)
    
    def finish_construction(self):
        """İnşaatı tamamla"""
        if not self.is_active or not self.builder:
            return
            
        self.is_active = False
        self.progress = 1.0
        
        # İnşaatçıya ödül ver (100 altın)
        self.builder.money += 100
        self.builder.buildings_built += 1
        print(f"İnşaat tamamlandı! İnşaatçı {self.builder.name} 100 altın kazandı. Toplam altın: {self.builder.money}")
        
        # İnşaat tamamlandı sinyali gönder
        self.construction_finished.emit(self)
        
        # İnşaatçıyı serbest bırak
        builder = self.builder
        self.builder = None
        
        # İnşaatçının durumunu güncelle
        if hasattr(builder, 'is_building'):
            builder.is_building = False
        
        print(f"İnşaat alanı ID: {self.id} tamamlandı ve ev inşa edildi!")
    
    def cancel_construction(self):
        """İnşaatı iptal et"""
        if not self.is_active or not self.builder:
            return
            
        self.is_active = False
        
        # İnşaatçıyı serbest bırak
        builder = self.builder
        self.builder = None
        
        # İnşaatçının durumunu güncelle
        if hasattr(builder, 'is_building'):
            builder.is_building = False
        
        print(f"İnşaat alanı ID: {self.id} iptal edildi!")
    
    def contains_point(self, x: float, y: float) -> bool:
        """Verilen nokta inşaat alanının içinde mi kontrol et"""
        return self.rect.contains(x, y)
    
    def get_entrance(self) -> tuple[float, float]:
        """İnşaat alanının giriş noktasını döndür"""
        # Varsayılan olarak alanın alt orta noktası
        return (self.x + self.width / 2, self.y) 