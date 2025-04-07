from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPixmap, QColor, QTransform, QFont, QPen, QBrush, QPainterPath, QLinearGradient
from ..models.villager import Villager
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
        self.ground_height = 3
        
        # Çizim yapıldı mı?
        self.is_drawing = False
        
        # Resimlerin yüklenip yüklenmediğini takip et
        self.images_loaded = False
        
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
            "pazar3": None,   # Pazar3 resmi
            "pazar4": None,   # Pazar4 resmi
            "kilise": None,  # Kilise resmi
            "gardiyan": None,  # Gardiyan resmi
            "degirmen": None,  # Değirmen resmi
            "kuyu": None,  # Kuyu resmi
            "kurt": None,  # Kurt resmi
            "kus": None,  # Kuş resmi
            "karga": None,  # Karga resmi
            "han": None,  # Han resmi
            "duvar": None,  # Duvar resmi
            "fener": None,   # Fener resmi
            "ahir": None,    # Ahır resmi
            "balya": None,    # Balya resmi
            "cit": None,    # Çit resmi
            "araba": None,    # Araba resmi
            "torch": None,     # Meşale resmi
            "fici": None      # Fıçı resmi
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
                "pazar3": None,   # Pazar3 resmi
                "pazar4": None,   # Pazar4 resmi
                "kilise": None,  # Kilise resmi
                "gardiyan": None,  # Gardiyan resmi
                "degirmen": None,  # Değirmen resmi
                "kuyu": None,  # Kuyu resmi
                "kurt": None,  # Kurt resmi
                "kus": None,  # Kuş resmi
                "karga": None,  # Karga resmi
                "han": None,  # Han resmi
                "duvar": None,  # Duvar resmi
                "fener": None,   # Fener resmi
                "ahir": None,    # Ahır resmi
                "balya": None,    # Balya resmi
                "cit": None,    # Çit resmi
                "araba": None,    # Araba resmi
                "torch": None,     # Meşale resmi
                "fici": None      # Fıçı resmi
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
            
            # Pazar resimlerini yükle (tüm pazar assetleri için)
            pazar_types = ["Pazar1", "Pazar2", "pazar3", "pazar4"]
            for i, pazar_type in enumerate(pazar_types, 1):
                pazar_path = os.path.join("src", "assets", f"{pazar_type}.png")
                if os.path.exists(pazar_path):
                    self.images[f"pazar{i}"] = QPixmap(pazar_path)
                    print(f"{pazar_type} resmi yüklendi: {pazar_path}")
            else:
                    print(f"UYARI: {pazar_type} resmi bulunamadı: {pazar_path}")
            
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
                
            # Han resmini yükle
            han_path = os.path.join("src", "assets", "Han.png")
            if os.path.exists(han_path):
                self.images["han"] = QPixmap(han_path)
                print(f"Han resmi yüklendi: {han_path}")
            else:
                print(f"UYARI: Han resmi bulunamadı: {han_path}")
            
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
            
            # Duvar resmini yükle
            duvar_path = os.path.join("src", "assets", "duvar.png")
            if os.path.exists(duvar_path):
                self.images["duvar"] = QPixmap(duvar_path)
                print(f"Duvar resmi yüklendi: {duvar_path}")
            else:
                print(f"UYARI: Duvar resmi bulunamadı: {duvar_path}")
            
            # Fener resmini yükle
            fener_path = os.path.join("src", "assets", "fener.png")
            if os.path.exists(fener_path):
                self.images["fener"] = QPixmap(fener_path)
                print(f"Fener resmi yüklendi: {fener_path}")
            else:
                print(f"UYARI: Fener resmi bulunamadı: {fener_path}")
            
            # Ahır resmini yükle
            ahir_path = os.path.join("src", "assets", "ahır.png")
            if os.path.exists(ahir_path):
                self.images["ahir"] = QPixmap(ahir_path)
                print(f"Ahır resmi yüklendi: {ahir_path}")
            else:
                print(f"UYARI: Ahır resmi bulunamadı: {ahir_path}")
            
            # Balya resmini yükle
            balya_path = os.path.join("src", "assets", "balya.png")
            if os.path.exists(balya_path):
                self.images["balya"] = QPixmap(balya_path)
                print(f"Balya resmi yüklendi: {balya_path}")
            else:
                print(f"UYARI: Balya resmi bulunamadı: {balya_path}")
            
            # Çit resmini yükle
            cit_path = os.path.join("src", "assets", "cit.png")
            if os.path.exists(cit_path):
                self.images["cit"] = QPixmap(cit_path)
                print(f"Çit resmi yüklendi: {cit_path}")
            else:
                print(f"UYARI: Çit resmi bulunamadı: {cit_path}")
            
            # Araba resmini yükle
            araba_path = os.path.join("src", "assets", "araba.png")
            if os.path.exists(araba_path):
                self.images["araba"] = QPixmap(araba_path)
                print(f"Araba resmi yüklendi: {araba_path}")
            else:
                print(f"UYARI: Araba resmi bulunamadı: {araba_path}")
            
            # Meşale resmini yükle
            torch_path = os.path.join("src", "assets", "torch.png")
            if os.path.exists(torch_path):
                self.images["torch"] = QPixmap(torch_path)
                print(f"Meşale resmi yüklendi: {torch_path}")
            else:
                print(f"UYARI: Meşale resmi bulunamadı: {torch_path}")
            
            # Fıçı resmini yükle
            fici_path = os.path.join("src", "assets", "fici.png")
            if os.path.exists(fici_path):
                self.images["fici"] = QPixmap(fici_path)
                print(f"Fıçı resmi yüklendi: {fici_path}")
            else:
                print(f"UYARI: Fıçı resmi bulunamadı: {fici_path}")
            
            print("Resimler yüklendi")
            # Resimlerin yüklendiğini işaretle
            self.images_loaded = True
            
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
        if self.is_drawing:
            return
            
        self.is_drawing = True
        
        try:
            if not self.images_loaded:
                self.load_images()
                
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Arkaplanı çizme - transparan olması için
            # Önceki mavi gökyüzü çizimi kaldırıldı
            
            # Duvarı çiz - en altta olsun (zeminin altında)
            self.draw_wall(painter)
            
            # Zemin çiz
            self.draw_ground(painter)
            
            # Kuşları çiz
            if self.game_controller and hasattr(self.game_controller, 'birds'):
                self.draw_birds(painter)
            
            # Ağaçları çiz - yapılardan ÖNCE çizerek yapıların önde olmasını sağlıyoruz
            if self.game_controller and hasattr(self.game_controller, 'trees'):
                self.draw_trees(painter)
            
            # Mağarayı çiz
            if self.game_controller and hasattr(self.game_controller, 'cave'):
                self.draw_cave(painter)
            
            # Kurtları çiz
            if self.game_controller and hasattr(self.game_controller, 'wolves'):
                self.draw_wolves(painter)
            
            # Çiti çiz - ahır ile balya arasına
            if self.images["cit"]:
                self.draw_fence(painter)
            
            # ---- Yapıları çiz (hepsi ağaçlardan sonra) ----
            
            # Kaleyi çiz
            if self.game_controller and hasattr(self.game_controller, 'castle'):
                self.draw_castle(painter)
            
            # Kiliseyi çiz
            if self.images["kilise"]:
                self.draw_church(painter)
            
            # Ahırı çiz
            if self.images["ahir"]:
                self.draw_stable(painter)
            
            # Balyayı çiz
            if self.images["balya"]:
                self.draw_hay_bale(painter)
            
            # Arabayı çiz
            if self.images["araba"]:
                self.draw_cart(painter)
            
            # Fıçıyı çiz - Han'ın arkasında
            if self.images["fici"]:
                self.draw_barrel(painter)
            
            # Pazarı çiz
            if self.game_controller and hasattr(self.game_controller, 'market'):
                self.draw_markets(painter)
                
            # Hanı çiz
            if self.images["han"]:
                self.draw_inn(painter)
            
            # Gardiyanı çiz
            if self.images["gardiyan"]:
                self.draw_guard(painter)
            
            # Meşaleyi çiz
            if self.images["torch"]:
                self.draw_torch(painter)
            
            # Değirmeni çiz
            if self.images["degirmen"]:
                self.draw_mill(painter)
                
            # Kuyuyu çiz
            if self.images["kuyu"]:
                self.draw_well(painter)
            
            # Fenerleri çiz
            if self.images["fener"]:
                self.draw_lanterns(painter)
            
            # İnşaat alanlarını çiz
            if self.game_controller and hasattr(self.game_controller, 'building_sites'):
                self.draw_building_sites(painter)
            
            # Evleri çiz
            if self.game_controller and hasattr(self.game_controller, 'houses'):
                self.draw_houses(painter)
            
            # ---- En son köylüleri çiz (her şeyin üzerinde) ----
            
            # Köylüleri çiz
            if self.game_controller and hasattr(self.game_controller, 'villagers'):
                self.draw_villagers(painter)
            
            painter.end()
            
        except Exception as e:
            print(f"HATA: Çizim hatası: {e}")
            import traceback
            traceback.print_exc()
        
        self.is_drawing = False
    
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
            ground_y = self.height() - new_height + 19
            
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
            castle_width = 190
            castle_height = 190
            scaled_castle = self.images["castle"].scaled(castle_width, castle_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Kaleyi x ekseni boyunca aynala
            transform = QTransform().scale(-1, 1)  # X ekseninde aynala
            scaled_castle = scaled_castle.transformed(transform)
            
            # Kale pozisyonu - sol tarafta, zemin üzerinde
            x = 1
            # Zemin seviyesini hesapla
            ground_y = self.height() - self.ground_height
            # Kaleyi zemin üzerine yerleştir
            y = ground_y - scaled_castle.height()   # Biraz gömülü olsun
            
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
            church_width = 90
            church_height = 90
            
            # Kilise resmini ölçeklendir
            scaled_church = self.images["kilise"].scaled(church_width, church_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Kalenin konumundan 300 piksel sağda
            church_x = 520  # Kale 10 pikselde başlıyor
            
            # Y pozisyonunu hesapla (zemin üzerinde)
            church_y = self.height() - self.ground_height - church_height + 10
            
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
                tree_y = self.height() - self.ground_height - tree.height  # +2'den +15'e değiştirildi
                
                # Ağacı çiz
                painter.drawPixmap(tree_x, tree_y, tree.width, tree.height, tree_img)
                
                # Eğer ağaç kesiliyor ise ilerleme çubuğu göster
                if hasattr(tree, 'is_being_cut') and tree.is_being_cut and hasattr(tree, 'cut_progress'):
                    progress = tree.cut_progress
                    
                    # İlerleme çubuğu boyutları
                    bar_width = int(tree.width * 0.8)
                    bar_height = 10
                    bar_x = tree_x + int(tree.width * 0.1)  # Ağacın merkezine hizala
                    bar_y = tree_y - 15  # Ağacın üstünde
                    
                    # Arkaplan
                    painter.fillRect(bar_x, bar_y, bar_width, bar_height, QColor(0, 0, 0, 128))
                    
                    # İlerleme
                    progress_width = int(bar_width * progress / 100)
                    painter.fillRect(bar_x, bar_y, progress_width, bar_height, QColor(255, 0, 0, 200))
                    
                    # İlerleme yüzdesi
                    painter.setPen(Qt.white)
                    painter.setFont(QFont("Arial", 8))
                    painter.drawText(
                        bar_x, bar_y, bar_width, bar_height,
                        Qt.AlignCenter, f"%{progress}"
                    )
                
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
                y = int(house.y - house.height - 8)
                
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
        """Pazar alanlarını çiz - Dört farklı pazar tezgahı ile kuyu ortada olacak şekilde"""
        try:
            # Han'ın konumunu referans olarak al
            # Han'ın draw_inn metodundaki varsayılan konumu
            han_x = 200  
            han_width = 90  # Han genişliği
            
            # Pazar tezgahları için boyutlar
            market_width = 30
            market_height = 30
            
            # Han'ın sağından başlayarak pazar tezgahlarının pozisyonlarını hesapla
            # Han'ın 50 piksel sağına pazar1
            market1_x = han_x + han_width + 45
            
            # Pazar1'in 5 piksel sağına pazar2
            market2_x = market1_x + market_width + 5
            
            # Kuyu'nun pozisyonu (draw_well metodunda kullanılacak)
            # Pazar2'nin 10 piksel sağına kuyu
            kuyu_x = market2_x + market_width + 10
            # Kuyu boyutları
            kuyu_width = 25
            
            # Kuyu'nun 10 piksel sağına pazar3
            market3_x = kuyu_x + kuyu_width + 10
            
            # Pazar3'ün 5 piksel sağına pazar4
            market4_x = market3_x + market_width + 5
            
            # Pazar tezgahlarının Y pozisyonu (hepsi aynı hizada)
            # Tüm tezgahların kesinlikle aynı yükseklikte olması için sabit y değeri
            market_y = self.height() - self.ground_height - market_height + 5
            
            # Kuyu'nun X pozisyonunu global olarak sakla (draw_well metodunda kullanılacak)
            self.kuyu_x = kuyu_x
            
            # Pazar tezgahlarını çiz - her biri için farklı görsel kullanarak
            market_positions = [market1_x, market2_x, market3_x, market4_x]
            market_images = ["pazar1", "pazar2", "pazar3", "pazar4"]
            
            for i, market_x in enumerate(market_positions):
                # Doğru pazarı seç
                pazar_img = self.images[market_images[i]]
                if not pazar_img:
                    print(f"UYARI: {market_images[i]} resmi yüklenmemiş")
                    continue
                
                # Tezgah resmini ölçeklendir
                scaled_market = pazar_img.scaled(market_width, market_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # Tüm pazarlar için kesinlikle aynı y değerini kullan
                # Tezgahı çiz - scaled_market'in boyutlarını dikkate alarak
                painter.drawPixmap(int(market_x), int(market_y), scaled_market)
                
                # Game controller'a tezgah pozisyonunu bildir (eğer market ve stalls varsa)
                if self.game_controller and hasattr(self.game_controller, 'market') and self.game_controller.market:
                    market = self.game_controller.market
                    if hasattr(market, 'stalls') and i < len(market.stalls):
                        market.stalls[i].x = market_x + market_width/2
                        market.stalls[i].y = market_y + market_height
                
                print(f"Pazar tezgahı #{i+1} ({market_images[i]}) çizildi: Konum=({int(market_x)}, {int(market_y)})")
            
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
            guard_width = 130
            guard_height = 130
            
            # Gardiyan resmini ölçeklendir
            scaled_guard = self.images["gardiyan"].scaled(guard_width, guard_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Kalenin sağında, kilise ve pazarın sonrasında olsun
            # Kilise 310'da, pazar yaklaşık 400, tezgahlar 660'a kadar
            guard_x = 870  # Kilise ve pazardan sonra
            
            # Y pozisyonunu kilise ile aynı seviyede hesapla (kilise Y=955'te çiziliyor)
            guard_y = self.height() - self.ground_height - guard_height + 20
            
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
            
            # Gardiyan kulesinin konumu
             # draw_guard metodundan alındı
            
            # Değirmeni gardiyanın 40 piksel soluna yerleştir
            mill_x = 1050
            
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
        """Kuyuyu çiz - Pazar tezgahları arasına yerleştirilmiş olarak"""
        try:
            if not self.images["kuyu"]:
                print("UYARI: Kuyu resmi yüklenmemiş")
                return
            
            # Kuyu boyutlarını ayarla
            well_width = 25
            well_height = 25
            
            # Kuyu resmini ölçeklendir
            scaled_well = self.images["kuyu"].scaled(well_width, well_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Kuyu pozisyonu
            # draw_markets metodunda hesaplanan kuyu_x değerini kullan
            if hasattr(self, 'kuyu_x'):
                well_x = self.kuyu_x
            else:
                # Varsayılan konum (kuyu_x yoksa)
                well_x = 370
            
            # Y pozisyonunu hesapla (pazar tezgahlarıyla aynı seviyede)
            well_y = self.height() - self.ground_height - well_height + 3
            
            # Kuyuyu çiz
            painter.drawPixmap(int(well_x), int(well_y), scaled_well)
            
            print(f"Kuyu çizildi: Konum=({int(well_x)}, {int(well_y)}), Boyut={well_width}x{well_height}")
            
        except Exception as e:
            print(f"HATA: Kuyu çizme hatası: {e}")
            import traceback
            traceback.print_exc()

    def draw_wolves(self, painter):
        """Kurtları çiz"""
        try:
            # Game controller kontrolü
            if not hasattr(self, 'game_controller') or not self.game_controller:
                print("Game controller bulunamadı, kurtlar çizilemedi")
                return
                
            # Kurt resmi kontrolü
            if not self.images.get("kurt"):
                print("UYARI: Kurt resmi yüklenemedi!")
                return
                
            # Kurtlar listesi kontrolü
            if not hasattr(self.game_controller, 'wolves') or not self.game_controller.wolves:
                print("Kurtlar listesi boş veya bulunamadı")
                return
            
            # Zemin seviyesini hesapla
            ground_y = self.height() - self.ground_height
            
            # Tüm kurtları çiz
            for wolf in self.game_controller.wolves:
                try:
                    # Kurt boyutlarını ayarla
                    wolf_width = int(getattr(wolf, 'width', 40))
                    wolf_height = int(getattr(wolf, 'height', 30))
                    
                    # Resmi ölçeklendir
                    scaled_wolf = self.images["kurt"].scaled(wolf_width, wolf_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    
                    # Kurdun yönünü kontrol et (direction_x kullan, yoksa direction)
                    direction = getattr(wolf, 'direction_x', getattr(wolf, 'direction', 1))
                    
                    # Transformasyon matrisi oluştur
                    transform = QTransform()
                    
                    # Yön kontrolü - direction değeri 1 ise sağa, -1 ise sola bakacak
                    # NOT: Kurt resminin varsayılan yönünü kontrol edip, doğru transformasyonu uygula
                    # Resim varsayılan olarak sola bakıyorsa, sağa hareket için çevir
                    if direction > 0:  # Sağa gidiyorsa ve resim sola bakıyorsa çevir
                        transform.scale(-1, 1)
                    
                    # Rotasyonu uygula - animation_frame kullan
                    rotation = 0
                    if hasattr(wolf, 'animation_frame'):
                        # Animasyon karesine göre rotasyon açısını belirle
                        if wolf.animation_frame == 1:
                            rotation = -5  # Sola eğilme
                        elif wolf.animation_frame == 3:
                            rotation = 5   # Sağa eğilme
                    
                    if rotation != 0:
                        transform.rotate(rotation)
                    
                    # Resmi dönüştür
                    transformed_wolf = scaled_wolf.transformed(transform)
                    
                    # Kurdu çiz - zemin üzerinde
                    x = int(wolf.x - wolf_width/2)
                    y = int(ground_y - wolf_height)  # Zemin üzerinde
                    painter.drawPixmap(x, y, transformed_wolf)
                    
                    # Yön bilgisini göster (Debug)
                    if hasattr(wolf, 'direction') and hasattr(wolf, 'direction_x'):
                        yontext = f"D:{wolf.direction} DX:{wolf.direction_x}"
                        painter.setPen(Qt.red)
                        painter.setFont(QFont("Arial", 7))
                        painter.drawText(x, y - 10, yontext)
                    
                except Exception as e:
                    print(f"HATA: Kurt çizim hatası: {e}")
                    import traceback
                    traceback.print_exc()
                
        except Exception as e:
            print(f"HATA: Kurtları çizerken hata: {e}")
            import traceback
            traceback.print_exc()

    def draw_birds(self, painter):
        """Kuşları çiz"""
        try:
            # Game controller kontrolü
            if not hasattr(self, 'game_controller') or not self.game_controller:
                return
                
            # Kuşlar listesi kontrolü
            if not hasattr(self.game_controller, 'birds') or not self.game_controller.birds:
                return
            
            # Kuşları ve kargaları çiz
            for bird in self.game_controller.birds:
                # Bird type kontrolü
                bird_type = getattr(bird, 'bird_type', "kuş")  # Varsayılan olarak "kuş"
                
                # Doğru resmi seç
                if bird_type == "karga":
                    img = self.images.get("karga")
                else:  # "kuş" varsayılan
                    img = self.images.get("kus")
                
                if not img:
                    continue
                
                # Kuş boyutlarını ayarla
                bird_width = int(getattr(bird, 'width', 30))
                bird_height = int(getattr(bird, 'height', 20))
                
                # Resmi ölçeklendir
                scaled_img = img.scaled(bird_width, bird_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # Kuşun yönünü kontrol et ve gerekirse resmi çevir
                direction = getattr(bird, 'direction', 1)  # Varsayılan olarak sağa doğru
                
                if direction == -1:  # Sola doğru uçuyorsa
                    transform = QTransform().scale(-1, 1)  # X ekseninde çevir
                    scaled_img = scaled_img.transformed(transform)
                
                # Kuşu çiz
                x = int(bird.x - bird_width/2)
                y = int(bird.y - bird_height/2)
                painter.drawPixmap(x, y, scaled_img)
                
                # Debug bilgisi yazdır
                # print(f"{bird_type.capitalize()} #{bird.bird_id} çizildi: ({x}, {y})")
            
        except Exception as e:
            print(f"HATA: Kuşları çizerken hata: {e}")
            import traceback
            traceback.print_exc()

    def draw_inn(self, painter):
        """Hanı çiz"""
        try:
            if not self.images["han"]:
                print("UYARI: Han resmi yüklenmemiş")
                return
            
            # Han boyutlarını ayarla
            inn_width = 90
            inn_height = 90
            
            # Han resmini ölçeklendir
            scaled_inn = self.images["han"].scaled(inn_width, inn_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Pazarın son tezgahının konumunu hesapla (pazarın 10 piksel sağına yerleştirmek için)
 
            inn_x = 200
            
            # Y pozisyonunu hesapla (zemin üzerinde, diğer yapılarla aynı)
            inn_y = self.height() - self.ground_height - inn_height + 20
            
            # Koordinatları int'e dönüştür, drawPixmap int değer bekliyor
            inn_x_int = int(inn_x)
            inn_y_int = int(inn_y)
            
            # Hanı çiz
            painter.drawPixmap(inn_x_int, inn_y_int, scaled_inn)
            
            print(f"Han çizildi: Konum=({inn_x_int}, {inn_y_int}), Boyut={inn_width}x{inn_height}")
            
        except Exception as e:
            print(f"HATA: Han çizme hatası: {e}")
            import traceback
            traceback.print_exc()

    def draw_wall(self, painter):
        """Duvarı çiz - zeminin üstünde, yatay olarak (parçaları üst üste bindirerek)"""
        try:
            # Duvar resmi yüklü değilse çıkış yap
            if self.images["duvar"] is None:
                print("UYARI: Duvar resmi yüklenemediği için çizilemedi")
                return
            
            # Duvar resmi boyutlarını ayarla
            duvar_width = 25  # Zemin ile aynı genişlik
            duvar_height = 40  # Duvar yüksekliği
            
            # Duvar resmini ölçeklendir
            scaled_duvar = self.images["duvar"].scaled(duvar_width, duvar_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            
            # Duvarın başlangıç ve bitiş noktalarını belirle
            start_x = 0  # En soldan başla
            end_x = 900  # Gardiyan kulesine kadar
            
            # Duvarın y pozisyonu - zemin üzerinde, köylülerin yürüdüğü seviyede
            wall_y = self.height() - self.ground_height - duvar_height + 4
            
            # Duvar parçalarını önemli derecede üst üste bindirerek çiz
            # Her parçayı bir öncekiyle %50 üst üste binerek yerleştir
            overlap = int(duvar_width * 0.5)  # %50 üst üste binme
            step = duvar_width - overlap
            
            # x pozisyonlarını hesapla
            positions = []
            current_x = start_x
            while current_x < end_x:
                positions.append(current_x)
                current_x += step
            
            # Her pozisyona duvar parçasını çiz
            for x in positions:
                painter.drawPixmap(int(x), int(wall_y), scaled_duvar)
            
            print(f"Duvar çizildi: {len(positions)} adet parça, %{int(overlap/duvar_width*100)} üst üste bindirme oranı")
            
        except Exception as e:
            print(f"HATA: Duvar çizme hatası: {e}")
            import traceback
            traceback.print_exc()

    def draw_lanterns(self, painter):
        """Fenerleri belirtilen konumlara çiz"""
        try:
            if not self.images["fener"]:
                print("UYARI: Fener resmi yüklenmemiş")
                return
            
            # Fener boyutunu ayarla
            fener_width = 15
            fener_height = 20
            
            # Fener resmini ölçeklendir
            scaled_fener = self.images["fener"].scaled(fener_width, fener_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Aynalanan fener için QTransform kullan
            transform = QTransform().scale(-1, 1)  # X ekseninde aynala
            mirrored_fener = scaled_fener.transformed(transform)
            
            # Zemin seviyesini hesapla
            ground_y = self.height() - self.ground_height
            
            # Fenerin y pozisyonu (zemin üstünde)
            fener_y = ground_y - fener_height + 1
            
            # 1. Fener: Kalenin 6 piksel sağı
            # Kale x pozisyonu + kale genişliği + 6
            kale_x = 1  # draw_castle metodundan
            kale_width = 190  # draw_castle metodundan
            fener1_x = kale_x + kale_width + 6
            painter.drawPixmap(int(fener1_x), int(fener_y), scaled_fener)
            print(f"Fener 1 çizildi: Konum=({int(fener1_x)}, {int(fener_y)})")
            
            # 2. Fener: Hanın 15 piksel sağı (AYNALANIYOR)
            han_x = 200  # draw_inn metodundan
            han_width = 90  # draw_inn metodundan
            fener2_x = han_x + han_width + 15
            painter.drawPixmap(int(fener2_x), int(fener_y), mirrored_fener)  # Aynalanan fener kullanılıyor
            print(f"Fener 2 çizildi (aynalı): Konum=({int(fener2_x)}, {int(fener_y)})")
            
            # 3. Fener: pazar4'ün 6 piksel sağı
            # market_positions ve market_width değerlerini draw_markets metodundan alıyoruz
            # pazar4 en sağdaki tezgah (market4_x)
            market4_x = self.kuyu_x + 25 + 10 + 30 + 5  # draw_markets metodundan hesapla
            market_width = 30  # draw_markets metodundan
            fener3_x = market4_x + market_width + 6
            painter.drawPixmap(int(fener3_x), int(fener_y), scaled_fener)
            print(f"Fener 3 çizildi: Konum=({int(fener3_x)}, {int(fener_y)})")
            
            # 4. Fener: Kilisenin 6 piksel sağı (AYNALANIYOR)
            church_x = 520  # draw_church metodundan
            church_width = 85  # draw_church metodundan
            fener4_x = church_x + church_width + 6
            painter.drawPixmap(int(fener4_x), int(fener_y), mirrored_fener)  # Aynalanan fener kullanılıyor
            print(f"Fener 4 çizildi (aynalı): Konum=({int(fener4_x)}, {int(fener_y)})")
            
        except Exception as e:
            print(f"HATA: Fener çizme hatası: {e}")
            import traceback
            traceback.print_exc()

    def draw_stable(self, painter):
        """Ahırı çiz - Kilisenin 50 piksel sağında"""
        try:
            if not self.images["ahir"]:
                print("UYARI: Ahır resmi yüklenmemiş")
                return
            
            # Ahır boyutlarını ayarla
            stable_width = 80
            stable_height = 70
            
            # Ahır resmini ölçeklendir
            scaled_stable = self.images["ahir"].scaled(stable_width, stable_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Kilisenin konumu ve genişliği (draw_church metodundan)
            church_x = 520
            church_width = 90
            
            # Ahırın konumunu hesapla (kilisenin 50 piksel sağı)
            stable_x = church_x + church_width + 50
            
            # Y pozisyonunu hesapla (zemin üzerinde, diğer yapılarla hizalı)
            stable_y = self.height() - self.ground_height - stable_height + 12
            
            # Ahırı çiz
            painter.drawPixmap(int(stable_x), int(stable_y), scaled_stable)
            
            print(f"Ahır çizildi: Konum=({int(stable_x)}, {int(stable_y)}), Boyut={stable_width}x{stable_height}")
            
        except Exception as e:
            print(f"HATA: Ahır çizme hatası: {e}")
            import traceback
            traceback.print_exc()

    def draw_hay_bale(self, painter):
        """Balyayı çiz - Ahırın 100 piksel sağında"""
        try:
            if not self.images["balya"]:
                print("UYARI: Balya resmi yüklenmemiş")
                return
            
            # Balya boyutlarını ayarla
            hay_bale_width = 15
            hay_bale_height = 10
            
            # Balya resmini ölçeklendir
            scaled_hay_bale = self.images["balya"].scaled(hay_bale_width, hay_bale_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Ahırın konumu ve genişliği (draw_stable metodundan)
            church_x = 520
            church_width = 90
            stable_x = church_x + church_width + 50  # Kilisenin 50 piksel sağı
            stable_width = 80  # Ahır genişliği
            
            # Balyanın konumunu hesapla (ahırın 100 piksel sağı)
            hay_bale_x = stable_x + stable_width + 80
            
            # Y pozisyonunu hesapla (zemin üzerinde, diğer yapılarla hizalı)
            hay_bale_y = self.height() - self.ground_height - hay_bale_height + 2
            
            # Balyayı çiz
            painter.drawPixmap(int(hay_bale_x), int(hay_bale_y), scaled_hay_bale)
            
            print(f"Balya çizildi: Konum=({int(hay_bale_x)}, {int(hay_bale_y)}), Boyut={hay_bale_width}x{hay_bale_height}")
            
        except Exception as e:
            print(f"HATA: Balya çizme hatası: {e}")
            import traceback
            traceback.print_exc()

    def draw_fence(self, painter):
        """Çiti çiz - Ahır ile balya arasında, yatay olarak"""
        try:
            # Çit resmi yüklü değilse çıkış yap
            if self.images["cit"] is None:
                print("UYARI: Çit resmi yüklenemediği için çizilemedi")
                return
            
            # Çit resmi boyutlarını ayarla
            cit_width = 30  # Çit parçasının genişliği
            cit_height = 35  # Çit parçasının yüksekliği
            
            # Çit resmini ölçeklendir
            scaled_cit = self.images["cit"].scaled(cit_width, cit_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Ahırın konumu ve boyutları (draw_stable metodundan)
            church_x = 520
            church_width = 90
            stable_x = church_x + church_width + 50  # Kilisenin 50 piksel sağı
            stable_width = 80  # Ahır genişliği
            
            # Balyanın konumu (draw_hay_bale metodundan)
            hay_bale_x = stable_x + stable_width + 60
            
            # Çitin başlangıç ve bitiş noktalarını belirle
            start_x = stable_x + stable_width -30  # Ahırın bitişinden başla
            end_x = hay_bale_x  # Balyanın başlangıcında bitir
            
            # Çitin y pozisyonu - zemin üzerinde, köylülerin yürüdüğü seviyede
            fence_y = self.height() - self.ground_height - cit_height + 15
            
            # Çit parçalarını üst üste bindirerek çiz
            # Her parçayı bir öncekiyle %30 üst üste binerek yerleştir
            overlap = int(cit_width * 0.3)  # %30 üst üste binme
            step = cit_width - overlap
            
            # Kaç tane çit parçası gerektiğini hesapla
            fence_width = end_x - start_x
            tile_count = int(fence_width / step) + 1  # +1 ekstra parça (sağ kenar için)
            
            # Her pozisyona çit parçasını çiz
            for i in range(tile_count):
                x = start_x + (i * step)
                painter.drawPixmap(int(x), int(fence_y), scaled_cit)
            
            print(f"Çit çizildi: {tile_count} adet parça, toplam genişlik: {fence_width} piksel, üst üste bindirme: {overlap} piksel")
            
        except Exception as e:
            print(f"HATA: Çit çizme hatası: {e}")
            import traceback
            traceback.print_exc()

    def draw_cart(self, painter):
        """Arabayı çiz - Balyanın 2 piksel sağında"""
        try:
            if not self.images["araba"]:
                print("UYARI: Araba resmi yüklenmemiş")
                return
            
            # Araba boyutlarını ayarla
            cart_width = 50
            cart_height = 40
            
            # Araba resmini ölçeklendir
            scaled_cart = self.images["araba"].scaled(cart_width, cart_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Balya konumu ve boyutları (draw_hay_bale metodundan)
            church_x = 520
            church_width = 90
            stable_x = church_x + church_width + 50  # Kilisenin 50 piksel sağı
            stable_width = 80  # Ahır genişliği
            hay_bale_x = stable_x + stable_width + 80  # Balya x konumu
            hay_bale_width = 15  # Balya genişliği
            
            # Arabanın konumu (balyanın 2 piksel sağı)
            cart_x = hay_bale_x + hay_bale_width + 2
            
            # Y pozisyonunu hesapla (zemin üzerinde, diğer yapılarla hizalı)
            cart_y = self.height() - self.ground_height - cart_height + 14
            
            # Arabayı çiz
            painter.drawPixmap(int(cart_x), int(cart_y), scaled_cart)
            
            print(f"Araba çizildi: Konum=({int(cart_x)}, {int(cart_y)}), Boyut={cart_width}x{cart_height}")
            
        except Exception as e:
            print(f"HATA: Araba çizme hatası: {e}")
            import traceback
            traceback.print_exc()

    def draw_torch(self, painter):
        """Meşaleyi çiz - Gardiyan kulesinin 2 piksel sağında"""
        try:
            if not self.images["torch"]:
                print("UYARI: Meşale resmi yüklenmemiş")
                return
            
            # Meşale boyutlarını ayarla
            torch_width = 10
            torch_height = 20
            
            # Meşale resmini ölçeklendir
            scaled_torch = self.images["torch"].scaled(torch_width, torch_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Gardiyan kulesi konumu ve boyutları (draw_guard metodundan)
            guard_x = 870  # Gardiyan kulesi x konumu
            guard_width = 130  # Gardiyan kulesi genişliği
            
            # Meşalenin konumunu hesapla (gardiyan kulesinin 2 piksel sağı)
            torch_x = guard_x + guard_width - 63
            
            # Y pozisyonunu hesapla (zemin üzerinde, diğer yapılarla hizalı)
            torch_y = self.height() - self.ground_height - torch_height
            
            # Meşaleyi çiz
            painter.drawPixmap(int(torch_x), int(torch_y), scaled_torch)
            
            print(f"Meşale çizildi: Konum=({int(torch_x)}, {int(torch_y)}), Boyut={torch_width}x{torch_height}")
            
        except Exception as e:
            print(f"HATA: Meşale çizme hatası: {e}")
            import traceback
            traceback.print_exc()

    def draw_barrel(self, painter):
        """Fıçıyı çiz - Han'ın hemen arkasında"""
        try:
            if not self.images["fici"]:
                print("UYARI: Fıçı resmi yüklenmemiş")
                return
            
            # Fıçı boyutlarını ayarla
            barrel_width = 10
            barrel_height = 10
            
            # Fıçı resmini ölçeklendir
            scaled_barrel = self.images["fici"].scaled(barrel_width, barrel_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Han'ın konumu (draw_inn metodundan)
            inn_x = 200
            inn_width = 90
            inn_y = self.height() - self.ground_height - 40 # Han'ın y konumu
            
            # Fıçının konumunu hesapla (Han'ın arkasına yerleştir)
            barrel_x = 190  # Han'ın ortasına hizala
            barrel_y = inn_y # Han'ın biraz arkasında/üstünde olacak şekilde
            
            # Fıçıyı çiz
            painter.drawPixmap(int(barrel_x), int(barrel_y), scaled_barrel)
            
            print(f"Fıçı çizildi: Konum=({int(barrel_x)}, {int(barrel_y)}), Boyut={barrel_width}x{barrel_height}")
            
        except Exception as e:
            print(f"HATA: Fıçı çizme hatası: {e}")
            import traceback
            traceback.print_exc()