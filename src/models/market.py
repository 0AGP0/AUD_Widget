from dataclasses import dataclass, field
from typing import Dict, List, Optional
from PyQt5.QtCore import QObject, QRectF, pyqtSignal

class MarketStall(QObject):
    """Pazar tezgahı sınıfı - Merkezi Stok Sistemiyle Uyumlu"""
    
    def __init__(self, x: float, y: float, width: int = 50, height: int = 40, stall_type: str = "odun"):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.stall_type = stall_type  # odun, erzak, vb.
        self.owner = None  # Tezgahı kiralayan köylü
        self.is_active = False  # Tezgah şu anda aktif mi?
        self.inventory = 0  # Basitleştirilmiş envanter (sadece sayı)
        self.id = id(self)
        
        # Merkezi pazara referans
        self.market = None
        
        # Tezgahın çarpışma alanı
        self.rect = QRectF(self.x - self.width / 2, self.y - self.height, self.width, self.height)
    
    def set_market(self, market):
        """Tezgahın bağlı olduğu pazarı ayarla"""
        self.market = market
    
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
        self.inventory = 0
        print(f"Tezgah ID: {self.id} serbest bırakıldı.")
    
    def add_inventory(self, amount: int) -> None:
        """Tezgah envanterine ürün ekle - Merkezi stok sistemine aktarılır"""
        if self.market:
            if self.stall_type == "odun":
                self.market.add_wood(amount)
            elif self.stall_type == "yiyecek":
                self.market.add_food(amount)
    
    def has_enough_inventory(self, amount: int) -> bool:
        """Tezgahta (veya merkezi stokta) yeterli ürün var mı kontrol et"""
        if not self.market:
            return False
            
        if self.stall_type == "odun":
            return self.market.wood_stock >= amount
        elif self.stall_type == "yiyecek":
            return self.market.food_stock >= amount
        
        return False
    
    def remove_inventory(self, amount: int) -> bool:
        """Tezgah envanterinden ürün çıkar - Merkezi stok sisteminden çekilir"""
        if not self.market:
            return False
            
        if self.stall_type == "odun":
            return self.market.remove_wood(amount)
        elif self.stall_type == "yiyecek":
            return self.market.remove_food(amount)
            
        return False
    
    def get_price(self, amount: int) -> int:
        """Ürün fiyatını hesapla (sabit fiyat)"""
        if not self.market:
            return 0
            
        if self.stall_type == "odun":
            return self.market.wood_price * amount
        elif self.stall_type == "yiyecek":
            return self.market.food_price * amount
            
        return 0
    
    def contains_point(self, x: float, y: float) -> bool:
        """Verilen nokta tezgahın içinde mi kontrol et"""
        return self.rect.contains(x, y)


