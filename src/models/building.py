from dataclasses import dataclass, field
from typing import Dict
from PyQt5.QtCore import QRectF

@dataclass
class Building:
    """Yapı sınıfı"""
    x: float
    y: float
    width: float
    height: float
    building_type: str  # 'castle', 'tree', 'house' vb.
    owner: str = None  # Yapının sahibi (ev için)
    inventory: Dict[str, int] = field(default_factory=dict)  # Envanter (kale için)
    
    def __post_init__(self):
        """Başlangıç değerlerini ayarla"""
        # Yapının çarpışma alanı - yapının alt kısmı
        self.rect = QRectF(self.x, self.y - self.height, self.width, self.height)
        print(f"{self.building_type} oluşturuldu: ({self.x}, {self.y}), {self.width}x{self.height}")
        
        # Kale ise başlangıç envanterini ayarla
        if self.building_type == "castle":
            self.inventory = {
                "odun": 0,
                "erzak": 0,
                "altın": 0
            }
            print(f"Kale envanteri oluşturuldu: {self.inventory}")
    
    def contains_point(self, x: float, y: float) -> bool:
        """Verilen nokta yapının içinde mi kontrol et"""
        return self.rect.contains(x, y)
    
    def get_entrance(self) -> tuple[float, float]:
        """Yapının giriş noktasını döndür"""
        # Varsayılan olarak yapının alt orta noktası
        return (self.x + self.width / 2, self.y)
    
    def add_to_inventory(self, item: str, amount: int) -> None:
        """Envantere öğe ekle"""
        if self.building_type != "castle":
            print(f"UYARI: Sadece kale envanteri destekleniyor, {self.building_type} için envanter işlemi yapılamaz.")
            return
            
        if item in self.inventory:
            self.inventory[item] += amount
        else:
            self.inventory[item] = amount
        print(f"Kale envanterine {amount} {item} eklendi. Yeni durum: {self.inventory}")
    
    def remove_from_inventory(self, item: str, amount: int) -> bool:
        """Envanterden öğe çıkar, başarılı olursa True döndür"""
        if self.building_type != "castle":
            print(f"UYARI: Sadece kale envanteri destekleniyor, {self.building_type} için envanter işlemi yapılamaz.")
            return False
            
        if item in self.inventory and self.inventory[item] >= amount:
            self.inventory[item] -= amount
            print(f"Kale envanterinden {amount} {item} çıkarıldı. Yeni durum: {self.inventory}")
            return True
        else:
            print(f"UYARI: Kale envanterinde yeterli {item} yok. Mevcut: {self.inventory.get(item, 0)}, İstenen: {amount}")
            return False
    
    def get_inventory(self) -> dict:
        """Envanteri döndür"""
        if self.building_type != "castle" or not hasattr(self, 'inventory'):
            return {}
        return self.inventory.copy() 