from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QRect, QTimer, QPoint
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow
from PyQt5.QtGui import QScreen, QColor
from src.models.building import Building
from src.models.villager import Villager, TestVillager
from src.models.tree import Tree
import random
import os
import time

class GameController(QObject):
    """Oyun kontrolcü sınıfı"""
    villagers_updated = pyqtSignal(list)  # Köylü listesi güncellendiğinde sinyal gönder
    day_night_changed = pyqtSignal(bool)  # Gece/gündüz değiştiğinde sinyal gönder (True = Gündüz)
    
    DAY_DURATION = 300  # 5 dakika (saniye cinsinden)
    NIGHT_DURATION = 180  # 3 dakika (saniye cinsinden)
    
    def __init__(self):
        super().__init__()
        
        print("GameController başlatılıyor...")
        
        # Gece/Gündüz sistemi için değişkenler
        self.is_daytime = True  # True = Gündüz, False = Gece
        self.remaining_time = self.DAY_DURATION * 1000
        
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
        self.selected_villager = None
        
        # Döngüsel import sorununu çözmek için, GameWindow sınıfını import etmek yerine,
        # QMainWindow sınıfını kullanacağız ve pencereyi daha sonra oluşturacağız
        self.window = None
        
        # Kontrol paneli referansı
        self.control_panel = None
        
        # Timer
        print("Zamanlayıcılar oluşturuluyor...")
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.toggle_day_night)
        self.update_timer.start(self.DAY_DURATION * 1000)  # Milisaniye cinsinden
        
        # Kalan süre için timer
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
            self.castle = Building(x=400, y=self.ground_y, width=150, height=150, building_type="castle")
            print("Kale oluşturuldu")
            
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
            
            # Kale pozisyonu (varsayılan olarak x=100)
            castle_x = 100
            
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
            professions = ["Oduncu", "Madenci", "İnşaatcı", "İşsiz", "Sanatçı"]
            has_lumberjack = False
            
            # Erkek ve kadın isimleri
            male_names = ["Ahmet", "Mehmet", "Ali", "Mustafa", "Hasan", "Hüseyin", "İbrahim", "Osman", "Yusuf", "Murat"]
            female_names = ["Ayşe", "Fatma", "Zeynep", "Emine", "Hatice", "Merve", "Elif", "Esra", "Seda", "Gül"]
            
            print(f"Erkek isimleri: {male_names}")
            print(f"Kadın isimleri: {female_names}")
            
            # 4 köylü oluştur
            for i in range(4):
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
                    y=self.ground_height - 60,  # Zemin üzerinde
                    gender=gender,
                    appearance=appearance
                )
                
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
                
                # Son köylü ve hala oduncu yoksa, oduncu yap
                if i == 3 and not has_lumberjack:
                    profession = "Oduncu"
                    has_lumberjack = True
                else:
                    # Meslek seçimi
                    if not has_lumberjack and random.random() < 0.4:  # %40 şans
                        profession = "Oduncu"
                        has_lumberjack = True
                    else:
                        available_professions = [p for p in professions if p != "Oduncu"]
                        profession = random.choice(available_professions)
                
                print(f"Meslek: {profession}")
                villager.set_profession(profession)
                villager.set_game_controller(self)
                self.villagers.append(villager)
                print(f"Köylü oluşturuldu: {villager.name} ({villager.gender}) - {profession}")
                print(f"  Özellikler: {', '.join(villager.traits)}")
                print(f"  Eşinde aradığı: {', '.join(villager.desired_traits)}")
            
            # Köylü listesini güncelle
            print(f"Köylü listesi güncelleniyor: {len(self.villagers)} köylü")
            self.villagers_updated.emit(self.villagers)
            
            print(f"Toplam köylü sayısı: {len(self.villagers)}")
            if has_lumberjack:
                print("En az bir oduncu başarıyla oluşturuldu!")
            
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
            villager_width = 40  # 60'dan 40'a düşürüldü
            villager_height = 40  # 60'dan 40'a düşürüldü
            
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
            
            # Timer'ı başlat
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.toggle_day_night)
            self.update_timer.start(self.DAY_DURATION * 1000)  # Milisaniye cinsinden
            
            print("Gündüz/gece döngüsü başlatıldı")
            
        except Exception as e:
            print(f"HATA: Gündüz/gece döngüsü başlatılamadı: {e}")
            import traceback
            traceback.print_exc()
    
    def toggle_day_night(self):
        """Gündüz/gece döngüsünü değiştir"""
        try:
            self.is_daytime = not self.is_daytime
            
            # Sinyal gönder
            self.day_night_changed.emit(self.is_daytime)
            
            # Timer'ı yeni süreye ayarla
            new_duration = self.DAY_DURATION if self.is_daytime else self.NIGHT_DURATION
            self.update_timer.setInterval(new_duration * 1000)
            
            # Gündüz başladıysa oduncuların kesme sayılarını sıfırla
            if self.is_daytime:
                for villager in self.villagers:
                    if villager.profession == "Oduncu":
                        villager.trees_cut_today = 0
                        print(f"{villager.name} yeni güne başladı, kesme hakkı: {villager.max_trees_per_day}")
                self.start_villagers_wandering()
            else:
                self.return_villagers_to_castle()
            
            print(f"Gündüz/gece değişti: {'Gündüz' if self.is_daytime else 'Gece'}")
            
        except Exception as e:
            print(f"HATA: Gündüz/gece değiştirme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def return_villagers_to_castle(self):
        """Köylüleri kaleye döndür"""
        try:
            for villager in self.villagers:
                # Köylünün hedefini kaleye ayarla
                villager.target_x = 100  # Kale x pozisyonu
                villager.target_y = self.ground_y - 150  # Kale y pozisyonu
                villager.is_moving = True
                villager.is_wandering = False  # Dolaşmayı durdur
                
                # Eğer oduncu ise kesme işlemini durdur
                if villager.profession == "Oduncu":
                    if villager.target_tree:
                        villager.target_tree.stop_cutting()
                    villager.is_cutting = False
                    villager.target_tree = None
                
                print(f"{villager.name} kaleye dönüyor")
            
            print("Tüm köylüler kaleye dönüyor")
            
        except Exception as e:
            print(f"HATA: Köylüler kaleye döndürülemedi: {e}")
            import traceback
            traceback.print_exc()
    
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
    
    def get_remaining_time(self) -> tuple[int, int]:
        """Kalan süreyi dakika ve saniye olarak döndür"""
        minutes = self.remaining_time // 60000  # milisaniyeyi dakikaya çevir
        seconds = (self.remaining_time % 60000) // 1000  # kalan milisaniyeyi saniyeye çevir
        return minutes, seconds
    
    def update_remaining_time(self):
        """Kalan süreyi güncelle"""
        self.remaining_time -= 1000
        if self.remaining_time <= 0:
            self.toggle_day_night()
    
    def on_tree_removed(self, tree):
        """Ağaç kesildiğinde çağrılır"""
        try:
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
            
        except Exception as e:
            print(f"HATA: Ağaç kaldırma hatası: {e}")
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
            
            # Kale pozisyonu (varsayılan olarak x=100)
            castle_x = 400
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