class Stall:
    """Pazar tezgahı sınıfı"""
    
    def __init__(self, x, y, width, height, stall_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.stall_type = stall_type  # "odun", "yemek", "meyve", vb.
        self.inventory = 0  # Başlangıçta boş
        self.is_active = False  # Başlangıçta aktif değil
        self.owner = None
    
    def set_owner(self, villager):
        """Tezgahın sahibini ayarla"""
        if not self.is_active:
            self.owner = villager
            self.is_active = True
            return True
        return False
    
    def release_stall(self):
        """Tezgahı serbest bırak"""
        self.owner = None
        self.is_active = False
        self.inventory = 0
    
    def add_inventory(self, amount):
        """Envantere ürün ekle"""
        self.inventory += amount
        return True
    
    def remove_inventory(self, amount):
        """Envanterden ürün çıkar"""
        if self.inventory >= amount:
            self.inventory -= amount
            return True
        return False
    
    def has_enough_inventory(self, amount):
        """Yeterli envanter var mı kontrol et"""
        return self.inventory >= amount
    
    def get_price(self, amount):
        """Fiyatı hesapla"""
        # Odun için sabit fiyat: 2 altın
        if self.stall_type == "odun":
            return 2 * amount
        elif self.stall_type == "yemek":
            return 3 * amount
        elif self.stall_type == "meyve":
            return 1 * amount
        else:
            return 5 * amount  # Diğer stall tipleri için 