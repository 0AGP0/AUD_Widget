from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QRectF
import random
import time
import os

class BuildingSite(QObject):
    """İnşaat alanı sınıfı"""
    construction_finished = pyqtSignal(object)  # İnşaat tamamlandığında sinyal gönder
    construction_progress_updated = pyqtSignal(object, float)  # İnşaat ilerlemesi güncellendiğinde sinyal gönder
    
    def __init__(self, x: float, y: float, width: int = 60, height: int = 75):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_active = True
        self.progress = 0.0  # 0.0 - 100.0 arası ilerleme (yüzde)
        self.construction_time = 10.0  # 10 saniye
        self.start_time = None
        self.builder = None
        self.house_type = None  # Ev tipi (rastgele seçilecek)
        self.id = id(self)
        
        # Rastgele ev tipi seç
        self.select_random_house_type()
        
        # Ev tipine göre boyutları ayarla
        self.adjust_size_by_type()
        
        # Çarpışma alanını güncelle
        self.rect = QRectF(self.x - self.width / 2, self.y - self.height, self.width, self.height)
        
        print(f"İnşaat alanı oluşturuldu: ({self.x}, {self.y}), {self.width}x{self.height}, Ev tipi: {self.house_type}")
    
    def select_random_house_type(self):
        """Rastgele ev tipi seç"""
        house_types = ["ev1", "ev2", "ev3"]  # Farklı ev tipleri
        self.house_type = random.choice(house_types)
    
    def adjust_size_by_type(self):
        """Ev tipine göre boyutları ayarla"""
        base_width = 60  # 80'den 60'a düşürüldü
        base_height = 75  # 100'den 75'e düşürüldü
        
        if self.house_type == "ev1":
            # Küçük ev
            self.width = base_width
            self.height = base_height
        elif self.house_type == "ev2":
            # Orta boy ev
            self.width = base_width * 1.2
            self.height = base_height * 1.2
        elif self.house_type == "ev3":
            # Büyük ev
            self.width = base_width * 1.5
            self.height = base_height * 1.5
        else:
            # Varsayılan boyut
            self.width = base_width
            self.height = base_height
    
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
                wood_amount = castle.get_inventory().get('odun', 0)
                
                # En az 30 odun gerekiyor
                if wood_amount < 30:
                    print(f"İnşaat başlatılamadı: Kale envanterinde yeterli odun yok! Mevcut: {wood_amount}/30")
                    return False
                
                # Odunu envanterden çıkar
                if not castle.remove_from_inventory("odun", 30):
                    print(f"İnşaat başlatılamadı: Kale envanterinden odun çıkarılamadı!")
                    return False
                
                print(f"İnşaat için 30 odun kullanıldı! Kalan odun: {castle.get_inventory().get('odun', 0)}")
                
                # Kontrol panelini güncelle
                if hasattr(game_controller, 'control_panel') and game_controller.control_panel:
                    game_controller.control_panel.update_castle_inventory()
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
        if not self.is_active or not self.builder or self.progress >= 100.0:
            return
            
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        # İlerlemeyi hesapla (0.0 - 100.0 arası)
        self.progress = min(elapsed_time / self.construction_time * 100.0, 100.0)
        
        # İlerleme sinyali gönder
        self.construction_progress_updated.emit(self, self.progress)
        
        # İnşaat tamamlandı mı kontrol et
        if self.progress >= 100.0:
            self.finish_construction()
        else:
            # 100ms sonra tekrar güncelle
            QTimer.singleShot(100, self.update_progress)
    
    def finish_construction(self):
        """İnşaatı tamamla"""
        if not self.is_active or not self.builder:
            return
            
        self.is_active = False
        self.progress = 100.0
        
        # İnşaatçıya ödül ver (100 altın)
        self.builder.money += 100
        self.builder.buildings_built += 1
        print(f"İnşaat tamamlandı! İnşaatçı {self.builder.name} 100 altın kazandı. Toplam altın: {self.builder.money}")
        
        # Rastgele bir köylüye evi tahsis et
        if hasattr(self.builder, 'game_controller') and self.builder.game_controller:
            game_controller = self.builder.game_controller
            potential_owners = [v for v in game_controller.villagers 
                               if not hasattr(v, 'has_house') or not v.has_house]
            
            if potential_owners:
                # Evi satın alacak rastgele bir köylü seç
                future_owner = random.choice(potential_owners)
                print(f"Yeni inşa edilen ev, rastgele {future_owner.name} kişisine tahsis edildi.")
                
                # Ev sahipliği bayrağı oluşturulacak ev içinde ayarlanacak
                self.future_owner = future_owner
        
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
    
    def stop_construction(self):
        """İnşaatı durdur (gece olduğunda)"""
        if not self.is_active or not self.builder:
            return
        
        # İnşaatçıyı serbest bırak ama inşaat alanını aktif tut
        builder = self.builder
        self.builder = None
        
        # İnşaatçının durumunu güncelle
        if hasattr(builder, 'is_building'):
            builder.is_building = False
        
        print(f"İnşaat alanı ID: {self.id} geçici olarak durduruldu (gece olduğu için)!")
    
    def contains_point(self, x: float, y: float) -> bool:
        """Verilen nokta inşaat alanının içinde mi kontrol et"""
        return self.rect.contains(x, y)
    
    def get_entrance(self) -> tuple[float, float]:
        """İnşaat alanının giriş noktasını döndür"""
        # Varsayılan olarak alanın alt orta noktası
        return (self.x, self.y) 