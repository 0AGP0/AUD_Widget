from dataclasses import dataclass, field
from typing import Dict, List, Optional
from PyQt5.QtCore import QObject, QRectF, pyqtSignal

class MarketStall(QObject):
    """Pazar tezgahı sınıfı"""
    
    def __init__(self, x: float, y: float, width: int = 50, height: int = 40, stall_type: str = "odun"):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.stall_type = stall_type  # odun, erzak, vb.
        self.owner = None  # Tezgahı kiralayan köylü
        self.is_active = False  # Tezgah şu anda aktif mi?
        self.inventory = {stall_type: 0}  # Tezgahtaki ürün miktarı
        self.price = self.get_default_price()  # Varsayılan fiyat
        self.id = id(self)
        
        # Tezgahın çarpışma alanı
        self.rect = QRectF(self.x - self.width / 2, self.y - self.height, self.width, self.height)
        
    def get_default_price(self) -> int:
        """Ürün tipine göre varsayılan fiyatı döndürür"""
        price_map = {
            "odun": 5,  # Odun birim fiyatı
            "erzak": 7,  # Erzak birim fiyatı
            "ev": 100,   # Ev fiyatı
        }
        return price_map.get(self.stall_type, 10)  # Varsayılan fiyat
    
    def set_owner(self, villager) -> bool:
        """Tezgah sahibini ayarla"""
        if self.owner is not None and self.is_active:
            print(f"Tezgah ID: {self.id} zaten {self.owner.name} tarafından kullanılıyor!")
            return False
            
        self.owner = villager
        self.is_active = True
        print(f"Tezgah ID: {self.id} sahibi: {villager.name}, Ürün: {self.stall_type}")
        return True
    
    def release_stall(self) -> None:
        """Tezgahı serbest bırak"""
        self.owner = None
        self.is_active = False
        self.inventory = {self.stall_type: 0}
        print(f"Tezgah ID: {self.id} serbest bırakıldı.")
    
    def add_inventory(self, amount: int) -> None:
        """Tezgah envanterine ürün ekle"""
        self.inventory[self.stall_type] += amount
        print(f"Tezgah ID: {self.id} envanterine {amount} {self.stall_type} eklendi. Yeni durum: {self.inventory}")
    
    def has_enough_inventory(self, amount: int) -> bool:
        """Tezgahta yeterli ürün var mı kontrol et"""
        return self.inventory.get(self.stall_type, 0) >= amount
    
    def remove_inventory(self, amount: int) -> bool:
        """Tezgah envanterinden ürün çıkar"""
        if not self.has_enough_inventory(amount):
            print(f"Tezgah ID: {self.id} envanterinde yeterli {self.stall_type} yok!")
            return False
            
        self.inventory[self.stall_type] -= amount
        print(f"Tezgah ID: {self.id} envanterinden {amount} {self.stall_type} çıkarıldı. Yeni durum: {self.inventory}")
        return True
    
    def set_price(self, new_price: int) -> None:
        """Ürün fiyatını ayarla"""
        self.price = max(1, new_price)  # En düşük fiyat 1 altın
        print(f"Tezgah ID: {self.id} fiyatı: {self.price} altın olarak güncellendi.")
    
    def contains_point(self, x: float, y: float) -> bool:
        """Verilen nokta tezgahın içinde mi kontrol et"""
        return self.rect.contains(x, y)
    
    def negotiate_price(self, buyer, amount: int) -> int:
        """Alıcı ile pazarlık yap ve son fiyatı belirle"""
        if not self.owner or not self.is_active:
            return 0
            
        base_price = self.price * amount  # Temel fiyat
        
        # İlişki durumunu kontrol et
        relationship_bonus = 0
        if buyer.name in self.owner.relationships:
            relationship_value = self.owner.relationships[buyer.name]
            relationship_bonus = relationship_value / 20  # -5 ile +5 arası bonus
        
        # Satıcı ve alıcının özelliklerini kontrol et
        seller_trait_bonus = 0
        if "Kurnaz" in self.owner.traits:
            seller_trait_bonus += 1  # Satıcı kurnazsa fiyat artar
        if "Cömert" in self.owner.traits:
            seller_trait_bonus -= 2  # Satıcı cömertse fiyat azalır
        
        buyer_trait_bonus = 0
        if "Kurnaz" in buyer.traits:
            buyer_trait_bonus -= 1  # Alıcı kurnazsa fiyat azalır
        if "Cömert" in buyer.traits:
            buyer_trait_bonus += 1  # Alıcı cömertse fiyat artar
        
        # Müzakere başarı şansını hesapla
        charisma_diff = (buyer.charisma - self.owner.charisma) / 10  # -5 ile +5 arası
        
        # Toplam fiyat ayarlaması
        price_adjustment = relationship_bonus + seller_trait_bonus + buyer_trait_bonus + charisma_diff
        adjusted_price = max(1, int(base_price * (1 + price_adjustment / 10)))  # En fazla %50 indirim/artış
        
        print(f"Pazarlık: {buyer.name} ve {self.owner.name} arasında {amount} {self.stall_type} için pazarlık.")
        print(f"Başlangıç fiyatı: {base_price}, Son fiyat: {adjusted_price} altın")
        
        return adjusted_price


