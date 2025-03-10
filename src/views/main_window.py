from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication, QDesktopWidget
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QScreen, QPainter, QPalette, QColor
from src.views.ground_widget import GroundWidget
from src.views.control_panel import ControlPanel
from src.controllers.game_controller import GameController

class MainWindow(QMainWindow):
    """Ana pencere sınıfı"""
    def __init__(self, game_controller: GameController):
        super().__init__(None)
        self.setWindowTitle("Çağlar Boyu Savaş")
        self.game_controller = game_controller
        
        # Tüm ekranları al
        desktop = QDesktopWidget()
        total_width = 0
        max_height = 0
        min_x = float('inf')
        
        # Her ekranın bilgilerini topla
        for i in range(desktop.screenCount()):
            screen = desktop.screenGeometry(i)
            total_width += screen.width()
            max_height = max(max_height, screen.height())
            min_x = min(min_x, screen.x())
            print(f"Ekran {i+1}: ({screen.x()}, {screen.y()}, {screen.width()}x{screen.height()})")
        
        # Pencere özelliklerini ayarla
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        # Ana widget
        main_widget = QWidget()
        main_widget.setAttribute(Qt.WA_TranslucentBackground)
        main_widget.setAttribute(Qt.WA_NoSystemBackground)
        self.setCentralWidget(main_widget)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Kenar boşluklarını kaldır
        layout.setSpacing(0)  # Widget'lar arası boşluğu kaldır
        main_widget.setLayout(layout)
        
        # Zemin widget'ı
        self.ground_widget = GroundWidget(parent=main_widget, game_controller=self.game_controller)
        
        # Eğer game_controller varsa, yüksekliği ondan al
        ground_height = 200
        if self.game_controller:
            ground_height = self.game_controller.ground_height
            
        self.ground_widget.setFixedSize(total_width, ground_height)
        layout.addWidget(self.ground_widget)
        
        # Kontrol paneli
        self.control_panel = ControlPanel(self)
        self.control_panel.set_game_controller(self.game_controller)  # Oyun kontrolcüsünü ayarla
        self.control_panel.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.control_panel.setAttribute(Qt.WA_TranslucentBackground)
        self.control_panel.setAttribute(Qt.WA_NoSystemBackground)
        
        # Kontrol panelini sağ üst köşeye yerleştir
        control_panel_x = min_x + total_width - 400  # Sağdan 400 piksel
        self.control_panel.setGeometry(
            control_panel_x,  # X pozisyonu
            20,  # Üstten 20 piksel
            380,  # Genişlik
            500   # Yükseklik
        )
        
        # Kontrol panelini göster
        self.control_panel.show()
        
        # Kontrol paneli sinyallerini bağla
        self.control_panel.close_game.connect(QApplication.quit)  # Çarpı butonuna basınca oyunu kapat
        self.control_panel.minimize_game.connect(self.showMinimized)  # Küçült butonuna basınca pencereyi küçült
        
        # Gece/gündüz sinyalini kontrol paneline bağla
        self.game_controller.day_night_changed.connect(self.control_panel.update_day_night)
        
        # Köylü listesi sinyalini kontrol paneline bağla
        self.game_controller.villagers_updated.connect(self.control_panel.update_villagers)
        
        # İlk köylü listesini gönder
        self.game_controller.villagers_updated.emit(self.game_controller.villagers)
        
        # Pencereyi tüm ekranları kapsayacak şekilde ayarla
        window_y = max_height - ground_height
        self.setGeometry(min_x, window_y, total_width, ground_height)
        
        # Debug bilgisi
        print(f"Toplam genişlik: {total_width}")
        print(f"Başlangıç X: {min_x}")
        print(f"Başlangıç Y: {window_y}")
        print(f"Ekran sayısı: {desktop.screenCount()}")
        print(f"Kontrol paneli konumu: ({control_panel_x}, 20)")
    
    def paintEvent(self, event):
        """Pencereyi çiz"""
        try:
            super().paintEvent(event)
            
            # Ground widget'ı yeniden çiz
            if hasattr(self, 'ground_widget'):
                self.ground_widget.update()
        except Exception as e:
            print(f"MainWindow.paintEvent hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def keyPressEvent(self, event):
        """Tuş basma olayı"""
        # ESC tuşuna basılınca oyundan çık
        if event.key() == Qt.Key_Escape:
            QApplication.quit()