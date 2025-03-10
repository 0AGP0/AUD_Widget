from dataclasses import dataclass, field
from typing import List
from PyQt5.QtCore import QRectF
from .building import Building
from .villager import Villager

@dataclass
class Ground:
    """Zemin sınıfı"""
    width: float
    height: float
    tile_width: float = 64.0  # zemin.png genişliği
    
    def __post_init__(self):
        """Başlangıç değerlerini ayarla"""
        self.rect = QRectF(0, 0, self.width, self.height)
        self.buildings: List[Building] = []
        self.villagers: List[Villager] = []
        self.calculate_tile_count()
    
    def calculate_tile_count(self) -> None:
        """Kaç adet zemin.png gerektiğini hesapla"""
        self.horizontal_tiles = int(self.width / self.tile_width) + 1
        self.vertical_tiles = int(self.height / self.tile_width) + 1
    
    def add_building(self, building: Building) -> None:
        """Yeni yapı ekle"""
        self.buildings.append(building)
    
    def add_villager(self, villager: Villager) -> None:
        """Yeni köylü ekle"""
        self.villagers.append(villager)
    
    def get_building_at(self, x: float, y: float) -> Building | None:
        """Verilen konumdaki yapıyı döndür"""
        for building in self.buildings:
            if building.contains_point(x, y):
                return building
        return None
    
    def get_villager_at(self, x: float, y: float) -> Villager | None:
        """Verilen konumdaki köylüyü döndür"""
        for villager in self.villagers:
            if abs(villager.x - x) < 20 and abs(villager.y - y) < 20:
                return villager
        return None
    
    def is_position_valid(self, x: float, y: float) -> bool:
        """Verilen konum geçerli mi kontrol et"""
        # Sınırlar içinde mi?
        if not self.rect.contains(x, y):
            return False
        
        # Başka yapı var mı?
        if self.get_building_at(x, y):
            return False
            
        return True 