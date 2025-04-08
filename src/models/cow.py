from PyQt5.QtCore import QObject, pyqtSignal
import random
import time
import math

class Cow(QObject):
    """İnek sınıfı"""
    
    def __init__(self, x: float, y: float, min_x: float, max_x: float):
        super().__init__()
        
        # Temel özellikler
        self.x = x
        self.y = y
        self.width = 35
        self.height = 35
        
        # Hareket sistemi
        self.speed = 0.25  # Köylülerden daha yavaş
        self.direction_x = random.choice([-1, 1])  # 1: sağa, -1: sola
        self.is_moving = True
        
        # Hareket alanı - çit arasında
        self.min_x = min_x
        self.max_x = max_x
        
        # Dolaşma sistemi
        self.target_x = 0
        self.wander_counter = 0
        self.max_wander_time = random.randint(150, 250)  # Hedef değişim sayacı
        
        # Animasyon
        self.animation_frame = 0
        self.animation_counter = 0
        self.animation_speed = 15  # Daha yavaş animasyon
        self.last_frame_time = time.time()
        
        # İnek kimliği
        self.cow_id = random.randint(1000, 9999)
        
        print(f"İnek #{self.cow_id} oluşturuldu: x={self.x}, sınırlar={self.min_x}-{self.max_x}")
        
        # Başlangıçta rastgele bir hedef belirle
        self.wander()
    
    def move_towards(self, target_x):
        """Hedefe doğru hareket et"""
        self.is_moving = True
        
        # Hareket adımı
        move_step = self.speed
        
        # Hedef pozisyona göre yön belirle
        if target_x > self.x:
            self.direction_x = 1  # Sağa
            self.x += move_step
        else:
            self.direction_x = -1  # Sola
            self.x -= move_step
        
        # Sınırlara ulaşıldıysa
        if self.x <= self.min_x:
            self.x = self.min_x
            self.direction_x = 1  # Sağa dön
            print(f"İnek #{self.cow_id} sol sınıra ulaştı, sağa dönüyor")
        elif self.x >= self.max_x:
            self.x = self.max_x
            self.direction_x = -1  # Sola dön
            print(f"İnek #{self.cow_id} sağ sınıra ulaştı, sola dönüyor")
    
    def wander(self):
        """Rastgele dolaş"""
        # Yeni hedef belirle
        distance = random.randint(30, 60)  # 30-60 piksel arasında bir mesafe
        direction = random.choice([-1, 1])  # Rastgele yön
        
        # Mevcut konuma göre yeni hedef hesapla
        new_x = self.x + (direction * distance)
        
        # Sınırlar içinde kalmasını sağla
        new_x = max(self.min_x, min(self.max_x, new_x))
        
        # Hedefi ayarla
        self.target_x = new_x
        self.is_moving = True
        
        print(f"İnek #{self.cow_id} yeni hedef: {new_x} (mesafe: {distance}, yön: {direction})")
    
    def update(self):
        """İnek güncelleme fonksiyonu"""
        try:
            # Dolaşma sayacını artır
            self.wander_counter += 1
            
            # Belirli aralıklarla yeni hedef belirle
            if self.wander_counter >= self.max_wander_time or abs(self.x - self.target_x) < 2:
                self.wander_counter = 0
                self.max_wander_time = random.randint(150, 250)  # Yeni bir bekleme süresi
                self.wander()  # Yeni hedef
            
            # Hedefe doğru hareket et
            self.move_towards(self.target_x)
            
            # Animasyon güncelleme
            current_time = time.time()
            if current_time - self.last_frame_time >= 0.2:  # Her 200ms'de bir
                self.animation_counter += 1
                if self.animation_counter >= self.animation_speed:
                    self.animation_counter = 0
                    self.animation_frame = (self.animation_frame + 1) % 4
                self.last_frame_time = current_time
            
            # Ara sıra hareket bilgisi
            if random.random() < 0.005:  # %0.5 ihtimalle
                print(f"İnek #{self.cow_id} hareket ediyor: x={self.x:.1f}, hedef={self.target_x}, yön={self.direction_x}")
            
            return True
            
        except Exception as e:
            print(f"HATA: İnek güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
            return False 