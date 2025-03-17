from dataclasses import dataclass
from PyQt5.QtCore import QRectF

@dataclass
class House:
    """Ev sınıfı"""
    x: float
    y: float
    width: float
    height: float
    house_type: str  # 'ev1', 'ev2', 'ev3', 'ev4' vb.
    owner: str = None  # Evin sahibi olan köylünün adı
    
    def __post_init__(self):
        """Başlangıç değerlerini ayarla"""
        # Evin çarpışma alanı - evin alt kısmı
        self.rect = QRectF(self.x, self.y - self.height, self.width, self.height)
        self.id = id(self)
        print(f"Ev oluşturuldu: ({self.x}, {self.y}), {self.width}x{self.height}, Tip: {self.house_type}, Sahip: {self.owner or 'Yok'}")
    
    def contains_point(self, x: float, y: float) -> bool:
        """Verilen nokta evin içinde mi kontrol et"""
        return self.rect.contains(x, y)
    
    def get_entrance(self) -> tuple[float, float]:
        """Evin giriş noktasını döndür"""
        # Varsayılan olarak evin alt orta noktası
        return (self.x + self.width / 2, self.y)
    
    def set_owner(self, villager_name: str) -> None:
        """Ev sahibini ayarla"""
        self.owner = villager_name
        print(f"Ev ID: {self.id} sahibi değişti: {villager_name}")
    
    def is_owned(self) -> bool:
        """Evin bir sahibi var mı kontrol et"""
        return self.owner is not None 