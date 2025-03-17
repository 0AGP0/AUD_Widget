from dataclasses import dataclass
from typing import Optional
import random
import time
import math
from PyQt5.QtCore import QTimer

@dataclass
class Villager:
    """Köylü sınıfı"""
    name: str
    gender: str
    profession: str = ""  # Varsayılan değer olarak boş string
    appearance: int = 0
    x: float = 0.0
    y: float = 0.0
    direction: int = 1  # 1 = sağa, -1 = sola
    health: int = 100
    money: int = 0
    happiness: int = 100
    is_daytime: bool = True  # Gündüz/gece durumu
    
    # Köylü özellikleri
    charisma: int = 50
    education: int = 0
    age: int = 20
    
    # Karakteristik özellikler
    traits: list = None  # Köylünün karakteristik özellikleri
    desired_traits: list = None  # Eşinde aradığı özellikler
    
    # Hareket özellikleri
    speed: float = 1.0  # Hızı 5.0'dan 1.0'a düşürdük
    move_counter: int = 0
    max_move_time: int = 50
    is_wandering: bool = True
    target_x: float = 0.0
    target_y: float = 0.0
    
    # Animasyon özellikleri
    current_frame: int = 0
    frame_count: int = 4
    animation_speed: float = 0.2
    last_frame_time: float = 0
    is_moving: bool = False
    
    # Hareket ve zıplama özellikleri
    base_y: float = 0.0  # Temel Y pozisyonu
    jump_height: float = 2.0  # Zıplama yüksekliği
    jump_speed: float = 8.0  # Zıplama hızı
    animation_time: float = 0.0  # Animasyon zamanı
    
    # Eğilme özellikleri
    rotation: float = 0.0  # Eğilme açısı
    rotation_speed: float = 0.3  # Eğilme hızı
    rotation_direction: int = 1  # Eğilme yönü (1: sağa, -1: sola)
    last_rotation_time: float = 0.0  # Son eğilme zamanı
    rotation_interval: float = 0.4  # Her 0.4 saniyede bir yön değiştir
    max_rotation: float = 8.0  # Maksimum eğilme açısı
    current_rotation: float = 0.0  # Mevcut eğilme açısı
    
    # Oduncu özellikleri
    trees_cut_today: int = 0
    max_trees_per_day: int = 2
    cutting_power: int = 1
    target_tree: Optional['Tree'] = None
    is_cutting: bool = False
    last_cut_time: float = 0.0
    
    # Hareket değişkenleri
    max_speed: float = 1.5  # Maksimum hız
    acceleration: float = 0.1  # Hızlanma
    deceleration: float = 0.2  # Yavaşlama
    current_speed: float = 0  # Mevcut hız
    wander_counter: int = 0  # Dolaşma sayacı
    max_wander_time: int = 0  # Rastgele dolaşma süresi
    
    # Tüm karakteristik özellikler
    ALL_TRAITS = [
        "Tembel", "Çalışkan", "Karizmatik", "Sinirli", "Uykucu", "Yobaz", "Babacan",
        "Romantik", "Merhametli", "Sabırlı", "İnatçı", "Esprili", "Güvenilir", "Kurnaz",
        "Meraklı", "Dikkatli", "Hırslı", "Sabırsız", "İyimser", "Karamsar", "Pratik",
        "Mantıklı", "Duygusal", "Soğukkanlı", "Cömert", "Kıskanç", "Merhametsiz", "İlgisiz"
    ]
    
    def __post_init__(self):
        """Başlangıç değerlerini ayarla"""
        if self.traits is None:
            self.traits = []
        if self.desired_traits is None:
            self.desired_traits = []
    
    def __hash__(self):
        """Hash değerini döndür"""
        return hash((self.name, self.gender))
    
    def __eq__(self, other):
        """Eşitlik kontrolü"""
        if not isinstance(other, Villager):
            return False
        return self.name == other.name and self.gender == other.gender
    
    def set_profession(self, profession: str) -> None:
        """Meslek ata"""
        self.profession = profession
        print(f"{self.name} mesleği atandı: {profession}")
        
        # Oduncu için özel ayarlar
        if profession == "Oduncu":
            self.trees_cut_today = 0  # Bugün kesilen ağaç sayısı
            self.max_trees_per_day = 2  # Günlük kesebileceği maksimum ağaç
            self.is_cutting = False  # Şu an ağaç kesiyor mu?
            self.target_tree = None  # Hedef ağaç
            self.last_cut_time = 0  # Son kesme zamanı
    
    def update_stats(self) -> None:
        """Özellikleri güncelle"""
        # Bu metod daha sonra detaylandırılacak
        pass
    
    def update_animation(self) -> None:
        """Animasyon karesini güncelle"""
        try:
            current_time = time.time()
            
            # Animasyon zamanını güncelle
            self.animation_time += 0.016  # Yaklaşık 60 FPS
            
            # Eğilme animasyonunu güncelle
            if self.is_moving or self.is_cutting:
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
                
                # Zıplama animasyonu
                jump = math.sin(self.animation_time * 6.0) * 2.0  # Daha az zıplama
                self.y = self.base_y - jump
            else:
                # Duruyorsa yumuşak şekilde dik pozisyona dön
                self.current_rotation += (0 - self.current_rotation) * self.rotation_speed * 2
                self.rotation = self.current_rotation
                self.y = self.base_y
            
            # Animasyon hızına göre kare değişimi
            if current_time - self.last_frame_time >= self.animation_speed:
                if self.is_moving or self.is_cutting:
                    self.current_frame = (self.current_frame + 1) % self.frame_count
                else:
                    self.current_frame = 0
                self.last_frame_time = current_time
                
        except Exception as e:
            print(f"HATA: {self.name} animasyon güncelleme hatası: {e}")
        
    def move(self):
        """Köylüyü hareket ettir"""
        try:
            # Oduncu ise ve gündüz ise
            if self.profession == "Oduncu" and hasattr(self, 'game_controller'):
                if self.game_controller.is_daytime:
                    if self.trees_cut_today < self.max_trees_per_day:
                        self.handle_woodcutter()
                    else:
                        self.wander()  # Limit dolmuşsa dolaş
                else:
                    self.go_home()  # Gece olunca eve dön
            else:
                self.wander()  # Diğer meslekler dolaşır
                
        except Exception as e:
            print(f"HATA: {self.name} hareket hatası: {e}")
    
    def handle_woodcutter(self):
        """Oduncu mantığı"""
        # Eğer ağaç kesiyorsa
        if self.is_cutting and self.target_tree:
            # Ağaç görünür değilse veya listeden kaldırılmışsa
            if not self.target_tree.is_visible:
                self.is_cutting = False
                print(f"{self.name} ağaç ID: {self.target_tree.id} kesildi, yeni ağaç arıyor.")
                self.target_tree = None
                # Ağaç kesildikten sonra kısa bir süre bekle, sonra yeni ağaç ara
                QTimer.singleShot(2000, self.find_tree)
                # Bu arada biraz dolaş
                self.wander()
            else:
                current_time = time.time()
                if current_time - self.last_cut_time >= 1.0:  # Her saniye hasar ver
                    self.target_tree.take_damage()
                    self.last_cut_time = current_time
            return
            
        # Yeni ağaç ara
        self.find_tree()
    
    def find_tree(self):
        """En yakın uygun ağacı bul"""
        if not hasattr(self, 'game_controller') or not self.game_controller.trees:
            return
            
        # Eğer zaten ağaç kesiyorsa yeni ağaç arama
        if self.is_cutting and self.target_tree:
            return
            
        closest_tree = None
        min_distance = float('inf')
        
        # En yakın kesilebilir ağacı bul
        for tree in self.game_controller.trees:
            if tree.is_visible and not tree.is_being_cut:
                distance = abs(tree.x - self.x)
                if distance < min_distance:
                    min_distance = distance
                    closest_tree = tree
        
        # Ağaç bulunduysa
        if closest_tree:
            if min_distance < 30:  # Kesme mesafesindeyse
                if closest_tree.start_cutting(self):  # Kesmeye başla
                    self.target_tree = closest_tree
                    self.is_cutting = True
                    self.is_moving = False
                    self.last_cut_time = time.time()
                    print(f"{self.name} ağaç kesmeye başladı. Ağaç ID: {closest_tree.id}")
            else:  # Ağaca doğru git
                self.move_towards(closest_tree.x)
                print(f"{self.name} ağaca doğru ilerliyor. Mesafe: {min_distance:.1f}")
        else:
            self.wander()  # Ağaç yoksa dolaş
    
    def move_towards(self, target_x):
        """Hedefe doğru hareket et"""
        self.is_moving = True
        self.is_cutting = False
        
        if target_x > self.x:
            self.direction = 1
            self.x += self.speed
        else:
            self.direction = -1
            self.x -= self.speed
    
    def wander(self):
        """Rastgele dolaş"""
        if not self.is_moving or abs(self.target_x - self.x) < 5:
            # Yeni hedef belirle
            new_x = self.x + random.choice([-1, 1]) * random.randint(100, 200)
            new_x = max(100, min(1820, new_x))  # Ekran sınırları
            self.target_x = new_x
            self.is_moving = True
        
        # Hedefe doğru hareket et
        self.move_towards(self.target_x)
    
    def go_home(self):
        """Eve dön"""
        if self.is_cutting:
            if self.target_tree:
                self.target_tree.stop_cutting()
            self.is_cutting = False
            self.target_tree = None
        
        self.move_towards(100)  # Kale x koordinatı
    
    def set_game_controller(self, game_controller):
        """Oyun kontrolcüsünü ayarla"""
        self.game_controller = game_controller
        self.is_daytime = game_controller.is_daytime  # Gündüz/gece durumunu al

