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
    width: int = 15  # Köylü genişliği (40'tan 20'ye düşürüldü)
    height: int = 15  # Köylü yüksekliği (40'tan 20'ye düşürüldü)
    direction: int = 1  # 1 = sağa, -1 = sola
    direction_x: int = 1  # 1 = sağa, -1 = sola (çizim için)
    health: int = 100
    money: int = 0  # Başlangıçta 0 altın (İnşaatçı sınıfı hariç)
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
    speed: float = 0.30  # Hızı 0.65'ten 1.8'e yükseltildi
    move_counter: int = 0
    max_move_time: int = 50
    is_wandering: bool = True
    target_x: float = 0.0
    target_y: float = 0.0
    
    # Animasyon özellikleri
    current_frame: int = 0
    frame_count: int = 4
    animation_speed: float = 0.1  # 0.2'den 0.1'e düşürdüm (daha hızlı animasyon)
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
    max_trees_per_day: int = 3  # Günlük kesebileceği maksimum ağaç
    is_cutting: bool = False  # Şu an ağaç kesiyor mu?
    target_tree = None  # Hedef ağaç
    cutting_start_time: float = 0.0  # Kesime başlama zamanı
    
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
    max_speed: float = 2.5  # Maksimum hız (1.5'ten 2.5'e yükseltildi)
    acceleration: float = 0.15  # Hızlanma (0.1'den 0.15'e yükseltildi)
    deceleration: float = 0.25  # Yavaşlama (0.2'den 0.25'e yükseltildi)
    current_speed: float = 0  # Mevcut hız
    wander_counter: int = 0  # Dolaşma sayacı
    max_wander_time: int = 0  # Rastgele dolaşma süresi
    
    # Ticaret özellikleri
    has_market_stall: bool = False  # Şu anda bir tezgahı var mı?
    current_stall = None  # Şu anki tezgah
    is_selling: bool = False  # Satış yapıyor mu?
    is_buying: bool = False  # Alış yapıyor mu?
    target_buyer = None  # Hedef alıcı
    target_seller = None  # Hedef satıcı
    target_product: str = ""  # Hedef ürün
    last_trade_time: float = 0.0  # Son ticaret zamanı
    trade_cooldown: float = 5.0  # Ticaret bekleme süresi
    market_visit_cooldown: float = 0  # Pazar ziyareti bekleme süresi
    
    # Tüm karakteristik özellikler
    ALL_TRAITS = [
        "Tembel", "Çalışkan", "Karizmatik", "Sinirli", "Uykucu", "Yobaz", "Babacan",
        "Romantik", "Merhametli", "Sabırlı", "İnatçı", "Esprili", "Güvenilir", "Kurnaz",
        "Meraklı", "Dikkatli", "Hırslı", "Sabırsız", "İyimser", "Karamsar", "Pratik",
        "Mantıklı", "Duygusal", "Soğukkanlı", "Cömert", "Kıskanç", "Merhametsiz", "İlgisiz"
    ]
    
    def __post_init__(self):
        """İnit sonrası ayarlamalar"""
        # Davranış düğümü ve durumu için özellikler
        self.behavior_tree = None
        
        # Referanslar
        self.game_controller = None
        
        # Ek özellikler
        self.is_chatting = False
        self.chat_partner = None
        
        # Son konuşma metinleri
        self.last_speaker = None  # Son konuşan kişi
        self.last_message_was_question = False  # Son mesaj soru mu?
        self.conversation_counter = 0  # Toplam konuşma mesajı sayısı
        self.last_chat_message_time = 0  # Son mesaj zamanı
        
        # Diyalog baloncuğu için
        self.active_bubble = False  # Aktif konuşma baloncuğu var mı?
        self.bubble_start_time = 0  # Baloncuk başlangıç zamanı
        self.current_bubble = None  # Mevcut baloncuk referansı
        
        # Animasyon için
        self.has_hop = True  # Zıplama animasyonu olsun mu?
        self.base_y = self.y  # Temel y koordinatı
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # 50ms'de bir animasyon güncelle (20 FPS)
        
        # Meslekler
        self.available_professions = [
            "Oduncu", "Çiftçi", "Avcı", "Balıkçı", "Demirci", 
            "Tüccar", "Gardiyan", "Papaz", "İnşaatçı"
        ]
                
        # Eğer profession atanmamışsa, rastgele bir meslek seç
        if not self.profession:
            self.profession = random.choice(self.available_professions)
        
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
        
        # İnşaatçı için 50 altın başlangıç parası, diğerleri için 0
        if profession == "İnşaatçı":
            self.money = 0  # Başlangıç parası
            # İnşaatçı özellikleri
            self.buildings_built = 0
            self.max_buildings_per_day = 1
            self.building_skill = 1
            self.target_building_site = None
            self.is_building = False
            self.building_progress = 0.0
            print(f"{self.name} inşaatçı olarak çalışmaya başladı. Günlük inşaat limiti: {self.max_buildings_per_day}")
        else:
            self.money = 0
            print(f"{self.name} başlangıç parası: 0 altın")
        
        # Oduncu için özel ayarlar
        if profession == "Oduncu":
            self.trees_cut_today = 0
            self.max_trees_per_day = 3
            self.is_cutting = False
            self.target_tree = None
            self.cutting_start_time = 0.0
            print(f"{self.name} oduncu olarak çalışmaya başladı.")
        
        # İnşaatçı için özel ayarlar - silindi
        
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
            
            # Animasyon zamanını güncelle - daha hızlı güncelleme
            self.animation_time += 0.032  # 0.016'nın 2 katı (daha akıcı animasyon)
            
            # Eğilme animasyonunu güncelle
            if self.is_moving or self.is_building or self.is_cutting:
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
                if self.is_moving or self.is_building or self.is_cutting:
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
                
            # Satış/alış yapıyorsa hareketi durdur
            if self.is_selling or self.is_buying:
                self.is_moving = False
                return
                
            # Gündüz - mesleğe göre davranış
            if self.profession == "Oduncu":
                # Günlük kesim limitini kontrol et
                if self.trees_cut_today < self.max_trees_per_day:
                    # Ağaç kesmeye öncelik ver
                    self.handle_woodcutter()
                    self.state = "Ağaç Arıyor" if not self.is_cutting else "Ağaç Kesiyor"
                else:
                    # Günlük kesim limiti dolduysa dolaş
                    self.wander()
                    self.state = "Günlük Ağaç Limiti Doldu"
            elif self.profession == "İnşaatçı":
                # İnşaatçı için davranış ağacı kontrolü
                if hasattr(self, 'game_controller') and self.game_controller:
                    # Davranış ağacındaki fonksiyonu kullanmak için is_building kontrolü yap
                    if self.is_building:
                        # Zaten inşaat yapıyor, durumunu koru
                        pass
                    elif self.buildings_built < self.max_buildings_per_day:
                        # Kullanılabilir odun kontrolü
                        castle = self.game_controller.castle
                        if castle:
                            wood_amount = castle.get_inventory().get('odun', 0)
                            if wood_amount >= 30:
                                # Yeterli odun var, inşaat kontrol fonksiyonunu çağır
                                success = self.game_controller.check_for_auto_building()
                                if success:
                                    self.state = "İnşaat Yapıyor"
                                    return
                                
                    # İnşaat yapmıyorsa dolaş
                    self.wander()
                    if self.buildings_built >= self.max_buildings_per_day:
                        self.state = "Günlük İnşaat Limiti Doldu"
                    else:
                        self.state = "İnşaat Malzemesi Bekliyor"
                else:
                    # Game controller yoksa sadece dolaş
                    self.wander()
                    self.state = "Dolaşıyor"
            elif self.profession == "Avcı":
                if self.animals_hunted < self.max_hunts_per_day:
                    self.handle_hunter()
                    self.state = "Avlanıyor"
                else:
                    self.wander()
                    self.state = "Yoruldu Dolaşıyor"
            elif self.profession == "Çiftçi":
                if self.crops_harvested < self.max_harvests_per_day:
                    self.handle_farmer()
                    self.state = "Çiftçilik Yapıyor"
                else:
                    self.wander()
                    self.state = "Yoruldu Dolaşıyor"
            elif self.profession == "Gardiyan":
                if self.patrol_count < self.max_patrols_per_day:
                    self.handle_guard()
                    self.state = "Devriye Geziyor"
                else:
                    self.wander()
                    self.state = "Yoruldu Dolaşıyor"
            elif self.profession == "Papaz":
                if self.ceremonies_performed < self.max_ceremonies_per_day:
                    self.handle_priest()
                    self.state = "Dua Ediyor"
                else:
                    self.wander()
                    self.state = "Yoruldu Dolaşıyor"
            else:
                # Ev satın almak için pazara git veya dolaş
                if self.money >= 100 and not self.has_house:  # Ev alacak parası varsa
                    self.handle_house_buying()
                else:
                    self.wander()  # Diğer meslekler dolaşır
                    self.state = "Dolaşıyor"
                
            # Animasyonu güncelle
            self.update_animation()
                
        except Exception as e:
            print(f"HATA: {self.name} hareket hatası: {e}")
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

    def move_towards(self, target_x):
        """Hedefe doğru hareket et"""
        self.is_moving = True
        self.is_cutting = False
        
        # Her frame'de daha fazla hareket
        move_step = self.speed * 1.5  # Hareket adımını 1.5 kat artır
        
        if target_x > self.x:
            self.direction = 1
            self.direction_x = 1  # Sağa doğru
            self.x += move_step
        else:
            self.direction = -1
            self.direction_x = -1  # Sola doğru
            self.x -= move_step
    
    def wander(self):
        """Rastgele dolaş"""
        if not self.is_moving or abs(self.target_x - self.x) < 5:
            # Yeni hedef belirle - daha geniş mesafe
            new_x = self.x + random.choice([-1, 1]) * random.randint(150, 300)  # 100-200 yerine 150-300
            new_x = max(100, min(1820, new_x))  # Ekran sınırları
            self.target_x = new_x
            self.is_moving = True
            self.state = "Dolaşıyor"
        
        # Hedefe doğru hareket et
        self.move_towards(self.target_x)
    
    def handle_house_buying(self):
        """Ev satın alma davranışı"""
        try:
            current_time = time.time()
            
            # Bekleme süresi dolduysa
            if current_time - self.market_visit_cooldown < 10.0 and self.market_visit_cooldown > 0:
                self.wander()  # Biraz dolaş
                self.state = "Pazara Gitmek için Bekliyor"
                return
                
            # Oyun kontrolcüsü var mı kontrol et
            if not hasattr(self, 'game_controller') or not self.game_controller:
                self.wander()
                return
                
            # Zaten ev sahibiyse dolaş
            if self.has_house:
                self.wander()
                self.state = "Dolaşıyor"
                return
                
            # Evi satın almak için 100 altın gerekiyor
            if self.money < 100:
                self.wander()
                self.state = "Ev Almak İçin Para Biriktiriyor"
                return
            
            # Satılık ev var mı kontrol et
            houses_for_sale = [h for h in self.game_controller.houses if hasattr(h, 'for_sale') and h.for_sale]
            
            if not houses_for_sale:
                self.wander()
                self.state = "Satılık Ev Arıyor"
                return
            
            # Kaleye doğru git (evi almak için krala yaklaş)
            if hasattr(self.game_controller, 'castle') and self.game_controller.castle:
                castle = self.game_controller.castle
                distance_to_castle = abs(castle.x - self.x)
                
                if distance_to_castle < 30:  # Kaleye ulaştıysa
                    # En yakın satılık evi bul
                    closest_house = min(houses_for_sale, key=lambda h: abs(h.x - self.x))
                    
                    # Evi satın al
                    self.money -= 100  # 100 altın öde
                    closest_house.set_owner(self.name)
                    self.has_house = True
                    self.house_id = closest_house.id
                    
                    # Ödemeyi inşaatçıya yap
                    if hasattr(closest_house, 'builder') and closest_house.builder:
                        closest_house.builder.money += 100
                        print(f"{self.name}, ev için 100 altını inşaatçı {closest_house.builder.name}'ye ödedi!")
                    
                    self.state = "Ev Satın Aldı"
                    print(f"{self.name} kraldan evi satın aldı! Kalan para: {self.money} altın")
                    
                    # Biraz bekle
                    self.market_visit_cooldown = current_time
                else:
                    # Kaleye git
                    self.move_towards(castle.x)
                    self.state = "Ev Almak İçin Kaleye Gidiyor"
            else:
                # Kale yoksa dolaş
                self.wander()
                self.state = "Kaleyi Arıyor"
                
        except Exception as e:
            print(f"HATA: {self.name} ev satın alma davranışı hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def create_house_for_self(self):
        """Kendine ev oluştur"""
        try:
            if not hasattr(self, 'game_controller') or not self.game_controller:
                return
                
            from src.models.house import House
            
            # Ev için rastgele bir konum seç (kale civarında)
            if hasattr(self.game_controller, 'castle') and self.game_controller.castle:
                castle_x = self.game_controller.castle.x
                min_x = castle_x + 200  # Kaleden en az 200 piksel uzakta
                max_x = castle_x + 1000  # Kaleden en fazla 1000 piksel uzakta
                x = random.uniform(min_x, max_x)
                y = self.game_controller.ground_y
                
                # Rastgele ev tipini seç
                house_types = ["ev1", "ev2", "ev3"]
                house_type = random.choice(house_types)
                
                # Ev oluştur
                house = House(x, y, 80, 100, house_type)
                house.set_owner(self.name)
                
                # Oyuna ekle
                self.game_controller.houses.append(house)
                
                # Köylünün ev bilgilerini güncelle
                self.has_house = True
                self.house_id = house.id
                
                print(f"{self.name} kendine bir ev satın aldı! Ev ID: {house.id}, Tip: {house_type}")
            else:
                print(f"UYARI: {self.name} için ev oluşturulamadı, kale bulunamadı!")
                
        except Exception as e:
            print(f"HATA: {self.name} ev oluşturma hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def release_market_stall(self):
        """Pazar tezgahını serbest bırak"""
        if self.has_market_stall and self.current_stall:
            self.current_stall.release_stall()
            self.has_market_stall = False
            self.current_stall = None
            self.is_selling = False
            print(f"{self.name} pazar tezgahını serbest bıraktı.")

    def handle_woodcutter(self):
        """Oduncu davranışı"""
        try:
            # Günlük limit kontrolü
            if self.trees_cut_today >= self.max_trees_per_day:
                self.state = "Günlük Ağaç Limiti Doldu"
                self.wander()
                return
            
            # Eğer kesim yapılıyorsa kontrol et
            if self.is_cutting and self.target_tree:
                # Ağaç görünür mü?
                if not self.target_tree.is_visible:
                    # Ağaç kesilmiş, yeni ağaç ara
                    self.is_cutting = False
                    self.target_tree = None
                    return
                
                # Kesim süresi kontrolü
                current_time = time.time()
                elapsed_time = current_time - self.cutting_start_time
                
                # Kesim 10 saniye sürüyor
                if elapsed_time >= 10.0:
                    # Kesim tamamlandı
                    self.is_cutting = False
                    
                    # Ağacı kaldır
                    self.target_tree.is_visible = False
                    
                    # Odun stoğuna ekle
                    if hasattr(self.game_controller, 'market') and self.game_controller.market:
                        market = self.game_controller.market
                        market.add_wood(10)  # Her ağaçtan 10 odun
                        print(f"{self.name} ağacı kesti! Pazara 10 odun eklendi. Toplam stok: {market.wood_stock}")
                    
                    # Kale envanterine de odun ekle
                    if hasattr(self.game_controller, 'castle') and self.game_controller.castle:
                        self.game_controller.castle.add_to_inventory("odun", 10)  # Her ağaçtan 10 odun
                        print(f"{self.name} ağacı kesti! Kale envanterine 10 odun eklendi.")
                        # Kontrol paneli güncellemesi için
                        if hasattr(self.game_controller, 'control_panel') and self.game_controller.control_panel:
                            self.game_controller.control_panel.update_castle_inventory()
                    
                    # Kesilen ağaç sayısını artır
                    self.trees_cut_today += 1
                    print(f"{self.name} bugün toplam {self.trees_cut_today}/{self.max_trees_per_day} ağaç kesti.")
                    
                    # Hedefi temizle
                    self.target_tree = None
                    
                    # Günlük limit kontrolü
                    if self.trees_cut_today >= self.max_trees_per_day:
                        self.state = "Günlük Ağaç Limiti Doldu"
                        print(f"{self.name} günlük ağaç kesim limitine ulaştı.")
                    
                    return
                
                # Kesim devam ediyor
                self.state = "Ağaç Kesiyor"
                self.is_moving = False
                
                # İlerleme yüzdesini hesapla
                progress = int((elapsed_time / 10.0) * 100)
                self.target_tree.cut_progress = progress
                
                return
            
            # Eğer kesim yapılmıyorsa ağaç ara
            # En yakın ağacı bul
            closest_tree = self.find_closest_tree()
            
            if closest_tree:
                # Ağaca git ve kesmeye başla
                distance = abs(closest_tree.x - self.x)
                
                if distance < 45:  # Kesme mesafesi
                    # Kesmeye başla
                    self.state = "Ağaç Kesiyor"
                    self.target_tree = closest_tree
                    self.is_cutting = True
                    self.is_moving = False
                    self.cutting_start_time = time.time()
                    
                    # Ağacı kesme moduna geçir
                    closest_tree.is_being_cut = True
                    
                    print(f"{self.name} ağaç kesmeye başladı. ID: {closest_tree.id}")
                else:
                    # Ağaca yaklaş
                    self.state = "Ağaca Yaklaşıyor"
                    self.move_towards(closest_tree.x)
            else:
                # Ağaç bulunamadı, dolaş
                self.state = "Ağaç Arıyor"
                self.wander()
        
        except Exception as e:
            print(f"HATA (Oduncu): {self.name} - {e}")
            import traceback
            traceback.print_exc()
            self.wander()

    def find_closest_tree(self):
        """En yakın ağacı bul"""
        try:
            if not hasattr(self.game_controller, 'trees'):
                return None
            
            # Kesilebilir ağaçları bul (görünür ve kesilmemiş)
            available_trees = [tree for tree in self.game_controller.trees 
                              if tree.is_visible and not hasattr(tree, 'is_being_cut') or not tree.is_being_cut]
            
            if not available_trees:
                return None
            
            # En yakın ağacı bul
            closest_tree = None
            min_distance = float('inf')
            
            for tree in available_trees:
                distance = abs(tree.x - self.x)
                if distance < min_distance:
                    min_distance = distance
                    closest_tree = tree
            
            return closest_tree
        
        except Exception as e:
            print(f"HATA (Ağaç Bulma): {e}")
            import traceback
            traceback.print_exc()
            return None 