class Market(QObject):
    """Basit pazar sınıfı"""
    transaction_completed = pyqtSignal(object, object, str, int, int)  # satıcı, alıcı, ürün, miktar, fiyat
    
    def __init__(self, x: float, y: float, width: int = 50, height: int = 50):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Merkezi stok sistemi
        self.wood_stock = 0  # Odun stoğu
        self.food_stock = 0  # Yiyecek stoğu
        
        # Sabit fiyatlar
        self.wood_price = 2  # Odun fiyatı sabit: 2 altın
        self.food_price = 3  # Yiyecek fiyatı sabit: 3 altın
        
        # Pazar alanının sınırları
        self.rect = QRectF(self.x, self.y - self.height, self.width, self.height)
        
        # Tezgahlar
        self.stalls = []
        
        # Kuyu pozisyonu (ground_widget tarafından kullanılacak)
        self.kuyu_x = 0
        
        # Varsayılan tezgahları oluştur
        self.create_default_stalls()
        
        print(f"Pazar alanı oluşturuldu: ({self.x}, {self.y}), {self.width}x{self.height}")
    
    def create_default_stalls(self):
        """Varsayılan tezgahları oluştur - Sadece görsel amaçlı"""
        stall_types = ["tezgah1", "tezgah2", "tezgah3", "tezgah4"]  # İşlevsel olmayan tezgahlar
        stall_width = 50
        stall_gap = 6  # Tezgahlar arası mesafe 6 piksel
        
        # Tezgah başlangıç pozisyonu
        base_x = self.x + 60
        
        # Tüm tezgahları yan yana yerleştir
        for i, stall_type in enumerate(stall_types):
            # Tezgah pozisyonu: Tüm tezgahlar yan yana 6 piksel arayla
            stall_x = base_x + (i * (stall_width + stall_gap))
            stall_y = self.y - 40  # Zeminden 40 piksel yukarıda
            
            stall = MarketStall(stall_x, stall_y, stall_width, 40, stall_type)
            stall.set_market(self)  # Pazara referans ver
            self.stalls.append(stall)
            
            print(f"Tezgah {i+1} oluşturuldu: ({stall_x}, {stall_y})")
        
        # Kuyu artık kalenin 300 piksel sağına yerleştirildi, burada hesaplamaya gerek yok
    
    def find_stall_by_type(self, stall_type: str) -> Optional[MarketStall]:
        """Belirli tipteki tezgahı bul"""
        for stall in self.stalls:
            if stall.stall_type == stall_type:
                return stall
        return None
    
    def find_stall_by_owner(self, villager) -> Optional[MarketStall]:
        """Belirli köylüye ait tezgahı bul"""
        for stall in self.stalls:
            if stall.owner == villager:
                return stall
        return None
    
    def get_wood_price(self) -> int:
        """Odun fiyatını döndür"""
        return self.wood_price
    
    def get_food_price(self) -> int:
        """Yiyecek fiyatını döndür"""
        return self.food_price
    
    def contains_point(self, x: float, y: float) -> bool:
        """Verilen nokta pazar alanının içinde mi kontrol et"""
        return self.rect.contains(x, y)
    
    def add_wood(self, amount: int) -> None:
        """Pazar stoğuna odun ekle"""
        self.wood_stock += amount
        print(f"Pazar stoğuna {amount} odun eklendi. Toplam: {self.wood_stock}")
        
        # Kontrol panelini güncelle
        if hasattr(self, 'game_controller') and self.game_controller:
            if hasattr(self.game_controller, 'control_panel') and self.game_controller.control_panel:
                self.game_controller.control_panel.update_market_inventory()
    
    def remove_wood(self, amount: int) -> bool:
        """Pazar stoğundan odun çıkar"""
        if self.wood_stock >= amount:
            self.wood_stock -= amount
            print(f"Pazar stoğundan {amount} odun çıkarıldı. Kalan: {self.wood_stock}")
            
            # Kontrol panelini güncelle
            if hasattr(self, 'game_controller') and self.game_controller:
                if hasattr(self.game_controller, 'control_panel') and self.game_controller.control_panel:
                    self.game_controller.control_panel.update_market_inventory()
                
            return True
        else:
            print(f"HATA: Pazarda yeterli odun yok! İstenen: {amount}, Mevcut: {self.wood_stock}")
            return False
    
    def sell_wood(self, seller, amount: int) -> None:
        """Oduncunun odun satması"""
        # Odun stoğuna ekle
        self.add_wood(amount)
        
        # Satıcıya para öde
        earned_money = amount * self.wood_price
        seller.money += earned_money
        
        # İşlem bilgisini bildir
        print(f"{seller.name} pazara {amount} odun sattı ve {earned_money} altın kazandı!")
        # Signal gönder
        self.transaction_completed.emit(seller, None, "odun", amount, earned_money)
    
    def buy_wood(self, buyer, amount: int) -> bool:
        """Alıcının odun satın alması"""
        # Yeterli odun var mı kontrol et
        if self.wood_stock < amount:
            print(f"HATA: Pazarda yeterli odun yok! İstenen: {amount}, Mevcut: {self.wood_stock}")
            return False
        
        # Alıcının parası yeterli mi kontrol et
        cost = amount * self.wood_price
        if buyer.money < cost:
            print(f"HATA: {buyer.name}'in parası yeterli değil! Gerekli: {cost}, Mevcut: {buyer.money}")
            return False
        
        # İşlemi gerçekleştir
        self.remove_wood(amount)
        buyer.money -= cost
        
        # İşlem bilgisini bildir
        print(f"{buyer.name} pazardan {amount} odun satın aldı ve {cost} altın ödedi!")
        # Signal gönder
        self.transaction_completed.emit(None, buyer, "odun", amount, cost)
        
        return True
    
    def add_food(self, amount: int) -> None:
        """Pazar stoğuna yiyecek ekle"""
        self.food_stock += amount
        print(f"Pazar stoğuna {amount} yiyecek eklendi. Toplam: {self.food_stock}")
        
        # Kontrol panelini güncelle
        if hasattr(self, 'game_controller') and self.game_controller:
            if hasattr(self.game_controller, 'control_panel') and self.game_controller.control_panel:
                self.game_controller.control_panel.update_market_inventory()
    
    def remove_food(self, amount: int) -> bool:
        """Pazar stoğundan yiyecek çıkar"""
        if self.food_stock >= amount:
            self.food_stock -= amount
            print(f"Pazar stoğundan {amount} yiyecek çıkarıldı. Kalan: {self.food_stock}")
            
            # Kontrol panelini güncelle
            if hasattr(self, 'game_controller') and self.game_controller:
                if hasattr(self.game_controller, 'control_panel') and self.game_controller.control_panel:
                    self.game_controller.control_panel.update_market_inventory()
                
            return True
        else:
            print(f"HATA: Pazarda yeterli yiyecek yok! İstenen: {amount}, Mevcut: {self.food_stock}")
            return False
    
    def sell_food(self, seller, amount: int) -> None:
        """Çiftçinin yiyecek satması"""
        # Yiyecek stoğuna ekle
        self.add_food(amount)
        
        # Satıcıya para öde
        earned_money = amount * self.food_price
        seller.money += earned_money
        
        # İşlem bilgisini bildir
        print(f"{seller.name} pazara {amount} yiyecek sattı ve {earned_money} altın kazandı!")
        # Signal gönder
        self.transaction_completed.emit(seller, None, "yiyecek", amount, earned_money)
    
    def buy_food(self, buyer, amount: int) -> bool:
        """Alıcının yiyecek satın alması"""
        # Yeterli yiyecek var mı kontrol et
        if self.food_stock < amount:
            print(f"HATA: Pazarda yeterli yiyecek yok! İstenen: {amount}, Mevcut: {self.food_stock}")
            return False
        
        # Alıcının parası yeterli mi kontrol et
        cost = amount * self.food_price
        if buyer.money < cost:
            print(f"HATA: {buyer.name}'in parası yeterli değil! Gerekli: {cost}, Mevcut: {buyer.money}")
            return False
        
        # İşlemi gerçekleştir
        self.remove_food(amount)
        buyer.money -= cost
        
        # İşlem bilgisini bildir
        print(f"{buyer.name} pazardan {amount} yiyecek satın aldı ve {cost} altın ödedi!")
        # Signal gönder
        self.transaction_completed.emit(None, buyer, "yiyecek", amount, cost)
        
        return True
        
    def process_transaction(self, buyer, seller, item_type, amount):
        """Uyumluluk için eski işlem metodu"""
        if item_type == "odun":
            if seller:
                self.sell_wood(seller, amount)
                return True
            elif buyer:
                return self.buy_wood(buyer, amount)
        elif item_type == "yiyecek":
            if seller:
                self.sell_food(seller, amount)
                return True
            elif buyer:
                return self.buy_food(buyer, amount)
        
        return False

    def set_game_controller(self, game_controller):
        """Oyun kontrolcüsünü ayarla"""
        self.game_controller = game_controller 