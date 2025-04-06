from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QListWidget, QListWidgetItem,
                             QProgressBar, QMessageBox, QTabWidget, QTextEdit, QTableWidget,
                             QTableWidgetItem, QHeaderView, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize, QPoint
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap
from PyQt5.QtWidgets import QApplication
import os
import time

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
            
            # Köylü görünümüne uygun resim anahtarını oluştur
            gender = "kadin_koylu" if self.villager.gender == "Kadın" else "koylu"
            
            # Dosya yolunu güncelle - ground_widget.py ile uyumlu olmak için {gender}{i} formatını kullan
            image_path = os.path.join("src", "assets", "villagers", f"{gender}{self.villager.appearance}.png")
            
            # Eğer o resim yoksa varsayılan resmi kullan
            if not os.path.exists(image_path):
                print(f"UYARI: Köylü resmi bulunamadı: {image_path}, varsayılan resim kullanılıyor")
                image_path = os.path.join("src", "assets", "villagers", f"{gender}1.png")
                
            # Varsayılan resim de yoksa, hata ver ve devam et
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
            else:
                print(f"HATA: Köylü varsayılan resmi de bulunamadı: {image_path}")
            
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
        
        # Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background-color: rgba(44, 62, 80, 0.95);
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 5px 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #36445a;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background-color: #2c3e50;
            }
        """)
        
        # Bilgi Sekmesi
        self.info_tab = QWidget()
        info_layout = QVBoxLayout(self.info_tab)
        
        # Başlık
        self.title_label = QLabel("Köylü Detayları")
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(self.title_label)
        
        # Temel bilgiler
        self.info_frame = QFrame()
        info_frame_layout = QVBoxLayout(self.info_frame)
        
        self.name_label = QLabel("İsim: -")
        self.gender_label = QLabel("Cinsiyet: -")
        self.profession_label = QLabel("Meslek: -")
        
        info_frame_layout.addWidget(self.name_label)
        info_frame_layout.addWidget(self.gender_label)
        info_frame_layout.addWidget(self.profession_label)
        
        info_layout.addWidget(self.info_frame)
        
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
        
        info_layout.addWidget(self.stats_frame)
        
        # Özellikler
        self.traits_label = QLabel("Özellikler:")
        self.traits_label.setFont(QFont("Arial", 10, QFont.Bold))
        info_layout.addWidget(self.traits_label)
        
        self.traits_text = QLabel("-")
        self.traits_text.setWordWrap(True)
        info_layout.addWidget(self.traits_text)
        
        # Eşinde aradığı özellikler
        self.desired_traits_label = QLabel("Eşinde Aradığı Özellikler:")
        self.desired_traits_label.setFont(QFont("Arial", 10, QFont.Bold))
        info_layout.addWidget(self.desired_traits_label)
        
        self.desired_traits_text = QLabel("-")
        self.desired_traits_text.setWordWrap(True)
        info_layout.addWidget(self.desired_traits_text)
        
        # Boşluk bırak
        info_layout.addStretch()
        
        # İlişkiler Sekmesi
        self.relations_tab = QWidget()
        relations_layout = QVBoxLayout(self.relations_tab)
        
        # İlişki tablosu başlığı
        relations_title = QLabel("Köylü İlişkileri")
        relations_title.setFont(QFont("Arial", 12, QFont.Bold))
        relations_layout.addWidget(relations_title)
        
        # İlişki tablosu
        self.relations_table = QTableWidget()
        self.relations_table.setColumnCount(3)
        self.relations_table.setHorizontalHeaderLabels(["Köylü", "İlişki Seviyesi", "Durum"])
        self.relations_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.relations_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.relations_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.relations_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(30, 30, 30, 0.7);
                gridline-color: #3d3d3d;
                border: none;
            }
            QTableWidget::item {
                color: white;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 5px;
                border: 1px solid #3d3d3d;
            }
        """)
        relations_layout.addWidget(self.relations_table)
        
        # Ruh hali
        self.mood_frame = QFrame()
        mood_layout = QHBoxLayout(self.mood_frame)
        
        self.mood_label = QLabel("Ruh Hali:")
        self.mood_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.mood_value = QLabel("-")
        
        mood_layout.addWidget(self.mood_label)
        mood_layout.addWidget(self.mood_value)
        mood_layout.addStretch()
        
        relations_layout.addWidget(self.mood_frame)
        
        # Tabları ekle
        self.tab_widget.addTab(self.info_tab, "Bilgiler")
        self.tab_widget.addTab(self.relations_tab, "İlişkiler")
        
        # Ana düzene tab widget'ı ekle
        layout.addWidget(self.tab_widget)
        
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
            
        # Eşinde aradığı özellikleri güncelle
        if hasattr(villager, 'desired_traits'):
            desired_traits_text = ", ".join(villager.desired_traits) if villager.desired_traits else "Yok"
            self.desired_traits_text.setText(desired_traits_text)
        
        # İlişkileri güncelle
        self.update_relations(villager)
        
        # Ruh halini güncelle
        if hasattr(villager, 'mood'):
            self.mood_value.setText(villager.mood)
            
            # Ruh haline göre renk
            mood_colors = {
                "Mutlu": "#27ae60",  # Yeşil
                "Üzgün": "#3498db",  # Mavi
                "Sinirli": "#e74c3c", # Kırmızı
                "Sakin": "#f1c40f"   # Sarı
            }
            
            color = mood_colors.get(villager.mood, "#ffffff")
            self.mood_value.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def update_relations(self, villager):
        """Köylünün ilişkilerini güncelle"""
        if not hasattr(villager, 'relationships'):
            return
            
        # Tabloyu temizle
        self.relations_table.setRowCount(0)
        
        # İlişkileri ekle
        row = 0
        for other_name, value in villager.relationships.items():
            self.relations_table.insertRow(row)
            
            # Köylü adı
            name_item = QTableWidgetItem(other_name)
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # İlişki değeri
            value_item = QTableWidgetItem(str(value))
            value_item.setTextAlignment(Qt.AlignCenter)
            
            # İlişki durumu
            if value <= -50:
                status = "Düşman"
                color = "#e74c3c"  # Kırmızı
            elif value <= -20:
                status = "Hoşlanmıyor"
                color = "#e67e22"  # Turuncu
            elif value <= 20:
                status = "Nötr"
                color = "#f1c40f"  # Sarı
            elif value <= 50:
                status = "İyi"
                color = "#2ecc71"  # Yeşil
            else:
                status = "Dost"
                color = "#27ae60"  # Koyu yeşil
            
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            status_item.setForeground(QColor(color))
            
            self.relations_table.setItem(row, 0, name_item)
            self.relations_table.setItem(row, 1, value_item)
            self.relations_table.setItem(row, 2, status_item)
            
            row += 1

