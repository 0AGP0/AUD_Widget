from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QFrame, QScrollArea, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from src.models.villager import Villager
from ..controllers.game_controller import GameController
import os

class VillagerInfoWidget(QWidget):
    """Köylü bilgi widget'ı"""
    def __init__(self, villager: Villager):
        super().__init__()
        self.villager = villager
        self.setup_ui()
        
        # Köylü resmini yükle
        self.load_villager_image()
    
    def load_villager_image(self):
        """Köylü resmini yükle"""
        try:
            # Resim dosya adını belirle
            if self.villager.gender == "Erkek":
                image_name = f"koylu{self.villager.appearance + 1}.png"
            else:
                image_name = f"kadin_koylu{self.villager.appearance + 1}.png"
            
            # Resim dosyasının tam yolunu oluştur
            image_path = os.path.join("assets", image_name)
            
            # Resmi yükle ve boyutlandır
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.villager_image.setPixmap(scaled_pixmap)
            else:
                print(f"UYARI: {image_path} dosyası bulunamadı!")
        except Exception as e:
            print(f"Köylü resmi yükleme hatası: {e}")
    
    def setup_ui(self):
        """Arayüzü hazırla"""
        layout = QVBoxLayout()
        
        # Üst kısım - Resim ve temel bilgiler
        top_layout = QHBoxLayout()
        
        # Köylü resmi
        self.villager_image = QLabel()
        self.villager_image.setFixedSize(50, 50)
        self.villager_image.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.villager_image)
        
        # İsim ve meslek
        info_layout = QVBoxLayout()
        name_label = QLabel(f"{self.villager.name} ({self.villager.gender})")
        name_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(name_label)
        
        profession_label = QLabel(self.villager.profession or "İşsiz")
        info_layout.addWidget(profession_label)
        
        top_layout.addLayout(info_layout)
        layout.addLayout(top_layout)
        
        # Özellikler
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Box)
        stats_layout = QVBoxLayout()
        
        # Sağlık
        health_bar = self.create_stat_bar("Sağlık", self.villager.health)
        stats_layout.addLayout(health_bar)
        
        # Para
        money_label = QLabel(f"Para: {self.villager.money}")
        stats_layout.addWidget(money_label)
        
        # Mutluluk
        happiness_bar = self.create_stat_bar("Mutluluk", self.villager.happiness)
        stats_layout.addLayout(happiness_bar)
        
        # Karizma
        charisma_bar = self.create_stat_bar("Karizma", self.villager.charisma)
        stats_layout.addLayout(charisma_bar)
        
        # Eğitim
        education_bar = self.create_stat_bar("Eğitim", self.villager.education)
        stats_layout.addLayout(education_bar)
        
        # Yaş
        age_label = QLabel(f"Yaş: {self.villager.age}")
        stats_layout.addWidget(age_label)
        
        stats_frame.setLayout(stats_layout)
        layout.addWidget(stats_frame)
        
        self.setLayout(layout)
    
    def create_stat_bar(self, name: str, value: int) -> QHBoxLayout:
        """İstatistik çubuğu oluştur"""
        layout = QHBoxLayout()
        
        label = QLabel(name)
        layout.addWidget(label)
        
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setValue(value)
        layout.addWidget(progress)
        
        return layout

