from dataclasses import dataclass
from typing import Optional
import random
import time
import math
from PyQt5.QtCore import QTimer

@dataclass
class Bird:
    """Kuş sınıfı - Ağaçların arasında uçan kuşlar"""
    bird_id: int  # Kuş kimlik numarası
    x: float = 0.0  # X koordinatı
    y: float = 0.0  # Y koordinatı
    width: int = 4  # Kuş genişliği
    height: int = 3  # Kuş yüksekliği
    bird_type: str = "kus"  # Kuş tipi: "kus" veya "karga"
    direction_x: int = 1  # 1 = sağa, -1 = sola (çizim için)
    state: str = "Uçuyor"  # Kuşun durumu
    
    # Kaynak ağaç ve hedef ağaç
    source_tree_x: float = 0.0  # Kaynak ağaç X koordinatı
    target_tree_x: float = 0.0  # Hedef ağaç X koordinatı
    target_tree_found: bool = False  # Hedef ağaç bulundu mu?
    
    # Uçuş özellikleri
    speed: float = 2.0  # Hızı - kuşlar hızlı uçar
    speed_variation: float = 0.0  # Hız değişimi - doğal uçuş için
    base_speed: float = 2.0  # Temel hız
    flight_time: float = 0.0  # Uçuş süresi
    max_flight_time: float = 15.0  # Maksimum uçuş süresi (saniye)
    altitude: float = 0.0  # Uçuş yüksekliği
    max_altitude: float = 100.0  # Maksimum uçuş yüksekliği (ağaçtan 100 piksel yukarısı)
    min_altitude: float = 40.0  # Minimum uçuş yüksekliği (ağaç tepesine yakın)
    target_altitude: float = 70.0  # Hedef uçuş yüksekliği
    altitude_change_speed: float = 0.5  # Yükseklik değişim hızı
    is_flying: bool = True  # Uçuyor mu?
    is_landing: bool = False  # İniyor mu?
    is_taking_off: bool = True  # Kalkıyor mu?
    should_remove: bool = False  # Kaldırılmalı mı?
    
    # Fiziksel uçuş parametreleri
    vertical_offset: float = 0.0  # Dikey salınım için ofset
    vertical_wave_speed: float = 1.0  # Dikey salınım hızı
    vertical_wave_amplitude: float = 8.0  # Dikey salınım genliği
    horizontal_wave_speed: float = 0.3  # Yatay salınım hızı
    horizontal_wave_amplitude: float = 2.0  # Yatay salınım genliği
    
    # Animasyon özellikleri
    current_frame: int = 0
    frame_count: int = 2
    animation_speed: float = 0.2
    last_frame_time: float = 0
    animation_time: float = 0.0
    
    # Kanat çırpma animasyonu
    wing_angle: float = 0.0  # Kanat açısı
    wing_speed: float = 0.3  # Kanat çırpma hızı
    max_wing_angle: float = 20.0  # Maksimum kanat açısı
    wing_direction: int = 1  # Kanat hareket yönü
    wing_cycle_position: float = 0.0  # Kanat döngüsü pozisyonu (0-1 arası)
    wing_cycle_speed: float = 8.0  # Kanat döngüsü hızı
    wing_ease_factor: float = 0.6  # Kanat hareketini yumuşatma faktörü (0-1 arası)
    
    # Game controller referansı
    game_controller = None
    
    def __post_init__(self):
        """Başlangıç değerlerini ayarla"""
        # Uçuş yüksekliğini belirle
        self.altitude = self.y
        self.target_altitude = random.uniform(self.min_altitude, self.max_altitude)
        self.last_frame_time = time.time()
        self.flight_time = 0.0
        
        # Rastgele uçuş süresi belirle (10-15 saniye)
        self.max_flight_time = random.uniform(10.0, 15.0)
        
        # Kaynak ağaç pozisyonunu kaydet
        self.source_tree_x = self.x
        
        # Kuş tipine göre farklı hız ve kanat çırpma özellikleri ayarla
        if self.bird_type == "kus":
            # Normal kuşlar hızlı ve hafif kanat çırpma
            self.base_speed = random.uniform(1.8, 2.5)
            self.wing_cycle_speed = random.uniform(7.0, 10.0)
            self.vertical_wave_amplitude = random.uniform(6.0, 10.0)
        else:  # karga
            # Kargalar daha yavaş ve ağır kanat çırpma
            self.base_speed = random.uniform(1.2, 1.8)
            self.wing_cycle_speed = random.uniform(5.0, 7.0)
            self.vertical_wave_amplitude = random.uniform(4.0, 7.0)
        
        # Başlangıç hızı
        self.speed = self.base_speed
    
    def __hash__(self):
        """Hash değerini döndür"""
        return hash((self.bird_id, self.bird_type))
    
    def __eq__(self, other):
        """Eşitlik kontrolü"""
        if not isinstance(other, Bird):
            return False
        return self.bird_id == other.bird_id and self.bird_type == other.bird_type
    
    def update(self, dt):
        """Kuşu güncelle"""
        try:
            # Uçuş süresini artır
            self.flight_time += dt
            
            # Uçuş süresi doldu mu?
            if self.flight_time >= self.max_flight_time and not self.is_landing and self.target_tree_found:
                # İnişe geç
                self.is_landing = True
                self.is_taking_off = False
                print(f"{self.bird_type.capitalize()} #{self.bird_id} inişe geçiyor!")
            
            # Hız varyasyonu ekle - kuşun dönemsel olarak hızlanıp yavaşlaması
            self.speed_variation = math.sin(self.flight_time * 0.8) * 0.4
            self.speed = self.base_speed + self.speed_variation
            
            # Yükseklik sınırlarını kontrol et - ağaç tepesi ile ağaç tepesi + 100px arasında tut
            if hasattr(self, 'game_controller') and self.game_controller:
                # Zemin ve ağaç bilgilerini al
                ground_y = self.game_controller.ground_y
                tree_height = 80  # Varsayılan ağaç yüksekliği
                tree_top_y = ground_y - tree_height  # Ağaç tepesi
                
                # Yükseklik sınırları
                min_y = tree_top_y  # En düşük uçuş seviyesi (ağaç tepesi)
                max_y = tree_top_y - 100  # En yüksek uçuş seviyesi (ağaç tepesinden 100px yukarı)
                
                # Hedef yüksekliği sınırla
                self.target_altitude = max(max_y, min(self.target_altitude, min_y))
            
            # Uçuş modu - kalkış, normal uçuş veya iniş
            if self.is_taking_off:
                # Kalkış - yükselme
                self.y -= self.altitude_change_speed * 2
                
                # Kanat çırpma hızını artır - kalkış sırasında hızlı kanat çırpma
                current_wing_cycle_speed = self.wing_cycle_speed * 1.5
                
                # Hedef yüksekliğe ulaşıldı mı?
                if self.y <= self.target_altitude:
                    self.is_taking_off = False
                    print(f"{self.bird_type.capitalize()} #{self.bird_id} hedef yüksekliğe ulaştı!")
                
                # Maksimum yüksekliği aşmama kontrolü
                if hasattr(self, 'game_controller') and self.game_controller:
                    ground_y = self.game_controller.ground_y
                    tree_height = 80
                    max_y = ground_y - tree_height - 100  # En fazla ağaç tepesinden 100px yukarı
                    
                    if self.y < max_y:
                        self.y = max_y
                        self.is_taking_off = False
                        print(f"{self.bird_type.capitalize()} #{self.bird_id} maksimum yüksekliğe ulaştı!")
                
            elif self.is_landing and self.target_tree_found:
                # İniş - alçalma
                distance_to_target = abs(self.x - self.target_tree_x)
                
                # Kanat çırpma hızını azalt - iniş sırasında yavaş kanat çırpma
                current_wing_cycle_speed = self.wing_cycle_speed * 0.7
                
                if distance_to_target < 20:
                    # Hedef ağaca yaklaştıkça hızla alçal
                    self.y += self.altitude_change_speed * 4
                    # Yavaşla
                    self.speed = max(0.5, self.speed * 0.95)
                
                # Hedef ağaca ve zemine ulaşıldı mı?
                tree_height = 80  # Ağaç yüksekliği
                ground_level = self.game_controller.ground_y - tree_height
                
                if abs(self.x - self.target_tree_x) < 10 and self.y >= ground_level - 20:
                    self.should_remove = True
                    print(f"{self.bird_type.capitalize()} #{self.bird_id} ağaca indi ve kayboldu!")
            else:
                # Normal uçuş - doğal dalgalanma
                current_wing_cycle_speed = self.wing_cycle_speed
                
                # Yukarı-aşağı salınım (ana sinüs dalgası)
                main_wave = math.sin(self.flight_time * self.vertical_wave_speed) * self.vertical_wave_amplitude
                
                # İkincil salınım (daha küçük, hızlı titreşim)
                secondary_wave = math.sin(self.flight_time * 3.0) * 2.0
                
                # Yükseklik değişimi - birincil ve ikincil dalgaları birleştir
                vertical_movement = main_wave + secondary_wave
                
                # Uygula - ancak sınırlar içinde kal
                if hasattr(self, 'game_controller') and self.game_controller:
                    # Zemin ve yükseklik sınırları
                    ground_y = self.game_controller.ground_y
                    tree_height = 80
                    min_y = ground_y - tree_height  # En düşük (ağaç tepesi)
                    max_y = min_y - 100  # En yüksek (ağaç tepesinden 100px yukarı)
                    
                    # Hedef yüksekliği sınırla
                    target_y = self.target_altitude + vertical_movement
                    
                    # Sınırlar içinde tut
                    if target_y < max_y:
                        target_y = max_y
                    elif target_y > min_y:
                        target_y = min_y
                    
                    # Yüksekliği güncelle
                    self.y = target_y
                else:
                    # Game controller yoksa normal hesaplama
                    self.y = self.target_altitude + vertical_movement
                
                # Belirli aralıklarla yeni bir hedef yükseklik belirle
                if random.random() < 0.005:  # %0.5 şans
                    if hasattr(self, 'game_controller') and self.game_controller:
                        # Zemin ve yükseklik sınırları
                        ground_y = self.game_controller.ground_y
                        tree_height = 80
                        min_y = ground_y - tree_height  # En düşük (ağaç tepesi)
                        max_y = min_y - 100  # En yüksek (ağaç tepesinden 100px yukarı)
                        
                        # Sınırlar içinde rastgele bir yükseklik seç
                        self.target_altitude = random.uniform(max_y, min_y)
                    else:
                        # Game controller yoksa normal sınırlar kullan
                        self.target_altitude = random.uniform(self.min_altitude, self.max_altitude)
                    
                    # Yeni hedef için yumuşak geçiş (ani değişim olmasın)
                    self.target_altitude = self.y * 0.7 + self.target_altitude * 0.3
            
            # X yönünde hareket (sağa veya sola)
            if self.target_tree_found:
                # Hedef ağaca doğru hareket et
                if self.x < self.target_tree_x:
                    self.direction_x = 1  # Sağa
                else:
                    self.direction_x = -1  # Sola
                
                # Hedefe olan mesafe
                dir_x = self.target_tree_x - self.x
                # Hafif yatay salınım ekle - ağaca giden yolda hafif dalgalanma
                side_movement = math.sin(self.flight_time * self.horizontal_wave_speed) * self.horizontal_wave_amplitude
                
                # Düz çizgiden sapmayan bir hareket (hedefe giden yol + hafif salınım)
                move_x = (dir_x * 0.01 + self.direction_x * self.speed) + side_movement * 0.3
                self.x += move_x
            else:
                # Rastgele yönlerde hareket et (daha doğal salınımlı uçuş)
                side_movement = math.sin(self.flight_time * self.horizontal_wave_speed) * self.horizontal_wave_amplitude
                self.x += self.speed * self.direction_x + side_movement
                
                # Rastgele yön değişimi
                if random.random() < 0.01:  # %1 şans
                    self.direction_x *= -1
            
            # Animasyonu güncelle
            self.update_animation(dt, current_wing_cycle_speed if 'current_wing_cycle_speed' in locals() else self.wing_cycle_speed)
            
            # Hedef ağaç bulunmadıysa ve uygun bir süre geçtiyse, hedef ara
            if not self.target_tree_found and self.flight_time > self.max_flight_time * 0.5:
                self.find_target_tree()
                
        except Exception as e:
            print(f"HATA: Kuş güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def update_animation(self, dt, wing_cycle_speed=None):
        """Animasyonu güncelle"""
        try:
            # Eğer belirtilmemişse, varsayılan kanat çırpma hızını kullan
            if wing_cycle_speed is None:
                wing_cycle_speed = self.wing_cycle_speed
                
            current_time = time.time()
            
            # Animasyon zamanını güncelle
            self.animation_time += dt
            
            # Kanat çırpma animasyonu - daha gerçekçi sinüs dalgası
            # 0-1 arasında değişen döngü pozisyonunu güncelle
            self.wing_cycle_position = (self.wing_cycle_position + dt * wing_cycle_speed) % 1.0
            
            # Kanat çırpma döngüsü - 0-360 derece arasında
            cycle_angle = self.wing_cycle_position * 2 * math.pi
            
            # Gerçekçi kanat hareketi için easing fonksiyonu
            # Kanatlar aşağıda daha fazla duraklar, yukarıda ise hızlı hareket eder
            if self.wing_cycle_position < 0.5:
                # Aşağı hareket (yavaş)
                ease_value = math.pow(self.wing_cycle_position * 2, self.wing_ease_factor)
                self.wing_angle = -(ease_value * self.max_wing_angle)
            else:
                # Yukarı hareket (hızlı)
                ease_value = math.pow((1.0 - self.wing_cycle_position) * 2, self.wing_ease_factor)
                self.wing_angle = ease_value * self.max_wing_angle
            
            # Kuş tipine göre kanat açısını ayarla
            if self.bird_type == "karga":
                # Karga için daha büyük açı
                self.wing_angle *= 1.2
            
            # Uçuş durumu ve hıza göre kanat açısını değiştir
            if self.is_taking_off:
                # Kalkış sırasında daha yüksek kanat açısı
                self.wing_angle *= 1.4
            elif self.is_landing and abs(self.x - self.target_tree_x) < 50:
                # İniş sırasında hafifçe artırılmış kanat açısı
                self.wing_angle *= 1.2
            
            # Kare değişimi
            if current_time - self.last_frame_time >= self.animation_speed:
                self.current_frame = (self.current_frame + 1) % self.frame_count
                self.last_frame_time = current_time
                
        except Exception as e:
            print(f"HATA: Kuş animasyon güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def find_target_tree(self):
        """Hedef ağaç bul"""
        try:
            if not self.game_controller or not hasattr(self.game_controller, 'trees'):
                return False
                
            # Kaynak ağaçtan en az 800 piksel uzaktaki bir ağaç bul
            min_distance = 800
            nearest_tree = None
            nearest_distance = float('inf')
            
            for tree in self.game_controller.trees:
                if not tree.is_visible:
                    continue
                    
                # Ağaç ile kaynak ağaç arasındaki mesafe
                distance_from_source = abs(tree.x - self.source_tree_x)
                
                # En az 800 piksel uzakta olmalı
                if distance_from_source >= min_distance:
                    # Kuşun şu anki konumuna olan mesafe
                    distance = abs(tree.x - self.x)
                    
                    # Şimdiye kadar bulunan en yakın ağaçtan daha yakınsa
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_tree = tree
            
            if nearest_tree:
                self.target_tree_x = nearest_tree.x
                self.target_tree_found = True
                print(f"{self.bird_type.capitalize()} #{self.bird_id} için hedef ağaç bulundu: x={self.target_tree_x}")
                return True
            else:
                # Uygun ağaç bulunamadıysa, rastgele bir yön seç ve uçmaya devam et
                print(f"{self.bird_type.capitalize()} #{self.bird_id} için uygun ağaç bulunamadı, uçuşa devam ediyor")
                # Uçuş süresini uzat
                self.max_flight_time += 5.0
                return False
                
        except Exception as e:
            print(f"HATA: Hedef ağaç bulma hatası: {e}")
            import traceback
            traceback.print_exc()
            return False 