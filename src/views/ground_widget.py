from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QPixmap, QColor, QTransform, QFont, QPen, QBrush
from ..models.villager import Villager, TestVillager
import random
import os

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
        self.ground_height = 25
        
        # Çizim yapıldı mı?
        self.is_drawing = False
        
        # Resimleri saklamak için sözlük
        self.images = {
            "ground": None,
            "castle": None,
            "tree": None,
            "villager": {},
            "house": {}
        }
        
        # Resimleri yükle
        self.load_images()
        
        print(f"GroundWidget oluşturuldu: {self.width()}x{self.height()}")
    
    def load_images(self):
        """Resimleri yükle"""
        try:
            # Resim sözlüğü
            self.images = {
                "ground": None,
                "castle": None,
                "tree": None,
                "villager": {},
                "house": {}
            }
            
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
            
            # Ağaç resmini yükle
            tree_path = os.path.join("src", "assets", "agac.png")
            if os.path.exists(tree_path):
                self.images["tree"] = QPixmap(tree_path)
                print(f"Ağaç resmi yüklendi: {tree_path}")
            else:
                print(f"HATA: Ağaç resmi bulunamadı: {tree_path}")
            
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
            # Çizim zaten yapılıyorsa çıkış yap
            if self.is_drawing:
                return
                
            # Çizim başladı
            self.is_drawing = True
            
            # Painter oluştur
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            # Arka planı transparan yap
            painter.fillRect(self.rect(), Qt.transparent)
            
            # Zemini çiz
            self.draw_ground(painter)
            
            # Kaleyi çiz
            self.draw_castle(painter)
            
            # Evleri çiz
            self.draw_houses(painter)
            
            # İnşaat alanlarını çiz
            self.draw_building_sites(painter)
            
            # Ağaçları çiz
            self.draw_trees(painter)
            
            # Köylüleri çiz
            self.draw_villagers(painter)
            
            # Painter'ı kapat
            painter.end()
            
            # Çizim bitti
            self.is_drawing = False
            
        except Exception as e:
            # Çizim bitti (hata durumunda da)
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
            ground_y = self.height() - new_height
            
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
    
    def draw_trees(self, painter):
        """Ağaçları çiz"""
        try:
            if not self.images["tree"]:
                return
                
            ground_y = self.height() - self.ground_height
            
            for tree in self.game_controller.trees:
                # Sadece görünür ağaçları çiz
                if not tree.is_visible:
                    continue
                    
                x = int(tree.x)
                tree_width = 80
                tree_height = 120
                
                # Ağacın y pozisyonunu köylülerle aynı hizaya getir
                # Köylü yüksekliği 40 piksel, ağaç yüksekliği 80 piksel
                # Ağacın alt kısmı zemin seviyesinde olsun
                y = ground_y - tree_height + 43  # +40 ile ağacı yukarı kaldırıyoruz
                
                # Ağaç resmini ölçeklendir
                scaled_img = self.images["tree"].scaled(tree_width, tree_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # Ağacı çiz
                painter.drawPixmap(x - tree_width // 2, y, scaled_img)
                
        except Exception as e:
            print(f"HATA: Ağaç çizme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_villagers(self, painter):
        """Köylüleri çiz"""
        try:
            # Oyun kontrolcüsü yoksa çıkış yap
            if not self.game_controller:
                return
                
            # Köylüler yoksa çıkış yap
            if not hasattr(self.game_controller, 'villagers') or not self.game_controller.villagers:
                return
                
            # Köylü resimleri yüklü değilse çıkış yap
            if not self.images["villager"]:
                return
            
            # Zemin seviyesini hesapla
            ground_y = self.height() - self.ground_height
            
            # Tüm köylüleri çiz
            for villager in self.game_controller.villagers:
                # Köylü aktif değilse çizme (hasattr ile kontrol et)
                if hasattr(villager, 'is_active') and not villager.is_active:
                    continue
                    
                # Köylü konumunu hesapla
                x = int(villager.x - villager.width / 2)
                y = int(ground_y - villager.height)  # Zemin üzerinde
                
                # Köylü resmini seç
                img = None
                if villager.gender == "Erkek":
                    img_key = f"koylu{villager.appearance}"
                    if img_key in self.images["villager"]:
                        img = self.images["villager"][img_key]
                else:
                    img_key = f"kadin_koylu{villager.appearance}"
                    if img_key in self.images["villager"]:
                        img = self.images["villager"][img_key]
                
                # Eğer resim bulunamadıysa varsayılan resmi kullan
                if not img:
                    default_key = "koylu1" if villager.gender == "Erkek" else "kadin_koylu1"
                    if default_key in self.images["villager"]:
                        img = self.images["villager"][default_key]
                    else:
                        # Hiç resim yoksa çizme
                        continue
                
                # Köylü resmini ölçeklendir
                scaled_img = img.scaled(villager.width, villager.height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
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
                
                # Yazı alanı genişliği (köylü genişliğinin 2 katı)
                text_width = villager.width * 2
                text_x = x - (text_width - villager.width) // 2  # Merkezle
                
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
                
                # Köylü taşıdığı kaynakları çiz
                if hasattr(villager, 'carrying') and villager.carrying:
                    resource_text = f"{villager.carrying['type']}: {villager.carrying['amount']}"
                    painter.setPen(Qt.cyan)
                    painter.drawText(
                        text_x, y + villager.height + 5, text_width, 15,
                        Qt.AlignCenter, resource_text
                    )
                
                # Köylünün parasını göster
                if hasattr(villager, 'money'):
                    money_text = f"{villager.money} altın"
                    painter.setPen(Qt.green)
                    painter.drawText(
                        text_x, y + villager.height + 20, text_width, 15,
                        Qt.AlignCenter, money_text
                    )
                
                # Ev sahibi olma durumunu göster
                if hasattr(villager, 'has_house') and villager.has_house:
                    house_text = "Ev Sahibi"
                    painter.setPen(QColor(255, 165, 0))  # Turuncu
                    painter.drawText(
                        text_x, y + villager.height + 35, text_width, 15,
                        Qt.AlignCenter, house_text
                    )
                
        except Exception as e:
            print(f"HATA: Köylü çizim hatası: {e}")
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