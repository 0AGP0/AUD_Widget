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
    width: int = 25  # Köylü genişliği (40'tan 20'ye düşürüldü)
    height: int = 25  # Köylü yüksekliği (40'tan 20'ye düşürüldü)
    direction: int = 1  # 1 = sağa, -1 = sola
    direction_x: int = 1  # 1 = sağa, -1 = sola (çizim için)
    health: int = 100
    money: int = 0
    happiness: int = 100
    is_daytime: bool = True  # Gündüz/gece durumu
    state: str = "Dolaşıyor"  # Köylünün durumu
    
    # Köylü özellikleri
    charisma: int = 50
    education: int = 0
    age: int = 20
    
    # Karakteristik özellikler
    traits: list = None  # Köylünün karakteristik özellikleri
    desired_traits: list = None  # Eşinde aradığı özellikler
    
    # Ev sahibi olma durumu
    has_house: bool = False
    house_id: int = None
    
    # İlişki sistemi
    relationships: dict = None  # Diğer köylülerle olan ilişkileri
    mood: str = "Sakin"  # Günlük ruh hali
    
    # Hareket özellikleri
    speed: float = 0.35  # Hızı 5.0'dan 1.0'a düşürdük
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
    rotation_interval: float = 0.2  # Her 0.4 saniyede bir yön değiştir
    max_rotation: float = 10.0  # Maksimum eğilme açısı
    current_rotation: float = 0.0  # Mevcut eğilme açısı
    
    # Oduncu özellikleri
    trees_cut_today: int = 0
    max_trees_per_day: int = 2
    cutting_power: int = 1
    target_tree: Optional['Tree'] = None
    is_cutting: bool = False
    last_cut_time: float = 0.0
    
    # İnşaatçı özellikleri
    buildings_built: int = 0
    max_buildings_per_day: int = 1
    building_skill: int = 1
    target_building_site: Optional['BuildingSite'] = None
    is_building: bool = False
    building_progress: float = 0.0
    
    # Avcı özellikleri
    animals_hunted: int = 0
    max_hunts_per_day: int = 3
    hunting_skill: int = 1
    is_hunting: bool = False
    hunting_progress: float = 0.0
    
    # Çiftçi özellikleri
    crops_harvested: int = 0
    max_harvests_per_day: int = 2
    farming_skill: int = 1
    target_field: Optional['Field'] = None
    is_farming: bool = False
    farming_progress: float = 0.0
    
    # Gardiyan özellikleri
    patrol_count: int = 0
    max_patrols_per_day: int = 4
    guard_skill: int = 1
    is_patrolling: bool = False
    target_villager: Optional['Villager'] = None
    
    # Papaz özellikleri
    ceremonies_performed: int = 0
    max_ceremonies_per_day: int = 2
    faith_skill: int = 1
    is_praying: bool = False
    target_ceremony: str = ""
    
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
        if self.relationships is None:
            self.relationships = {}
        
        # Temel Y pozisyonunu ayarla
        self.base_y = self.y
        
        # Günlük ruh halini belirle
        self.set_daily_mood()
    
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
        
        # İnşaatçı için özel ayarlar
        elif profession == "İnşaatçı":
            self.buildings_built = 0  # Bugün inşa edilen bina sayısı
            self.max_buildings_per_day = 1  # Günlük inşa edebileceği maksimum bina
            self.is_building = False  # Şu an inşaat yapıyor mu?
            self.target_building_site = None  # Hedef inşaat alanı
            self.building_progress = 0.0  # İnşaat ilerleme durumu
        
        # Avcı için özel ayarlar
        elif profession == "Avcı":
            self.animals_hunted = 0  # Bugün avlanan hayvan sayısı
            self.max_hunts_per_day = 3  # Günlük avlanabileceği maksimum hayvan
            self.is_hunting = False  # Şu an avlanıyor mu?
            self.hunting_progress = 0.0  # Avlanma ilerleme durumu
        
        # Çiftçi için özel ayarlar
        elif profession == "Çiftçi":
            self.crops_harvested = 0  # Bugün hasat edilen ürün sayısı
            self.max_harvests_per_day = 2  # Günlük hasat edebileceği maksimum ürün
            self.is_farming = False  # Şu an çiftçilik yapıyor mu?
            self.target_field = None  # Hedef tarla
            self.farming_progress = 0.0  # Çiftçilik ilerleme durumu
        
        # Gardiyan için özel ayarlar
        elif profession == "Gardiyan":
            self.patrol_count = 0  # Bugün yapılan devriye sayısı
            self.max_patrols_per_day = 4  # Günlük yapabileceği maksimum devriye
            self.is_patrolling = False  # Şu an devriye geziyor mu?
            self.target_villager = None  # Hedef köylü (sorun çıkaran)
        
        # Papaz için özel ayarlar
        elif profession == "Papaz":
            self.ceremonies_performed = 0  # Bugün gerçekleştirilen tören sayısı
            self.max_ceremonies_per_day = 2  # Günlük gerçekleştirebileceği maksimum tören
            self.is_praying = False  # Şu an dua ediyor mu?
            self.target_ceremony = ""  # Hedef tören (evlilik, cenaze vb.)
    
    def update_stats(self) -> None:
        """Özellikleri güncelle"""
        # Bu metod daha sonra detaylandırılacak
        pass
    
    def initialize_behavior_tree(self):
        """Davranış ağacını başlat"""
        try:
            from src.models.ai.villager_behaviors import create_villager_behavior_tree
            self.behavior_tree = create_villager_behavior_tree(self)
            print(f"{self.name} için davranış ağacı oluşturuldu")
        except Exception as e:
            print(f"HATA: Davranış ağacı oluşturma hatası: {e}")
            self.behavior_tree = None
            import traceback
            traceback.print_exc()
    
    def update_behavior_tree(self):
        """Davranış ağacını güncelle"""
        try:
            if self.behavior_tree:
                dt = 0.016  # ~60 FPS için 1/60
                status = self.behavior_tree.run(self, dt)
                # Davranış ağacı durumunu güncelle, hareketleri yönetmeye devam et
                self.move()
                self.update_animation()
                
                # Özel durum kontrolleri
                if self.state == "Dolaşıyor" and not self.is_moving:
                    # Durması gereken bir durum değilse hareketi devam ettir
                    if random.random() < 0.02:  # %2 şans ile yeni hedef belirle
                        self.wander()
                    
        except Exception as e:
            print(f"HATA: {self.name} için davranış ağacı güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
            # Hata durumunda güvenli bir şekilde hareketi devam ettir
            self.move()
            self.update_animation()
    
    def update_animation(self) -> None:
        """Animasyon karesini güncelle"""
        try:
            current_time = time.time()
            
            # Animasyon zamanını güncelle
            self.animation_time += 0.016  # Yaklaşık 60 FPS
            
            # Eğilme animasyonunu güncelle
            if self.is_moving or self.is_cutting or self.is_building:
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
                if self.is_moving or self.is_cutting or self.is_building:
                    self.current_frame = (self.current_frame + 1) % self.frame_count
                else:
                    self.current_frame = 0
                self.last_frame_time = current_time
                
        except Exception as e:
            print(f"HATA: {self.name} animasyon güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
        
    def move(self):
        """Köylüyü hareket ettir"""
        try:
            # Gece kontrolü - gece olunca herkes eve döner
            if hasattr(self, 'game_controller') and not self.game_controller.is_daytime:
                self.go_home()
                return
                
            # Gündüz - mesleğe göre davranış
            if self.profession == "Oduncu":
                if self.trees_cut_today < self.max_trees_per_day:
                    self.handle_woodcutter()
                    self.state = "Ağaç Arıyor" if not self.is_cutting else "Ağaç Kesiyor"
                else:
                    self.wander()  # Limit dolmuşsa dolaş
                    self.state = "Dolaşıyor (Limit)"
            elif self.profession == "İnşaatçı":
                if self.buildings_built < self.max_buildings_per_day:
                    self.handle_builder()
                    self.state = "İnşaat Arıyor" if not self.is_building else "İnşaat Yapıyor"
                else:
                    self.wander()
                    self.state = "Dolaşıyor (Limit)"
            elif self.profession == "Avcı":
                if self.animals_hunted < self.max_hunts_per_day:
                    self.handle_hunter()
                    self.state = "Avlanıyor"
                else:
                    self.wander()
                    self.state = "Dolaşıyor (Limit)"
            elif self.profession == "Çiftçi":
                if self.crops_harvested < self.max_harvests_per_day:
                    self.handle_farmer()
                    self.state = "Çiftçilik Yapıyor"
                else:
                    self.wander()
                    self.state = "Dolaşıyor (Limit)"
            elif self.profession == "Gardiyan":
                if self.patrol_count < self.max_patrols_per_day:
                    self.handle_guard()
                    self.state = "Devriye Geziyor"
                else:
                    self.wander()
                    self.state = "Dolaşıyor (Limit)"
            elif self.profession == "Papaz":
                if self.ceremonies_performed < self.max_ceremonies_per_day:
                    self.handle_priest()
                    self.state = "Dua Ediyor"
                else:
                    self.wander()
                    self.state = "Dolaşıyor (Limit)"
            else:
                self.wander()  # Diğer meslekler dolaşır
                self.state = "Dolaşıyor"
                
            # Animasyonu güncelle
            self.update_animation()
                
        except Exception as e:
            print(f"HATA: {self.name} hareket hatası: {e}")
            
    def handle_builder(self):
        """İnşaatçı mantığı"""
        try:
            # Eğer inşaat yapıyorsa
            if self.is_building and self.target_building_site:
                # İnşaat alanı görünür değilse veya listeden kaldırılmışsa
                if not hasattr(self.target_building_site, 'is_active') or not self.target_building_site.is_active:
                    self.is_building = False
                    print(f"{self.name} inşaat ID: {self.target_building_site.id} tamamlandı, yeni inşaat alanı arıyor.")
                    self.target_building_site = None
                    # İnşaat tamamlandıktan sonra kısa bir süre bekle, sonra yeni inşaat alanı ara
                    QTimer.singleShot(2000, self.find_building_site)
                    # Bu arada biraz dolaş
                    self.wander()
                return
                
            # Yeni inşaat alanı ara
            self.find_building_site()
            
        except Exception as e:
            print(f"HATA: {self.name} inşaatçı mantığı hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def find_building_site(self):
        """İnşaat alanı bul veya oluştur"""
        try:
            if not hasattr(self, 'game_controller') or not self.game_controller:
                return
                
            # Eğer zaten inşaat yapıyorsa yeni inşaat alanı arama
            if self.is_building and self.target_building_site:
                return
                
            # Mevcut inşaat alanlarını kontrol et
            for site in self.game_controller.building_sites:
                if hasattr(site, 'is_active') and site.is_active and not site.builder:
                    # İnşaat alanına git
                    distance = abs(site.x - self.x)
                    if distance < 30:  # İnşaat mesafesindeyse
                        # İnşaata başla
                        if site.start_construction(self):
                            self.target_building_site = site
                            self.is_building = True
                            self.is_moving = False
                            print(f"{self.name} inşaata başladı. İnşaat ID: {site.id}")
                            return
                    else:  # İnşaat alanına doğru git
                        self.move_towards(site.x)
                        self.state = "İnşaat Alanına Gidiyor"
                        print(f"{self.name} inşaat alanına doğru ilerliyor. Mesafe: {distance:.1f}")
                        return
            
            # Mevcut inşaat alanı yoksa ve kale envanterinde yeterli odun varsa yeni inşaat alanı oluştur
            if hasattr(self.game_controller, 'castle') and self.game_controller.castle:
                castle = self.game_controller.castle
                wood_amount = castle.get_inventory().get('odun', 0)
                
                # Kale envanterinde en az 20 odun olmalı
                if wood_amount >= 20:
                    # Rastgele bir konum seç (kale civarında)
                    castle_x = self.game_controller.castle.x
                    min_x = castle_x + 200  # Kaleden en az 200 piksel uzakta
                    max_x = castle_x + 1000  # Kaleden en fazla 1000 piksel uzakta
                    x = random.uniform(min_x, max_x)
                    y = self.game_controller.ground_y
                    
                    # İnşaat alanı oluşturma şansı
                    if random.random() < 0.5:  # %50 şans (0.3'ten 0.5'e yükseltildi)
                        # İnşaat alanı oluştur
                        building_site = self.game_controller.create_building_site(x, y)
                        if building_site:
                            # İnşaat alanına git
                            self.move_towards(building_site.x)
                            self.state = "Yeni İnşaat Alanına Gidiyor"
                            print(f"{self.name} yeni inşaat alanına doğru ilerliyor. Mesafe: {abs(building_site.x - self.x):.1f}")
                            return
                else:
                    # Yeterli odun yoksa durumu güncelle
                    self.state = "Odun Bekleniyor"
                    # Dolaşmaya devam et
                    self.wander()
                    print(f"{self.name} inşaat için yeterli odun bekliyor. Mevcut odun: {wood_amount}/20")
                    return
            
            # İnşaat alanı bulunamadı veya oluşturulamadı, dolaş
            self.wander()
            self.state = "Dolaşıyor (İnşaat Bekliyor)"
            
        except Exception as e:
            print(f"HATA: {self.name} inşaat alanı bulma hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_hunter(self):
        """Avcı mantığı"""
        # Şimdilik sadece dolaş
        self.wander()
        
    def handle_farmer(self):
        """Çiftçi mantığı"""
        # Şimdilik sadece dolaş
        self.wander()
        
    def handle_guard(self):
        """Gardiyan mantığı"""
        # Şimdilik sadece dolaş
        self.wander()
        
    def handle_priest(self):
        """Papaz mantığı"""
        # Şimdilik sadece dolaş
        self.wander()
    
    def handle_woodcutter(self):
        """Oduncu mantığı"""
        # Günlük kesim limitini kontrol et
        if self.trees_cut_today >= self.max_trees_per_day:
            self.state = "Günlük Kesim Limiti Doldu"
            self.wander()
            return
            
        # Eğer ağaç kesiyorsa
        if self.is_cutting and self.target_tree:
            # Hareket etmeyi durdur
            self.is_moving = False
            # Durumu güncelle
            self.state = "Ağaç Kesiyor"
            
            # Ağaç görünür değilse veya listeden kaldırılmışsa
            if not self.target_tree.is_visible:
                self.is_cutting = False
                print(f"{self.name} ağaç ID: {self.target_tree.id} kesildi, yeni ağaç arıyor.")
                self.target_tree = None
                # Kesim sayısını güncelle
                print(f"{self.name} bugün {self.trees_cut_today}/{self.max_trees_per_day} ağaç kesti.")
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
        # Günlük kesim limitini kontrol et
        if self.trees_cut_today >= self.max_trees_per_day:
            self.state = "Günlük Kesim Limiti Doldu"
            self.wander()
            return
            
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
                    self.state = "Ağaç Kesiyor"
                    print(f"{self.name} ağaç kesmeye başladı. Ağaç ID: {closest_tree.id}")
            else:  # Ağaca doğru git
                self.move_towards(closest_tree.x)
                self.state = "Ağaca Gidiyor"
                print(f"{self.name} ağaca doğru ilerliyor. Mesafe: {min_distance:.1f}")
        else:
            self.wander()  # Ağaç yoksa dolaş
            self.state = "Ağaç Arıyor"
    
    def move_towards(self, target_x):
        """Hedefe doğru hareket et"""
        self.is_moving = True
        self.is_cutting = False
        
        if target_x > self.x:
            self.direction = 1
            self.direction_x = 1  # Sağa doğru
            self.x += self.speed
        else:
            self.direction = -1
            self.direction_x = -1  # Sola doğru
            self.x -= self.speed
    
    def wander(self):
        """Rastgele dolaş"""
        if not self.is_moving or abs(self.target_x - self.x) < 5:
            # Yeni hedef belirle
            new_x = self.x + random.choice([-1, 1]) * random.randint(100, 200)
            new_x = max(100, min(1820, new_x))  # Ekran sınırları
            self.target_x = new_x
            self.is_moving = True
            self.state = "Dolaşıyor"
        
        # Hedefe doğru hareket et
        self.move_towards(self.target_x)
    
    def go_home(self):
        """Eve veya kaleye dön"""
        try:
            # Ev sahibiyse evine dön
            if self.has_house and hasattr(self, 'game_controller') and self.game_controller:
                house = self.game_controller.find_house_by_id(self.house_id)
                if house:
                    target_x = house.get_entrance()[0]
                    # Eğer eve yakınsa durma
                    if abs(self.x - target_x) < 20:
                        self.is_moving = False
                        self.state = "Evde"
                        return
                    # Eve doğru hareket et
                    self.move_towards(target_x)
                    self.state = "Eve Dönüyor"
                    return
            
            # Ev sahibi değilse veya ev bulunamadıysa kaleye dön
            if hasattr(self, 'game_controller') and self.game_controller and hasattr(self.game_controller, 'castle'):
                castle = self.game_controller.castle
                if castle:
                    target_x = castle.x  # Direkt kalenin x konumuna git
                    # Eğer kaleye yakınsa durma
                    if abs(self.x - target_x) < 20:
                        self.is_moving = False
                        self.state = "Kalede"
                        return
                    # Kaleye doğru hareket et
                    self.move_towards(target_x)
                    self.state = "Kaleye Dönüyor"
                    return
            
            # Kale de bulunamadıysa dolaş
            self.wander()
            self.state = "Dolaşıyor"
            
        except Exception as e:
            print(f"HATA: {self.name} eve dönme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def set_game_controller(self, game_controller):
        """Oyun kontrolcüsünü ayarla"""
        self.game_controller = game_controller
        self.is_daytime = game_controller.is_daytime  # Gündüz/gece durumunu al

    def set_daily_mood(self):
        """Günlük ruh halini belirle"""
        moods = ["Mutlu", "Üzgün", "Sinirli", "Sakin"]
        self.mood = random.choice(moods)
        print(f"{self.name} bugün {self.mood} ruh halinde.")

    def get_relationship_with(self, other_villager):
        """Diğer köylü ile olan ilişki seviyesini döndür"""
        try:
            if other_villager.name in self.relationships:
                relationship_value = self.relationships[other_villager.name]
                
                if relationship_value <= -50:
                    return "Düşman"
                elif relationship_value <= -20:
                    return "Hoşlanmıyor"
                elif relationship_value <= 20:
                    return "Nötr"
                elif relationship_value <= 50:
                    return "İyi"
                else:
                    return "Dost"
            else:
                return "Nötr"
            
        except Exception as e:
            print(f"HATA: İlişki seviyesi hesaplama hatası: {e}")
            return "Nötr"

    def increase_relationship(self, other_villager):
        """Diğer köylü ile olan ilişkiyi artır"""
        try:
            if other_villager.name not in self.relationships:
                self.relationships[other_villager.name] = 0
            
            # İlişki değerini artır (maksimum 100)
            self.relationships[other_villager.name] = min(100, self.relationships[other_villager.name] + 10)
            
            # İlişki seviyesini yazdır
            print(f"{self.name} ile {other_villager.name} arasındaki ilişki arttı. Yeni seviye: {self.get_relationship_with(other_villager)}")
            
        except Exception as e:
            print(f"HATA: İlişki artırma hatası: {e}")

    def decrease_relationship(self, other_villager):
        """Diğer köylü ile olan ilişkiyi azalt"""
        try:
            if other_villager.name not in self.relationships:
                self.relationships[other_villager.name] = 0
            
            # İlişki değerini azalt (minimum -100)
            self.relationships[other_villager.name] = max(-100, self.relationships[other_villager.name] - 10)
            
            # İlişki seviyesini yazdır
            print(f"{self.name} ile {other_villager.name} arasındaki ilişki azaldı. Yeni seviye: {self.get_relationship_with(other_villager)}")
            
        except Exception as e:
            print(f"HATA: İlişki azaltma hatası: {e}")

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