from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QRect, QTimer, QPoint
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow
from PyQt5.QtGui import QScreen, QColor
from src.models.building import Building
from src.models.villager import Villager
from src.models.tree import Tree
import random
import os

class GameController(QObject):
    """Oyun kontrolcü sınıfı"""
    villagers_updated = pyqtSignal(list)  # Köylü listesi güncellendiğinde sinyal gönder
    day_night_changed = pyqtSignal(bool)  # Gece/gündüz değiştiğinde sinyal gönder (True = Gündüz)
    
    def __init__(self):
        super().__init__()
        
        print("GameController başlatılıyor...")
        
        # Gece/Gündüz sistemi için değişkenler
        self.is_daytime = True  # True = Gündüz, False = Gece
        self.day_duration = 300  # 5 dakika
        self.night_duration = 180  # 3 dakika
        self.day_night_timer = QTimer()
        self.day_night_timer.timeout.connect(self.toggle_day_night)
        self.remaining_time = 0  # Kalan süre (milisaniye cinsinden)
        
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
        self.ground_height = 200
        
        # Zeminin y pozisyonunu ekranın en altına ayarla
        self.ground_y = max_height - self.ground_height
        
        # Oyun nesneleri
        self.buildings: List[Building] = []
        self.trees: List[Tree] = []
        self.villagers: List[Villager] = []
        self.selected_villager: Optional[Villager] = None
        
        # Döngüsel import sorununu çözmek için, GameWindow sınıfını import etmek yerine,
        # QMainWindow sınıfını kullanacağız ve pencereyi daha sonra oluşturacağız
        self.window = None
        
        # Timer
        self.update_timer = None
        
        # NOT: setup_game() ve window.show() çağrıları kaldırıldı
    
    def setup_game(self):
        """Oyunu kur"""
        try:
            print("Oyun kuruluyor...")
            
            # Gece/gündüz döngüsünü başlat
            self.start_day_night_cycle()
            
            # Zemin seviyesi - sabit değer
            self.ground_y = 64
            print(f"Zemin seviyesi: {self.ground_y}")
            
            # Binaları oluştur
            self.buildings = []
            
            # Kaleyi oluştur
            castle = Building(
                x=100,
                y=self.ground_y - 150,  # Zemin üzerinde
                width=150,
                height=150,
                building_type="castle"
            )
            self.buildings.append(castle)
            print(f"Kale oluşturuldu: ({castle.x}, {castle.y}), {castle.width}x{castle.height}")
            
            # Ağaçları oluştur
            self.create_trees()
            
            # Köylüleri oluştur
            self.create_initial_villagers()
            
            # Timer'ı başlat
            self.update_timer = QTimer()
            self.update_timer.setInterval(50)  # 50 ms'de bir güncelle (daha sık güncelleme)
            self.update_timer.timeout.connect(self.update_game)
            self.update_timer.start()
            print("Timer başlatıldı")
            
            print("Oyun kurulumu tamamlandı")
            
        except Exception as e:
            print(f"HATA: Oyun kurulumu hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def create_trees(self):
        """Ağaçları oluştur"""
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
    
    def create_initial_villagers(self):
        """Başlangıç köylülerini oluştur"""
        try:
            print("Başlangıç köylüleri oluşturuluyor...")
            
            # Erkek isimleri
            male_names = [
                "Ahmet", "Mehmet", "Ali", "Veli", "Hasan", "Hüseyin", "İbrahim",
                "Mustafa", "Ömer", "Yusuf", "Kemal", "Murat", "Emre", "Burak"
            ]
            
            # Kadın isimleri
            female_names = [
                "Ayşe", "Fatma", "Zeynep", "Emine", "Hatice", "Meryem", "Elif",
                "Esra", "Selin", "Deniz", "Berna", "Gizem", "Selin", "Berna"
            ]
            
            # Meslekler
            professions = [
                "Çiftçi", "Oduncu", "Madenci", "Balıkçı", "Avcı", "Tüccar",
                "Demirci", "Marangoz", "Dokumacı", "Aşçı", "Bahçıvan", "Çoban"
            ]
            
            # İlk köylüyü erkek olarak oluştur
            first_villager = Villager(
                name=random.choice(male_names),
                gender="Erkek",
                profession=random.choice(professions),
                appearance=random.randint(0, 3)
            )
            self.villagers.append(first_villager)
            
            # İkinci köylüyü kadın olarak oluştur
            second_villager = Villager(
                name=random.choice(female_names),
                gender="Kadın",
                profession=random.choice(professions),
                appearance=random.randint(0, 3)
            )
            self.villagers.append(second_villager)
            
            # Diğer köylüleri rastgele cinsiyetle oluştur
            for _ in range(3):  # 3 köylü daha
                gender = random.choice(["Erkek", "Kadın"])
                name = random.choice(male_names if gender == "Erkek" else female_names)
                villager = Villager(
                    name=name,
                    gender=gender,
                    profession=random.choice(professions),
                    appearance=random.randint(0, 3)
                )
                self.villagers.append(villager)
            
            # Köylü listesini güncelle
            self.villagers_updated.emit(self.villagers)
            
            print(f"Başlangıç köylüleri oluşturuldu: {len(self.villagers)} köylü")
            
        except Exception as e:
            print(f"HATA: Köylü oluşturma hatası: {e}")
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
    
    def update_game(self):
        """Oyunu güncelle"""
        try:
            # Statik değişken - güncelleme sayacı
            if not hasattr(self, '_update_count'):
                self._update_count = 0
            self._update_count += 1
            
            # Her 10 güncellemede bir debug mesajı
            if self._update_count % 10 == 0:
                print(f"Oyun güncelleniyor... (güncelleme sayısı: {self._update_count})")
            
            # Köylüleri hareket ettir
            try:
                for villager in self.villagers:
                    # Gece ise ve köylü kaleye dönmediyse
                    if not self.is_daytime and villager.x > 150:  # 150 = kale pozisyonu
                        # Köylüyü kaleye doğru hareket ettir
                        if villager.x > 150:
                            villager.x -= 5  # Sola doğru hareket
                        villager.direction = -1  # Sola baksın
                        villager.update_animation()
                    # Gündüz ise normal hareket
                    elif self.is_daytime:
                        # Köylüyü hareket ettir
                        villager.move()
                        # Animasyonu güncelle
                        villager.update_animation()
            except Exception as e:
                print(f"HATA: Köylü hareketi sırasında hata: {e}")
                import traceback
                traceback.print_exc()
            
            # Oyun penceresini güncelle
            if self.window:
                # Ekranı güncelle
                self.window.update()
                
                # Timer'ı yeniden başlat - sürekli güncelleme için
                QTimer.singleShot(0, self.update_timer.start)
            
        except Exception as e:
            print(f"HATA: Oyun güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def start_day_night_cycle(self):
        """Gündüz/gece döngüsünü başlat"""
        try:
            # Gündüz süresi (5 dakika = 300 saniye)
            self.day_duration = 300
            # Gece süresi (3 dakika = 180 saniye)
            self.night_duration = 180
            
            # Başlangıçta gündüz
            self.is_night = False
            self.remaining_time = self.day_duration
            
            # Timer'ı başlat
            self.day_night_timer = QTimer()
            self.day_night_timer.timeout.connect(self.update_day_night)
            self.day_night_timer.start(1000)  # Her saniye güncelle
            
            print("Gündüz/gece döngüsü başlatıldı")
            
        except Exception as e:
            print(f"HATA: Gündüz/gece döngüsü başlatılamadı: {e}")
            import traceback
            traceback.print_exc()
    
    def update_day_night(self):
        """Gündüz/gece durumunu güncelle"""
        try:
            # Kalan süreyi azalt
            self.remaining_time -= 1
            
            # Kontrol panelini güncelle
            if hasattr(self, 'main_window') and hasattr(self.main_window, 'control_panel_window'):
                control_panel = self.main_window.control_panel_window.control_panel
                control_panel.update_day_night(self.is_night, self.remaining_time)
            
            # Süre doldu mu kontrol et
            if self.remaining_time <= 0:
                # Gece/gündüz durumunu değiştir
                self.is_night = not self.is_night
                
                # Yeni süreyi ayarla
                if self.is_night:
                    self.remaining_time = self.night_duration
                    print("Gece başladı")
                    # Köylüleri kaleye döndür
                    self.return_villagers_to_castle()
                else:
                    self.remaining_time = self.day_duration
                    print("Gündüz başladı")
                    # Köylüleri tekrar dolaşmaya başlat
                    self.start_villagers_wandering()
            
        except Exception as e:
            print(f"HATA: Gündüz/gece durumu güncellenemedi: {e}")
            import traceback
            traceback.print_exc()
    
    def return_villagers_to_castle(self):
        """Köylüleri kaleye döndür"""
        try:
            for villager in self.villagers:
                # Köylünün hedefini kaleye ayarla
                villager.target_x = 100  # Kale x pozisyonu
                villager.target_y = self.main_window.height() - 150  # Kale y pozisyonu
                villager.is_moving = True
                
            print("Köylüler kaleye dönüyor")
            
        except Exception as e:
            print(f"HATA: Köylüler kaleye döndürülemedi: {e}")
            import traceback
            traceback.print_exc()
    
    def start_villagers_wandering(self):
        """Köylüleri tekrar dolaşmaya başlat"""
        try:
            for villager in self.villagers:
                # Köylünün hedefini rastgele bir noktaya ayarla
                villager.target_x = random.randint(0, self.main_window.width())
                villager.target_y = self.main_window.height() - 100
                villager.is_moving = True
                
            print("Köylüler tekrar dolaşmaya başladı")
            
        except Exception as e:
            print(f"HATA: Köylüler dolaşmaya başlatılamadı: {e}")
            import traceback
            traceback.print_exc()
    
    def get_remaining_time(self) -> tuple[int, int]:
        """Kalan süreyi dakika ve saniye olarak döndür"""
        minutes = self.remaining_time // 60000  # milisaniyeyi dakikaya çevir
        seconds = (self.remaining_time % 60000) // 1000  # kalan milisaniyeyi saniyeye çevir
        return minutes, seconds
    
    def toggle_day_night(self):
        """Gündüz/gece döngüsünü değiştir"""
        try:
            self.is_daytime = not self.is_daytime
            
            # Sinyal gönder
            self.day_night_changed.emit(self.is_daytime)
            
            # Timer'ı yeni süreye ayarla
            new_duration = self.day_duration if self.is_daytime else self.night_duration
            self.day_night_timer.setInterval(new_duration * 1000)
            
            print(f"Gündüz/gece değişti: {'Gündüz' if self.is_daytime else 'Gece'}")
            
        except Exception as e:
            print(f"HATA: Gündüz/gece değiştirme hatası: {e}")
            import traceback
            traceback.print_exc() 