class TestVillager(Villager):
    def __init__(self, x, y):
        super().__init__(
            name="Test Köylüsü",
            gender="Erkek",
            profession="Test",
            appearance=0,
            x=x,
            y=y
        )  # Tüm gerekli parametreleri veriyorum
        self.health = 100
        self.money = 50
        self.happiness = 75
        self.charisma = 60
        self.education = 80
        self.traits = ["Test Özelliği"]

        # Diğer özellikler
        self.direction = 1  # 1: sağa, -1: sola
        self.speed = 1.0  # Sabit hız
        self.rotation = 0  # Eğilme açısı
        self.max_rotation = 10  # Maksimum eğilme açısı
        self.last_rotation_time = time.time()  # Son eğilme zamanı
        self.rotation_direction = 1  # 1: sağa eğil, -1: sola eğil
        self.rotation_interval = 0.3  # Her 0.3 saniyede bir yön değiştir
        
        print(f"Test köylüsü oluşturuldu: ({self.x}, {self.y})")
    
    def move(self):
        """Köylüyü hareket ettir ve eğilme animasyonunu güncelle"""
        try:
            # Yatay hareket
            self.x += self.speed * self.direction
            
            # Sınırlara gelince yön değiştir
            if self.x < 100 or self.x > 1820:
                self.direction *= -1
            
            # Eğilme animasyonunu güncelle
            current_time = time.time()
            time_diff = current_time - self.last_rotation_time
            
            # Her rotation_interval sürede bir yön değiştir
            if time_diff >= self.rotation_interval:
                self.rotation_direction *= -1
                self.last_rotation_time = current_time
            
            # Yumuşak geçiş için progress hesapla (0-1 arası)
            progress = time_diff / self.rotation_interval
            
            # Eğilme açısını hesapla
            target_rotation = self.max_rotation * self.rotation_direction
            self.rotation = target_rotation * progress
            
            # Debug bilgisi
            if time_diff >= 0.1:  # Her 0.1 saniyede bir yazdır
                print(f"Test köylüsü: x={self.x:.1f}, rotation={self.rotation:.1f}°")
            
        except Exception as e:
            print(f"Test köylüsü hareket hatası: {e}")
            import traceback
            traceback.print_exc() 