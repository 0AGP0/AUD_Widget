from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QRect, QTimer, QPoint
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow
from PyQt5.QtGui import QScreen, QColor
import random
import time
import os
import math
from PyQt5.QtCore import QObject, QTimer, QThread, QDateTime
from PyQt5.QtWidgets import QDesktopWidget
from ..models.tree import Tree
from ..models.villager import Villager
from ..models.building import Building
from ..models.building_site import BuildingSite
from ..models.house import House
from ..models.wolf import Wolf
from ..models.bird import Bird
from ..models.market import Market, MarketStall
from ..models.ai.dialogue.dialogue_manager import DialogueManager
from ..utils.constants import MALE_NAMES, FEMALE_NAMES, PROFESSIONS

class GameController(QObject):
    """Oyun kontrolcü sınıfı"""
    villagers_updated = pyqtSignal(list)  # Köylü listesi güncellendiğinde sinyal gönder
    day_night_changed = pyqtSignal(bool)  # Gece/gündüz değiştiğinde sinyal gönder (True = Gündüz)
    chat_message = pyqtSignal(object, str)  # Köylü ve mesaj sinyali
    trade_completed = pyqtSignal(object, object, str, int, int)  # Ticaret tamamlandığında sinyal gönder
    
    DAY_DURATION = 300  # 5 dakika (saniye cinsinden)
    NIGHT_DURATION = 180  # 3 dakika (saniye cinsinden)
    
    def __init__(self, parent=None):
        """Game Controller sınıfını başlat"""
        super().__init__(parent)
        
        print("GameController başlatılıyor...")
        
        # Ekran boyutları
        self.width = 1920  # Varsayılan genişlik
        self.height = 1080  # Varsayılan yükseklik
        self.ground_y = self.height - 100  # Zemin seviyesi
        
        # Oyun durumu
        self.is_running = False
        self.is_daytime = True
        self.day_time = 0
        self.remaining_time = self.DAY_DURATION
        self.day_night_timer = QTimer()
        self.day_night_timer.timeout.connect(self.update_remaining_time)
        
        # Oyun nesneleri
        self.villagers = []
        self.trees = []
        self.houses = []
        self.building_sites = []
        self.castle = None
        self.cave = None
        self.market = None
        self.wolves = []
        self.birds = []
        self.structures = []  # Yapılar listesi eklendi
        
        # Kurt oluşturma parametreleri
        self.last_wolf_spawn = 0
        self.wolf_spawn_interval = 5  # 5 saniye
        
        # Oyun döngüsü zamanlayıcısı
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game_loop)
        
        # Kontrol paneli referansı
        self.control_panel = None
        
        # Oyun kontrolcüsü için değişkenler
        self.ground_height = 25  # Zemin yüksekliği
        self.day_count = 1      # Gün sayısı
        
        # Zamanı izleyen timer
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_remaining_time)
        self.time_timer.start(1000)  # Her saniye güncelle
        
        # Kaynaklar
        self.food = 0
        self.wood = 0
        self.stone = 0
        self.gold = 100
        
        # Timer'lar
        self.last_resource_update = time.time()
        self.last_periodic_update = time.time()
        self.last_bird_spawn = time.time()  # Son kuş oluşturma zamanı
        
        # Oyun kontrolcüsü için değişkenler
        self.ground_y = self.ground_y
        self.ground_height = self.ground_height
        
        # Diyalog yöneticisini başlat
        self.dialogue_manager = DialogueManager()
        self.dialogue_manager.set_game_controller(self)
        print("Diyalog yöneticisi başlatıldı")
        
        # Ekran boyutlarını al ve zemini ayarla
        desktop = QDesktopWidget()
        max_height = 0
        
        # Tüm ekranların yüksekliklerini kontrol et ve en büyüğünü bul
        for i in range(desktop.screenCount()):
            screen_geo = desktop.screenGeometry(i)
            if screen_geo.height() > max_height:
                max_height = screen_geo.height()
        
        print(f"Ekran yüksekliği: {max_height}")
        
        # Zeminin y pozisyonunu ekranın en altına ayarla
        self.ground_y = max_height - self.ground_height
        
        print("GameController başlatıldı")
        # NOT: setup_game() ve window.show() çağrıları kaldırıldı
        
        # Rastgelelik için seed ayarla
        random.seed(time.time())
        
        # Bird spawn settings
        self.bird_spawn_interval = 15.0  # Saniye
        self.bird_spawn_chance = 0.3     # %30 şans
        self.max_birds = 5              # Maksimum aynı anda kuş sayısı
        
        # Oyunu başlat
        self.setup_game()
    
    def setup_game(self):
        """Oyunu başlat ve gerekli nesneleri oluştur"""
        try:
            print("Oyun kuruluyor...")
            
            # Gece/gündüz döngüsünü başlat
            print("Gece/gündüz döngüsü başlatılıyor...")
            self.start_day_night_cycle()
            
            # Diyalog yöneticisini villager_behaviors'a bağla
            from src.models.ai.villager_behaviors import set_dialogue_manager
            set_dialogue_manager(self.dialogue_manager)
            print("Diyalog yöneticisi davranış sistemine bağlandı.")
            
            # Zemin seviyesini ayarla
            print("Zemin seviyesi ayarlanıyor...")
            if hasattr(self, 'window') and hasattr(self.window, 'ground_widget'):
                self.ground_y = self.window.ground_widget.height() - self.window.ground_widget.ground_height
                print(f"Zemin seviyesi: {self.ground_y}")
            else:
                self.ground_y = 400  # Varsayılan değer
                print(f"Varsayılan zemin seviyesi: {self.ground_y}")
            
            # Binaları oluştur (şimdilik sadece kale)
            print("Kale oluşturuluyor...")
            self.castle = Building(x=0, y=self.ground_y, width=150, height=150, building_type="castle")
            print("Kale oluşturuldu")
            
            # Kale envanterine başlangıç odun ekle - 0 odunla başlasın
            self.castle.add_to_inventory("odun", 0)
            print("Kale envanterine 0 odun eklendi")
            
            # Pazar alanını oluştur
            print("Pazar alanı oluşturuluyor...")
            self.create_market()
            print("Pazar alanı oluşturuldu")
            
            # Mağarayı oluştur
            print("Mağara oluşturuluyor...")
            self.create_cave()
            print("Mağara oluşturuldu")
            
            # Ağaçları oluştur
            print("Ağaçlar oluşturuluyor...")
            self.create_trees()
            print(f"{len(self.trees)} ağaç oluşturuldu")
            
            # Köylüleri oluştur
            print("Köylüler oluşturuluyor...")
            self.create_initial_villagers()
            print(f"{len(self.villagers)} köylü oluşturuldu")
            
            # Kurtları oluştur
            print("Kurtlar oluşturuluyor...")
            self.create_wolves()
            
            # Kontrol panelini güncelle
            print("Kontrol paneli güncelleniyor...")
            if hasattr(self, 'control_panel'):
                print("Kontrol paneli bulundu, köylü listesi güncelleniyor...")
                self.villagers_updated.emit(self.villagers)
            else:
                print("Kontrol paneli bulunamadı!")
            
            # Ağaç sinyallerini bağla
            for tree in self.trees:
                tree.tree_removed.connect(self.on_tree_removed)
            
            # Oyun güncelleme zamanlayıcısını başlat
            print("Oyun güncelleme zamanlayıcısı başlatılıyor...")
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_game)
            self.timer.start(8)  # ~120 FPS (16ms -> 8ms)
            
            print("Oyun kurulumu tamamlandı")
            
        except Exception as e:
            print(f"HATA: Oyun kurulum hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def create_trees(self):
        """Ağaçları oluştur"""
        try:
            # Ağaçları temizle
            self.trees = []
            
            # Tüm ağaçlar için sabit boyutlar
            tree_width = 50 # 80'den 50'ye düşürüldü
            tree_height = 60  # 120'den 80'e düşürüldü
            
            # Kale pozisyonu (varsayılan olarak x=0)
            castle_x = 0
            
            # Ağaçların başlangıç pozisyonu (kaleden 200 piksel sağda)
            start_x = castle_x + 200
            
            # Tüm ekranların toplam genişliğini kullan
            total_width = 0
            desktop = QDesktopWidget()
            for i in range(desktop.screenCount()):
                screen_geo = desktop.screenGeometry(i)
                total_width += screen_geo.width()
            
            # Ekranı bölgelere ayır ve her bölgede farklı yoğunlukta ağaç yerleştir
            # Sağa doğru gittikçe bölgelerdeki ağaç sayısı artsın
            regions = 5  # 5 farklı bölge
            region_width = (total_width - start_x) / regions
            
            total_trees = 0
            
            # Ağaçlar arası minimum mesafe
            min_distance = 15
            
            # Her bölge için ağaç oluştur
            for region in range(regions):
                # Bölgenin başlangıç ve bitiş x koordinatları
                region_start = start_x + (region * region_width)
                region_end = region_start + region_width
                
                # Bölgedeki ağaç sayısı - sağa doğru gittikçe artsın
                # İlk bölgede az, son bölgede çok ağaç olsun
                base_tree_count = 7  # İlk bölgedeki minimum ağaç sayısı
                region_tree_count = base_tree_count + (region * 5)  # Her bölgede 5 ağaç daha fazla
                
                # Rastgele bir faktör ekle (±20%)
                random_factor = random.uniform(0.8, 1.2)
                region_tree_count = int(region_tree_count * random_factor)
                
                print(f"Bölge {region+1}: {region_start}-{region_end}, {region_tree_count} ağaç")
                
                # Bölgedeki ağaçları oluştur
                attempts = 0  # Deneme sayısı
                max_attempts = 100  # Maksimum deneme sayısı
                trees_in_region = 0  # Bu bölgede oluşturulan ağaç sayısı
                
                while trees_in_region < region_tree_count and attempts < max_attempts:
                    # Bölge içinde rastgele bir x pozisyonu seç
                    x = random.uniform(region_start, region_end)
                    
                    # Diğer ağaçlarla çakışma kontrolü
                    is_valid_position = True
                    for existing_tree in self.trees:
                        if abs(existing_tree.x - x) < (min_distance):
                            is_valid_position = False
                            break
                    
                    if is_valid_position:
                        # Rastgele ağaç tipi seç (1, 2 veya 3)
                        tree_type = random.randint(1, 3)
                        
                        # Ağacı oluştur
                        tree = Tree(
                            x=x,  # Rastgele x pozisyonu
                            y=0,  # Y pozisyonu çizim sırasında hesaplanacak
                            width=tree_width,  # Sabit genişlik
                            height=tree_height,  # Sabit yükseklik
                            tree_type=tree_type  # Ağaç tipi
                        )
                        
                        # Ağacı listeye ekle
                        self.trees.append(tree)
                        total_trees += 1
                        trees_in_region += 1
                        print(f"Ağaç {total_trees} oluşturuldu: ({tree.x:.1f}, {tree.y}), tip: {tree_type}, bölge: {region+1}")
                    
                    attempts += 1
                
                if attempts >= max_attempts:
                    print(f"Uyarı: Bölge {region+1}'de maksimum deneme sayısına ulaşıldı. {trees_in_region}/{region_tree_count} ağaç yerleştirilebildi.")
            
            print(f"Toplam {total_trees} ağaç oluşturuldu")
            
        except Exception as e:
            print(f"HATA: Ağaç oluşturma hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def create_initial_villagers(self):
        """İlk köylüleri oluştur"""
        try:
            print("Köylüler oluşturuluyor...")
            # Meslekleri güncelle
            professions = PROFESSIONS.copy()
            
            # Erkek ve kadın isimleri
            male_names = MALE_NAMES.copy()  # Orijinal listeyi değiştirmemek için copy kullanıyoruz
            female_names = FEMALE_NAMES.copy()
            
            print(f"Erkek isimleri: {male_names}")
            print(f"Kadın isimleri: {female_names}")
            
            # 5 köylü oluştur ve belirli meslekleri ata
            required_professions = ["Gardiyan", "Papaz", "Oduncu", "Avcı", "İnşaatçı"]
            
            for i in range(5):
                print(f"Köylü {i+1} oluşturuluyor...")
                # Cinsiyet seçimi (en az 1 erkek ve 1 kadın olmalı)
                if i == 0:
                    gender = "Erkek"
                elif i == 1:
                    gender = "Kadın"
                else:
                    gender = random.choice(["Erkek", "Kadın"])
                
                print(f"Cinsiyet: {gender}")
                
                # İsim seçimi
                if gender == "Erkek":
                    name = random.choice(male_names)
                    male_names.remove(name)  # Aynı ismi tekrar kullanmamak için
                else:
                    name = random.choice(female_names)
                    female_names.remove(name)  # Aynı ismi tekrar kullanmamak için
                
                print(f"İsim: {name}")
                
                # Görünüm numarası (0-3 arası)
                appearance = random.randint(0, 3)
                print(f"Görünüm: {appearance}")
                
                # Köylüyü oluştur
                print(f"Köylü nesnesi oluşturuluyor: {name}, {gender}, {appearance}")
                villager = Villager(
                    name=name,  # İsim ekledik
                    x=random.randint(100, 200),  # Kale civarında başla
                    y=self.ground_y,  # Zemin üzerinde, ağaçlarla aynı düzlemde
                    gender=gender,
                    appearance=appearance
                )
                
                # Başlangıç parası (rastgele 5-20 altın)
                villager.money = random.randint(5, 20)
                print(f"Başlangıç parası: {villager.money} altın")
                
                print(f"Köylü nesnesi oluşturuldu: {villager}")
                
                # Karakteristik özellikler (4 adet rastgele)
                all_traits = villager.ALL_TRAITS.copy()
                selected_traits = []
                for _ in range(4):
                    if all_traits:
                        trait = random.choice(all_traits)
                        selected_traits.append(trait)
                        all_traits.remove(trait)
                
                villager.traits = selected_traits
                print(f"Özellikler: {villager.traits}")
                
                # Eşinde aradığı özellikler (2 adet rastgele)
                all_traits = villager.ALL_TRAITS.copy()
                desired_traits = []
                for _ in range(2):
                    if all_traits:
                        trait = random.choice(all_traits)
                        desired_traits.append(trait)
                        all_traits.remove(trait)
                
                villager.desired_traits = desired_traits
                print(f"Eşinde aradığı: {villager.desired_traits}")
                
                # Sırayla belirli meslekleri ata
                profession = required_professions[i]
                print(f"Meslek: {profession}")
                
                villager.set_profession(profession)
                villager.set_game_controller(self)
                self.villagers.append(villager)
                print(f"Köylü oluşturuldu: {villager.name} ({villager.gender}) - {profession}")
                print(f"  Özellikler: {', '.join(villager.traits)}")
                print(f"  Eşinde aradığı: {', '.join(villager.desired_traits)}")
                print(f"  Para: {villager.money} altın")
            
            # Köylü listesini güncelle
            print(f"Köylü listesi güncelleniyor: {len(self.villagers)} köylü")
            self.villagers_updated.emit(self.villagers)
            
            print(f"Toplam köylü sayısı: {len(self.villagers)}")
            print("Meslekler: Gardiyan, Papaz, Oduncu, Avcı, İnşaatçı")
            
        except Exception as e:
            print(f"HATA: Köylü oluşturma genel hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def select_villager(self, x: float, y: float) -> Optional[Villager]:
        """Verilen koordinatlardaki köylüyü seç"""
        try:
            print(f"Köylü seçiliyor: ({x}, {y})")
            
            # Zemin seviyesini hesapla
            ground_y = 0
            if hasattr(self, 'window') and hasattr(self.window, 'ground_widget'):
                ground_widget = self.window.ground_widget
                ground_y = ground_widget.height() - ground_widget.ground_height
            
            # Köylü boyutları - draw_villagers metoduyla aynı olmalı
            villager_width = 25  # 40'tan 20'ye düşürüldü
            villager_height = 25  # 40'tan 20'ye düşürüldü
            
            # Tüm köylüleri kontrol et
            for villager in self.villagers:
                # Köylünün sınırlarını hesapla (basit bir dikdörtgen)
                # Çizim metoduyla aynı hesaplama
                villager_x = int(villager.x) - villager_width // 2
                villager_y = ground_y - villager_height
                
                villager_rect = QRect(
                    villager_x,  # Sol
                    villager_y,  # Üst
                    villager_width,  # Genişlik
                    villager_height   # Yükseklik
                )
                
                # Tıklama köylünün üzerinde mi kontrol et
                if villager_rect.contains(QPoint(int(x), int(y))):
                    print(f"Köylü seçildi: {villager.name}")
                    return villager
            
            print("Köylü seçilemedi")
            return None
            
        except Exception as e:
            print(f"HATA: Köylü seçme hatası: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def find_nearest_available_tree(self, woodcutter) -> Optional[Tree]:
        """En yakın müsait ağacı bul"""
        try:
            nearest_tree = None
            min_distance = float('inf')
            
            for tree in self.trees:
                # Ağaç görünür ve kesilmiyorsa
                if tree.is_visible and not tree.is_being_cut:
                    # Ağaç ile oduncu arasındaki mesafeyi hesapla
                    distance = abs(tree.x - woodcutter.x)
                    
                    # En yakın ağacı güncelle
                    if distance < min_distance:
                        min_distance = distance
                        nearest_tree = tree
            
            return nearest_tree
            
        except Exception as e:
            print(f"HATA: En yakın ağaç bulma hatası: {e}")
            return None
    
    def update_game(self):
        """Oyun güncellemesi - her kare çalışır"""
        try:
            # Güncel zaman
            current_time = time.time()
            
            # Köylü sayısını kontrol et ve 5'ten fazlaysa fazla olanları kaldır
            if len(self.villagers) > 5:
                print(f"Köylü sayısı 5'i aşıyor! Mevcut: {len(self.villagers)}")
                # 5 köylü kalacak şekilde fazla olanları kaldır, ilk 5 köylüyü tut
                self.villagers = self.villagers[:5]
                print(f"Köylü sayısı 5'e düşürüldü. Yeni sayı: {len(self.villagers)}")
                # Köylü listesini güncelle
                if hasattr(self, 'villagers_updated'):
                    self.villagers_updated.emit(self.villagers)
            
            # Tüm köylü davranışlarını güncelle
            for villager in self.villagers:
                # Köylünün davranış ağacını güncelle
                if hasattr(villager, 'update_behavior_tree'):
                    villager.update_behavior_tree()
                else:
                    villager.move()  # Davranış ağacı yoksa temel hareket
                    
                    # Animasyon kontrolü - animasyon hızını yavaşlat
                    if not hasattr(villager, 'last_animation_update'):
                        villager.last_animation_update = current_time
                    
                    # Sadece hareket ediyorsa animasyonu güncelle, yavaş tempoda
                    if villager.is_moving and current_time - villager.last_animation_update > 0.25:  # Her 250ms'de bir kare değişimi
                        if hasattr(villager, 'update_animation'):
                            villager.update_animation()
                        villager.last_animation_update = current_time
            
            # Kurtları güncelle
            self.update_wolves()
            
            # Kuşları güncelle
            self.update_birds()
            
            # Pazar tezgahlarını güncelle
            self.update_market_stalls()
            
            # İnşaat alanlarını güncelle
            for site in self.building_sites[:]:  # Kopyasını kullan (döngü esnasında liste değişebilir)
                if hasattr(site, 'update'):
                    if not site.update():
                        # İnşaat tamamlandı veya silindi, listeden çıkar
                        if site in self.building_sites:
                            self.building_sites.remove(site)
            
            # Periyodik olarak rastgele diyalog oluştur (her 60 saniyede bir)
            current_time = time.time()
            if current_time - self.last_periodic_update > 60:  # Her 60 saniyede bir
                self.last_periodic_update = current_time
                # Rastgele diyalog üret
                self.generate_random_dialogue()
                # Köylüleri birbirleriyle ilişkilendir
                self.update_villager_relationships()
                # Yeni bir kuş/karga oluştur
                self.try_spawn_bird()
                
        except Exception as e:
            print(f"HATA: Oyun güncellemesi sırasında hata: {e}")
            import traceback
            traceback.print_exc()
    
    def start_day_night_cycle(self):
        """Gündüz/gece döngüsünü başlat"""
        try:
            # Gündüz süresi (5 dakika = 300 saniye)
            self.DAY_DURATION = 300
            # Gece süresi (3 dakika = 180 saniye)
            self.NIGHT_DURATION = 180
            
            # Başlangıçta gündüz
            self.is_daytime = True
            self.remaining_time = self.DAY_DURATION * 1000
            
            print("Gündüz/gece döngüsü başlatıldı")
            
        except Exception as e:
            print(f"HATA: Gündüz/gece döngüsü başlatılamadı: {e}")
            import traceback
            traceback.print_exc()
    
    def return_villagers_to_castle(self):
        """Köylüleri kaleye döndür"""
        try:
            for villager in self.villagers:
                # Köylünün hedefini kaleye ayarla
                villager.target_x = self.castle.x  # Kale x pozisyonu
                villager.target_y = self.ground_y  # Zemin seviyesi
                villager.is_moving = True
                villager.is_wandering = False  # Dolaşmayı durdur
                
                # Eğer oduncu ise kesme işlemini durdur
                if villager.profession == "Oduncu":
                    if villager.target_tree:
                        villager.target_tree.stop_cutting()
                    villager.is_cutting = False
                    villager.target_tree = None
                
                # Eğer inşaatçı ise inşaat işlemini durdur
                if villager.profession == "İnşaatçı":
                    if villager.target_building_site:
                        villager.target_building_site.stop_construction()
                    villager.is_building = False
                    villager.target_building_site = None
                
                print(f"{villager.name} kaleye dönüyor")
            
            print("Tüm köylüler kaleye dönüyor")
            
        except Exception as e:
            print(f"HATA: Köylüler kaleye döndürülemedi: {e}")
            import traceback
            traceback.print_exc()
    
    def get_time_as_minutes_seconds(self):
        """Kalan süreyi dakika:saniye formatında döndür"""
        minutes = self.remaining_time // 60000
        seconds = (self.remaining_time // 1000) % 60
        return minutes, seconds
    
    def update_remaining_time(self):
        """Kalan süreyi güncelle"""
        try:
            # Kalan süreyi azalt
            self.remaining_time -= 1000  # 1 saniye (milisaniye cinsinden)
            
            # Süre doldu mu kontrol et
            if self.remaining_time <= 0:
                self.toggle_day_night()
            
            # Kontrol panelini güncelle
            if hasattr(self, 'control_panel'):
                self.control_panel.update_time_label()
                
        except Exception as e:
            print(f"HATA: Süre güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def toggle_day_night(self):
        """Gündüz/gece durumunu değiştir"""
        # Gece/gündüz durumunu değiştir
        self.is_daytime = not self.is_daytime
        
        # Yeni süreyi ayarla
        if self.is_daytime:
            self.remaining_time = self.DAY_DURATION * 1000
            self.day_count += 1  # Gündüz başladığında gün sayısını artır
            print(f"Gün {self.day_count} başladı")
        else:
            self.remaining_time = self.NIGHT_DURATION * 1000
            print(f"Gün {self.day_count} sona erdi, gece başladı")
        
        # Gündüz veya gece değişimi olduğunda özel işlemler
        self.handle_day_night_change()
    
    def update_market_stalls(self):
        """Pazar tezgahlarını güncelle"""
        try:
            if not self.market or not hasattr(self.market, 'stalls'):
                return
            
            # Her tezgahın durumunu kontrol et
            for stall in self.market.stalls:
                # Tezgah sahibi var mı?
                if not stall.owner or not stall.is_active:
                    continue
                
                # Tezgahta stok var mı?
                inventory_count = stall.inventory.get(stall.stall_type, 0)
                if inventory_count <= 0:
                    # Stok yoksa tezgahı boşalt
                    stall.release_stall()
                    print(f"Tezgah #{stall.stall_id} stok bittiği için boşaltıldı")
                    continue
                
                # Tezgah sahibi köylüyü kontrol et
                owner = stall.owner
                if not hasattr(owner, 'has_market_stall') or not owner.has_market_stall:
                    # Köylü tezgahı bırakmış
                    stall.release_stall()
                    print(f"Tezgah #{stall.stall_id} sahibi ayrıldığı için boşaltıldı")
                    continue
                
                # Fiyat güncelleme, pazarlık gibi ek mantıklar burada olabilir
                
                # Otomatik satış/müşteri sistemi için buraya ek kodlar eklenebilir
                
        except Exception as e:
            print(f"HATA: Pazar tezgahları güncellenirken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def find_available_stall(self, stall_type):
        """Belirtilen türde boş bir tezgah bul"""
        if not self.market or not hasattr(self.market, 'stalls'):
            return None
        
        # Boş tezgah ara
        for stall in self.market.stalls:
            if stall.stall_type == stall_type and not stall.owner:
                return stall
        return None
    
    def get_remaining_time(self):
        """Gündüz/gece döngüsünde kalan süreyi dakika:saniye olarak döndür"""
        remaining_seconds = self.remaining_time // 1000
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        return minutes, seconds
    
    def handle_day_night_change(self):
        """Gündüz veya gece değişimi olduğunda yapılacak işlemler"""
        try:
            if self.is_daytime:
                # Gündüz başladığında köylüleri dolaşmaya başlat
                for villager in self.villagers:
                    if hasattr(villager, 'update_daytime'):
                        villager.update_daytime(self.is_daytime)
                    
                    # Oduncuların günlük kesme hakkını sıfırla
                    if villager.profession == "Oduncu":
                        villager.trees_cut_today = 0
                        print(f"{villager.name} yeni güne başladı, kesme hakkı: {villager.max_trees_per_day}")
                    
                    # İnşaatçıların günlük inşaat hakkını sıfırla
                    elif villager.profession == "İnşaatçı":
                        villager.buildings_built = 0
                        print(f"{villager.name} yeni güne başladı, inşaat hakkı: {villager.max_buildings_per_day}")
                
                # Köylüleri dolaşmaya başlat
                if hasattr(self, 'start_villagers_wandering'):
                    self.start_villagers_wandering()
            else:
                # Gece başladığında köylüleri kaleye döndür
                if hasattr(self, 'return_villagers_to_castle'):
                    self.return_villagers_to_castle()
            
            # Kurtların gündüz/gece durumunu güncelle
            for wolf in self.wolves:
                if hasattr(wolf, 'update_daytime'):
                    wolf.update_daytime(self.is_daytime)
            
            # Sinyal gönder (eğer bu sinyal varsa)
            if hasattr(self, 'day_night_changed'):
                self.day_night_changed.emit(self.is_daytime)
            
            print(f"Gündüz/gece değişti: {'Gündüz' if self.is_daytime else 'Gece'}")
            
            # Kontrol panelini güncelle
            if hasattr(self, 'control_panel') and self.control_panel:
                # Kontrol paneli hazırsa update_time_label metodunu çağır
                if hasattr(self.control_panel, 'update_time_label'):
                    self.control_panel.update_time_label()
                    
        except Exception as e:
            print(f"HATA: Gündüz/gece değişim işlemi hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def on_tree_removed(self, tree):
        """Ağaç kesildiğinde çağrılır"""
        try:
            print(f"Ağaç kaldırıldı: {tree.id}")
            
            # Ağacı ID'sine göre listeden kaldır
            tree_id = tree.id
            removed = False
            
            for i, t in enumerate(self.trees[:]):
                if t.id == tree_id:
                    self.trees.pop(i)
                    print(f"Ağaç ID: {tree_id} listeden tamamen kaldırıldı")
                    removed = True
                    break
            
            if not removed:
                print(f"UYARI: Ağaç ID: {tree_id} listede bulunamadı!")
            
            # 10 saniye sonra yeni bir ağaç ekle
            QTimer.singleShot(10000, self.add_new_tree)
            print(f"Yeni ağaç 10 saniye sonra eklenecek")
            
            # Kale envanterini güncelle
            if hasattr(self, 'control_panel'):
                self.control_panel.update_castle_inventory()
                
        except Exception as e:
            print(f"HATA: Ağaç kaldırma işlemi sırasında hata: {e}")
            import traceback
            traceback.print_exc()
    
    def add_new_tree(self):
        """Yeni ağaç ekle"""
        try:
            # Rastgele bir konumda yeni ağaç oluştur
            # Ekranın tamamında rastgele bir konum seç
            desktop = QDesktopWidget()
            total_width = 0
            for i in range(desktop.screenCount()):
                screen_geo = desktop.screenGeometry(i)
                total_width += screen_geo.width()
            
            # Kale pozisyonu (varsayılan olarak x=0)
            castle_x = 0
            # Ağaçların başlangıç pozisyonu (kaleden 200 piksel sağda)
            min_x = castle_x + 200
            max_x = total_width - 100  # Ekranın sağ kenarından 100 piksel içeride
            
            # Ağaç boyutları
            tree_width = 50  # 80'den 50'ye düşürüldü
            tree_height = 80  # 120'den 80'e düşürüldü
            
            # Ağaçlar arası minimum mesafe
            min_distance = 50
            
            # Geçerli bir konum bulana kadar dene
            max_attempts = 20
            attempts = 0
            valid_position = False
            x = 0
            
            while not valid_position and attempts < max_attempts:
                x = random.randint(min_x, max_x)  # Ekran sınırları içinde
                valid_position = True
                
                # Diğer ağaçlarla çakışma kontrolü
                for existing_tree in self.trees:
                    if abs(existing_tree.x - x) < min_distance:
                        valid_position = False
                        break
                
                attempts += 1
            
            if not valid_position:
                print(f"UYARI: Geçerli bir ağaç konumu bulunamadı, rastgele bir konum kullanılıyor.")
            
            y = self.ground_height - 100  # Zemin üzerinde
            
            # Rastgele ağaç tipi seç (1 veya 2)
            tree_type = random.randint(1, 2)
            
            new_tree = Tree(x, y, tree_width, tree_height, tree_type=tree_type)
            new_tree.tree_removed.connect(self.on_tree_removed)
            self.trees.append(new_tree)
            
            print(f"Yeni ağaç eklendi: ID: {new_tree.id}, Tip: {tree_type}, Konum: ({x}, {y})")
            
        except Exception as e:
            print(f"HATA: Yeni ağaç ekleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def set_control_panel(self, control_panel):
        """Kontrol panelini ayarla"""
        self.control_panel = control_panel
        
        # Kontrol panelini diyalog yöneticisine de bağla
        if hasattr(self, 'dialogue_manager'):
            self.dialogue_manager.set_game_controller(self)

    def create_building_site(self, x: float, y: float, min_distance=80) -> BuildingSite:
        """İnşaat alanı oluştur"""
        try:
            # Zemin seviyesini kullan
            ground_y = self.ground_y
            
            # Diğer yapılarla çakışma kontrolü
            MIN_BUILDING_DISTANCE = min_distance  # Yapılar arası minimum mesafe (parametreden alınıyor)
            
            # Diğer inşaat alanlarıyla çakışıyor mu kontrol et
            for building_site in self.building_sites:
                distance = abs(building_site.x - x)
                if distance < MIN_BUILDING_DISTANCE:
                    print(f"İnşaat alanı oluşturulamadı: Başka bir inşaat alanına çok yakın! Mesafe: {distance} < {MIN_BUILDING_DISTANCE}")
                    return None
            
            # Evlerle çakışıyor mu kontrol et
            for house in self.houses:
                distance = abs(house.x - x)
                if distance < MIN_BUILDING_DISTANCE:
                    print(f"İnşaat alanı oluşturulamadı: Bir eve çok yakın! Mesafe: {distance} < {MIN_BUILDING_DISTANCE}")
                    return None
            
            # Diğer özel yapılarla çakışıyor mu kontrol et (kale, kilise, pazar vs.)
            if hasattr(self, 'castle') and self.castle:
                distance = abs(self.castle.x - x)
                if distance < MIN_BUILDING_DISTANCE:
                    print(f"İnşaat alanı oluşturulamadı: Kaleye çok yakın! Mesafe: {distance} < {MIN_BUILDING_DISTANCE}")
                    return None
            
            # Kilise konumu yaklaşık olarak 310
            distance_to_church = abs(310 - x)
            if distance_to_church < MIN_BUILDING_DISTANCE:
                print(f"İnşaat alanı oluşturulamadı: Kiliseye çok yakın! Mesafe: {distance_to_church} < {MIN_BUILDING_DISTANCE}")
                return None
            
            # Pazar yeri kontrolü
            if hasattr(self, 'market') and self.market:
                distance = abs(self.market.x - x)
                if distance < MIN_BUILDING_DISTANCE:
                    print(f"İnşaat alanı oluşturulamadı: Pazar yerine çok yakın! Mesafe: {distance} < {MIN_BUILDING_DISTANCE}")
                    return None
            
            # İnşaat alanını oluştur (zemin seviyesinde)
            building_site = BuildingSite(x=x, y=ground_y)
            
            # Sinyalleri bağla
            building_site.construction_finished.connect(self.on_construction_finished)
            
            # Listeye ekle
            self.building_sites.append(building_site)
            
            print(f"İnşaat alanı oluşturuldu: ({x}, {ground_y}), Tip: {building_site.house_type}")
            return building_site
            
        except Exception as e:
            print(f"HATA: İnşaat alanı oluşturma hatası: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def on_construction_finished(self, building_site: BuildingSite):
        """İnşaat tamamlandığında çağrılır"""
        try:
            print(f"İnşaat tamamlandı: {building_site.id}")
            
            # Zemin seviyesini hesapla
            ground_y = self.ground_y + 35
            
            # Ev oluştur - y değerini zemin seviyesi olarak ayarla
            house = House(
                x=building_site.x,
                y=ground_y,  # Zemin seviyesine yerleştir
                width=building_site.width,
                height=building_site.height,
                house_type=building_site.house_type
            )
            
            # İnşaatçı bilgisini taşı
            if building_site.builder:
                house.builder = building_site.builder
                # İnşaatçının yaptığı ev sayısını artır
                building_site.builder.buildings_built += 1
                print(f"{building_site.builder.name} bir ev inşa etti. Toplam: {building_site.builder.buildings_built}")
            
            # Rastgele seçilen köylüye evi ver
            if hasattr(building_site, 'future_owner') and building_site.future_owner:
                future_owner = building_site.future_owner
                # Ev sahibini ayarla
                house.set_owner(future_owner.name)
                
                # Köylüye ev sahibi olduğunu bildir
                future_owner.has_house = True
                future_owner.house_id = house.id
                
                print(f"Ev ID: {house.id} sahibi: {future_owner.name}")
            else:
                # Evi satılık olarak işaretle (sahibi yok, ama inşaatçı kayıtlı)
                house.for_sale = True
                print(f"Ev ID: {house.id} satışa çıkarıldı. Tip: {house.house_type}")
            
            # Listeye ekle
            self.houses.append(house)
            
            # İnşaat alanını listeden kaldır
            for i, site in enumerate(self.building_sites[:]):
                if site.id == building_site.id:
                    self.building_sites.pop(i)
                    print(f"İnşaat alanı ID: {building_site.id} listeden kaldırıldı")
                    break
            
            # Kontrol panelini güncelle
            if hasattr(self, 'control_panel'):
                self.control_panel.update_castle_inventory()
            
            print(f"Ev oluşturuldu: {house.id}, Tip: {house.house_type}, Konum: ({house.x}, {house.y})")
            
        except Exception as e:
            print(f"HATA: İnşaat tamamlama hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def try_sell_house(self, house: House):
        """Evi satmayı dene"""
        try:
            # Ev zaten satılmışsa işlem yapma
            if house.is_owned():
                print(f"Ev ID: {house.id} zaten satılmış! Sahibi: {house.owner}")
                return
                
            # Satın alabilecek köylüleri bul (100 altın veya daha fazlası olanlar)
            potential_buyers = [v for v in self.villagers if v.money >= 100 and not v.has_house]
            
            if not potential_buyers:
                print(f"Ev ID: {house.id} için alıcı bulunamadı!")
                return
                
            # Rastgele bir alıcı seç
            buyer = random.choice(potential_buyers)
            
            # Evi sat
            house_price = 100  # Ev fiyatı: 100 altın
            buyer.money -= house_price
            house.set_owner(buyer.name)
            
            # Köylünün ev sahibi olduğunu işaretle
            buyer.has_house = True
            buyer.house_id = house.id
            
            # İnşaatçıya ödemeyi yap
            if hasattr(house, 'builder') and house.builder:
                house.builder.money += house_price
                print(f"İnşaatçı {house.builder.name} ev satışından {house_price} altın kazandı! Toplam: {house.builder.money} altın")
            
            print(f"Ev ID: {house.id} satıldı! Alıcı: {buyer.name}, Ödenen: {house_price} altın, Kalan para: {buyer.money} altın")
            
        except Exception as e:
            print(f"HATA: Ev satma hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def find_house_by_id(self, house_id) -> Optional[House]:
        """ID'ye göre ev bul"""
        for house in self.houses:
            if house.id == house_id:
                return house
        return None
    
    def find_house_by_owner(self, owner_name: str) -> Optional[House]:
        """Sahibine göre ev bul"""
        for house in self.houses:
            if house.owner == owner_name:
                return house
        return None
    
    def start_villagers_wandering(self):
        """Köylüleri tekrar dolaşmaya başlat"""
        try:
            for villager in self.villagers:
                # Köylünün hedefini rastgele bir noktaya ayarla
                villager.target_x = random.randint(100, self.width - 100)
                villager.target_y = self.ground_y - 100
                villager.is_moving = True
                villager.is_wandering = True  # Dolaşmayı başlat
                
                # Eğer oduncu ise kesme sayısını sıfırla
                if villager.profession == "Oduncu":
                    villager.trees_cut_today = 0
                    print(f"{villager.name} yeni güne başladı, kesme hakkı: {villager.max_trees_per_day}")
                
                print(f"{villager.name} dolaşmaya başlıyor")
            
            print("Tüm köylüler dolaşmaya başladı")
            
        except Exception as e:
            print(f"HATA: Köylüler dolaşmaya başlatılamadı: {e}")
            import traceback
            traceback.print_exc()
    
    def go_home(self):
        """Eve veya kaleye dön"""
        try:
            print("Köylüler evlerine veya kaleye dönüyor...")
            
            for villager in self.villagers:
                # Köylünün hedef noktasına doğru hareket etmesini sağla
                if hasattr(villager, 'has_house') and villager.has_house:
                    # Ev sahibi olanlar evlerine gitsin
                    house = self.find_house_by_id(villager.house_id)
                    if house:
                        # Evin giriş noktası
                        entrance = house.get_entrance()
                        target_x, target_y = entrance
                        
                        # Hedefe ayarla
                        villager.target_x = target_x
                        villager.target_y = target_y
                        villager.is_moving = True
                        villager.is_wandering = False  # Dolaşmayı durdur
                        villager.state = "Eve Dönüyor"
                        
                        print(f"{villager.name} evine dönüyor. Hedef: ({target_x}, {target_y})")
                    else:
                        # Ev bulunamadıysa kaleye git
                        self._direct_villager_to_castle(villager)
                else:
                    # Ev sahibi olmayanlar kaleye gitsin
                    self._direct_villager_to_castle(villager)
            
        except Exception as e:
            print(f"HATA: Köylüler eve gönderilirken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def _direct_villager_to_castle(self, villager):
        """Köylüyü kaleye yönlendir"""
        try:
            # Kale varsa
            if hasattr(self, 'castle') and self.castle:
                # Kalenin giriş noktası
                entrance = self.castle.get_entrance()
                target_x, target_y = entrance
                
                # Hedefe ayarla
                villager.target_x = target_x
                villager.target_y = target_y
                villager.is_moving = True
                villager.is_wandering = False  # Dolaşmayı durdur
                villager.state = "Kaleye Dönüyor"
                
                print(f"{villager.name} kaleye dönüyor. Hedef: ({target_x}, {target_y})")
        except Exception as e:
            print(f"HATA: Köylü kaleye yönlendirilirken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def create_dialogue_bubble(self, villager, message):
        """Diyalog baloncuğu oluştur"""
        try:
            # Diyalog özelliklerini ayarla
            villager.chat_message = message
            villager.chat_bubble_visible = True
            villager.chat_bubble_time = time.time()
            
            # Mesajı tüm sisteme bildir
            self.chat_message.emit(villager, message)
            
            # Kontrol paneline ilet
            if hasattr(self, 'control_panel') and self.control_panel:
                # İlişki seviyesini al (eğer sohbet ortağı varsa)
                relationship = ""
                if hasattr(villager, 'chat_partner') and villager.chat_partner:
                    relationship = villager.get_relationship_with(villager.chat_partner)
                    # Mesajı panele ekle
                    self.control_panel.add_dialogue_to_chat(
                        villager.name, 
                        villager.chat_partner.name if villager.chat_partner else "Tüm Köy",
                        message,
                        relationship
                    )
            
            # Her baloncuk için 3 saniyelik otomatik silme zamanlayıcısı ekle
            QTimer.singleShot(3000, lambda v=villager: self.remove_dialogue_bubble(v))
            
            # İşlem başarılı
            return True
            
        except Exception as e:
            print(f"HATA: Diyalog baloncuğu oluşturma hatası: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def remove_dialogue_bubble(self, villager_or_bubble):
        """Diyalog baloncuğu kaldır"""
        try:
            # Parametre kontrol et (villager veya bubble)
            if isinstance(villager_or_bubble, bool):
                # Parametre bir boolean değer (zaten başarıyı temsil ediyor)
                return True
            
            # Villager mi kontrol et
            if hasattr(villager_or_bubble, 'chat_bubble_visible'):
                # Diyalog özelliklerini temizle
                villager_or_bubble.chat_bubble_visible = False
                villager_or_bubble.chat_message = ""
            
            # İşlem başarılı
            return True
            
        except Exception as e:
            print(f"HATA: Diyalog baloncuğu kaldırma hatası: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_wolves(self, num_wolves=5):
        """Kurtları oluştur"""
        try:
            # Kurtları temizle
            self.wolves = []
            
            # Mağara konumunu bul
            cave_x = 2500  # Varsayılan mağara konumu
            
            # Eğer mağara nesnesi varsa, onun konumunu kullan
            for structure in self.structures:
                if hasattr(structure, 'name') and structure.name == "cave":
                    cave_x = structure.x
                    break
            
            print(f"Mağara konumu: x={cave_x}")
            
            # Kalenin konumunu belirle
            castle_x = 0
            if hasattr(self, 'castle') and self.castle:
                castle_x = self.castle.x
            
            # Belirtilen sayıda kurt oluştur
            for i in range(num_wolves):
                # Mağaranın etrafında rastgele x pozisyonu
                wolf_x = cave_x + random.randint(-200, 200)
                
                # Doğru yapıcı parametrelerini geçerek kurt oluştur
                wolf = Wolf(
                    wolf_id=i+1,  # wolf_id parametresi gerekli
                    x=wolf_x,
                    y=self.ground_y,  # Y koordinatı zemin seviyesine ayarlandı
                    width=50,
                    height=35
                )
                
                # Mağara konumunu ayarla
                wolf.cave_x = cave_x
                # Köy sınırını ayarla
                wolf.min_x = castle_x + 500
                
                # Game controller'ı ayarla
                wolf.set_game_controller(self)
                
                # Kurt nesnesini listeye ekle
                self.wolves.append(wolf)
                print(f"Kurt {i+1} oluşturuldu: x={wolf_x}, y={self.ground_y}, cave_x={cave_x}, min_x={wolf.min_x}")
                
            print(f"Toplam {num_wolves} kurt oluşturuldu")
                
        except Exception as e:
            print(f"HATA: Kurt oluşturma hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def create_cave(self):
        """Mağarayı oluştur"""
        try:
            # Tüm ekranların toplam genişliğini kullan
            total_width = 0
            desktop = QDesktopWidget()
            for i in range(desktop.screenCount()):
                screen_geo = desktop.screenGeometry(i)
                total_width += screen_geo.width()
            
            # Mağaranın x pozisyonu (ekranın en sağ tarafı)
            cave_x = total_width - 200
            
            # Mağara nesnesi oluştur
            cave = Building(
                x=cave_x,
                y=self.ground_y,
                width=100,
                height=70,
                building_type="cave"
            )
            
            # Nesneye özel adı ekle
            cave.name = "cave"
            
            # Structures listesine ekle
            self.structures.append(cave)
            
            print(f"Mağara oluşturuldu: x={cave_x}, y={self.ground_y}")
            return cave
            
        except Exception as e:
            print(f"HATA: Mağara oluşturma hatası: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_wolves(self):
        """Kurtları güncelle"""
        try:
            if not hasattr(self, 'wolves') or not self.wolves:
                return
            
            # Güncel zaman
            current_time = time.time()
            
            # Kurtları güncelle
            for wolf in self.wolves:
                # Kurt update metodunu çağır
                if hasattr(wolf, 'update'):
                    wolf.update()
                else:
                    # Eski sisteme uyumluluk için
                    # Hareket kontrol değişkenlerini tanımla (eğer yoksa)
                    if not hasattr(wolf, 'last_animation_update'):
                        wolf.last_animation_update = current_time
                    if not hasattr(wolf, 'animation_frame'):
                        wolf.animation_frame = 1
                    
                    # Kurt hareketi
                    if not hasattr(wolf, 'target_x') or not hasattr(wolf, 'target_y'):
                        # İlk hedef noktasını belirle
                        wolf.target_x = random.randint(100, self.width - 100)
                        wolf.target_y = self.ground_y
                    
                    # Hedef noktaya doğru hareket et
                    dx = wolf.target_x - wolf.x
                    dy = wolf.target_y - wolf.y
                    
                    # Hareket hızı
                    speed = 1.5  # 2'den 1.5'e düşürüldü
                    is_moving = False
                    
                    # Yönü belirle
                    if dx > 0:
                        wolf.direction = 1  # Sağa doğru
                        is_moving = True
                    elif dx < 0:
                        wolf.direction = -1  # Sola doğru
                        is_moving = True
                    
                    # Hareket et
                    if abs(dx) > speed:
                        wolf.x += speed * wolf.direction
                        is_moving = True
                    else:
                        wolf.x = wolf.target_x
                    
                    if abs(dy) > speed:
                        wolf.y += speed
                        is_moving = True
                    else:
                        wolf.y = wolf.target_y
                    
                    # Sadece hareket ediyorsa animasyonu güncelle, yavaş tempoda
                    if is_moving and current_time - wolf.last_animation_update > 0.25:  # Her 250ms'de bir kare değişimi
                        wolf.animation_frame = (wolf.animation_frame % 4) + 1
                        wolf.last_animation_update = current_time
                    
                    # Hedefe ulaşıldıysa yeni hedef belirle
                    if abs(dx) < speed and abs(dy) < speed:
                        # Yeni hedef belirle
                        if hasattr(wolf, 'wander'):
                            wolf.wander()
                        else:
                            # Eski sistemle uyumlu
                            wolf.target_x = random.randint(100, self.width - 100)
                            wolf.target_y = self.ground_y
                
        except Exception as e:
            print(f"HATA: Kurtları güncellerken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def spawn_wolf(self):
        """Yeni kurt oluştur"""
        try:
            # Mağara yakınında rastgele bir konum belirle
            if self.cave:
                # Mağaranın etrafında rastgele bir konum
                cave_x = self.cave.x
                cave_y = self.cave.y
                
                # Mağaranın 100-300 piksel uzağında rastgele bir konum
                offset_x = random.randint(-300, 300)
                offset_y = random.randint(-100, 100)
                
                x = cave_x + offset_x
                y = cave_y + offset_y
            else:
                # Mağara yoksa ekranın sağ tarafında rastgele bir konum
                x = random.randint(self.width - 400, self.width - 100)
                y = self.ground_y
            
            # Kurt nesnesini oluştur
            from src.models.wolf import Wolf
            wolf = Wolf(x=x, y=y)
            
            # Kurt özelliklerini ayarla
            wolf.width = 40
            wolf.height = 30
            wolf.direction = 1  # Varsayılan olarak sağa doğru
            wolf.animation_frame = 1
            
            # Kurtu listeye ekle
            self.wolves.append(wolf)
            
            print(f"Yeni kurt oluşturuldu: ID={wolf.wolf_id}, Konum=({x}, {y})")
            return wolf
            
        except Exception as e:
            print(f"HATA: Kurt oluşturma hatası: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_birds(self):
        """Kuşları güncelle"""
        try:
            # Kuşlar listesini kontrol et
            if not hasattr(self, 'birds'):
                self.birds = []
                return
            
            # Mevcut kuşları güncelle
            for bird in self.birds[:]:  # Kopyasını kullan
                if hasattr(bird, 'update'):
                    if not bird.update():  # False dönerse kuş ekrandan çıkmıştır
                        if bird in self.birds:
                            self.birds.remove(bird)
                            print(f"Kuş #{bird.bird_id} ekrandan çıktı, silindi")
            
        except Exception as e:
            print(f"HATA: Kuşları güncellerken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def try_spawn_bird(self):
        """Yeni bir kuş oluşturmayı dene"""
        try:
            # Kuş oluşturma için uygun mu kontrol et
            if len(self.birds) >= self.max_birds:
                return  # Maksimum kuş sayısına ulaşıldı
            
            current_time = time.time()
            if current_time - self.last_bird_spawn < self.bird_spawn_interval:
                return  # Oluşturma aralığı henüz dolmadı
            
            # Kuş oluşturma şansını kontrol et
            if random.random() < self.bird_spawn_chance:
                self.spawn_bird()
            
            self.last_bird_spawn = current_time
                
        except Exception as e:
            print(f"HATA: Kuş oluşturma denemesi sırasında hata: {e}")
            import traceback
            traceback.print_exc()
    
    def spawn_bird(self):
        """Yeni bir kuş oluştur"""
        try:
            from src.models.bird import Bird
            
            # Rastgele kuş tipi seç
            bird_type = random.choice(["kuş", "karga"])
            
            # Rastgele bir yönden gelsin (sol/sağ)
            direction = random.choice([-1, 1])  # -1: soldan sağa, 1: sağdan sola
            
            # Kuşun başlangıç X konumu (ekranın dışından)
            # Ekran genişliğini hesapla
            screen_width = 0
            if hasattr(self, 'window') and hasattr(self.window, 'width'):
                screen_width = self.window.width()
            else:
                # Varsayılan değer
                screen_width = 1920
            
            # Yöne göre başlangıç X konumu
            start_x = screen_width + 50 if direction == -1 else -50
            
            # Rastgele bir Y yüksekliği (gökyüzünde)
            start_y = random.randint(50, 300)
            
            # Kuş oluştur
            bird = Bird(x=start_x, y=start_y, direction=direction, bird_type=bird_type)
            self.birds.append(bird)
            
            print(f"Yeni {bird_type} oluşturuldu: ID={bird.bird_id}, Konum=({start_x}, {start_y}), Yön={direction}")
            return bird
        
        except Exception as e:
            print(f"HATA: Kuş oluşturma hatası: {e}")
            import traceback
            traceback.print_exc()
            return None

    def create_market(self):
        """Köy pazarını oluştur"""
        try:
            # Kalenin konumuna göre pazar yerini belirle
            castle_x = self.castle.x if hasattr(self, 'castle') and self.castle else 500
            market_x = castle_x + 240  # Kaleden 240 piksel sağda (kiliseye yakın)
            
            # Pazar yapısı için y değeri - ground_y kullan, kilise benzeri konumlandırma
            market_y = self.ground_y  # Zemin seviyesi
            
            # Market nesnesini oluştur
            from src.models.market import Market
            self.market = Market(market_x, market_y, 4)  # 4 tezgahlı pazar (2'den 4'e çıkarıldı)
            
            # Market'a GameController referansı ver
            if hasattr(self.market, 'set_game_controller'):
                self.market.set_game_controller(self)
            
            # Pazar sinyallerini bağla
            self.market.transaction_completed.connect(self.on_trade_completed)
            
            # Başarılı oluşturma bildirimi
            print(f"Pazar alanı oluşturuldu. Konum: ({market_x}, {market_y})")
            self.notify("Köy pazarı kuruldu!", "trade")

            return self.market
        except Exception as e:
            print(f"Pazar oluşturma hatası: {e}")
            import traceback
            traceback.print_exc()
            return None

    def on_trade_completed(self, seller, buyer, product, amount, price):
        """Ticaret tamamlandığında çağrılır"""
        # İlgili köylülere durumu bildir
        seller_msg = f"{buyer.name} ile {amount} {product} için {price} altına ticaret yaptı."
        buyer_msg = f"{seller.name}'den {amount} {product} satın aldı, {price} altın ödedi."
        
        self.create_dialogue_bubble(seller, seller_msg)
        self.create_dialogue_bubble(buyer, buyer_msg)
        
        # Tüm bileşenlerin trade_completed sinyalini duyması için ilet
        self.trade_completed.emit(seller, buyer, product, amount, price)
        
        print(f"Ticaret tamamlandı: {seller.name} -> {buyer.name}, {amount} {product}, {price} altın")
        
    def update_game_loop(self):
        """Oyun döngüsünü güncelle"""
        try:
            # Oyunda aktif bir şey yoksa çık
            if not self.is_running:
                return
                
            # Hızlı referanslar oluştur
            villagers = self.villagers
            trees = self.trees
            
            # Oyun zamanını güncelle
            current_time = time.time()
            
            # Kurt yönetimi (gece aktif)
            if not self.is_daytime:
                # Kurtları güncelle
                self.update_wolves()
                
                # Her 5 saniyede bir yeni kurt oluşturma şansı
                if current_time - self.last_wolf_spawn > self.wolf_spawn_interval:
                    self.last_wolf_spawn = current_time
                    if random.random() < 0.2:  # %20 şans
                        self.spawn_wolf()
            
            # Kuşları güncelle
            self.update_birds()
            
            # Kuş oluşturmayı dene (gündüz aktif)
            if self.is_daytime:
                self.try_spawn_bird()
            
            # İnşaatçı kontrolü - envanteri kontrol et ve gerekirse inşaat başlat
            if self.is_daytime:  # Sadece gündüz inşaat yapılsın
                # İnşaatçıları bul
                builders = [v for v in self.villagers if v.profession == "İnşaatçı"]
                # İnşaatçılar varsa ve inşaat yapmıyorlarsa kontrol et
                if builders and not any(b.is_building for b in builders):
                    # Günlük limiti dolmamış inşaatçı var mı?
                    if any(b.buildings_built < b.max_buildings_per_day for b in builders):
                        # Odun kontrolü ve inşaat başlatma
                        self.check_for_auto_building()
            
            # Pazar tezgahlarını güncelle
            self.update_market_stalls()
            
            # Zamanı güncelle
            self.update_time()
            
            # Raptiye ve Kopar sistemi için periyodik görevler
            if current_time - self.last_periodic_update > 5.0:  # 5 saniyede bir
                self.last_periodic_update = current_time
                
                # Yeni yapılmış evleri satmayı dene
                for house in self.houses:
                    if not house.is_owned() and house.for_sale:
                        self.try_sell_house(house)
            
        except Exception as e:
            print(f"HATA: Oyun döngüsü hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def check_for_auto_building(self):
        """Kale envanterinde yeterli odun varsa inşaat başlat"""
        try:
            # Kale yoksa çık
            if not self.castle:
                return
                
            # Envanteri kontrol et
            wood_amount = self.castle.get_inventory().get('odun', 0)
            
            # 30 odun varsa ve aktif bir inşaatçı varsa inşaat başlat
            if wood_amount >= 30:
                # İnşaatçıları bul
                builders = [v for v in self.villagers if v.profession == "İnşaatçı"]
                
                if not builders:
                    return  # İnşaatçı yok
                
                # Günlük limiti dolmamış bir inşaatçı bul
                available_builders = [b for b in builders if b.buildings_built < b.max_buildings_per_day]
                
                if not available_builders:
                    return  # Müsait inşaatçı yok
                
                # Rastgele bir inşaatçı seç
                builder = random.choice(available_builders)
                
                # Potansiyel ev konumlarını belirle
                potential_locations = self.find_potential_building_locations()
                
                # Uygun konum yoksa minimum mesafeyi azaltarak tekrar dene
                if not potential_locations:
                    print("Normal mesafe ile uygun inşaat alanı bulunamadı, daha sıkışık deneniyor...")
                    potential_locations = self.find_potential_building_locations(min_distance=60)
                
                # Hala bulunamadıysa daha da azalt
                if not potential_locations:
                    print("Mesafe 60 ile uygun inşaat alanı bulunamadı, daha da sıkışık deneniyor...")
                    potential_locations = self.find_potential_building_locations(min_distance=40)
                
                if not potential_locations:
                    print("Uygun inşaat alanı bulunamadı! Minimum mesafe 40 ile bile bulunamadı.")
                    return False
                
                # Rastgele bir konum seç
                building_x = random.choice(potential_locations)
                
                # İnşaat alanı oluştur
                building_site = self.create_building_site(building_x, self.ground_y, min_distance=min(80, 40 if len(potential_locations) <= 3 else 60 if len(potential_locations) <= 5 else 80))
                
                if building_site:
                    # İnşaatı başlat
                    if building_site.start_construction(builder):
                        # İnşaatçının durum bilgilerini güncelle
                        builder.is_building = True
                        builder.target_building_site = building_site
                        builder.state = "İnşaat Yapıyor"
                        print(f"{builder.name} yeni bir ev inşaatına başladı! Konum: {building_x}")
                        return True
                
            return False
                
        except Exception as e:
            print(f"HATA: Otomatik inşaat kontrolü: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def find_potential_building_locations(self, min_distance=80):
        """Ev inşaatı için potansiyel konumlar bulur"""
        try:
            MIN_BUILDING_DISTANCE = min_distance  # Yapılar arası minimum mesafe
            potential_locations = []
            
            # Ekran genişliğini ve kullanılabilir alanı hesapla
            # Ekranın sol sınırı 100, sağ sınırı 1820 piksel olarak kabul edelim
            left_boundary = 100  # Ekranın solunda da yer olsun
            right_boundary = 1820
            
            # 100 piksel aralıklarla potansiyel konumları kontrol et
            step_size = 100
            
            for x in range(int(left_boundary), int(right_boundary - MIN_BUILDING_DISTANCE), step_size):
                # Bu konumun uygun olup olmadığını kontrol et
                is_suitable = True
                
                # Kaleye çok yakın mı kontrol et
                if hasattr(self, 'castle') and self.castle:
                    castle_x = self.castle.x
                    castle_width = self.castle.width
                    if abs(x - (castle_x + castle_width / 2)) < MIN_BUILDING_DISTANCE:
                        is_suitable = False
                        continue
                
                # Diğer inşaat alanlarını kontrol et
                for site in self.building_sites:
                    if abs(site.x - x) < MIN_BUILDING_DISTANCE:
                        is_suitable = False
                        break
                
                # Evleri kontrol et
                if is_suitable:
                    for house in self.houses:
                        if abs(house.x - x) < MIN_BUILDING_DISTANCE:
                            is_suitable = False
                            break
                
                # Kiliseyi kontrol et (310 civarında)
                if is_suitable and abs(310 - x) < MIN_BUILDING_DISTANCE:
                    is_suitable = False
                
                # Pazarı kontrol et
                if is_suitable and hasattr(self, 'market') and self.market:
                    if abs(self.market.x - x) < MIN_BUILDING_DISTANCE:
                        is_suitable = False
                
                # Eğer uygunsa listeye ekle
                if is_suitable:
                    potential_locations.append(x)
            
            # Konumları biraz rastgele yap
            if potential_locations:
                # Her bir konuma +-10 piksel rastgele değişim ekle
                potential_locations = [x + random.randint(-10, 10) for x in potential_locations]
                # Uzun bir liste ise, en fazla 10 konum seç
                if len(potential_locations) > 10:
                    potential_locations = random.sample(potential_locations, 10)
            
            print(f"Potansiyel inşaat konumları bulundu (min. mesafe: {min_distance}): {len(potential_locations)} adet")
            if potential_locations:
                print(f"Örnek konumlar: {potential_locations[:3]}")
            return potential_locations
        
        except Exception as e:
            print(f"HATA: Potansiyel inşaat konumları bulunurken hata: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def update_time(self):
        """Zamanı güncelle"""
        try:
            # Güncel zaman
            current_time = time.time()
            
            # Tüm köylü davranışlarını güncelle
            for villager in self.villagers:
                if hasattr(villager, 'update_behavior_tree'):
                    villager.update_behavior_tree()
                else:
                    villager.move()
            
            # Kurt hareketlerini güncelle
            for wolf in self.wolves:
                if hasattr(wolf, 'update'):
                    wolf.update()
            
            # İnşaat alanlarını güncelle
            self.update_building_sites()
            
            # Her bir saniyede bir güncellenen işlemler
            if current_time - self.last_resource_update > 1.0:
                self.last_resource_update = current_time
                
                # Kaynakları güncelle
                self.update_resources()
                
                # Gündüz/gece döngüsünü güncelle
                self.update_day_night_cycle()
            
            # Her 10 saniyede bir güncellenen işlemler
            if current_time - self.last_periodic_update > 10.0:
                self.last_periodic_update = current_time
                
                # Çalışma bölgelerini güncelle
                self.update_work_areas()
                
                # Köylü ihtiyaçlarını güncelle
                self.update_villager_needs()
            
        except Exception as e:
            print(f"HATA: Oyun döngüsü güncelleme hatası: {e}")
            import traceback
            traceback.print_exc() 