from dataclasses import dataclass
from PyQt5.QtCore import QRectF

@dataclass
class Building:
    """Yapı sınıfı"""
    x: float
    y: float
    width: float
    height: float
    building_type: str  # 'castle', 'tree', vb.
    
    def __post_init__(self):
        """Başlangıç değerlerini ayarla"""
        # Yapının çarpışma alanı - yapının alt kısmı
        self.rect = QRectF(self.x, self.y - self.height, self.width, self.height)
        print(f"{self.building_type} oluşturuldu: ({self.x}, {self.y}), {self.width}x{self.height}")
    
    def contains_point(self, x: float, y: float) -> bool:
        """Verilen nokta yapının içinde mi kontrol et"""
        return self.rect.contains(x, y)
    
    def get_entrance(self) -> tuple[float, float]:
        """Yapının giriş noktasını döndür"""
        # Varsayılan olarak yapının alt orta noktası
        return (self.x + self.width / 2, self.y) 