from dataclasses import dataclass
from PyQt5.QtCore import QRectF

@dataclass
class House:
    """Ev sınıfı"""
    x: float
    y: float
    width: float
    height: float
    house_type: str = "ev1"  # Varsayılan ev tipi
    owner: str = None  # Ev sahibi
    builder: str = None  # Evi inşa eden inşaatçı
    for_sale: bool = False  # Ev satılık mı?
    
    def __post_init__(self):
        """Başlangıç değerlerini ayarla"""
        # Ev tipine göre boyutları ayarla
        self.adjust_size_by_type()
        
        # Evin çarpışma alanı - evin alt kısmı
        self.rect = QRectF(self.x - self.width / 2, self.y - self.height, self.width, self.height)
        self.id = id(self)
        print(f"Ev oluşturuldu: ID: {self.id}, Tip: {self.house_type}, Konum: {self.x}, {self.y}")
    
    def adjust_size_by_type(self):
        """Ev tipine göre boyutları ayarla"""
        base_width = 60
        base_height = 75
        
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
    
    def get_image_name(self) -> str:
        """Ev görüntüsünün dosya adını döndür"""
        # Ev tipine göre resim adını belirle
        return f"{self.house_type}.png"
    
    def get_entrance(self) -> tuple:
        """Ev girişinin konumunu döndür"""
        entrance_x = self.x
        entrance_y = self.y
        return (entrance_x, entrance_y)
    
    def set_owner(self, owner_name: str) -> bool:
        """Ev sahibini ayarla"""
        self.owner = owner_name
        self.for_sale = False  # Ev artık satılık değil
        print(f"Ev ID: {self.id}, Yeni Sahip: {owner_name}")
        return True
    
    def is_owned(self) -> bool:
        """Evin sahibi var mı kontrol et"""
        return self.owner is not None 