class ChatPanel(QWidget):
    """Sohbet paneli"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.dialogue_history = []
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Başlık
        title_label = QLabel("Köy Sohbetleri")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Sohbet metni
        self.chat_text = QTextEdit()
        self.chat_text.setReadOnly(True)
        self.chat_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(30, 30, 30, 0.7);
                color: white;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.chat_text)
        
        # Temizle butonu
        clear_button = QPushButton("Sohbeti Temizle")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        clear_button.clicked.connect(self.clear_chat)
        layout.addWidget(clear_button)
        
    def add_dialogue(self, speaker, listener, message, relationship=""):
        """Diyalog ekle"""
        timestamp = time.strftime("%H:%M:%S")
        
        # İlişki durumu rengi
        relationship_colors = {
            "Düşman": "#e74c3c",
            "Hoşlanmıyor": "#e67e22",
            "Nötr": "#f1c40f",
            "İyi": "#2ecc71",
            "Dost": "#27ae60"
        }
        
        rel_color = relationship_colors.get(relationship, "#ffffff")
        
        # HTML formatında diyalog ekle
        html = f"""
        <p style="margin: 5px;">
            <span style="color: #3498db; font-weight: bold;">[{timestamp}]</span> 
            <span style="color: #2ecc71; font-weight: bold;">{speaker}</span>
            <span style="color: #ffffff;"> → </span>
            <span style="color: #e74c3c; font-weight: bold;">{listener}</span>
            <span style="color: {rel_color}; font-style: italic;"> ({relationship})</span>
            <br>
            <span style="color: #ffffff; margin-left: 20px;">"{message}"</span>
        </p>
        """
        
        # Diyaloğu kaydet
        self.dialogue_history.append({
            "timestamp": timestamp,
            "speaker": speaker,
            "listener": listener,
            "message": message,
            "relationship": relationship
        })
        
        # Ekrana ekle
        self.chat_text.append(html)
        
        # Otomatik kaydır
        scrollbar = self.chat_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_chat(self):
        """Sohbeti temizle"""
        self.chat_text.clear()
        self.dialogue_history = []

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
            
            # Kale envanterini güncelle
            self.update_castle_inventory()
            
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
            
            # Üst düğmeler
            self.minimize_button = QPushButton("_")
            self.minimize_button.setFixedSize(30, 30)
            self.minimize_button.clicked.connect(self.minimize_game.emit)
            self.minimize_button.setStyleSheet("""
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
            title_layout.addWidget(self.minimize_button)
            
            # Kapat butonu
            self.close_button = QPushButton("×")
            self.close_button.setFixedSize(30, 30)
            self.close_button.clicked.connect(self.close_game.emit)
            self.close_button.setStyleSheet("""
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
            title_layout.addWidget(self.close_button)
            
            left_layout.addWidget(title_bar)
            
            # Ayırıcı çizgi
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setStyleSheet("background-color: #2D2D2D;")
            left_layout.addWidget(separator)
            
            # Kale Envanteri Bölümü
            castle_inventory_widget = QWidget()
            castle_inventory_widget.setObjectName("castleInventory")
            castle_inventory_layout = QVBoxLayout(castle_inventory_widget)
            castle_inventory_layout.setContentsMargins(10, 10, 10, 10)
            castle_inventory_layout.setSpacing(5)
            
            # Kale Envanteri Başlığı
            castle_inventory_title = QLabel("Kale Envanteri")
            castle_inventory_title.setStyleSheet("""
                QLabel {
                    color: #E4E4E4;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            castle_inventory_layout.addWidget(castle_inventory_title)
            
            # Envanter öğeleri
            self.inventory_labels = {}
            for item_name, icon_color in [
                ("odun", "#8B4513"),  # Kahverengi
                ("erzak", "#27ae60"),  # Yeşil
                ("altın", "#f1c40f")   # Sarı
            ]:
                item_layout = QHBoxLayout()
                
                # Renkli ikon
                icon = QLabel("■")
                icon.setStyleSheet(f"color: {icon_color}; font-size: 14px;")
                item_layout.addWidget(icon)
                
                # Öğe adı
                item_label = QLabel(item_name.capitalize())
                item_label.setStyleSheet("color: #E4E4E4; font-size: 12px;")
                item_layout.addWidget(item_label)
                
                # Miktar
                amount_label = QLabel("0")
                amount_label.setStyleSheet("color: #E4E4E4; font-size: 12px; font-weight: bold;")
                amount_label.setAlignment(Qt.AlignRight)
                item_layout.addWidget(amount_label)
                
                castle_inventory_layout.addLayout(item_layout)
                self.inventory_labels[item_name] = amount_label
            
            left_layout.addWidget(castle_inventory_widget)
            
            # Ayırıcı çizgi
            separator2 = QFrame()
            separator2.setFrameShape(QFrame.HLine)
            separator2.setStyleSheet("background-color: #2D2D2D;")
            left_layout.addWidget(separator2)
            
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
            
            # Sağ panel (detaylar ve sohbetler)
            right_panel = QWidget()
            right_panel.setObjectName("rightPanel")
            right_layout = QVBoxLayout(right_panel)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(0)
            
            # Tab Widget
            tab_widget = QTabWidget()
            tab_widget.setObjectName("rightTabs")
            
            # Detaylar Sekmesi
            self.details_container = QWidget()
            self.details_container.setObjectName("detailsContainer")
            
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
            
            # Detay panelini oluştur
            self.details_panel = VillagerDetailsPanel(self.details_container)
            details_container_layout.addWidget(self.details_panel)
            
            # Sohbet Sekmesi
            self.chat_panel = ChatPanel()
            
            # Tabları ekle
            tab_widget.addTab(self.details_container, "Köylü Detayları")
            tab_widget.addTab(self.chat_panel, "Köy Sohbetleri")
            
            # Sağ panele tab widget ekle
            right_layout.addWidget(tab_widget)
            
            # Ana düzene panelleri ekle
            layout.addWidget(left_panel)
            layout.addWidget(right_panel)
            
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
                #rightPanel {
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
                #castleInventory {
                    background-color: #0A1F0A;
                    border-radius: 8px;
                    border: 1px solid #132813;
                    margin: 5px;
                }
                #rightTabs::pane {
                    border: 1px solid #3d3d3d;
                    background-color: #1E1E1E;
                    border-radius: 5px;
                }
                #rightTabs > QTabBar::tab {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                    border: 1px solid #3d3d3d;
                    border-bottom: none;
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;
                    padding: 5px 10px;
                    margin-right: 2px;
                }
                #rightTabs > QTabBar::tab:selected {
                    background-color: #36445a;
                    border-bottom: none;
                }
                #rightTabs > QTabBar::tab:hover {
                    background-color: #2c3e50;
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
            self.resize(700, 600)
            self.move_to_right()
            
        except Exception as e:
            print(f"HATA: Kontrol paneli arayüzü hazırlanırken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def update_castle_inventory(self):
        """Kale envanterini güncelle"""
        try:
            # GameController kontrol et
            if not hasattr(self, 'game_controller') or not self.game_controller:
                print("UYARI: GameController bulunamadı!")
                return
            
            # Kale kontrol et
            if not hasattr(self.game_controller, 'castle') or not self.game_controller.castle:
                print("UYARI: Kale bulunamadı! Envanter güncellenemedi.")
                return
            
            # Kale envanterini kontrol et
            castle = self.game_controller.castle
            if not hasattr(castle, 'get_inventory'):
                print("UYARI: Kale get_inventory metodu bulunamadı!")
                return
            
            # Envanteri al ve güncelle
            inventory = castle.get_inventory()
            if inventory:
                for item_name, label in self.inventory_labels.items():
                    amount = inventory.get(item_name, 0)
                    label.setText(str(amount))
                
                print(f"Kale envanteri güncellendi: {inventory}")
            else:
                print("UYARI: Kale envanteri boş!")
                
            # Pazar envanterini de güncelle
            self.update_market_inventory()
            
        except Exception as e:
            print(f"HATA: Kale envanteri güncellenirken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def update_market_inventory(self):
        """Pazar envanterini güncelle"""
        try:
            # GameController kontrol et
            if not hasattr(self, 'game_controller') or not self.game_controller:
                print("UYARI: GameController bulunamadı!")
                return
            
            # Pazar kontrol et
            if not hasattr(self.game_controller, 'market') or not self.game_controller.market:
                print("UYARI: Pazar bulunamadı! Envanter güncellenemedi.")
                return
            
            # Pazar envanterini güncelle
            market = self.game_controller.market
            
            # Odun stoğu
            if hasattr(self, 'wood_stock_label') and hasattr(market, 'wood_stock'):
                self.wood_stock_label.setText(str(market.wood_stock))
            
            # Yiyecek stoğu
            if hasattr(self, 'food_stock_label') and hasattr(market, 'food_stock'):
                self.food_stock_label.setText(str(market.food_stock))
            
            print(f"Pazar envanteri güncellendi: Odun: {market.wood_stock}, Yiyecek: {market.food_stock}")
            
        except Exception as e:
            print(f"HATA: Pazar envanteri güncellenirken hata: {e}")
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
            
            # Detay sekmesine geçiş yap
            for i in range(self.layout().itemAt(1).widget().layout().count()):
                widget = self.layout().itemAt(1).widget().layout().itemAt(i).widget()
                if isinstance(widget, QTabWidget):
                    widget.setCurrentIndex(0)
                    break
            
        except Exception as e:
            print(f"HATA: Köylü detayları gösterilirken hata: {e}")
            import traceback
            traceback.print_exc()
    
    def add_dialogue_to_chat(self, speaker, listener, message, relationship=""):
        """Diyaloğu sohbet paneline ekle"""
        try:
            self.chat_panel.add_dialogue(speaker, listener, message, relationship)
        except Exception as e:
            print(f"HATA: Diyalog ekleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def update_day_night_style(self, is_daytime):
        """Gündüz/gece değişiminde stil güncelleme"""
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
    
    def update_time_label(self):
        """Kalan süreyi güncelle"""
        try:
            if hasattr(self, 'game_controller') and self.game_controller:
                remaining_minutes, remaining_seconds = self.game_controller.get_remaining_time()
                time_text = f"{'Gündüz' if self.game_controller.is_daytime else 'Gece'}: {remaining_minutes:02}:{remaining_seconds:02}"
                
                if hasattr(self, 'time_label'):
                    self.time_label.setText(time_text)
        
        except Exception as e:
            print(f"HATA: Zaman etiketi güncellenirken hata: {e}")
    
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

