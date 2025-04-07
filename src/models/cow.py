from PyQt5.QtCore import QObject, pyqtSignal
import random

class Cow(QObject):
    """İnek sınıfı"""
    
    def __init__(self, x: float, y: float, min_x: float, max_x: float):
        super().__init__()
        
        # Konum
        self.x = x
        self.y = y
        
        # Boyutlar
        self.width = 35
        self.height = 35
        
        # Hareket sınırları
        self.min_x = min_x
        self.max_x = max_x
        
        # Hareket özellikleri
        self.speed = 0.5  # Hareket hızı
        self.direction_x = 1  # 1: sağa, -1: sola
        self.animation_frame = 0  # Animasyon karesi
        
        # Hareket durumu
        self.is_moving = True
        self.movement_timer = 0
        self.movement_duration = random.randint(50, 150)  # Hareket süresi
        self.pause_duration = random.randint(30, 80)  # Durma süresi
        
    def update(self):
        """İneğin durumunu güncelle"""
        if self.is_moving:
            # Hareketi güncelle
            new_x = self.x + (self.speed * self.direction_x)
            
            # Sınırları kontrol et
            if new_x <= self.min_x:
                new_x = self.min_x
                self.direction_x = 1  # Sağa dön
            elif new_x >= self.max_x:
                new_x = self.max_x
                self.direction_x = -1  # Sola dön
            
            self.x = new_x
            
            # Animasyon karesini güncelle
            self.animation_frame = (self.animation_frame + 1) % 4
            
            # Hareket süresini kontrol et
            self.movement_timer += 1
            if self.movement_timer >= self.movement_duration:
                self.is_moving = False
                self.movement_timer = 0
                self.movement_duration = random.randint(50, 150)
        else:
            # Durma süresini kontrol et
            self.movement_timer += 1
            if self.movement_timer >= self.pause_duration:
                self.is_moving = True
                self.movement_timer = 0
                self.pause_duration = random.randint(30, 80)
                # Rastgele yön değiştir
                if random.random() < 0.5:
                    self.direction_x *= -1 