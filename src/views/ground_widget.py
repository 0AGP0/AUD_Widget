from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPixmap, QColor, QTransform, QFont, QPen, QBrush, QPainterPath
from ..models.villager import Villager, TestVillager
import random
import os
import math

class GroundWidget(QWidget):
    """Zemin widget'ı - Oyun alanını çizen widget"""
    def __init__(self, parent=None, game_controller=None):
        super().__init__(parent)
        
        # Transparan arka plan için ayarlar
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Fare izlemeyi aktif et
        self.setMouseTracking(True)
        
        # Oyun kontrolcüsünü ayarla
        self.game_controller = game_controller
        
        # Zemin yüksekliği - sabit değer
        self.ground_height = 10
        
        # Çizim yapıldı mı?
        self.is_drawing = False
        
        # Resimleri saklamak için sözlük
        self.images = {
            "tree": {},  # Ağaç resimleri için sözlük
            "villager": {},  # Köylü resimleri için sözlük
            "castle": None,  # Kale resmi
            "ground": None,  # Zemin resmi
            "building_site": None,  # İnşaat alanı resmi
            "house": {},  # Ev resimleri için sözlük
            "cave": None,  # Mağara resmi
            "pazar1": None,  # Pazar1 resmi
            "pazar2": None,   # Pazar2 resmi
            "kilise": None,  # Kilise resmi
            "gardiyan": None,  # Gardiyan resmi
            "degirmen": None,  # Değirmen resmi
            "kuyu": None,  # Kuyu resmi
            "kurt": None,  # Kurt resmi
            "kus": None,  # Kuş resmi
            "karga": None  # Karga resmi
        }
        
        # Resimleri yükle
        self.load_images()
        
        print(f"GroundWidget oluşturuldu: {self.width()}x{self.height()}")
    
    def load_images(self):
        """Resimleri yükle"""
        try:
            self.images = {
                "tree": {},  # Ağaç resimleri için sözlük
                "villager": {},  # Köylü resimleri için sözlük
                "castle": None,  # Kale resmi
                "ground": None,  # Zemin resmi
                "building_site": None,  # İnşaat alanı resmi
                "house": {},  # Ev resimleri için sözlük
                "cave": None,  # Mağara resmi
                "pazar1": None,  # Pazar1 resmi
                "pazar2": None,   # Pazar2 resmi
                "kilise": None,  # Kilise resmi
                "gardiyan": None,  # Gardiyan resmi
                "degirmen": None,  # Değirmen resmi
                "kuyu": None,  # Kuyu resmi
                "kurt": None,  # Kurt resmi
                "kus": None,  # Kuş resmi
                "karga": None  # Karga resmi
            }
            
            # Ağaç resimlerini yükle
            for tree_type in [1, 2, 3]:  # Üç farklı ağaç tipi için
                tree_path = os.path.join("src", "assets", f"agac{'' if tree_type == 1 else tree_type}.png")
                if os.path.exists(tree_path):
                    self.images["tree"][tree_type] = QPixmap(tree_path)
                    print(f"Ağaç resmi yüklendi: {tree_path}")
                else:
                    print(f"UYARI: Ağaç resmi bulunamadı: {tree_path}")
            
            # Zemin resmini yükle
            ground_path = os.path.join("src", "assets", "zemin.png")
            if os.path.exists(ground_path):
                self.images["ground"] = QPixmap(ground_path)
                print(f"Zemin resmi yüklendi: {ground_path}")
            else:
                print(f"HATA: Zemin resmi bulunamadı: {ground_path}")
            
            # Kale resmini yükle
            castle_path = os.path.join("src", "assets", "kale.png")
            if os.path.exists(castle_path):
                self.images["castle"] = QPixmap(castle_path)
                print(f"Kale resmi yüklendi: {castle_path}")
            else:
                print(f"HATA: Kale resmi bulunamadı: {castle_path}")
            
            # İnşaat alanı resmini yükle
            building_site_path = os.path.join("src", "assets", "inşaat_alanı.png")
            if os.path.exists(building_site_path):
                self.images["building_site"] = QPixmap(building_site_path)
                print(f"İnşaat alanı resmi yüklendi: {building_site_path}")
            else:
                print(f"HATA: İnşaat alanı resmi bulunamadı: {building_site_path}")
            
            # Ev resimlerini yükle
            house_types = ["ev1", "ev2", "ev3"]
            for house_type in house_types:
                house_path = os.path.join("src", "assets", f"{house_type}.png")
                if os.path.exists(house_path):
                    self.images["house"][house_type] = QPixmap(house_path)
                    print(f"Ev resmi yüklendi: {house_path}")
                else:
                    print(f"UYARI: Ev resmi bulunamadı: {house_path}")
            
            # Köylü resimlerini yükle
            for gender in ["koylu", "kadin_koylu"]:
                for i in range(1, 5):  # 1-4 arası
                    villager_path = os.path.join("src", "assets", "villagers", f"{gender}{i}.png")
                    if os.path.exists(villager_path):
                        self.images["villager"][f"{gender}{i}"] = QPixmap(villager_path)
                        print(f"Köylü resmi yüklendi: {villager_path}")
                    else:
                        print(f"UYARI: Köylü resmi bulunamadı: {villager_path}")
            
            # Mağara resmini yükle
            cave_path = os.path.join("src", "assets", "magara.png")
            if os.path.exists(cave_path):
                self.images["cave"] = QPixmap(cave_path)
                print(f"Mağara resmi yüklendi: {cave_path}")
            else:
                print(f"UYARI: Mağara resmi bulunamadı: {cave_path}")
            
            # Pazar resimlerini yükle
            pazar1_path = os.path.join("src", "assets", "Pazar1.png")
            if os.path.exists(pazar1_path):
                self.images["pazar1"] = QPixmap(pazar1_path)
                print(f"Pazar1 resmi yüklendi: {pazar1_path}")
            else:
                print(f"UYARI: Pazar1 resmi bulunamadı: {pazar1_path}")
            
            pazar2_path = os.path.join("src", "assets", "Pazar2.png")
            if os.path.exists(pazar2_path):
                self.images["pazar2"] = QPixmap(pazar2_path)
                print(f"Pazar2 resmi yüklendi: {pazar2_path}")
            else:
                print(f"UYARI: Pazar2 resmi bulunamadı: {pazar2_path}")
            
            # Kilise resmini yükle
            kilise_path = os.path.join("src", "assets", "kilise.png")
            if os.path.exists(kilise_path):
                self.images["kilise"] = QPixmap(kilise_path)
                print(f"Kilise resmi yüklendi: {kilise_path}")
            else:
                print(f"UYARI: Kilise resmi bulunamadı: {kilise_path}")
            
            # Gardiyan resmini yükle
            gardiyan_path = os.path.join("src", "assets", "gardiyan.png")
            if os.path.exists(gardiyan_path):
                self.images["gardiyan"] = QPixmap(gardiyan_path)
                print(f"Gardiyan resmi yüklendi: {gardiyan_path}")
            else:
                print(f"UYARI: Gardiyan resmi bulunamadı: {gardiyan_path}")
            
            # Değirmen resmini yükle
            degirmen_path = os.path.join("src", "assets", "degirmen.png")
            if os.path.exists(degirmen_path):
                self.images["degirmen"] = QPixmap(degirmen_path)
                print(f"Değirmen resmi yüklendi: {degirmen_path}")
            else:
                print(f"UYARI: Değirmen resmi bulunamadı: {degirmen_path}")
            
            # Kuyu resmini yükle
            kuyu_path = os.path.join("src", "assets", "Kuyu.png")
            if os.path.exists(kuyu_path):
                self.images["kuyu"] = QPixmap(kuyu_path)
                print(f"Kuyu resmi yüklendi: {kuyu_path}")
            else:
                print(f"UYARI: Kuyu resmi bulunamadı: {kuyu_path}")
            
            # Kurt resmini yükle
            kurt_path = os.path.join("src", "assets", "kurt.png")
            if os.path.exists(kurt_path):
                self.images["kurt"] = QPixmap(kurt_path)
                print(f"Kurt resmi yüklendi: {kurt_path}")
            else:
                print(f"UYARI: Kurt resmi bulunamadı: {kurt_path}")
            
            # Kuş ve karga resimlerini yükle
            kus_path = os.path.join("src", "assets", "kus.png")
            if os.path.exists(kus_path):
                self.images["kus"] = QPixmap(kus_path)
                print(f"Kuş resmi yüklendi: {kus_path}")
            else:
                print(f"UYARI: Kuş resmi bulunamadı: {kus_path}")
                
            karga_path = os.path.join("src", "assets", "karga.png")
            if os.path.exists(karga_path):
                self.images["karga"] = QPixmap(karga_path)
                print(f"Karga resmi yüklendi: {karga_path}")
            else:
                print(f"UYARI: Karga resmi bulunamadı: {karga_path}")
            
            print("Resimler yüklendi")
            
        except Exception as e:
            print(f"HATA: Resim yükleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def load_villager_image(self, villager):
        """Köylü resmini yükle"""
        try:
            # Resim dosya adını belirle
            if villager.gender == "Erkek":
                image_name = f"koylu{villager.appearance + 1}.png"
            else:
                image_name = f"kadin_koylu{villager.appearance + 1}.png"
            
            # Resim dosyasının tam yolunu oluştur
            current_dir = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(current_dir, "..", "assets")
            villagers_dir = os.path.join(assets_dir, "villagers")
            image_path = os.path.join(villagers_dir, image_name)
            
            # Debug bilgileri
            print(f"Köylü resmi yükleniyor:")
            print(f"  Köylü: {villager.name}")
            print(f"  Cinsiyet: {villager.gender}")
            print(f"  Görünüm: {villager.appearance}")
            print(f"  Resim adı: {image_name}")
            print(f"  Tam yol: {image_path}")
            print(f"  Klasör var mı: {os.path.exists(villagers_dir)}")
            print(f"  Resim var mı: {os.path.exists(image_path)}")
            
            # Villagers klasörünü kontrol et
            if not os.path.exists(villagers_dir):
                print(f"HATA: Villagers klasörü bulunamadı: {villagers_dir}")
                return None
            
            # Resmi yükle
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if pixmap.isNull():
                    print(f"HATA: Resim yüklenemedi: {image_path}")
                    return None
                    
                # Resmi 32x32 boyutuna küçült
                pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                print(f"Resim başarıyla yüklendi: {image_path}")
                return pixmap
            else:
                print(f"UYARI: Resim dosyası bulunamadı: {image_path}")
                return None
                
        except Exception as e:
            print(f"HATA: Köylü resmi yükleme hatası: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    def paintEvent(self, event):
        """Çizim olayı"""
        try:
            # Zaten çizim yapılıyorsa, tekrar çizim yapma
            if self.is_drawing:
                return
                
            self.is_drawing = True
            
            # Painter oluştur
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)  # Kenarları yumuşat
            
            # Zemini çiz
            self.draw_ground(painter)
            
            # Mağarayı çiz
            self.draw_cave(painter)
            
            # Kaleyi çiz
            self.draw_castle(painter)
            
            # Kiliseyi çiz
            self.draw_church(painter)
            
            # Ağaçları çiz
            self.draw_trees(painter)
            
            # Evleri çiz
            self.draw_houses(painter)
            
            # İnşaat alanları çiz
            self.draw_building_sites(painter)
            
            # Pazar yerini çiz
            self.draw_markets(painter)
            
            # Kuyuyu çiz
            self.draw_well(painter)
            
            # Gardiyanı çiz
            self.draw_guard(painter)
            
            # Değirmeni çiz
            self.draw_mill(painter)
            
            # Kuş ve kargaları çiz
            self.draw_birds(painter)
            
            # Kurtları çiz
            self.draw_wolves(painter)
            
            # Köylüleri çiz
            self.draw_villagers(painter)
            
            painter.end()
            self.is_drawing = False
            
        except Exception as e:
            self.is_drawing = False
            print(f"HATA: Çizim hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_ground(self, painter):
        """Zemini çiz"""
        try:
            # Zemin resmi yüklü değilse çıkış yap
            if self.images["ground"] is None:
                print("HATA: Zemin resmi yüklenemediği için çizilemedi")
                return
            
            # Orijinal zemin resminin boyutları
            original_width = self.images["ground"].width()
            original_height = self.images["ground"].height()
            
            print(f"Orijinal zemin boyutları: {original_width}x{original_height}")
            
            # Yeni boyutları hesapla (25x25 piksel)
            new_width = 25
            new_height = 25
            
            print(f"Yeni zemin boyutları: {new_width}x{new_height}")
            
            # Zemin resmini yeni boyuta ölçeklendir
            scaled_ground = self.images["ground"].scaled(new_width, new_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            
            # Zeminin y pozisyonunu hesapla (ekranın en altı)
            ground_y = self.height() - new_height + 15
            
            # Ekran genişliğini al
            screen_width = self.width()
            
            # Kaç tane zemin resmi gerektiğini hesapla
            tile_count = screen_width // new_width + 1  # +1 ekstra karo ekle (sağ kenar için)
            
            print(f"Ekran genişliği: {screen_width}, Gerekli karo sayısı: {tile_count}")
            
            # Zemini yatay olarak tekrarla
            for i in range(tile_count):
                x = i * new_width
                painter.drawPixmap(x, ground_y, scaled_ground)
            
            print(f"Zemin çizildi: {tile_count} adet karo, toplam genişlik: {tile_count * new_width} piksel")
            
        except Exception as e:
            print(f"HATA: Zemin çizme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_castle(self, painter):
        """Kaleyi çiz"""
        try:
            # Kale resmi yüklü değilse çıkış yap
            if self.images["castle"] is None:
                print("HATA: Kale resmi yüklenemediği için çizilemedi")
                return
            
            # Kale boyutlarını küçült
            castle_width = 150
            castle_height = 150
            scaled_castle = self.images["castle"].scaled(castle_width, castle_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Kale pozisyonu - sol tarafta, zemin üzerinde
            x = 10
            # Zemin seviyesini hesapla
            ground_y = self.height() - self.ground_height
            # Kaleyi zemin üzerine yerleştir
            y = ground_y - scaled_castle.height() + 20  # Biraz gömülü olsun
            
            # Kaleyi çiz
            painter.drawPixmap(x, y, scaled_castle)
            
        except Exception as e:
            print(f"HATA: Kale çizme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_church(self, painter):
        """Kiliseyi çiz"""
        try:
            if not self.images["kilise"]:
                print("UYARI: Kilise resmi yüklenmemiş")
                return
            
            # Kilise boyutlarını ayarla
            church_width = 130
            church_height = 130
            
            # Kilise resmini ölçeklendir
            scaled_church = self.images["kilise"].scaled(church_width, church_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Kalenin konumundan 300 piksel sağda
            church_x = 300 + 10  # Kale 10 pikselde başlıyor
            
            # Y pozisyonunu hesapla (zemin üzerinde)
            church_y = self.height() - self.ground_height - church_height + 15
            
            # Kiliseyi çiz
            painter.drawPixmap(church_x, church_y, scaled_church)
            
            print(f"Kilise çizildi: Konum=({church_x}, {church_y}), Boyut={church_width}x{church_height}")
            
        except Exception as e:
            print(f"HATA: Kilise çizme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_trees(self, painter):
        """Ağaçları çiz"""
        try:
            if not hasattr(self, 'game_controller') or not self.game_controller:
                return
                
            for tree in self.game_controller.trees:
                if not tree.is_visible:
                    continue
                    
                # Ağaç resmini al
                tree_img = self.images["tree"].get(tree.tree_type)
                if not tree_img:
                    # Eğer belirtilen tip için resim yoksa, tip 1'i kullan
                    tree_img = self.images["tree"].get(1)
                    if not tree_img:
                        continue
                
                # Ağacın ekrandaki pozisyonu
                tree_x = int(tree.x - tree.width / 2)
                tree_y = self.height() - self.ground_height - tree.height + 2 # +2'den +15'e değiştirildi
                
                # Ağacı çiz
                painter.drawPixmap(tree_x, tree_y, tree.width, tree.height, tree_img)
                
        except Exception as e:
            print(f"HATA: Ağaç çizme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_villagers(self, painter):
        """Köylüleri çiz"""
        try:
            print("Köylüler çiziliyor...")
            if not hasattr(self, 'game_controller') or not self.game_controller:
                print("HATA: game_controller bulunamadı")
                return
            
            # Köylüler için görüntü ekranı oluşturmaya hazırlanıyoruz
            ground_y = int(self.height() - self.ground_height)
            
            if not hasattr(self.game_controller, 'villagers') or not self.game_controller.villagers:
                print("UYARI: Köylüler listesi bulunamadı veya boş")
                return
                
            print(f"Toplam {len(self.game_controller.villagers)} köylü çizilecek")

            for i, villager in enumerate(self.game_controller.villagers):
                try:
                    print(f"Köylü çiziliyor: {villager.name}, x={villager.x}, y={villager.y}")
                    
                    # Köylünün ekrandaki pozisyonu - tam sayı olarak
                    x = int(villager.x)
                    y = int(ground_y - villager.height)  # Zemin üzerinde
                    
                    # Köylünün mesleki tipine göre resmi seç
                    if villager.gender == "Erkek":
                        img_key = f"koylu{villager.appearance}"
                    else:
                        img_key = f"kadin_koylu{villager.appearance}"
                    
                    img = self.images["villager"].get(img_key)
                    print(f"Köylü resim anahtarı: {img_key}, Resim bulundu: {img is not None}")
                    
                    # Eğer resim bulunamadıysa varsayılan resmi kullan
                    if not img:
                        default_key = "koylu1" if villager.gender == "Erkek" else "kadin_koylu1"
                        if default_key in self.images["villager"]:
                            img = self.images["villager"][default_key]
                            print(f"Varsayılan resim kullanılıyor: {default_key}")
                        else:
                            # Hiç resim yoksa çizme
                            print(f"HATA: Köylü için resim bulunamadı: {villager.name}")
                            continue
                    
                    # Köylü resmini ölçeklendir - tam sayı boyutlarıyla
                    villager_width = int(villager.width)
                    villager_height = int(villager.height)
                    scaled_img = img.scaled(villager_width, villager_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    
                    # Köylü hareket yönüne göre resmi çevir
                    if hasattr(villager, 'direction_x') and villager.direction_x < 0:  # Sola gidiyorsa
                        transform = QTransform().scale(-1, 1)  # Yatay eksende çevir
                        scaled_img = scaled_img.transformed(transform)
                    
                    # Eğilme animasyonunu uygula
                    if hasattr(villager, 'rotation') and villager.rotation != 0:
                        transform = QTransform()
                        transform.rotate(villager.rotation)
                        scaled_img = scaled_img.transformed(transform)
                    
                    # Köylüyü çiz
                    painter.drawPixmap(x, y, scaled_img)
                    print(f"Köylü çizildi: {villager.name}, konum: ({x}, {y})")
                    
                    # Konuşma baloncuğunu çiz - eğer köylü konuşuyorsa
                    if hasattr(villager, 'chat_message') and villager.chat_message:
                        print(f"Köylü konuşuyor: {villager.name}, mesaj: {villager.chat_message}")
                        self.draw_chat_bubble(painter, villager, x + villager_width // 2, y)
                    
                    # Yazı alanı genişliği (köylü genişliğinin 2 katı)
                    text_width = int(villager_width * 2)
                    text_x = int(x - (text_width - villager_width) // 2)  # Merkezle
                    
                    # Köylü ismini çiz
                    painter.setPen(Qt.white)
                    painter.setFont(QFont("Arial", 8))
                    painter.drawText(
                        text_x, y - 15, text_width, 15,
                        Qt.AlignCenter, villager.name
                    )
                    
                    # Köylü durumunu çiz
                    if hasattr(villager, 'state') and villager.state:
                        # Durum yazısı için arka plan çiz
                        state_rect = QRect(text_x, y - 30, text_width, 15)
                        painter.fillRect(state_rect, QColor(0, 0, 0, 128))  # Yarı saydam siyah arka plan
                        
                        painter.setPen(Qt.yellow)
                        painter.drawText(
                            state_rect,
                            Qt.AlignCenter, villager.state
                        )
                    else:
                        # Mesleğini göster
                        profession_rect = QRect(text_x, y - 30, text_width, 15)
                        painter.fillRect(profession_rect, QColor(0, 0, 0, 128))  # Yarı saydam siyah arka plan
                        
                        painter.setPen(Qt.yellow)
                        painter.drawText(
                            profession_rect,
                            Qt.AlignCenter, villager.profession
                        )
                except Exception as e:
                    print(f"HATA: Köylü çizme hatası ({villager.name}): {e}")
                    import traceback
                    traceback.print_exc()
        
        except Exception as e:
            print(f"HATA: Köylü çizim hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_chat_bubble(self, painter, villager, x, y):
        """Diyalog baloncuğunu çiz"""
        try:
            # Baloncuk boyutu
            bubble_width = max(140, len(villager.chat_message) * 6)  # Metin uzunluğuna göre genişlik
            bubble_height = 40
            
            # Baloncuk pozisyonu
            bubble_x = x - (bubble_width - villager.width) // 2  # Köylünün üzerinde merkezi
            bubble_y = y - bubble_height - 40  # Köylünün biraz yukarısında
            
            # Baloncuk arka planı (yuvarlak köşeli dikdörtgen)
            painter.setPen(Qt.black)
            painter.setBrush(QBrush(QColor(255, 255, 255, 230)))  # Beyaz, hafif saydam
            painter.drawRoundedRect(bubble_x, bubble_y, bubble_width, bubble_height, 15, 15)
            
            # Baloncuk kuyruğu (üçgen)
            path = QPainterPath()
            path.moveTo(x, bubble_y + bubble_height)  # Baloncuğun alt ortası
            path.lineTo(x - 10, bubble_y + bubble_height + 10)  # Sol alt köşe
            path.lineTo(x + 10, bubble_y + bubble_height + 10)  # Sağ alt köşe
            path.closeSubpath()
            painter.fillPath(path, QBrush(QColor(255, 255, 255, 230)))  # Beyaz, hafif saydam
            painter.strokePath(path, QPen(Qt.black))
            
            # Diyalog metnini çiz
            painter.setPen(Qt.black)
            painter.setFont(QFont("Arial", 8))
            
            # Metin için hizalama
            text_rect = QRect(bubble_x + 5, bubble_y + 5, bubble_width - 10, bubble_height - 10)
            painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, villager.chat_message)
            
        except Exception as e:
            print(f"HATA: Diyalog baloncuğu çizim hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def mousePressEvent(self, event):
        """Fare tıklama olayı"""
        try:
            if not hasattr(self, 'game_controller') or self.game_controller is None:
                print("HATA: game_controller bulunamadı")
                return
                
            # Tıklama pozisyonunu al
            x = event.x()
            y = event.y()
            print(f"Fare tıklaması: ({x}, {y})")
            
            # Köylü seç - tıklama olayı köylülerin hareketini etkilemesin
            selected_villager = self.game_controller.select_villager(x, y)
            
            # Eğer köylü seçildiyse ve kontrol paneli varsa, köylüyü panelde göster
            if selected_villager and hasattr(self.parent().parent(), 'control_panel_window'):
                control_panel = self.parent().parent().control_panel_window.control_panel
                control_panel.select_villager(selected_villager)
                
        except Exception as e:
            print(f"HATA: Fare tıklama olayı hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_houses(self, painter):
        """Evleri çiz"""
        try:
            # Oyun kontrolcüsü yoksa çıkış yap
            if not self.game_controller:
                return
                
            # Evler yoksa çıkış yap
            if not hasattr(self.game_controller, 'houses') or not self.game_controller.houses:
                return
                
            # Tüm evleri çiz
            for house in self.game_controller.houses:
                # Ev konumunu hesapla
                x = int(house.x - house.width / 2)
                y = int(house.y - house.height)
                
                # Ev tipine göre resmi seç
                house_type = house.house_type
                house_image = None
                
                if house_type in self.images["house"]:
                    house_image = self.images["house"][house_type]
                else:
                    # Varsayılan ev resmi
                    if self.images["house"]:
                        house_image = next(iter(self.images["house"].values()), None)
                
                if house_image:
                    # Evi çiz - int değerler kullanarak
                    scaled_img = house_image.scaled(int(house.width), int(house.height), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    painter.drawPixmap(x, y, scaled_img)
                else:
                    # Resim yoksa basit bir ev çiz
                    # Ev tipine göre renk seç
                    if house.house_type == "ev1":
                        color1 = QColor(255, 255, 224)  # Açık sarı
                        color2 = QColor(139, 69, 19)    # Kahverengi (çatı)
                    elif house.house_type == "ev2":
                        color1 = QColor(176, 224, 230)  # Açık mavi
                        color2 = QColor(47, 79, 79)     # Koyu mavi (çatı)
                    elif house.house_type == "ev3":
                        color1 = QColor(152, 251, 152)  # Açık yeşil
                        color2 = QColor(34, 139, 34)    # Koyu yeşil (çatı)
                    else:
                        color1 = QColor(200, 200, 200)  # Gri
                        color2 = QColor(100, 100, 100)  # Koyu gri (çatı)
                    
                    # Evin gövdesini çiz
                    house_body_height = int(house.height * 2/3)
                    house_body_y = y + house.height - house_body_height
                    
                    painter.setBrush(QBrush(color1))
                    painter.setPen(QPen(Qt.black, 2))
                    painter.drawRect(x, house_body_y, int(house.width), house_body_height)
                    
                    # Çatıyı çiz
                    roof_points = [
                        QPoint(x, house_body_y),
                        QPoint(x + int(house.width // 2), y),
                        QPoint(x + int(house.width), house_body_y)
                    ]
                    painter.setBrush(QBrush(color2))
                    painter.drawPolygon(roof_points)
                    
                    # Kapıyı çiz
                    door_width = int(house.width // 4)
                    door_height = house_body_height // 2
                    door_x = x + (int(house.width) - door_width) // 2
                    door_y = house_body_y + house_body_height - door_height
                    
                    painter.setBrush(QBrush(QColor(139, 69, 19)))  # Kahverengi
                    painter.drawRect(door_x, door_y, door_width, door_height)
                    
                    # Pencereyi çiz
                    window_size = int(house.width // 5)
                    window_x = x + (int(house.width) - window_size) // 2
                    window_y = house_body_y + house_body_height // 4
                    
                    painter.setBrush(QBrush(QColor(173, 216, 230)))  # Açık mavi
                    painter.drawRect(window_x, window_y, window_size, window_size)
                
                # Ev sahibi varsa, üzerine isim etiketi ekle
                if house.owner:
                    # Yazı alanı genişliği (ev genişliğinin 1.5 katı)
                    text_width = int(house.width * 1.5)
                    text_x = x - (text_width - int(house.width)) // 2  # Merkezle
                    
                    # Arka plan çiz
                    owner_rect = QRect(text_x, y - 20, text_width, 20)
                    painter.fillRect(owner_rect, QColor(0, 0, 0, 128))  # Yarı saydam siyah arka plan
                    
                    painter.setPen(Qt.white)
                    painter.setFont(QFont("Arial", 8))
                    painter.drawText(
                        owner_rect,
                        Qt.AlignCenter, f"{house.owner}'nin Evi"
                    )
                
        except Exception as e:
            print(f"HATA: Ev çizim hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_building_sites(self, painter):
        """İnşaat alanlarını çiz"""
        try:
            # Oyun kontrolcüsü yoksa çıkış yap
            if not self.game_controller:
                return
                
            # İnşaat alanları yoksa çıkış yap
            if not hasattr(self.game_controller, 'building_sites') or not self.game_controller.building_sites:
                return
                
            # Tüm inşaat alanlarını çiz
            for site in self.game_controller.building_sites:
                # İnşaat alanı konumunu hesapla
                x = int(site.x - site.width / 2)
                y = int(site.y - site.height)
                
                # İnşaat alanı çerçevesini çiz
                painter.setPen(QPen(Qt.black, 2, Qt.DashLine))
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(x, y, int(site.width), int(site.height))
                
                # İnşaat alanı zeminini çiz
                ground_rect = QRect(x, y, int(site.width), int(site.height))
                painter.fillRect(ground_rect, QColor(194, 178, 128, 100))  # Açık toprak rengi, yarı saydam
                
                # İnşaat iskeletini çiz
                if site.progress > 0:
                    # İlerleme durumuna göre iskelet yüksekliği
                    skeleton_height = int(site.height * min(site.progress / 100, 0.8))
                    skeleton_y = y + int(site.height) - skeleton_height
                    
                    # İskelet çerçevesi
                    painter.setPen(QPen(Qt.black, 2))
                    painter.setBrush(QBrush(QColor(139, 69, 19, 150)))  # Kahverengi, yarı saydam
                    painter.drawRect(x + 5, skeleton_y, int(site.width) - 10, skeleton_height)
                    
                    # İskelet çubukları
                    painter.setPen(QPen(QColor(101, 67, 33), 3))  # Koyu kahverengi
                    
                    # Dikey çubuklar
                    num_posts = 4
                    post_spacing = site.width / (num_posts + 1)
                    
                    for i in range(1, num_posts + 1):
                        post_x = x + int(i * post_spacing)
                        painter.drawLine(post_x, skeleton_y, post_x, skeleton_y + skeleton_height)
                    
                    # Yatay çubuklar
                    num_beams = 2
                    beam_spacing = skeleton_height / (num_beams + 1)
                    
                    for i in range(1, num_beams + 1):
                        beam_y = skeleton_y + int(i * beam_spacing)
                        painter.drawLine(x + 5, beam_y, x + int(site.width) - 5, beam_y)
                
                # İnşaat malzemeleri
                if site.progress < 100:
                    # Kereste yığını
                    wood_pile_width = int(site.width / 4)
                    wood_pile_height = int(site.height / 6)
                    wood_pile_x = x + int(site.width) - wood_pile_width - 5
                    wood_pile_y = y + int(site.height) - wood_pile_height
                    
                    painter.setBrush(QBrush(QColor(139, 69, 19)))  # Kahverengi
                    painter.setPen(QPen(Qt.black, 1))
                    painter.drawRect(int(wood_pile_x), int(wood_pile_y), wood_pile_width, wood_pile_height)
                    
                    # Kereste çizgileri
                    painter.setPen(QPen(QColor(101, 67, 33), 1))  # Koyu kahverengi
                    for i in range(3):
                        line_y = wood_pile_y + (i + 1) * wood_pile_height / 4
                        painter.drawLine(int(wood_pile_x), int(line_y), int(wood_pile_x) + wood_pile_width, int(line_y))
                
                # İlerleme çubuğu
                progress_height = 10
                progress_y = y - progress_height - 5
                
                # Arka plan
                painter.setBrush(QBrush(Qt.lightGray))
                painter.setPen(QPen(Qt.black, 1))
                painter.drawRect(x, progress_y, int(site.width), progress_height)
                
                # İlerleme
                progress_width = int(site.width * site.progress / 100)
                painter.setBrush(QBrush(Qt.green))
                painter.setPen(Qt.NoPen)
                painter.drawRect(x, progress_y, progress_width, progress_height)
                
                # İlerleme yüzdesi
                painter.setPen(Qt.black)
                painter.setFont(QFont("Arial", 8, QFont.Bold))
                painter.drawText(
                    x, progress_y, int(site.width), progress_height,
                    Qt.AlignCenter, f"%{int(site.progress)}"
                )
                
                # İnşaat bilgisi
                info_y = progress_y - 20
                info_height = 20
                info_rect = QRect(x - 10, info_y, int(site.width) + 20, info_height)
                
                # Arka plan
                painter.fillRect(info_rect, QColor(0, 0, 0, 128))  # Yarı saydam siyah
                
                # Bilgi metni
                painter.setPen(Qt.white)
                painter.setFont(QFont("Arial", 8))
                
                info_text = f"İnşaat Alanı: {site.house_type}"
                if site.builder:
                    info_text += f" - İnşaatçı: {site.builder}"
                
                painter.drawText(
                    info_rect,
                    Qt.AlignCenter, info_text
                )
                
        except Exception as e:
            print(f"HATA: İnşaat alanı çizim hatası: {e}")
            import traceback
            traceback.print_exc() 
    
    def draw_cave(self, painter):
        """Mağarayı çiz"""
        try:
            if not self.images["cave"]:
                print("UYARI: Mağara resmi yüklenmemiş")
                return
                
            # Mağara boyutlarını ağaçlarla aynı boyuta getir
            cave_width = 100  # Ağaç genişliği ile aynı
            cave_height = 70  # Ağaç yüksekliği ile aynı
            
            # Mağara resmini ölçeklendir
            scaled_cave = self.images["cave"].scaled(cave_width, cave_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Mağarayı ekranın en sağına yerleştir
            cave_x = self.width() - cave_width + 30  # En sağ kenara
            cave_y = self.height() - self.ground_height - cave_height + 15  # Ağaçlarla aynı hizada
            
            # Mağarayı çiz
            painter.drawPixmap(cave_x, cave_y, scaled_cave)
            
            print(f"Mağara çizildi: Konum=({cave_x}, {cave_y}), Boyut={cave_width}x{cave_height}")
            
        except Exception as e:
            print(f"HATA: Mağara çizme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_markets(self, painter):
        """Pazar yerlerini çiz"""
        try:
            if not self.images["pazar1"] or not self.images["pazar2"]:
                print("UYARI: Pazar resimleri yüklenememiş")
                return
            
            # Pazar boyutlarını ayarla
            market_width = 65
            market_height = 65
            
            # Pazar resimlerini ölçeklendir
            scaled_pazar1 = self.images["pazar1"].scaled(market_width, market_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            scaled_pazar2 = self.images["pazar2"].scaled(market_width, market_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Kalenin konumundan 300 piksel sağda başla
            base_x = 600 + 10  # Kale 10 pikselde başlıyor
            
            # Y pozisyonunu hesapla (zemin üzerinde)
            market_y = self.height() - self.ground_height - market_height + 11
            
            # Pazar1'i çiz
            painter.drawPixmap(base_x, market_y, scaled_pazar1)
            
            # Pazar2'yi çiz (10 piksel sağda)
            painter.drawPixmap(base_x + market_width + 10, market_y, scaled_pazar2)
            
            print(f"Pazarlar çizildi: Pazar1=({base_x}, {market_y}), Pazar2=({base_x + market_width + 10}, {market_y})")
            
        except Exception as e:
            print(f"HATA: Pazar çizme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_guard(self, painter):
        """Gardiyanı çiz"""
        try:
            if not self.images["gardiyan"]:
                print("UYARI: Gardiyan resmi yüklenmemiş")
                return
            
            # Gardiyan boyutlarını ayarla
            guard_width = 100
            guard_height = 100
            
            # Gardiyan resmini ölçeklendir
            scaled_guard = self.images["gardiyan"].scaled(guard_width, guard_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Kalenin konumundan 900 piksel sağda
            guard_x = 900 + 10  # Kale 10 pikselde başlıyor
            
            # Y pozisyonunu hesapla (zemin üzerinde)
            guard_y = self.height() - self.ground_height - guard_height + 5
            
            # Gardiyanı çiz
            painter.drawPixmap(guard_x, guard_y, scaled_guard)
            
            print(f"Gardiyan çizildi: Konum=({guard_x}, {guard_y}), Boyut={guard_width}x{guard_height}")
            
        except Exception as e:
            print(f"HATA: Gardiyan çizme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_mill(self, painter):
        """Değirmeni çiz"""
        try:
            if not self.images["degirmen"]:
                print("UYARI: Değirmen resmi yüklenmemiş")
                return
            
            # Değirmen boyutlarını ayarla
            mill_width = 110
            mill_height = 110
            
            # Değirmen resmini ölçeklendir
            scaled_mill = self.images["degirmen"].scaled(mill_width, mill_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Kalenin konumundan 1500 piksel sağda
            mill_x = 1500 + 10  # Kale 10 pikselde başlıyor
            
            # Y pozisyonunu hesapla (zemin üzerinde)
            mill_y = self.height() - self.ground_height - mill_height + 1
            
            # Değirmeni çiz
            painter.drawPixmap(mill_x, mill_y, scaled_mill)
            
            print(f"Değirmen çizildi: Konum=({mill_x}, {mill_y}), Boyut={mill_width}x{mill_height}")
            
        except Exception as e:
            print(f"HATA: Değirmen çizme hatası: {e}")
            import traceback
            traceback.print_exc()

    def draw_well(self, painter):
        """Kuyuyu çiz"""
        try:
            if not self.images["kuyu"]:
                print("UYARI: Kuyu resmi yüklenmemiş")
                return
            
            # Kuyu boyutlarını ayarla
            well_width = 45
            well_height = 45
            
            # Kuyu resmini ölçeklendir
            scaled_well = self.images["kuyu"].scaled(well_width, well_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Pazar2'nin konumundan 100 piksel sağda
            # Pazarların konumu: base_x = 600 + 10
            # Pazar2'nin konumu: base_x + market_width + 10 = 610 + 65 + 10 = 685
            well_x = 685 + 90  # Pazar2'nin konumu + 100 piksel
            
            # Y pozisyonunu hesapla (zemin üzerinde)
            well_y = self.height() - self.ground_height - well_height + 7
            
            # Kuyuyu çiz
            painter.drawPixmap(well_x, well_y, scaled_well)
            
            print(f"Kuyu çizildi: Konum=({well_x}, {well_y}), Boyut={well_width}x{well_height}")
            
        except Exception as e:
            print(f"HATA: Kuyu çizme hatası: {e}")
            import traceback
            traceback.print_exc()

    def draw_wolves(self, painter):
        """Kurtları çiz - köylülere benzer şekilde"""
        try:
            # Game controller kontrolü
            if not hasattr(self, 'game_controller') or not self.game_controller:
                print("UYARI: draw_wolves - game_controller bulunamadı")
                return
                
            # Kurt resmi yüklü değilse çıkış yap
            if not self.images.get("kurt"):
                print("UYARI: Kurt resmi yüklenmemiş")
                return
                
            # Kurtlar listesi kontrolü
            if not hasattr(self.game_controller, 'wolves') or not self.game_controller.wolves:
                print("UYARI: draw_wolves - wolves listesi bulunamadı veya boş")
                return
            
            print(f"Kurtlar çiziliyor... {len(self.game_controller.wolves)} kurt var")
            
            # Tüm kurtları çiz
            for i, wolf in enumerate(self.game_controller.wolves):
                try:
                    # Kurt varlığını görselleştir
                    wolf_pixmap = self.images["kurt"]
                    
                    # Kurdun X ve Y pozisyonunu ayarla
                    x = int(wolf.x)
                    
                    # Debug yazdır
                    print(f"Kurt çiziliyor: #{wolf.wolf_id}, pozisyon: ({x}, {wolf.y})")
                    
                    # Int değerlerle çalış
                    wolf_width = int(wolf.width)
                    wolf_height = int(wolf.height)
                    
                    # Eğilme özelliği için kurdun Y pozisyonunu hesapla
                    # Çömelme durumu varsa buna göre ayarla
                    if hasattr(wolf, 'is_crouching') and wolf.is_crouching:
                        crouch_offset = int(wolf.crouch_frame * 1.5)
                        scaled_wolf = wolf_pixmap.scaled(wolf_width, wolf_height - crouch_offset, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        wolf_y = int(self.height() - self.ground_height - (wolf_height - crouch_offset))
                    else:
                        # Sabit Y pozisyonu - zıplama yok
                        scaled_wolf = wolf_pixmap.scaled(wolf_width, wolf_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        wolf_y = int(self.height() - self.ground_height - wolf_height)
                    
                    # Kurt hareket yönüne göre görseli çevir
                    if hasattr(wolf, 'direction_x') and wolf.direction_x > 0:  # Sağa gidiyorsa resmi çevir
                        # Görüntüyü çevir - QTransform kullan
                        transform = QTransform().scale(-1, 1)
                        scaled_wolf = scaled_wolf.transformed(transform)
                    
                    # Eğilme animasyonunu uygula
                    if hasattr(wolf, 'rotation') and wolf.rotation != 0:
                        transform = QTransform()
                        # Dönüşüm merkezini ayarla - tam sayıya dönüştür
                        transform.translate(int(scaled_wolf.width() / 2), int(scaled_wolf.height()))
                        transform.rotate(wolf.rotation)
                        transform.translate(-int(scaled_wolf.width() / 2), -int(scaled_wolf.height()))
                        scaled_wolf = scaled_wolf.transformed(transform)
                    
                    # Kurdu çiz - tüm değerleri int olarak dönüştür
                    draw_x = int(x - scaled_wolf.width() // 2)
                    draw_y = int(wolf_y)
                    painter.drawPixmap(draw_x, draw_y, scaled_wolf)
                    
                    # Kurt durumunu göster
                    if hasattr(wolf, 'state') and wolf.state:
                        painter.setPen(Qt.white)
                        text_width = int(wolf_width * 2)
                        text_x = int(x - text_width // 2)
                        text_y = int(wolf_y - 15)
                        painter.drawText(text_x, text_y, text_width, 15, Qt.AlignCenter, wolf.state)
                    
                    print(f"Kurt başarıyla çizildi: #{wolf.wolf_id}")
                    
                except Exception as e:
                    print(f"HATA: Kurt çizme hatası: {e}")
                    import traceback
                    traceback.print_exc()
            
        except Exception as e:
            print(f"HATA: Kurtları çizme hatası: {e}")
            import traceback
            traceback.print_exc()

    def draw_birds(self, painter):
        """Kuş ve kargaları çiz"""
        try:
            # Game controller kontrolü
            if not hasattr(self, 'game_controller') or not self.game_controller:
                print("UYARI: draw_birds - game_controller bulunamadı")
                return
                
            # Kuşlar listesi kontrolü
            if not hasattr(self.game_controller, 'birds') or not self.game_controller.birds:
                return
                
            print(f"Kuşlar çiziliyor... {len(self.game_controller.birds)} kuş var")
            
            # Ağaç yüksekliği ve zemin seviyesi bilgilerini hesapla
            ground_y = self.height() - self.ground_height
            tree_height = 80  # Varsayılan ağaç yüksekliği
            tree_top_y = ground_y - tree_height  # Ağacın tepesinin y koordinatı
            
            # Kuşların uçabileceği minimum ve maksimum yükseklikler
            min_flight_y = tree_top_y  # Minimum uçuş yüksekliği (ağaç tepesi)
            max_flight_y = tree_top_y - 100  # Maksimum uçuş yüksekliği (ağaç tepesinden 100px yukarı)
                
            # Tüm kuşları çiz
            for bird in self.game_controller.birds:
                try:
                    # Kuş tipine göre resmi seç
                    bird_pixmap = self.images.get(bird.bird_type)
                    
                    if not bird_pixmap:
                        print(f"UYARI: {bird.bird_type} resmi bulunamadı")
                        continue
                    
                    # Kuş boyutları (daha küçük boyutlar)
                    bird_width = int(bird.width * 0.6)  # %60 daha küçük
                    bird_height = int(bird.height * 0.6)  # %60 daha küçük
                    
                    # Kuşun X ve Y pozisyonunu ayarla - tam sayı olarak
                    x = int(bird.x)
                    y = int(bird.y)
                    
                    # Uçuş animasyonu için yükseklik kontrolü
                    if hasattr(bird, 'is_taking_off') and bird.is_taking_off:
                        # Ağaçtan yükselme animasyonu - ağacın konumundan başla
                        source_tree_x = bird.source_tree_x
                        
                        # Animasyon ilerleme kontrolü - kaynak ağaca yakın ise
                        distance_from_source = abs(x - source_tree_x)
                        if distance_from_source < 50:
                            # Kuşun kanat çırpma animasyonunu hızlandır
                            bird.wing_cycle_speed = 12.0
                            
                            # Kuşun uçuş yüksekliğini kademeli olarak artır
                            flight_progress = min(1.0, distance_from_source / 50.0)
                            
                            # Ağacın tepesinden hedef yüksekliğe yükselme (yukarı doğru) - sınırlı yükseklik
                            smooth_progress = flight_progress * flight_progress  # Easing fonksiyonu
                            max_altitude_gain = min(100, tree_top_y - max_flight_y)  # En fazla 100px yükselme
                            
                            # Yukarı doğru yükselme - kısıtlı bir alanda
                            altitude_gain = max_altitude_gain * smooth_progress
                            y = int(tree_top_y - altitude_gain)
                            
                            # Animasyon debug bilgisi
                            print(f"Kuş yükseliyor: #{bird.bird_id}, ilerleme: {smooth_progress:.2f}, ağaç_tepe_y: {tree_top_y}, y: {y}")
                            
                            # Bird nesnesinin y koordinatını güncelle (game_controller'da kullanılabilmesi için)
                            bird.y = y
                    else:
                        # Normal uçuş - kuş.y değerini kullan, ancak yükseklik sınırlarına dikkat et
                        # Kuş çok yükseğe çıkmışsa sınırla
                        if y < max_flight_y:
                            y = max_flight_y
                            bird.y = float(y)
                            
                        # Kuş ağaç seviyesi altındaysa sınırla
                        elif y > min_flight_y:
                            y = min_flight_y
                            bird.y = float(y)
                    
                    # Debug yazdır
                    print(f"Kuş çiziliyor: {bird.bird_type} #{bird.bird_id}, pozisyon: ({x}, {y})")
                    
                    # Kuş resmini ölçeklendir
                    scaled_bird = bird_pixmap.scaled(bird_width, bird_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    
                    # Kuş hareket yönüne göre görseli çevir
                    if bird.direction_x < 0:  # Sola gidiyorsa
                        # Görüntüyü çevir - QTransform kullan
                        mirror_transform = QTransform().scale(-1, 1)
                        scaled_bird = scaled_bird.transformed(mirror_transform)
                    
                    # Kanat çırpma animasyonu (geliştirilmiş)
                    if hasattr(bird, 'wing_angle') and bird.wing_angle != 0:
                        # Yeni yöntem: Kanatları döndürmek yerine kuşun gövdesini hafifçe eğ
                        # Kanat açısına göre uçuş yönü eğimi
                        flight_tilt = bird.wing_angle * 0.2  # Daha az eğim
                        transform = QTransform()
                        transform.rotate(flight_tilt)
                        scaled_bird = scaled_bird.transformed(transform)
                        
                        # Ek olarak, kanat çırpma döngüsü pozisyonuna göre hafif dikey hareket ekle
                        if hasattr(bird, 'wing_cycle_position'):
                            # Sinüs dalgasıyla yumuşak bir yukarı-aşağı hareketi
                            vertical_offset = math.sin(bird.wing_cycle_position * 2 * math.pi) * 2
                            y += int(vertical_offset)
                    
                    # Kuşu çiz - tüm değerleri int olarak dönüştür
                    draw_x = int(x - scaled_bird.width() // 2)
                    draw_y = int(y)
                    painter.drawPixmap(draw_x, draw_y, scaled_bird)
                    
                    # Debug: Kuş durumunu göster (istenirse bu kısım kaldırılabilir)
                    if hasattr(bird, 'state') and bird.state and bird.state != "Uçuyor":
                        # Sadece özel durumlar için etiket göster
                        painter.setPen(Qt.white)
                        text_width = int(bird_width * 2)
                        text_x = int(x - text_width // 2)
                        text_y = int(y - 15)
                        
                        # Yarı-saydam arka plan
                        text_rect = QRect(text_x, text_y, text_width, 15)
                        painter.fillRect(text_rect, QColor(0, 0, 0, 100))
                        
                        # Metni çiz
                        painter.drawText(text_x, text_y, text_width, 15, Qt.AlignCenter, bird.state)
                    
                    print(f"Kuş başarıyla çizildi: {bird.bird_type} #{bird.bird_id}")
                    
                except Exception as e:
                    print(f"HATA: Kuş çizme hatası: {e}")
                    import traceback
                    traceback.print_exc()
            
        except Exception as e:
            print(f"HATA: Kuşları çizme hatası: {e}")
            import traceback
            traceback.print_exc()