from dataclasses import dataclass
from PyQt5.QtCore import QRectF

@dataclass
class House:
    """Ev sınıfı"""
    x: float
    y: float
    width: float
    height: float
    house_type: str  # 'ev1', 'ev2', 'ev3' vb.
    owner: str = None  # Evin sahibi olan köylünün adı
    
    def __post_init__(self):
        """Başlangıç değerlerini ayarla"""
        # Ev tipine göre boyutları ayarla
        self.adjust_size_by_type()
        
        # Evin çarpışma alanı - evin alt kısmı
        self.rect = QRectF(self.x - self.width / 2, self.y - self.height, self.width, self.height)
        self.id = id(self)
        print(f"Ev oluşturuldu: ({self.x}, {self.y}), {self.width}x{self.height}, Tip: {self.house_type}, Sahip: {self.owner or 'Yok'}")
    
    def adjust_size_by_type(self):
        """Ev tipine göre boyutları ayarla"""
        base_width = 80
        base_height = 100
        
        if self.house_type == "ev1":
            # Küçük ev
            self.width = base_width
            self.height = base_height
        elif self.house_type == "ev2":
            # Orta boy ev
            self.width = base_width * 1.2
            self.height = base_height * 1.2
        elif self.house_type == "ev3":
            # Büyük ev
            self.width = base_width * 1.5
            self.height = base_height * 1.5
        else:
            # Varsayılan boyut
            self.width = base_width
            self.height = base_height
    
    def contains_point(self, x: float, y: float) -> bool:
        """Verilen nokta evin içinde mi kontrol et"""
        return self.rect.contains(x, y)
    
    def get_entrance(self) -> tuple[float, float]:
        """Evin giriş noktasını döndür"""
        # Varsayılan olarak evin alt orta noktası
        return (self.x, self.y)
    
    def set_owner(self, villager_name: str) -> None:
        """Ev sahibini ayarla"""
        self.owner = villager_name
        print(f"Ev ID: {self.id} sahibi değişti: {villager_name}")
    
    def is_owned(self) -> bool:
        """Evin bir sahibi var mı kontrol et"""
        return self.owner is not None 