class ControlPanel(QWidget):
    """Kontrol paneli widget'ı"""
    # Sinyaller
    close_game = pyqtSignal()
    minimize_game = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Oyun kontrolcüsü
        self.game_controller = None
        
        # Seçili köylü
        self.selected_villager = None
        
        # Panel özellikleri
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        self.dragging = False
        self.offset = QPoint()
        
        # Gece/Gündüz durumu
        self.is_night = False
        self.remaining_time = 0  # Kalan süre (saniye)
        
        # Timer'ı başlat
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_panel)
        self.timer.start(1000)  # Her saniye güncelle
        
        # Arayüzü oluştur
        self.setup_ui()
        
        # Debug bilgisi
        print("Kontrol paneli oluşturuldu")
    
    def setup_ui(self):
        """Arayüzü oluştur"""
        try:
            # Ana layout
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            self.setLayout(layout)
            
            # Başlık çubuğu
            title_bar = QFrame()
            title_bar.setObjectName("titleBar")
            title_bar.setFixedHeight(30)
            title_bar.setStyleSheet("""
                QFrame#titleBar {
                    background-color: #2c3e50;
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;
                }
            """)
            
            title_layout = QHBoxLayout()
            title_layout.setContentsMargins(10, 0, 0, 0)
            title_bar.setLayout(title_layout)
            
            # Başlık etiketi
            title_label = QLabel("Köylü Bilgileri")
            title_label.setStyleSheet("color: white; font-weight: bold;")
            title_layout.addWidget(title_label)
            
            # Gece/Gündüz göstergesi ve sayaç
            self.day_night_label = QLabel("Gündüz (5:00)")
            self.day_night_label.setStyleSheet("color: white; font-weight: bold;")
            title_layout.addWidget(self.day_night_label)
            
            # Butonlar için boşluk
            title_layout.addStretch()
            
            # Küçültme butonu
            minimize_btn = QPushButton("_")
            minimize_btn.setFixedSize(30, 30)
            minimize_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
            """)
            minimize_btn.clicked.connect(self.minimize_game.emit)
            title_layout.addWidget(minimize_btn)
            
            # Kapatma butonu
            close_btn = QPushButton("×")
            close_btn.setFixedSize(30, 30)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e74c3c;
                }
            """)
            close_btn.clicked.connect(self.close_game.emit)
            title_layout.addWidget(close_btn)
            
            layout.addWidget(title_bar)
            
            # İçerik widget'ı
            content_widget = QFrame()
            content_widget.setObjectName("contentWidget")
            content_widget.setStyleSheet("""
                QFrame#contentWidget {
                    background-color: rgba(44, 62, 80, 0.9);
                    border-bottom-left-radius: 5px;
                    border-bottom-right-radius: 5px;
                }
            """)
            
            content_layout = QVBoxLayout()
            content_layout.setContentsMargins(10, 10, 10, 10)
            content_widget.setLayout(content_layout)
            
            # Köylü listesi
            self.villager_list = QListWidget()
            self.villager_list.setStyleSheet("""
                QListWidget {
                    background-color: transparent;
                    border: none;
                    color: white;
                    font-size: 12px;
                }
                QListWidget::item {
                    padding: 5px;
                    border-bottom: 1px solid #34495e;
                }
                QListWidget::item:selected {
                    background-color: #34495e;
                    color: white;
                }
            """)
            self.villager_list.itemClicked.connect(self.on_villager_selected)
            content_layout.addWidget(self.villager_list)
            
            # Seçili köylü bilgileri
            self.villager_info = QFrame()
            self.villager_info.setStyleSheet("""
                QFrame {
                    background-color: rgba(52, 73, 94, 0.5);
                    border-radius: 5px;
                    padding: 10px;
                }
                QLabel {
                    color: white;
                    font-size: 12px;
                }
            """)
            info_layout = QVBoxLayout()
            self.villager_info.setLayout(info_layout)
            
            # Köylü bilgi etiketleri
            self.name_label = QLabel("İsim: ")
            self.gender_label = QLabel("Cinsiyet: ")
            self.profession_label = QLabel("Meslek: ")
            self.health_label = QLabel("Sağlık: ")
            self.money_label = QLabel("Para: ")
            self.happiness_label = QLabel("Mutluluk: ")
            
            info_layout.addWidget(self.name_label)
            info_layout.addWidget(self.gender_label)
            info_layout.addWidget(self.profession_label)
            info_layout.addWidget(self.health_label)
            info_layout.addWidget(self.money_label)
            info_layout.addWidget(self.happiness_label)
            
            content_layout.addWidget(self.villager_info)
            
            layout.addWidget(content_widget)
            
            # Sabit boyut
            self.setFixedSize(380, 500)
            
            print("Kontrol paneli arayüzü oluşturuldu")
            
        except Exception as e:
            print(f"HATA: Kontrol paneli arayüzü oluşturma hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def load_villager_image(self, villager):
        """Köylü resmini yükle"""
        try:
            # Resim dosya adını belirle
            if villager.gender == "Erkek":
                image_name = f"koylu{villager.appearance + 1}.png"
            else:
                image_name = f"kadin_koylu{villager.appearance + 1}.png"
            
            # Resim dosyasının tam yolunu oluştur
            current_dir = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(current_dir, "..", "assets")
            villagers_dir = os.path.join(assets_dir, "villagers")
            image_path = os.path.join(villagers_dir, image_name)
            
            # Debug bilgileri
            print(f"Köylü resmi yükleniyor:")
            print(f"  Köylü: {villager.name}")
            print(f"  Cinsiyet: {villager.gender}")
            print(f"  Görünüm: {villager.appearance}")
            print(f"  Resim adı: {image_name}")
            print(f"  Tam yol: {image_path}")
            print(f"  Klasör var mı: {os.path.exists(villagers_dir)}")
            print(f"  Resim var mı: {os.path.exists(image_path)}")
            
            # Villagers klasörünü kontrol et
            if not os.path.exists(villagers_dir):
                print(f"HATA: Villagers klasörü bulunamadı: {villagers_dir}")
                return None
            
            # Resmi yükle
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if pixmap.isNull():
                    print(f"HATA: Resim yüklenemedi: {image_path}")
                    return None
                    
                # Resmi 32x32 boyutuna küçült
                pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                print(f"Resim başarıyla yüklendi: {image_path}")
                return pixmap
            else:
                print(f"UYARI: Resim dosyası bulunamadı: {image_path}")
                return None
                
        except Exception as e:
            print(f"HATA: Köylü resmi yükleme hatası: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_villagers(self, villagers: list):
        """Köylü listesini güncelle"""
        try:
            print("Köylü listesi güncelleniyor...")
            self.villager_list.clear()
            
            for villager in villagers:
                # Liste öğesi oluştur
                item = QListWidgetItem()
                
                # Özel widget oluştur
                item_widget = QWidget()
                item_layout = QHBoxLayout()
                item_layout.setContentsMargins(5, 2, 5, 2)
                item_layout.setSpacing(10)
                
                # Köylü resmini yükle
                pixmap = self.load_villager_image(villager)
                if pixmap:
                    image_label = QLabel()
                    image_label.setFixedSize(32, 32)  # Sabit boyut ayarla
                    image_label.setAlignment(Qt.AlignCenter)  # Ortala
                    image_label.setPixmap(pixmap)
                    item_layout.addWidget(image_label)
                    print(f"Resim widget'a eklendi: {villager.name}")
                
                # İsim etiketi
                name_label = QLabel(villager.name)
                name_label.setStyleSheet("color: white; font-size: 12px;")
                item_layout.addWidget(name_label)
                
                # Layout'u widget'a ekle
                item_widget.setLayout(item_layout)
                
                # Widget'ı liste öğesine ekle
                item.setSizeHint(item_widget.sizeHint())
                self.villager_list.addItem(item)
                self.villager_list.setItemWidget(item, item_widget)
                
                print(f"Köylü listeye eklendi: {villager.name}")
            
            print(f"Köylü listesi güncellendi: {len(villagers)} köylü")
            
        except Exception as e:
            print(f"HATA: Köylü listesi güncellenirken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def mousePressEvent(self, event):
        """Fare tıklama olayı"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
    
    def mouseMoveEvent(self, event):
        """Fare hareket olayı"""
        if self.dragging:
            self.move(self.mapToGlobal(event.pos() - self.offset))
    
    def mouseReleaseEvent(self, event):
        """Fare bırakma olayı"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
    
    def set_game_controller(self, game_controller: GameController):
        """Oyun kontrolcüsünü ayarla"""
        try:
            self.game_controller = game_controller
            print("Oyun kontrolcüsü ayarlandı")
        except Exception as e:
            print(f"HATA: Oyun kontrolcüsü ayarlama hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def on_villager_selected(self, item: QListWidgetItem):
        """Köylü seçildiğinde"""
        try:
            # Seçilen köylüyü bul
            index = self.villager_list.row(item)
            if 0 <= index < len(self.game_controller.villagers):
                self.selected_villager = self.game_controller.villagers[index]
                self.update_villager_info(self.selected_villager)
                print(f"Köylü seçildi: {self.selected_villager.name}")
            
        except Exception as e:
            print(f"HATA: Köylü seçilirken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def update_villager_info(self, villager):
        """Köylü bilgilerini güncelle"""
        try:
            if villager:
                self.name_label.setText(f"İsim: {villager.name}")
                self.gender_label.setText(f"Cinsiyet: {villager.gender}")
                self.profession_label.setText(f"Meslek: {villager.profession}")
                self.health_label.setText(f"Sağlık: {villager.health}")
                self.money_label.setText(f"Para: {villager.money}")
                self.happiness_label.setText(f"Mutluluk: {villager.happiness}")
                print(f"Köylü bilgileri güncellendi: {villager.name}")
            
        except Exception as e:
            print(f"HATA: Köylü bilgileri güncellenirken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def update_panel(self):
        """Kontrol panelini güncelle"""
        try:
            if self.game_controller:
                # Gece/gündüz durumunu güncelle
                self.is_night = not self.game_controller.is_daytime
                self.remaining_time = self.game_controller.remaining_time
                
                # Etiketi güncelle
                minutes = self.remaining_time // 60
                seconds = self.remaining_time % 60
                time_str = f"{minutes:02d}:{seconds:02d}"
                
                if self.is_night:
                    self.day_night_label.setText(f"Gece ({time_str})")
                    self.day_night_label.setStyleSheet("color: #4444ff; font-weight: bold;")
                else:
                    self.day_night_label.setText(f"Gündüz ({time_str})")
                    self.day_night_label.setStyleSheet("color: #ffff44; font-weight: bold;")
                
                # Tüm paneli yenile
                self.update()
                print(f"Panel güncellendi: {'Gece' if self.is_night else 'Gündüz'} ({time_str})")
                
        except Exception as e:
            print(f"HATA: Panel güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def update_day_night(self, is_night, remaining_time):
        """Gece/Gündüz durumunu güncelle"""
        try:
            self.is_night = is_night
            self.remaining_time = remaining_time
            print(f"Gece/Gündüz güncellendi: {'Gece' if is_night else 'Gündüz'}, Kalan süre: {remaining_time} saniye")
            
        except Exception as e:
            print(f"HATA: Gece/Gündüz güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def update_day_night_style(self, is_daytime: bool):
        """Gündüz/gece durumunu güncelle"""
        try:
            # Gece/gündüz durumuna göre stil değiştir
            if is_daytime:
                self.setStyleSheet("""
                    QFrame#contentWidget {
                        background-color: rgba(44, 62, 80, 0.9);
                    }
                """)
            else:
                self.setStyleSheet("""
                    QFrame#contentWidget {
                        background-color: rgba(25, 25, 25, 0.9);
                    }
                """)
            
            print(f"Gece/gündüz durumu güncellendi: {'Gündüz' if is_daytime else 'Gece'}")
            
        except Exception as e:
            print(f"HATA: Gece/gündüz durumu güncellenirken hata: {e}")
            import traceback
            traceback.print_exc() 