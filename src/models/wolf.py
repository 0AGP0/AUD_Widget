from dataclasses import dataclass
from typing import Optional
import random
import time
import math
from PyQt5.QtCore import QTimer

@dataclass
class Wolf:
    """Kurt sınıfı - Köye saldıran vahşi canavarlar"""
    wolf_id: int = 0  # Kurt kimlik numarası
    x: float = 0.0  # X koordinatı
    y: float = 0.0  # Y koordinatı
    width: int = 50  # Kurt genişliği
    height: int = 35  # Kurt yüksekliği
    direction: int = -1  # 1 = sağa, -1 = sola
    direction_x: int = -1  # 1 = sağa, -1 = sola (çizim için)
    health: int = 100  # Sağlık durumu
    is_daytime: bool = True  # Gündüz/gece durumu
    state: str = "Dolaşıyor"  # Kurdun durumu
    
    # Hareket özellikleri
    speed: float = 0.5  # Hız (2.0'dan 0.5'e düşürüldü)
    min_x: float = 1000.0  # Gündüz en soldaki limit
    cave_x: float = 0.0  # Mağaranın X konumu
    cave_radius: float = 300.0  # Mağara etrafında dolaşma yarıçapı
    is_wandering: bool = True  # Dolaşma durumu
    
    # Animasyon özellikleri
    current_frame: int = 0
    animation_frame: int = 0
    last_animation_update: float = 0
    
    # Hareket hedefi
    target_x: float = 0.0
    target_y: float = 0.0
    is_moving: bool = True
    
    # Game controller referansı
    game_controller = None
    
    def __post_init__(self):
        """Başlangıç değerlerini ayarla"""
        # Temel Y pozisyonunu ayarla
        self.base_y = self.y
        
        # Wolf ID kontrolü
        if self.wolf_id == 0:
            self.wolf_id = random.randint(1, 1000)
        
        # Animasyon değişkenlerini başlat
        self.last_animation_update = time.time()
        self.animation_frame = 1
        
        # İlk hedefi belirle
        self.target_x = self.x
        self.target_y = self.y
        self.is_moving = True
        
        print(f"Kurt #{self.wolf_id} oluşturuldu: x={self.x}, y={self.y}")
    
    def __hash__(self):
        """Hash değerini döndür"""
        return hash(self.wolf_id)
    
    def __eq__(self, other):
        """Eşitlik kontrolü"""
        if not isinstance(other, Wolf):
            return False
        return self.wolf_id == other.wolf_id
    
    def wander(self):
        """Rastgele dolaş - oyun kontrolcüsü için gerekli"""
        try:
            # Gündüzse mağara etrafında dolaş
            if self.is_daytime:
                # Mağaranın etrafında rastgele bir konum belirle
                angle = random.uniform(0, 2 * math.pi)  # 0-360 derece arası rastgele açı
                distance = random.uniform(50, self.cave_radius)
                
                # Yeni hedef X koordinatı
                new_target_x = self.cave_x + distance * math.cos(angle)
                
                # Eğer hedef min_x'in solundaysa, sağ tarafta kal
                if new_target_x < self.min_x:
                    angle = random.uniform(-0.5 * math.pi, 0.5 * math.pi)
                    new_target_x = self.cave_x + distance * math.cos(angle)
                
                self.target_x = new_target_x
                self.target_y = self.y  # Y koordinatını değiştirme
                self.state = "Mağara Etrafında"
            else:
                # Geceyse köye doğru git
                self.target_x = random.uniform(self.min_x - 500, self.min_x + 300)
                self.target_y = self.y  # Y koordinatını değiştirme
                self.state = "Avlanıyor (Gece)"
            
            # Hareket yönünü ayarla
            if self.target_x > self.x:
                self.direction = 1
                self.direction_x = 1
            else:
                self.direction = -1
                self.direction_x = -1
                
            self.is_moving = True
            self.is_wandering = True
            
            print(f"Kurt #{self.wolf_id}: Yeni hedef: {self.target_x}, Mevcut konum: {self.x}")
            
        except Exception as e:
            print(f"HATA: Kurt dolaşma hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def move(self):
        """Kurdu hareket ettir"""
        try:
            # Hareket etmiyorsa çıkış yap
            if not self.is_moving:
                return
            
            # Hedef noktaya doğru hareket et
            dx = self.target_x - self.x
            
            # Hareket hızı
            move_speed = self.speed * (1.5 if self.is_daytime else 0.8)  # Hız çarpanları düşürüldü
            
            # Hedefe doğru hareket et
            if abs(dx) > 5:
                if dx > 0:
                    # Sağa hareket
                    self.direction = 1
                    self.direction_x = 1
                    self.x += move_speed
                else:
                    # Sola hareket
                    self.direction = -1
                    self.direction_x = -1
                    self.x -= move_speed
            else:
                # Hedefe ulaşıldı, yeni hedef belirle
                self.wander()
            
            # Animasyon karesini güncelle (her 0.25 saniyede bir)
            current_time = time.time()
            if current_time - self.last_animation_update > 0.25:
                self.animation_frame = (self.animation_frame % 4) + 1
                self.last_animation_update = current_time
                
                # Her animasyon karesinde küçük bir şans ile yeni hedef belirle (gündüz vakti)
                if self.is_daytime and random.random() < 0.05:  # Olasılık 0.1'den 0.05'e düşürüldü
                    self.wander()
                
        except Exception as e:
            print(f"HATA: Kurt hareket hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def update_daytime(self, is_daytime):
        """Gündüz/gece durumunu güncelle"""
        self.is_daytime = is_daytime
        
        # Gündüz/gece değişimine göre davranışı güncelle
        if is_daytime:
            self.state = "Mağara Etrafında"
        else:
            self.state = "Avlanıyor (Gece)"
        
        # Yeni hedef belirle
        self.wander()
    
    def set_game_controller(self, game_controller):
        """Oyun kontrolcüsünü ayarla"""
        self.game_controller = game_controller
        
        # Mağara konumunu al (eğer game controller'da varsa)
        if hasattr(game_controller, 'cave') and game_controller.cave:
            self.cave_x = game_controller.cave.x
            print(f"Kurt #{self.wolf_id}: Mağara X konumu ayarlandı: {self.cave_x}")
        
        # İlk hedefi belirle
        self.wander()
        
    def update(self):
        """Kurt durumunu güncelle - her kare çalışır"""
        # Hareket ettir
        self.move()
    
    def update_animation(self):
        """Animasyon karesini güncelle"""
        try:
            current_time = time.time()
            
            # Eğilme animasyonunu güncelle
            if self.is_moving:
                time_diff = current_time - self.last_rotation_time
                
                # Her rotation_interval sürede bir yön değiştir
                if time_diff >= self.rotation_interval:
                    self.rotation_direction *= -1
                    self.last_rotation_time = current_time
                
                # Yumuşak geçiş için sinüs fonksiyonu kullan
                progress = (time_diff / self.rotation_interval) * math.pi
                target_rotation = math.sin(progress) * self.max_rotation * self.rotation_direction
                self.current_rotation += (target_rotation - self.current_rotation) * self.rotation_speed
                self.rotation = self.current_rotation
            else:
                # Duruyorsa yumuşak şekilde dik pozisyona dön
                self.current_rotation += (0 - self.current_rotation) * self.rotation_speed * 2
                self.rotation = self.current_rotation
            
            # Animasyon karesini güncelle
            if current_time - self.last_frame_time >= self.animation_speed:
                self.current_frame = (self.current_frame + 1) % self.frame_count
                self.last_frame_time = current_time
                
        except Exception as e:
            print(f"HATA: Kurt animasyon güncelleme hatası: {e}")
            import traceback
            traceback.print_exc() 