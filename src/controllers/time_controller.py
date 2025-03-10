from PyQt5.QtCore import QObject, QTimer, pyqtSignal

class TimeController(QObject):
    """Zaman kontrolcü sınıfı"""
    time_updated = pyqtSignal(bool)  # True = Gündüz, False = Gece
    
    def __init__(self):
        super().__init__()
        self.is_daytime = True
        
        # Gece/gündüz süresi (milisaniye)
        self.day_duration = 5 * 60 * 1000    # 5 dakika
        self.night_duration = 3 * 60 * 1000  # 3 dakika
        
        # Timer'ı başlat
        self.timer = QTimer()
        self.timer.timeout.connect(self.toggle_time)
        self.start_day()
    
    def start_day(self):
        """Günü başlat"""
        self.is_daytime = True
        self.timer.start(self.day_duration)
        self.time_updated.emit(True)
    
    def start_night(self):
        """Geceyi başlat"""
        self.is_daytime = False
        self.timer.start(self.night_duration)
        self.time_updated.emit(False)
    
    def toggle_time(self):
        """Gece/gündüz geçişi"""
        if self.is_daytime:
            self.start_night()
        else:
            self.start_day()
    
    def pause(self):
        """Zamanı durdur"""
        self.timer.stop()
    
    def resume(self):
        """Zamanı devam ettir"""
        if self.is_daytime:
            self.timer.start(self.day_duration)
        else:
            self.timer.start(self.night_duration) 