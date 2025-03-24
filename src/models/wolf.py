from dataclasses import dataclass
from typing import Optional
import random
import time
import math
from PyQt5.QtCore import QTimer

@dataclass
class Wolf:
    """Kurt sınıfı - Köye saldıran vahşi canavarlar"""
    wolf_id: int  # Kurt kimlik numarası
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
    speed: float = 0.8  # Hızı - köylülerden biraz daha hızlı (0.8'den 2.0'a yükseltildi)
    move_counter: int = 0
    max_move_time: int = 50
    is_wandering: bool = True
    target_x: float = 0.0
    target_y: float = 0.0
    min_x: float = 1000.0  # Gündüz en soldaki limit (kaleye yaklaşmamak için)
    cave_x: float = 0.0  # Mağaranın X konumu
    cave_radius: float = 300.0  # Mağara etrafında dolaşma yarıçapı
    
    # Animasyon özellikleri
    current_frame: int = 0
    frame_count: int = 2
    animation_speed: float = 0.1  # 0.2'den 0.1'e düşürüldü (daha hızlı animasyon)
    last_frame_time: float = 0
    is_moving: bool = False
    
    # Hareket ve zıplama özellikleri - köylülerdeki gibi
    base_y: float = 0.0  # Temel Y pozisyonu
    jump_height: float = 2.0  # Zıplama yüksekliği 
    jump_speed: float = 6.0  # Zıplama hızı
    animation_time: float = 0.0  # Animasyon zamanı
    
    # Eğilme özellikleri
    rotation: float = 0.0
    rotation_speed: float = 0.3  # Eğilme hızı (köylülerle aynı)
    rotation_direction: int = 1  # Eğilme yönü (1: sağa, -1: sola)
    last_rotation_time: float = 0.0  # Son eğilme zamanı
    rotation_interval: float = 0.2  # Her 0.2 saniyede bir yön değiştir (köylülerle aynı)
    max_rotation: float = 10.0  # Maksimum eğilme açısı (köylülerle aynı)
    current_rotation: float = 0.0  # Mevcut eğilme açısı
    is_crouching: bool = False  # Çömelme durumu
    crouch_frame: int = 0  # Çömelme karesi (animasyon için)
    
    # Hareket değişkenleri
    max_speed: float = 3.0  # Maksimum hız (1.8'den 3.0'a yükseltildi)
    wander_counter: int = 0  # Dolaşma sayacı
    max_wander_time: int = 200  # Maksimum dolaşma süresi
    
    # Kurt davranışını kontrol eden değişkenler
    is_hunting: bool = False  # Avlanıyor mu?
    hunger: int = 0  # Açlık seviyesi
    
    # Game controller referansı
    game_controller = None
    
    def __post_init__(self):
        """Başlangıç değerlerini ayarla"""
        # Temel Y pozisyonunu ayarla
        self.base_y = self.y
        
        # Eğer mağara konumu belirtilmemişse, başlangıç konumunu kullan
        if self.cave_x == 0.0:
            self.cave_x = self.x
        
        # Animasyon değişkenlerini başlat (köylülerle aynı)
        self.animation_time = 0.0
        self.rotation = 0.0
        self.current_rotation = 0.0
        self.rotation_direction = random.choice([-1, 1])
        self.last_rotation_time = time.time()
        
        # Çömelme değişkenlerini başlat
        self.is_crouching = False
        self.crouch_frame = 0
        
        # Hareket durumunu başlat
        self.is_moving = True  # Başlangıçta hareket etsin
    
    def __hash__(self):
        """Hash değerini döndür"""
        return hash(self.wolf_id)
    
    def __eq__(self, other):
        """Eşitlik kontrolü"""
        if not isinstance(other, Wolf):
            return False
        return self.wolf_id == other.wolf_id
    
    def move(self):
        """Kurdu hareket ettir"""
        try:
            # Eğer hareket etmiyorsa çıkış yap
            if not self.is_moving:
                return
                
            # Hedefe doğru hareket - her frame'de daha fazla hareket
            move_step = self.speed * 1.5  # Hareket adımını 1.5 kat artır
            
            if self.target_x > self.x:
                self.direction = 1
                self.direction_x = 1
                self.x += move_step
            else:
                self.direction = -1
                self.direction_x = -1
                self.x -= move_step
                
            # Hedefe ulaşıldı mı kontrol et
            if abs(self.target_x - self.x) < 10:  # 5 yerine 10 piksel hassasiyet
                # Hedefe ulaşıldı, dolaşma durumunu güncelle
                self.is_wandering = False
                self.move_counter = 0
                
                # Yeni bir hedef belirle
                self.wander()
                
        except Exception as e:
            print(f"HATA: Kurt hareket hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def update_animation(self):
        """Animasyon karesini güncelle - köylülerinkine benzer şekilde"""
        try:
            current_time = time.time()
            
            # Animasyon zamanını güncelle - daha hızlı güncelleme
            self.animation_time += 0.032  # 0.016'nın 2 katı, daha akıcı animasyon
            
            # Eğilme animasyonunu güncelle
            if self.is_moving or self.is_hunting:
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
                
                # Zıplama özelliğini kaldırdık - sabit Y pozisyonu
                self.y = self.base_y
            else:
                # Duruyorsa yumuşak şekilde dik pozisyona dön
                self.current_rotation += (0 - self.current_rotation) * self.rotation_speed * 2
                self.rotation = self.current_rotation
                self.y = self.base_y
            
            # Animasyon hızına göre kare değişimi - daha hızlı frame değişimi
            if current_time - self.last_frame_time >= self.animation_speed:
                if self.is_moving or self.is_hunting:
                    self.current_frame = (self.current_frame + 1) % self.frame_count
                else:
                    self.current_frame = 0
                self.last_frame_time = current_time
                
        except Exception as e:
            print(f"HATA: Kurt animasyon güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def wander(self):
        """Rastgele dolaş"""
        try:
            # Yeni max_wander_time belirle
            self.max_wander_time = random.randint(100, 300)
            self.wander_counter = 0
            
            # Gündüzse mağara etrafında dolaş
            if self.is_daytime:
                # Mağaranın etrafında rastgele bir konum belirle
                angle = random.uniform(0, 2 * math.pi)  # 0-360 derece arası rastgele açı
                distance = random.uniform(150, self.cave_radius)  # Mesafe artırıldı (100 yerine 150)
                
                # Polar koordinatları kartezyen koordinatlara dönüştür
                self.target_x = self.cave_x + distance * math.cos(angle)
                
                # Eğer hedef min_x'in solundaysa, sağ taraftaki bir hedef belirle
                if self.target_x < self.min_x:
                    self.target_x = self.cave_x + distance * math.cos(random.uniform(0, math.pi))  # Sadece sağ tarafta kal
                    
                self.state = "Mağara Etrafında (Gündüz)"
            else:
                # Geceyse köye yaklaş
                self.target_x = random.uniform(self.min_x - 500, self.min_x + 300)
                self.state = "Avlanıyor (Gece)"
            
            self.is_moving = True
            self.is_wandering = True
            
        except Exception as e:
            print(f"HATA: Kurt dolaşma hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def update_daytime(self, is_daytime):
        """Gündüz/gece durumunu güncelle"""
        self.is_daytime = is_daytime
        
        # Gündüz/gece değişimine göre davranışı güncelle
        if is_daytime:
            self.state = "Mağara Etrafında (Gündüz)"
            # Gündüzse mağara etrafına dön
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(100, self.cave_radius)
            self.target_x = self.cave_x + distance * math.cos(angle)
            
            # Eğer hedef min_x'in solundaysa, sağ taraftaki bir hedef belirle
            if self.target_x < self.min_x:
                self.target_x = self.cave_x + distance * math.cos(random.uniform(0, math.pi))
                
            self.is_moving = True
        else:
            self.state = "Avlanıyor (Gece)"
            # Geceyse köye yaklaş
            if random.random() < 0.7:  # %70 ihtimalle köye yaklaş
                self.target_x = self.min_x - random.randint(100, 400)
                self.is_moving = True
        
        # Yeni hedefe hareket etmeye başla
        self.wander()
    
    def set_game_controller(self, game_controller):
        """Oyun kontrolcüsünü ayarla"""
        self.game_controller = game_controller
        
    def update(self):
        """Kurt durumunu güncelle - hareket ve animasyon için"""
        try:
            # Kurdu hareket ettir
            self.move()
            
            # Animasyonu güncelle
            self.update_animation()
            
        except Exception as e:
            print(f"HATA: Kurt güncelleme hatası: {e}")
            import traceback
            traceback.print_exc() 