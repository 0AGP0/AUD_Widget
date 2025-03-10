from dataclasses import dataclass
from typing import Optional
import random
import time

@dataclass
class Villager:
    """Köylü sınıfı"""
    name: str
    gender: str
    profession: str
    appearance: int = 0
    x: float = 0.0
    y: float = 0.0
    direction: int = 1  # 1 = sağa, -1 = sola
    health: int = 100
    money: int = 0
    happiness: int = 100
    
    # Köylü özellikleri
    charisma: int = 50
    education: int = 0
    age: int = 20
    
    # Hareket özellikleri
    speed: float = 5.0  # Daha hızlı hareket (2.0 yerine)
    move_counter: int = 0  # Hareket sayacı
    max_move_time: int = 50  # Yön değiştirmeden önce maksimum hareket sayısı
    
    # Animasyon özellikleri
    current_frame: int = 0  # Mevcut animasyon karesi
    frame_count: int = 4  # Toplam animasyon karesi sayısı
    animation_speed: float = 0.2  # Animasyon hızı (saniye)
    last_frame_time: float = 0  # Son kare değişim zamanı
    is_moving: bool = False  # Hareket ediyor mu?
    
    def __post_init__(self):
        """Başlangıç değerlerini ayarla"""
        # Rastgele yaş ata (18-50 arası)
        self.age = random.randint(18, 50)
        
        # Rastgele yön ve hız ata
        self.direction = random.choice([-1, 1])
        self.speed = random.uniform(5.0, 10.0)  # Daha hızlı hareket (1.0-3.0 yerine)
        self.max_move_time = random.randint(30, 100)
        
        # Animasyon başlangıç zamanını ayarla
        self.last_frame_time = time.time()
        
        print(f"{self.name} oluşturuldu: ({self.x}, {self.y}), cinsiyet: {self.gender}, yön: {self.direction}, hız: {self.speed}")
    
    def __hash__(self):
        """Hash değerini döndür"""
        return hash((self.name, self.gender))
    
    def __eq__(self, other):
        """Eşitlik kontrolü"""
        if not isinstance(other, Villager):
            return False
        return self.name == other.name and self.gender == other.gender
    
    def set_profession(self, profession: str) -> None:
        """Meslek ata"""
        self.profession = profession
        print(f"{self.name} mesleği atandı: {profession}")
    
    def update_stats(self) -> None:
        """Özellikleri güncelle"""
        # Bu metod daha sonra detaylandırılacak
        pass
    
    def update_animation(self) -> None:
        """Animasyon karesini güncelle"""
        try:
            current_time = time.time()
            
            # Animasyon hızına göre kare değişimi
            if current_time - self.last_frame_time >= self.animation_speed:
                # Hareket ediyorsa animasyonu ilerlet
                if self.is_moving:
                    self.current_frame = (self.current_frame + 1) % self.frame_count
                else:
                    # Hareket etmiyorsa ilk kareyi göster
                    self.current_frame = 0
                
                self.last_frame_time = current_time
                
        except Exception as e:
            print(f"HATA: {self.name} animasyon güncelleme hatası: {e}")
        
    def move(self) -> None:
        """Köylüyü rastgele hareket ettir"""
        try:
            # Hareket sayacını artır
            self.move_counter += 1
            
            # Önceki pozisyonu kaydet
            old_x = self.x
            
            # Belirli bir süre sonra rastgele yön değiştir
            if self.move_counter >= self.max_move_time:
                self.direction = random.choice([-1, 1])
                self.speed = random.uniform(5.0, 10.0)  # Hızı tekrar ayarla
                self.max_move_time = random.randint(30, 100)
                self.move_counter = 0
                print(f"{self.name} yön değiştirdi: {self.direction}, yeni hız: {self.speed}")
            
            # Yöne göre hareket et
            self.x += self.speed * self.direction
            
            # Sınırları kontrol et (ekrandan çıkmasını engelle)
            if self.x < 50:  # Sol sınır
                self.x = 50
                self.direction = 1  # Sağa dön
                print(f"{self.name} sol sınıra ulaştı, sağa dönüyor")
            elif self.x > 5700:  # Sağ sınır (ekran genişliğine göre ayarla)
                self.x = 5700
                self.direction = -1  # Sola dön
                print(f"{self.name} sağ sınıra ulaştı, sola dönüyor")
            
            # Hareket olup olmadığını kontrol et
            if abs(self.x - old_x) > 0.01:
                self.is_moving = True
                # Sadece her 10 adımda bir mesaj ver
                if self.move_counter % 10 == 0:
                    print(f"{self.name} hareket etti: {old_x:.2f} -> {self.x:.2f}, değişim: {self.x - old_x:.2f}")
            else:
                self.is_moving = False
            
            # Animasyonu güncelle
            self.update_animation()
                
        except Exception as e:
            print(f"HATA: {self.name} hareket hatası: {e}")
            import traceback
            traceback.print_exc() 