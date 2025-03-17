from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QListWidget, QListWidgetItem,
                             QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize, QPoint
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap
from PyQt5.QtWidgets import QApplication
import os

class VillagerListItem(QWidget):
    """Köylü liste öğesi"""
    clicked = pyqtSignal(object)
    
    def __init__(self, villager, parent=None):
        super().__init__(parent)
        self.villager = villager
        self.setup_ui()
    
    def setup_ui(self):
        """Arayüzü hazırla"""
        try:
            layout = QHBoxLayout()  # QVBoxLayout yerine QHBoxLayout kullan
            layout.setContentsMargins(10, 8, 10, 8)
            layout.setSpacing(10)
            
            # Köylü resmi
            image_label = QLabel()
            image_path = os.path.join("src", "assets", "villagers", 
                                    f"{'kadin_koylu' if self.villager.gender == 'Kadın' else 'koylu'}{self.villager.appearance + 1}.png")
            
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
            else:
                print(f"HATA: Köylü resmi bulunamadı: {image_path}")
            
            layout.addWidget(image_label)
            
            # İsim ve meslek için dikey düzen
            text_layout = QVBoxLayout()
            text_layout.setSpacing(2)
            
            name_label = QLabel(self.villager.name)
            name_label.setStyleSheet("""
                QLabel {
                    color: #E4E4E4;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            text_layout.addWidget(name_label)
            
            profession_label = QLabel(self.villager.profession or "İşsiz")
            profession_label.setStyleSheet("""
                QLabel {
                    color: #9E9E9E;
                    font-size: 12px;
                }
            """)
            text_layout.addWidget(profession_label)
            
            # Dikey düzeni yatay düzene ekle
            layout.addLayout(text_layout)
            layout.addStretch()
            
            self.setStyleSheet("""
                QWidget {
                    background-color: #0A1F0A;
                    border-radius: 8px;
                    border: 1px solid #132813;
                }
                QWidget:hover {
                    background-color: #132813;
                    border: 1px solid #1A321A;
                }
            """)
            
            self.setLayout(layout)
            self.setCursor(Qt.PointingHandCursor)
            
        except Exception as e:
            print(f"HATA: Köylü liste öğesi arayüzü hazırlanırken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def mousePressEvent(self, event):
        """Tıklama olayı"""
        if event.button() == Qt.LeftButton:
            print(f"Köylü öğesine tıklandı: {self.villager.name}")
            self.clicked.emit(self.villager)
            event.accept()  # Olayı kabul et
            
    def mouseReleaseEvent(self, event):
        """Fare bırakma olayı"""
        if event.button() == Qt.LeftButton:
            event.accept()  # Olayı kabul et

class VillagerDetailsPanel(QFrame):
    """Köylü detay paneli"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Başlık
        self.title_label = QLabel("Köylü Detayları")
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.title_label)
        
        # Temel bilgiler
        self.info_frame = QFrame()
        info_layout = QVBoxLayout(self.info_frame)
        
        self.name_label = QLabel("İsim: -")
        self.gender_label = QLabel("Cinsiyet: -")
        self.profession_label = QLabel("Meslek: -")
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.gender_label)
        info_layout.addWidget(self.profession_label)
        
        layout.addWidget(self.info_frame)
        
        # İstatistikler
        self.stats_frame = QFrame()
        stats_layout = QVBoxLayout(self.stats_frame)
        
        self.stats = {}
        for stat_name, color in [
            ("Sağlık", "#27ae60"),
            ("Para", "#f1c40f"),
            ("Mutluluk", "#3498db"),
            ("Karizma", "#e74c3c"),
            ("Eğitim", "#9b59b6")
        ]:
            stat_layout = QHBoxLayout()
            label = QLabel(f"{stat_name}:")
            bar = QProgressBar()
            bar.setMaximumHeight(15)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    border-radius: 7px;
                    background-color: rgba(200, 200, 200, 0.3);
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 7px;
                }}
            """)
            stat_layout.addWidget(label)
            stat_layout.addWidget(bar)
            stats_layout.addLayout(stat_layout)
            self.stats[stat_name] = bar
        
        layout.addWidget(self.stats_frame)
        
        # Özellikler
        self.traits_label = QLabel("Özellikler:")
        self.traits_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.traits_label)
        
        self.traits_text = QLabel("-")
        self.traits_text.setWordWrap(True)
        layout.addWidget(self.traits_text)
        
        layout.addStretch()
        
        # Stil
        self.setStyleSheet("""
            VillagerDetailsPanel {
                background-color: rgba(44, 62, 80, 0.95);
                border-radius: 10px;
            }
            QLabel {
                color: white;
            }
            QFrame {
                border: none;
            }
        """)
    
    def update_villager(self, villager):
        """Köylü bilgilerini güncelle"""
        if not villager:
            return
            
        self.title_label.setText(f"{villager.name}")
        self.name_label.setText(f"İsim: {villager.name}")
        self.gender_label.setText(f"Cinsiyet: {villager.gender}")
        self.profession_label.setText(f"Meslek: {villager.profession}")
        
        # İstatistikleri güncelle
        self.stats["Sağlık"].setValue(villager.health)
        self.stats["Para"].setValue(min(villager.money, 100))
        self.stats["Mutluluk"].setValue(villager.happiness)
        self.stats["Karizma"].setValue(getattr(villager, 'charisma', 0))
        self.stats["Eğitim"].setValue(getattr(villager, 'education', 0))
        
        # Özellikleri güncelle
        if hasattr(villager, 'traits'):
            traits_text = ", ".join(villager.traits) if villager.traits else "Yok"
            self.traits_text.setText(traits_text)

class ControlPanel(QWidget):
    """Kontrol paneli"""
    close_game = pyqtSignal()
    minimize_game = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.dragging = False
        self.drag_position = None  # Sürükleme pozisyonunu tanımla
        self.villager_items = {}
        self.game_controller = None
        self.current_details_panel = None
        self.setup_ui()
    
    def set_game_controller(self, game_controller):
        """Oyun kontrolcüsünü ayarla"""
        try:
            self.game_controller = game_controller
            # Oyun kontrolcüsünü ayarladıktan sonra, kontrolcüye de kontrol panelini ayarla
            if hasattr(game_controller, 'set_control_panel'):
                game_controller.set_control_panel(self)
            print("Oyun kontrolcüsü başarıyla ayarlandı")
        except Exception as e:
            print(f"HATA: Oyun kontrolcüsü ayarlanırken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_ui(self):
        """Arayüzü hazırla"""
        try:
            # Ana düzen
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)
            
            # Sol panel (köylü listesi)
            left_panel = QWidget()
            left_panel.setObjectName("leftPanel")
            left_layout = QVBoxLayout(left_panel)
            left_layout.setContentsMargins(0, 0, 0, 0)
            left_layout.setSpacing(0)
            
            # Başlık çubuğu
            title_bar = QWidget()
            title_bar.setObjectName("titleBar")
            title_bar.setFixedHeight(40)
            title_layout = QHBoxLayout(title_bar)
            title_layout.setContentsMargins(15, 0, 10, 0)
            
            # Başlık
            title_label = QLabel("Köy Kontrol Paneli")
            title_label.setStyleSheet("""
                QLabel {
                    color: #E4E4E4;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            title_layout.addWidget(title_label)
            
            # Butonlar için spacer
            title_layout.addStretch()
            
            # Küçült butonu
            minimize_button = QPushButton("─")
            minimize_button.setFixedSize(30, 30)
            minimize_button.clicked.connect(self.minimize_game.emit)
            minimize_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #9E9E9E;
                    border: none;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #2D2D2D;
                }
            """)
            title_layout.addWidget(minimize_button)
            
            # Kapat butonu
            close_button = QPushButton("×")
            close_button.setFixedSize(30, 30)
            close_button.clicked.connect(self.close_game.emit)
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #9E9E9E;
                    border: none;
                    font-size: 20px;
                }
                QPushButton:hover {
                    background-color: #B03A3A;
                    color: #E4E4E4;
                }
            """)
            title_layout.addWidget(close_button)
            
            left_layout.addWidget(title_bar)
            
            # Ayırıcı çizgi
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setStyleSheet("background-color: #2D2D2D;")
            left_layout.addWidget(separator)
            
            # Scroll area
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setStyleSheet("""
                QScrollArea {
                    background-color: #1E1E1E;
                    border: none;
                }
                QScrollBar:vertical {
                    background-color: #1E1E1E;
                    width: 8px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background-color: #3D3D3D;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #4D4D4D;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)
            
            # Köylü listesi için widget
            self.villager_list = QWidget()
            self.villager_layout = QVBoxLayout(self.villager_list)
            self.villager_layout.setContentsMargins(10, 10, 10, 10)
            self.villager_layout.setSpacing(8)
            self.villager_layout.addStretch()
            
            scroll_area.setWidget(self.villager_list)
            left_layout.addWidget(scroll_area)
            
            # Zaman etiketi
            self.time_label = QLabel("Gündüz")
            self.time_label.setAlignment(Qt.AlignCenter)
            self.time_label.setStyleSheet("""
                QLabel {
                    color: #E4E4E4;
                    font-size: 12px;
                    padding: 10px;
                }
            """)
            left_layout.addWidget(self.time_label)
            
            # Sağ panel (detaylar)
            self.details_container = QWidget()
            self.details_container.setObjectName("detailsContainer")
            self.details_container.setFixedWidth(300)
            
            # Details container için layout oluştur
            details_container_layout = QVBoxLayout(self.details_container)
            details_container_layout.setContentsMargins(0, 0, 0, 0)
            details_container_layout.setSpacing(0)
            
            self.details_container.setStyleSheet("""
                #detailsContainer {
                    background-color: #0A1F0A;
                    border-radius: 10px;
                    border: 1px solid #132813;
                }
            """)
            self.details_container.hide()
            
            # Detay panelini oluştur
            self.details_panel = VillagerDetailsPanel(self.details_container)
            details_container_layout.addWidget(self.details_panel)
            
            # Ana düzene panelleri ekle
            layout.addWidget(left_panel)
            layout.addWidget(self.details_container)
            
            self.setLayout(layout)
            
            # Ana stil
            self.setStyleSheet("""
                QWidget {
                    background-color: #1E1E1E;
                }
                #leftPanel {
                    background-color: #1E1E1E;
                    border: 1px solid #2D2D2D;
                    border-radius: 10px;
                }
                #titleBar {
                    background-color: #1E1E1E;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                }
                #detailsContainer {
                    background-color: #1E1E1E;
                    border-radius: 10px;
                    border: 1px solid #2D2D2D;
                }
                QMessageBox {
                    background-color: #1E1E1E;
                }
                QMessageBox QLabel {
                    color: #E4E4E4;
                }
                QMessageBox QPushButton {
                    background-color: #2D2D2D;
                    color: #E4E4E4;
                    border: 1px solid #3D3D3D;
                    border-radius: 4px;
                    padding: 5px 15px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #3D3D3D;
                }
            """)
            
            # Boyut ve pozisyon
            self.resize(600, 600)
            self.move_to_right()
            
        except Exception as e:
            print(f"HATA: Kontrol paneli arayüzü hazırlanırken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def update_villagers(self, villagers):
        """Köylü listesini güncelle"""
        try:
            print(f"update_villagers çağrıldı: {len(villagers)} köylü")
            
            # Mevcut köylüleri kontrol et
            current_villagers = set(self.villager_items.keys())
            new_villagers = set(v.name for v in villagers)
            
            print(f"Mevcut köylüler: {current_villagers}")
            print(f"Yeni köylüler: {new_villagers}")
            
            # Silinecek köylüleri kaldır
            for name in current_villagers - new_villagers:
                if name in self.villager_items:
                    widget = self.villager_items[name]
                    self.villager_layout.removeWidget(widget)
                    widget.deleteLater()
                    del self.villager_items[name]
            
            # Yeni köylüleri ekle veya mevcut olanları güncelle
            for villager in villagers:
                print(f"Köylü işleniyor: {villager.name}")
                if villager.name not in self.villager_items:
                    item = VillagerListItem(villager)
                    item.clicked.connect(lambda checked=False, v=villager: self.show_villager_details(v))
                    self.villager_layout.insertWidget(self.villager_layout.count() - 1, item)
                    self.villager_items[villager.name] = item
                    print(f"Yeni köylü eklendi: {villager.name}")
            
            print(f"Köylü listesi güncellendi: {len(villagers)} köylü")
            
        except Exception as e:
            print(f"HATA: Köylü listesi güncellenirken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def show_villager_details(self, villager):
        """Köylü detaylarını göster"""
        try:
            print(f"Köylü detayları gösteriliyor: {villager.name}")
            
            # Detayları güncelle
            self.details_panel.update_villager(villager)
            
            # Detay panelini göster
            self.details_container.show()
            
        except Exception as e:
            print(f"HATA: Köylü detayları gösterilirken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def update_day_night_style(self, is_daytime):
        """Gece/gündüz stilini güncelle"""
        try:
            if is_daytime:
                self.time_label.setText("Gündüz")
                self.time_label.setStyleSheet("""
                    QLabel {
                        color: #90A090;
                        font-size: 12px;
                        padding: 10px;
                    }
                """)
            else:
                self.time_label.setText("Gece")
                self.time_label.setStyleSheet("""
                    QLabel {
                        color: #607060;
                        font-size: 12px;
                        padding: 10px;
                    }
                """)
                
        except Exception as e:
            print(f"HATA: Gece/gündüz stili güncellenirken hata: {e}")
    
    def move_to_right(self):
        """Paneli sağ tarafa taşı"""
        try:
            screen = QApplication.primaryScreen().geometry()
            x = screen.width() - self.width() - 20
            y = (screen.height() - self.height()) // 2
            self.move(x, y)
            
        except Exception as e:
            print(f"HATA: Panel sağa taşınırken hata: {e}")
    
    def mousePressEvent(self, event):
        """Fare basma olayı"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Fare hareket olayı"""
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Fare bırakma olayı"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

# Test kodunu kaldır
# test_villager = TestVillager(x=100, y=100)
# test_villager.move() 

