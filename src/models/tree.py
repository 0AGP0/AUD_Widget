from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import time
import math
import random

@dataclass
class Tree:
    """Ağaç sınıfı"""
    x: float
    y: float
    width: float
    height: float

class Tree(QObject):
    """Ağaç sınıfı"""
    woodcutter_finished = pyqtSignal(object)
    tree_removed = pyqtSignal(object)
    
    def __init__(self, x: float, y: float, width: int, height: int):
        super().__init__()
        self.x = x
        self.original_x = x
        self.y = y
        self.width = width
        self.height = height
        self.health = 10  # Ağaç canı 10 olarak ayarlandı
        self.is_visible = True
        self.is_being_cut = False
        self.current_woodcutter = None
        self.id = id(self)
        self.shake_offset = 0
        
    def start_cutting(self, woodcutter) -> bool:
        """Ağaç kesme işlemini başlat"""
        if not self.is_visible or self.is_being_cut:
            print(f"Ağaç ID: {self.id} kesilemez: görünür={self.is_visible}, kesiliyor={self.is_being_cut}")
            return False
            
        self.is_being_cut = True
        self.current_woodcutter = woodcutter
        print(f"Ağaç ID: {self.id} kesilmeye başlandı! Oduncu: {woodcutter.name}")
        return True
    
    def take_damage(self) -> bool:
        """Ağaca hasar ver"""
        if not self.is_being_cut or not self.is_visible:
            return False
            
        self.health -= 1  # Her vuruşta 1 hasar
        print(f"Ağaç ID: {self.id} hasar aldı! Kalan sağlık: {self.health}/10")
        
        if self.health <= 0:
            print(f"Ağaç ID: {self.id} sağlığı bitti, tamamen kesiliyor!")
            self.cut_down()
            return True
            
        return False
    
    def cut_down(self):
        """Ağacı kes"""
        if not self.is_visible:
            return
            
        # Ağacı tamamen kaldır
        self.is_visible = False
        self.is_being_cut = False
        
        if self.current_woodcutter:
            self.current_woodcutter.trees_cut_today += 1
            # Oduncuya 10 altın ekle
            self.current_woodcutter.money += 10
            self.woodcutter_finished.emit(self)
            print(f"Ağaç ID: {self.id} kesildi! Oduncu {self.current_woodcutter.name} bugün {self.current_woodcutter.trees_cut_today} ağaç kesti ve 10 altın kazandı. Toplam altın: {self.current_woodcutter.money}")
        
        self.current_woodcutter = None
        
        # Ağacın tamamen yok olduğunu bildir
        print(f"Ağaç ID: {self.id} tamamen yok oldu!")
        self.tree_removed.emit(self)
    
    def stop_cutting(self):
        """Kesmeyi durdur"""
        self.is_being_cut = False
        self.x = self.original_x
        self.current_woodcutter = None
        print(f"Ağaç {self.id} kesme işlemi durduruldu.")
    
    def update_animation(self):
        """Animasyonu güncelle"""
        # Ağaç görünür değilse animasyon güncelleme
        if not self.is_visible:
            return
            
        if self.is_being_cut:
            # Daha düzenli sallanma efekti
            current_time = time.time()
            # Her saniye yön değiştir (1 saniye sağa, 1 saniye sola)
            direction = 1 if int(current_time) % 2 == 0 else -1
            self.shake_offset = 5 * direction  # 5 piksel sabit sallanma
            self.x = self.original_x + self.shake_offset
        else:
            self.x = self.original_x
            self.shake_offset = 0
    
    def respawn(self):
        """Ağacı yeniden doğur"""
        if not self.is_visible:
            self.is_visible = True
            self.health = 100
            self.is_being_cut = False
            self.current_woodcutter = None
            self.x = self.original_x
            self.shake_offset = 0
            print(f"Ağaç {self.id} yeniden doğdu!")
