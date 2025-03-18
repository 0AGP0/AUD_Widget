from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QRect, QTimer, QPoint
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow
from PyQt5.QtGui import QScreen, QColor
try:
    from src.models.building import Building
except ImportError:
    # Alternatif import yöntemi
    import sys
    from pathlib import Path
    src_dir = str(Path(__file__).resolve().parent.parent.parent)
    if src_dir not in sys.path:
        sys.path.append(src_dir)
    from src.models.building import Building

from src.models.villager import Villager, TestVillager
from src.models.tree import Tree
from src.models.building_site import BuildingSite
from src.models.house import House
import random
import os
import time

class GameController(QObject):
    """Oyun kontrolcü sınıfı"""
    villagers_updated = pyqtSignal(list)  # Köylü listesi güncellendiğinde sinyal gönder
    day_night_changed = pyqtSignal(bool)  # Gece/gündüz değiştiğinde sinyal gönder (True = Gündüz)
    chat_message = pyqtSignal(object, str)  # Köylü ve mesaj sinyali
    
    DAY_DURATION = 300  # 5 dakika (saniye cinsinden)
    NIGHT_DURATION = 180  # 3 dakika (saniye cinsinden)
    
    def __init__(self):
        super().__init__()
        
        print("GameController başlatılıyor...")
        
        # Gece/Gündüz sistemi için değişkenler
        self.is_daytime = True  # True = Gündüz, False = Gece
        self.remaining_time = self.DAY_DURATION * 1000  # Milisaniye cinsinden
        
        # Tüm ekranları al
        desktop = QDesktopWidget()
        
        # Ekran sayısını ve toplam genişliği hesapla
        screen_count = desktop.screenCount()
        total_width = 0
        min_x = float('inf')
        max_height = 0
        
        print(f"Ekran sayısı: {screen_count}")
        
        # Her ekranın bilgilerini topla
        for i in range(screen_count):
            screen_geo = desktop.screenGeometry(i)
            total_width += screen_geo.width()
            min_x = min(min_x, screen_geo.x())
            max_height = max(max_height, screen_geo.height())
            print(f"Ekran {i+1}: ({screen_geo.x()}, {screen_geo.y()}, {screen_geo.width()}x{screen_geo.height()})")
        
        # Zemin yüksekliği
        self.ground_height = 800  # Zemin yüksekliği
        
        # Zeminin y pozisyonunu ekranın en altına ayarla
        self.ground_y = max_height - self.ground_height
        
        # Oyun nesneleri
        print("Oyun nesneleri oluşturuluyor...")
        self.buildings = []
        self.trees = []
        self.villagers = []
        self.building_sites = []  # İnşaat alanları
        self.houses = []  # Evler
        self.selected_villager = None
        
        # Döngüsel import sorununu çözmek için, GameWindow sınıfını import etmek yerine,
        # QMainWindow sınıfını kullanacağız ve pencereyi daha sonra oluşturacağız
        self.window = None
        
        # Kontrol paneli referansı
        self.control_panel = None
        
        # Sadece bir zamanlayıcı kullan - kalan süreyi güncelle
        print("Zamanlayıcı oluşturuluyor...")
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_remaining_time)
        self.time_timer.start(1000)  # Her saniye güncelle
        
        print("GameController başlatıldı")
        # NOT: setup_game() ve window.show() çağrıları kaldırıldı
    
    def setup_game(self):
        """Oyunu başlat ve gerekli nesneleri oluştur"""
        try:
            print("Oyun kuruluyor...")
            
            # Gece/gündüz döngüsünü başlat
            print("Gece/gündüz döngüsü başlatılıyor...")
            self.start_day_night_cycle()
            
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
            
            # Ağaçları oluştur
            print("Ağaçlar oluşturuluyor...")
            self.create_trees()
            print(f"{len(self.trees)} ağaç oluşturuldu")
            
            # Köylüleri oluştur
            print("Köylüler oluşturuluyor...")
            self.create_initial_villagers()
            print(f"{len(self.villagers)} köylü oluşturuldu")
            
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
            self.timer.start(16)  # ~60 FPS
            
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
            tree_width = 80
            tree_height = 120
            
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
                        # Ağacı oluştur
                        tree = Tree(
                            x=x,  # Rastgele x pozisyonu
                            y=0,  # Y pozisyonu çizim sırasında hesaplanacak
                            width=tree_width,  # Sabit genişlik
                            height=tree_height,  # Sabit yükseklik
                        )
                        
                        # Ağacı listeye ekle
                        self.trees.append(tree)
                        total_trees += 1
                        trees_in_region += 1
                        print(f"Ağaç {total_trees} oluşturuldu: ({tree.x:.1f}, {tree.y}), bölge: {region+1}")
                    
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
            professions = ["Oduncu", "İnşaatçı", "Avcı", "Çiftçi", "Gardiyan", "Papaz"]
            
            # Zorunlu meslekleri takip etmek için
            has_lumberjack = False  # Oduncu
            has_builder = False     # İnşaatçı
            has_guard = False       # Gardiyan
            has_priest = False      # Papaz
            
            # Erkek ve kadın isimleri
            male_names = ["Ahmet", "Mehmet", "Ali", "Mustafa", "Hasan", "Hüseyin", "İbrahim", "Osman", "Yusuf", "Murat"]
            female_names = ["Ayşe", "Fatma", "Zeynep", "Emine", "Hatice", "Merve", "Elif", "Esra", "Seda", "Gül"]
            
            print(f"Erkek isimleri: {male_names}")
            print(f"Kadın isimleri: {female_names}")
            
            # 6 köylü oluştur (4 yerine 6)
            for i in range(6):
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
                
                # Meslek atama stratejisi
                # Son köylüye geldiğimizde eksik zorunlu meslekleri kontrol et
                if i == 5:  # Son köylü
                    if not has_lumberjack:
                        profession = "Oduncu"
                        has_lumberjack = True
                    elif not has_builder:
                        profession = "İnşaatçı"
                        has_builder = True
                    elif not has_guard:
                        profession = "Gardiyan"
                        has_guard = True
                    elif not has_priest:
                        profession = "Papaz"
                        has_priest = True
                    else:
                        # Tüm zorunlu meslekler atanmışsa, kalan mesleklerden birini seç
                        available_professions = [p for p in professions if p not in ["Oduncu", "İnşaatçı", "Gardiyan", "Papaz"] or 
                                                (p == "Papaz" and not has_priest)]
                        profession = random.choice(available_professions)
                elif i == 4:  # 5. köylü
                    # Eksik zorunlu meslekleri kontrol et
                    missing_required = []
                    if not has_lumberjack:
                        missing_required.append("Oduncu")
                    if not has_builder:
                        missing_required.append("İnşaatçı")
                    if not has_guard:
                        missing_required.append("Gardiyan")
                    if not has_priest:
                        missing_required.append("Papaz")
                    
                    if missing_required:
                        profession = random.choice(missing_required)
                        if profession == "Oduncu":
                            has_lumberjack = True
                        elif profession == "İnşaatçı":
                            has_builder = True
                        elif profession == "Gardiyan":
                            has_guard = True
                        elif profession == "Papaz":
                            has_priest = True
                    else:
                        # Tüm zorunlu meslekler atanmışsa, kalan mesleklerden birini seç
                        available_professions = [p for p in professions if p not in ["Papaz"] or 
                                                (p == "Papaz" and not has_priest)]
                        profession = random.choice(available_professions)
                        if profession == "Papaz":
                            has_priest = True
                else:
                    # İlk 4 köylü için rastgele meslek ata, ancak Papaz'ı sadece bir kişiye ata
                    if not has_priest and random.random() < 0.2:  # %20 şans
                        profession = "Papaz"
                        has_priest = True
                    elif not has_lumberjack and random.random() < 0.3:  # %30 şans
                        profession = "Oduncu"
                        has_lumberjack = True
                    elif not has_builder and random.random() < 0.3:  # %30 şans
                        profession = "İnşaatçı"
                        has_builder = True
                    elif not has_guard and random.random() < 0.3:  # %30 şans
                        profession = "Gardiyan"
                        has_guard = True
                    else:
                        # Papaz hariç diğer mesleklerden birini seç
                        available_professions = [p for p in professions if p != "Papaz" or 
                                                (p == "Papaz" and not has_priest)]
                        profession = random.choice(available_professions)
                        if profession == "Oduncu":
                            has_lumberjack = True
                        elif profession == "İnşaatçı":
                            has_builder = True
                        elif profession == "Gardiyan":
                            has_guard = True
                        elif profession == "Papaz":
                            has_priest = True
                
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
            print(f"Oduncu: {'Var' if has_lumberjack else 'Yok'}")
            print(f"İnşaatçı: {'Var' if has_builder else 'Yok'}")
            print(f"Gardiyan: {'Var' if has_guard else 'Yok'}")
            print(f"Papaz: {'Var' if has_priest else 'Yok'}")
            
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
        """Oyun durumunu güncelle"""
        try:
            # Köylüleri güncelle
            for villager in self.villagers:
                # Davranış ağacı ile güncelleme
                if hasattr(villager, 'update_behavior_tree'):
                    villager.update_behavior_tree()
                else:
                    # Eski hareket sistemi
                    villager.move()
                    villager.update_animation()
            
            # Ağaç animasyonlarını güncelle
            for tree in self.trees:
                tree.update_animation()
            
            # Köylü listesi güncellendiğinde sinyal gönder
            self.villagers_updated.emit(self.villagers)
            
            # Oyun penceresini güncelle
            if hasattr(self, 'window'):
                self.window.update()
                
        except Exception as e:
            print(f"HATA: Oyun güncelleme hatası: {e}")
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
    
    def get_remaining_time(self) -> tuple[int, int]:
        """Kalan süreyi dakika ve saniye olarak döndür"""
        minutes = self.remaining_time // 60000  # milisaniyeyi dakikaya çevir
        seconds = (self.remaining_time % 60000) // 1000  # kalan milisaniyeyi saniyeye çevir
        return minutes, seconds
    
    def update_remaining_time(self):
        """Kalan süreyi güncelle"""
        try:
            # Kalan süreyi azalt
            self.remaining_time -= 1000  # Her saniye 1000 milisaniye azalt
            
            # Kalan süre bittiyse gece-gündüz değişimi yap
            if self.remaining_time <= 0:
                # Gündüz/gece durumunu değiştir
                self.is_daytime = not self.is_daytime
                
                # Yeni süreyi ayarla
                if self.is_daytime:
                    self.remaining_time = self.DAY_DURATION * 1000  # Gündüz süresi
                    print(f"Gündüz başladı. Süre: {self.DAY_DURATION} saniye")
                    
                    # Gündüz başladığında köylüleri dolaşmaya başlat
                    for villager in self.villagers:
                        if villager.profession == "Oduncu":
                            villager.trees_cut_today = 0
                            print(f"{villager.name} yeni güne başladı, kesme hakkı: {villager.max_trees_per_day}")
                        elif villager.profession == "İnşaatçı":
                            villager.buildings_built = 0
                            print(f"{villager.name} yeni güne başladı, inşaat hakkı: {villager.max_buildings_per_day}")
                    self.start_villagers_wandering()
                else:
                    self.remaining_time = self.NIGHT_DURATION * 1000  # Gece süresi
                    print(f"Gece başladı. Süre: {self.NIGHT_DURATION} saniye")
                    
                    # Gece başladığında köylüleri kaleye döndür
                    self.return_villagers_to_castle()
                
                # Sinyal gönder
                self.day_night_changed.emit(self.is_daytime)
                print(f"Gündüz/gece değişti: {'Gündüz' if self.is_daytime else 'Gece'}")
            
            # Kontrol panelini güncelle
            if hasattr(self, 'control_panel') and self.control_panel:
                # Kontrol paneli hazırsa update_time_label metodunu çağır
                if hasattr(self.control_panel, 'update_time_label'):
                    self.control_panel.update_time_label()
            
        except Exception as e:
            print(f"HATA: Kalan süre güncelleme hatası: {e}")
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
            tree_width = 80
            tree_height = 120
            
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
            
            new_tree = Tree(x, y, tree_width, tree_height)
            new_tree.tree_removed.connect(self.on_tree_removed)
            self.trees.append(new_tree)
            
            print(f"Yeni ağaç eklendi: ID: {new_tree.id}, Konum: ({x}, {y})")
            
        except Exception as e:
            print(f"HATA: Yeni ağaç ekleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def set_control_panel(self, control_panel):
        """Kontrol panelini ayarla"""
        try:
            self.control_panel = control_panel
            # İlk köylü listesini güncelle
            if self.villagers:
                self.villagers_updated.emit(self.villagers)
            print("Kontrol paneli başarıyla ayarlandı")
        except Exception as e:
            print(f"HATA: Kontrol paneli ayarlanırken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def create_building_site(self, x: float, y: float) -> BuildingSite:
        """İnşaat alanı oluştur"""
        try:
            # Zemin seviyesini kullan
            ground_y = self.ground_y
            
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
            
            # Listeye ekle
            self.houses.append(house)
            
            # İnşaat alanını listeden kaldır
            for i, site in enumerate(self.building_sites[:]):
                if site.id == building_site.id:
                    self.building_sites.pop(i)
                    print(f"İnşaat alanı ID: {building_site.id} listeden kaldırıldı")
                    break
            
            # Ev satın alma işlemini başlat
            self.try_sell_house(house)
            
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
                
            # Satın alabilecek köylüleri bul (5 altın veya daha fazlası olanlar)
            potential_buyers = [v for v in self.villagers if v.money >= 5 and not v.has_house]
            
            if not potential_buyers:
                print(f"Ev ID: {house.id} için alıcı bulunamadı!")
                return
                
            # Rastgele bir alıcı seç
            buyer = random.choice(potential_buyers)
            
            # Evi sat
            house_price = 5  # Ev fiyatını düşürdük (10'dan 5'e)
            buyer.money -= house_price
            house.set_owner(buyer.name)
            
            # Köylünün ev sahibi olduğunu işaretle
            buyer.has_house = True
            buyer.house_id = house.id
            
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
                villager.target_x = random.randint(100, 800)  # Kale etrafında rastgele bir nokta
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
                    target_x = castle.get_entrance()[0]
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
    
    def create_dialogue_bubble(self, villager, message):
        """Köylü için diyalog baloncuğu oluşturur"""
        try:
            # Köylünün chat_message ve chat_bubble_visible özelliklerini ayarla
            villager.chat_message = message
            villager.chat_bubble_visible = True
            villager.chat_bubble_time = time.time()
            
            # Sinyal gönder
            self.chat_message.emit(villager, message)
            
            # Konsola yazdır
            print(f"💬 {villager.name}: {message}")
            
            # Bubble ID olarak zamanı kullan
            bubble_id = time.time()
            
            # QTimer.singleShot için (tek seferlik) bir zamanlayıcı oluştur
            QTimer.singleShot(5000, lambda: self.remove_dialogue_bubble(bubble_id))
            
            return bubble_id
            
        except Exception as e:
            print(f"HATA: Diyalog baloncuğu oluşturma hatası: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def remove_dialogue_bubble(self, bubble_id):
        """Diyalog baloncuğunu kaldırır"""
        try:
            # Tüm köylüleri kontrol et
            for villager in self.villagers:
                # Baloncuğun zamanı bubble_id ile eşleşiyorsa kaldır
                if hasattr(villager, 'chat_bubble_time') and villager.chat_bubble_time == bubble_id:
                    villager.chat_bubble_visible = False
                    villager.chat_message = ""
                    return True
            
            return False
            
        except Exception as e:
            print(f"HATA: Diyalog baloncuğu kaldırma hatası: {e}")
            import traceback
            traceback.print_exc()
            return False 