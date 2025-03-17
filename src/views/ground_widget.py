from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPixmap, QColor, QTransform
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
            "trees": None,
            "villagers": {
                "Erkek": [],
                "Kadın": []
            }
        }
        
        # Resimleri yükle
        self.load_images()
        
        print(f"GroundWidget oluşturuldu: {self.width()}x{self.height()}")
    
    def load_images(self):
        """Resimleri yükle"""
        try:
            # Resim yolları
            image_paths = {
                "ground": os.path.join("src", "assets", "zemin.png"),
                "castle": os.path.join("src", "assets", "kale.png"),
                "trees": os.path.join("src", "assets", "agac.png"),
                "villagers": {
                    "Erkek": [
                        os.path.join("src", "assets", "villagers", "koylu1.png"),
                        os.path.join("src", "assets", "villagers", "koylu2.png"),
                        os.path.join("src", "assets", "villagers", "koylu3.png"),
                        os.path.join("src", "assets", "villagers", "koylu4.png")
                    ],
                    "Kadın": [
                        os.path.join("src", "assets", "villagers", "kadin_koylu1.png"),
                        os.path.join("src", "assets", "villagers", "kadin_koylu2.png"),
                        os.path.join("src", "assets", "villagers", "kadin_koylu3.png"),
                        os.path.join("src", "assets", "villagers", "kadin_koylu4.png")
                    ]
                }
            }
            
            # Zemin resmi
            if os.path.exists(image_paths["ground"]):
                self.images["ground"] = QPixmap(image_paths["ground"])
                # Zemin resminin boyutunu kontrol et
                if self.images["ground"].height() != self.ground_height:
                    # Zemin resmini doğru boyuta ölçeklendir
                    self.images["ground"] = self.images["ground"].scaled(
                        self.images["ground"].width(),
                        self.ground_height,
                        Qt.IgnoreAspectRatio,
                        Qt.SmoothTransformation
                    )
                print(f"Zemin resmi yüklendi: {image_paths['ground']}, boyut: {self.images['ground'].width()}x{self.images['ground'].height()}")
            else:
                print(f"HATA: Zemin resmi bulunamadı: {image_paths['ground']}")
            
            # Kale resmi
            if os.path.exists(image_paths["castle"]):
                self.images["castle"] = QPixmap(image_paths["castle"])
                print(f"Kale resmi yüklendi: {image_paths['castle']}")
            else:
                print(f"HATA: Kale resmi bulunamadı: {image_paths['castle']}")
            
            # Ağaç resmi
            if os.path.exists(image_paths["trees"]):
                self.images["trees"] = QPixmap(image_paths["trees"])
                print(f"Ağaç resmi yüklendi: {image_paths['trees']}")
            else:
                print(f"HATA: Ağaç resmi bulunamadı: {image_paths['trees']}")
            
            # Köylü resimleri - animasyon kareleri
            for gender in ["Erkek", "Kadın"]:
                self.images["villagers"][gender] = []
                for i, path in enumerate(image_paths["villagers"][gender]):
                    if os.path.exists(path):
                        self.images["villagers"][gender].append(QPixmap(path))
                        print(f"{gender} köylü resmi {i+1} yüklendi: {path}")
                    else:
                        print(f"HATA: {gender} köylü resmi {i+1} bulunamadı: {path}")
                
                # Eğer hiç resim yüklenemezse, boş bir pixmap ekle
                if not self.images["villagers"][gender]:
                    self.images["villagers"][gender].append(QPixmap(60, 60))
                    print(f"UYARI: {gender} için hiç köylü resmi yüklenemedi, boş resim kullanılıyor")
                
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
        """Widget'ı çiz"""
        try:
            # Çizim zaten devam ediyorsa çıkış yap
            if self.is_drawing:
                print("UYARI: Çizim zaten devam ediyor")
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
            x = 100
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
            if not self.images["trees"]:
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
                y = ground_y - tree_height + 40  # +40 ile ağacı yukarı kaldırıyoruz
                
                # Ağaç resmini ölçeklendir
                scaled_img = self.images["trees"].scaled(tree_width, tree_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # Ağacı çiz
                painter.drawPixmap(x - tree_width // 2, y, scaled_img)
                
        except Exception as e:
            print(f"HATA: Ağaç çizme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_villagers(self, painter):
        """Köylüleri çiz"""
        try:
            # Köylü listesi yok veya boşsa çıkış yap
            if not hasattr(self.game_controller, 'villagers') or not self.game_controller.villagers:
                return
                
            # Köylü resimleri yüklü değilse çıkış yap
            if not self.images["villagers"]["Erkek"] or not self.images["villagers"]["Kadın"]:
                return
            
            # Zemin seviyesini hesapla
            ground_y = self.height() - self.ground_height
            
            # Köylüleri çiz
            for villager in self.game_controller.villagers:
                # Köylü pozisyonunu hesapla
                x = int(villager.x)
                villager_width = 40
                villager_height = 40
                y = ground_y - villager_height
                
                # Cinsiyete göre resmi seç
                if villager.gender == "Erkek":
                    appearance_index = min(villager.appearance, len(self.images["villagers"]["Erkek"]) - 1)
                    img = self.images["villagers"]["Erkek"][appearance_index]
                else:
                    appearance_index = min(villager.appearance, len(self.images["villagers"]["Kadın"]) - 1)
                    img = self.images["villagers"]["Kadın"][appearance_index]
                
                # Köylü resmini ölçeklendir
                scaled_img = img.scaled(villager_width, villager_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # Eğilme animasyonunu uygula
                transform = QTransform()
                transform.rotate(villager.rotation)
                scaled_img = scaled_img.transformed(transform)
                
                # Köylünün hareket yönüne göre resmi çevir
                if villager.direction < 0:
                    transform = QTransform().scale(-1, 1)
                    scaled_img = scaled_img.transformed(transform)
                
                # Köylüyü çiz
                painter.drawPixmap(x - villager_width // 2, y, scaled_img)
                
        except Exception as e:
            print(f"HATA: Köylü çizme hatası: {e}")
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