class Market(QObject):
    """Pazar alanı sınıfı"""
    transaction_completed = pyqtSignal(object, object, str, int, int)  # Satıcı, alıcı, ürün, miktar, fiyat
    
    def __init__(self, x: float, y: float, width: int = 300, height: int = 200):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.stalls: List[MarketStall] = []
        self.is_active = True
        
        # Pazar alanının çarpışma alanı
        self.rect = QRectF(self.x, self.y - self.height, self.width, self.height)
        
        # Varsayılan tezgahları oluştur
        self.create_default_stalls()
        
        print(f"Pazar alanı oluşturuldu: ({self.x}, {self.y}), {self.width}x{self.height}")
    
    def create_default_stalls(self) -> None:
        """Varsayılan tezgahları oluştur"""
        stall_types = ["odun", "erzak", "ev"]
        stall_width = 50
        
        # Tezgahları yan yana yerleştir
        for i, stall_type in enumerate(stall_types):
            stall_x = self.x + 60 + (i * (stall_width + 20))  # 20 piksel boşluk
            stall_y = self.y - 40  # Zeminden 40 piksel yukarıda
            
            stall = MarketStall(stall_x, stall_y, stall_width, 40, stall_type)
            self.stalls.append(stall)
            
            print(f"{stall_type.capitalize()} tezgahı oluşturuldu: ({stall_x}, {stall_y})")
    
    def find_stall_by_type(self, stall_type: str) -> Optional[MarketStall]:
        """Belirli tipteki tezgahı bul"""
        for stall in self.stalls:
            if stall.stall_type == stall_type:
                return stall
        return None
    
    def find_available_stall(self, stall_type: str) -> Optional[MarketStall]:
        """Müsait olan belirli tipteki tezgahı bul"""
        stall = self.find_stall_by_type(stall_type)
        if stall and not stall.is_active:
            return stall
        return None
    
    def find_active_stall(self, stall_type: str) -> Optional[MarketStall]:
        """Aktif olan belirli tipteki tezgahı bul"""
        stall = self.find_stall_by_type(stall_type)
        if stall and stall.is_active:
            return stall
        return None
    
    def find_stall_by_owner(self, villager) -> Optional[MarketStall]:
        """Belirli köylüye ait tezgahı bul"""
        for stall in self.stalls:
            if stall.owner == villager:
                return stall
        return None
    
    def contains_point(self, x: float, y: float) -> bool:
        """Verilen nokta pazar alanının içinde mi kontrol et"""
        return self.rect.contains(x, y)
    
    def process_transaction(self, buyer, seller, stall_type: str, amount: int) -> bool:
        """Alışveriş işlemini gerçekleştir"""
        # Satıcının tezgahını bul
        seller_stall = self.find_stall_by_owner(seller)
        if not seller_stall or seller_stall.stall_type != stall_type:
            print(f"Satıcı {seller.name}'in {stall_type} tezgahı bulunamadı!")
            return False
        
        # Tezgahta yeterli ürün var mı kontrol et
        if not seller_stall.has_enough_inventory(amount):
            print(f"Satıcı {seller.name}'in tezgahında yeterli {stall_type} yok!")
            return False
        
        # Fiyatı belirle (pazarlık yaş)
        price = seller_stall.negotiate_price(buyer, amount)
        
        # Alıcının yeterli parası var mı kontrol et
        if buyer.money < price:
            print(f"Alıcı {buyer.name}'in yeterli parası yok! Gerekli: {price}, Mevcut: {buyer.money}")
            return False
        
        # Ürünü tezgahtan çıkar
        if not seller_stall.remove_inventory(amount):
            return False
        
        # Parayı transfer et
        buyer.money -= price
        seller.money += price
        
        # Alıcı ve satıcı arasındaki ilişkiyi güncelle
        # İşlem başarılı olduysa ilişkiyi biraz artır
        if buyer.name in seller.relationships:
            seller.relationships[buyer.name] += 2
        else:
            seller.relationships[buyer.name] = 2
            
        if seller.name in buyer.relationships:
            buyer.relationships[seller.name] += 2
        else:
            buyer.relationships[seller.name] = 2
        
        # Tamamlanan işlemi bildir
        self.transaction_completed.emit(seller, buyer, stall_type, amount, price)
        
        print(f"İşlem tamamlandı: {buyer.name}, {seller.name}'den {amount} {stall_type} satın aldı. Fiyat: {price} altın")
        return True 