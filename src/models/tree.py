from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import time
import math
import random
import os

@dataclass
class Tree:
    """Ağaç sınıfı"""
    x: float
    y: float
    width: float
    height: float

class Tree(QObject):
    """Ağaç sınıfı"""
    tree_removed = pyqtSignal(object)
    
    # Sınıf değişkeni olarak ID sayacı
    next_id = 1
    
    def __init__(self, x: float, y: float, width: int, height: int, tree_type: int = 1):
        super().__init__()
        self.x = x
        self.original_x = x
        self.y = y
        self.width = width
        self.height = height
        self.tree_type = tree_type  # 1: normal ağaç, 2: alternatif ağaç
        self.id = Tree.next_id
        Tree.next_id += 1
        self.is_visible = True
        self.is_being_cut = False  # Kesiliyor mu?
        self.cut_progress = 0  # Kesim ilerlemesi (0-100)
        
        # Animasyon için değişkenler
        self.sway_offset = 0.0
        self.sway_direction = 1
        self.sway_speed = random.uniform(0.02, 0.05)
        self.max_sway = random.uniform(1.0, 2.0)
        
        # Rüzgar efekti için başlangıç zamanı
        self.start_time = time.time()
    
    def get_image_name(self) -> str:
        """Ağaç görüntüsünün dosya adını döndür"""
        return f"agac{'2' if self.tree_type == 2 else ''}.png"
    
    def update(self, elapsed_time=None):
        """Ağacı güncelle"""
        try:
            # Sallantı animasyonunu güncelle
            if self.is_visible:
                self.sway_offset += self.sway_speed * self.sway_direction
                
                # Maksimum sallantı miktarına ulaşıldığında yön değiştir
                if abs(self.sway_offset) >= self.max_sway:
                    self.sway_direction *= -1
                    
                # Orijinal pozisyona göre x konumunu güncelle
                self.x = self.original_x + self.sway_offset
                
                # Eğer kesiliyor ise daha fazla sallantı ekle (1 piksel sağa sola)
                if self.is_being_cut:
                    # Her saniye 1 piksel sağa sola hareket
                    cutting_sway = math.sin(time.time() * 5.0) * 1.0
                    self.x += cutting_sway
            
        except Exception as e:
            print(f"HATA: Ağaç güncelleme hatası: {e}")

    def respawn(self):
        """Ağacı yeniden doğur"""
        if not self.is_visible:
            self.is_visible = True
            self.is_being_cut = False
            self.cut_progress = 0
            self.x = self.original_x
            self.sway_offset = 0
            print(f"Ağaç {self.id} yeniden doğdu!")
