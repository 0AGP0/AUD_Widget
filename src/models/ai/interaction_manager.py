import random
import time
from typing import Dict, List, Optional

from src.models.ai.rule_based_ai import RuleBasedAI
from PyQt5.QtCore import QTimer, QObject
from src.models.ai.dialogue_system import DialogueManager, DialogueType, EmotionType, create_dialogue_system
from src.models.ai.behavior_tree import BlackboardNode

class InteractionManager(QObject):
    """Köylüler arası etkileşimleri yöneten sınıf"""
    
    def __init__(self, game_controller):
        super().__init__()
        self.game_controller = game_controller
        self.ai_system = RuleBasedAI()
        
        # Etkileşim istatistikleri
        self.total_interactions = 0
        self.successful_interactions = 0
        self.failed_interactions = 0
        
        # Etkileşim zamanlaması
        self.last_interaction_check = time.time()
        self.interaction_check_interval = 5.0  # 5 saniyede bir etkileşim kontrolü
        
        # İstatistikler
        self.total_chats = 0  # Başlatılan toplam sohbet sayısı
        self.completed_chats = 0  # Tamamlanan sohbet sayısı
        self.chat_logs = []  # Sohbet kayıtları
        self.chat_topics = {}  # Konuşulan konuların istatistikleri
        
        # Son etkileşimleri takip et
        self.recent_chats = []  # Son sohbetler (initiator, partner, timestamp)
        self.recent_decisions = []  # Son kararlar (villager, decision, timestamp)
        
        self.active_chats = {}  # {chat_id: (initiator, partner, start_time, duration)}
        self.chat_id_counter = 0
        self.dialogue_manager = create_dialogue_system()
        
        # Rastgele etkileşim zamanını ayarla
        self.next_random_interaction_time = time.time() + random.uniform(30, 60)  # 30-60 saniye arası
    
    def update(self, dt=0.016):
        """Etkileşim yöneticisini güncelle"""
        current_time = time.time()
        
        # Belirli aralıklarla etkileşim kontrolü yap
        if current_time - self.last_interaction_check >= self.interaction_check_interval:
            self.check_interactions()
            self.last_interaction_check = current_time
        
        try:
            # Aktif sohbetleri kontrol et
            self.check_active_chats()
            
            # Rastgele etkileşim zamanı geldiyse
            if current_time >= self.next_random_interaction_time:
                # Yeni rastgele etkileşim zamanı ayarla
                self.next_random_interaction_time = current_time + random.uniform(30, 60)  # 30-60 saniye arası
                
                # Gündüzse rastgele etkileşim oluştur
                if self.game_controller.is_daytime:
                    self.create_random_interaction()
        except Exception as e:
            print(f"HATA: Etkileşim güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def check_interactions(self):
        """Köylüler arası etkileşimleri kontrol et"""
        # Gece ise etkileşim kontrolü yapma
        if not self.game_controller.is_daytime:
            return
        
        villagers = self.game_controller.villagers
        
        # Her köylü için etkileşim kontrolü
        for villager in villagers:
            # Zaten sohbet ediyorsa atla
            if villager.is_chatting:
                continue
            
            # Sohbet başlatma kontrolü
            should_chat, partner = self.ai_system.should_initiate_chat(villager, villagers)
            
            if should_chat and partner:
                # Sohbet başlat
                self.start_chat(villager, partner)
                self.total_interactions += 1
                self.successful_interactions += 1
            
            # Karar verme kontrolü
            decision = self.ai_system.make_decision(villager)
            if decision:
                self.apply_decision(villager, decision)
    
    def start_chat(self, initiator, partner):
        """Köylüler arasında sohbet başlat"""
        try:
            if not self.can_chat(initiator, partner):
                return False
                
            # Köylülerin sohbet etmeleri için yakın durmaları lazım
            distance = abs(initiator.x - partner.x)
            if distance > 50:  # 50 pikselden fazla uzaklıkta ise önce yaklaşsın
                initiator.state = f"{partner.name} ile Konuşmaya Gidiyor"
                return False
                
            print(f"Sohbet başlatılıyor: {initiator.name} -> {partner.name}")
            
            # Köylülerin sohbet bilgilerini ayarla
            initiator.is_chatting = True
            initiator.chat_partner = partner
            initiator.chat_time = 0.0
            initiator.chat_duration = random.uniform(30.0, 60.0)  # 30-60 saniye arası sohbet
            initiator.is_chat_initiator = True
            initiator.last_message_time = 0
            initiator.chat_topic = random.choice(initiator.CHAT_TOPICS)  # Rastgele bir konu seç
            
            partner.is_chatting = True
            partner.chat_partner = initiator
            partner.chat_time = 0.0  
            partner.chat_duration = initiator.chat_duration
            partner.is_chat_initiator = False
            partner.last_message_time = 0
            partner.chat_topic = initiator.chat_topic  # Aynı konuyu konuşsunlar
            
            # Köylülerin durumlarını güncelle
            initiator.state = f"{partner.name} ile Sohbet Ediyor"
            partner.state = f"{initiator.name} ile Sohbet Ediyor"
            
            # Hareketlerini durdur
            initiator.is_moving = False
            partner.is_moving = False
            
            # Birbirlerine dönük olsunlar
            if initiator.x < partner.x:
                initiator.direction = 1  # Sağa bak
                initiator.direction_x = 1
                partner.direction = -1  # Sola bak
                partner.direction_x = -1
            else:
                initiator.direction = -1  # Sola bak
                initiator.direction_x = -1
                partner.direction = 1  # Sağa bak
                partner.direction_x = 1
            
            # Selamlaşma mesajlarını göster (ilk kısmın bitiminde karşı taraf cevap versin)
            chat_delay = 1000  # 1 saniye sonra selamlaş
            
            # Diyalog başlatan kişiden gelen ilk mesaj (selamlaşma)
            initiator.chat_topic = "selamlaşma"  # İlk mesaj selamlaşma
            greeting_message = initiator.generate_chat_message(is_initiator=True)
            
            # İlk mesaj gecikmesi
            QTimer.singleShot(chat_delay, lambda: self.show_chat_message(initiator, greeting_message))
            
            # Karşı tarafın cevap vermesi için zamanlayıcı
            QTimer.singleShot(chat_delay + 2000, lambda: self.partner_respond_greeting(initiator, partner))
            
            # Sohbetin devam etmesi için zamanlayıcı
            QTimer.singleShot(chat_delay + 5000, lambda: self.continue_chat(initiator, partner))
            
            # İstatistikleri güncelle
            self.total_chats += 1
            self.recent_chats.append((initiator.name, partner.name, time.time()))
            
            # Son sohbet zamanını güncelle
            initiator.last_chat_time = time.time()
            partner.last_chat_time = time.time()
            
            return True
            
        except Exception as e:
            print(f"HATA: Sohbet başlatma hatası: {e}")
            import traceback
            traceback.print_exc()
            return False

    def partner_respond_greeting(self, initiator, partner):
        """Karşı tarafın selamlaşmaya cevap vermesi"""
        try:
            # Köylülerin hala sohbet ettiğini kontrol et
            if not initiator.is_chatting or not partner.is_chatting:
                return
                
            # Karşı tarafın cevap vermesi
            partner.chat_topic = "selamlaşma"  # Cevap olarak selamlaşma
            response_message = partner.generate_chat_message(is_initiator=False)
            
            # Yanıt mesajını göster
            self.show_chat_message(partner, response_message)
            
        except Exception as e:
            print(f"HATA: Selamlaşma cevabı hatası: {e}")
            import traceback
            traceback.print_exc()

    def continue_chat(self, initiator, partner):
        """Sohbeti devam ettir"""
        try:
            # Köylülerin hala sohbet ettiğini kontrol et
            if not initiator.is_chatting or not partner.is_chatting:
                return
                
            # Sohbet süresini kontrol et
            if initiator.chat_time > initiator.chat_duration:
                self.end_chat(initiator, partner, "Süre doldu")
                return
                
            # Sohbet konusunu belirle - ilk mesajdan sonra rastgele bir konu seçelim
            if initiator.chat_topic == "selamlaşma":
                # İlk konuşmadan sonra artık normal bir konuya geçelim
                new_topic = random.choice([t for t in initiator.CHAT_TOPICS if t != "selamlaşma"])
                
                # Mesleğe göre konu seçme olasılığını artır
                if initiator.profession:
                    profession_topic_map = {
                        "Oduncu": "meslek",
                        "İnşaatçı": "ev",
                        "Avcı": "meslek",
                        "Gardiyan": "dedikodu",
                        "Papaz": "felsefe",
                        "Çiftçi": "yemek"
                    }
                    
                    if initiator.profession in profession_topic_map:
                        if random.random() < 0.6:  # %60 şans ile mesleğe uygun konu
                            new_topic = profession_topic_map[initiator.profession]
                
                # Karakteristik özelliklere göre konu seçme olasılığını artır
                trait_topic_map = {
                    "Dedikodu": "dedikodu",
                    "Esprili": "şaka",
                    "Romantik": "ilişki",
                    "Yobaz": "felsefe",
                    "Karamsar": "hava",
                    "İyimser": "günlük"
                }
                
                for trait, topic in trait_topic_map.items():
                    if trait in initiator.traits and random.random() < 0.7:  # %70 şans
                        new_topic = topic
                        break
                
                # Konuyu ayarla
                initiator.chat_topic = new_topic
                partner.chat_topic = new_topic
            
            # Başlatan kişinin mesajını oluştur ve göster
            chat_message = initiator.generate_chat_message(is_initiator=True)
            self.show_chat_message(initiator, chat_message)
            
            # Karşı tarafın cevap vermesi için zamanlayıcı (5 saniye bekle)
            QTimer.singleShot(5000, lambda: self.partner_respond(initiator, partner))
            
            # Sohbet süresini 5 saniye artır (her konuşma için)
            initiator.chat_time += 5
            partner.chat_time += 5
            
        except Exception as e:
            print(f"HATA: Sohbet devam hatası: {e}")
            import traceback
            traceback.print_exc()

    def partner_respond(self, initiator, partner):
        """Karşı tarafın yanıt vermesi"""
        try:
            # Köylülerin hala sohbet ettiğini kontrol et
            if not initiator.is_chatting or not partner.is_chatting:
                return
                
            # Sohbet süresini kontrol et
            if initiator.chat_time > initiator.chat_duration:
                self.end_chat(initiator, partner, "Süre doldu")
                return
                
            # Karşı tarafın yanıt vermesi
            response_message = partner.generate_chat_message(is_initiator=False)
            self.show_chat_message(partner, response_message)
            
            # Yeni bir mesaj eklemek için rastgele şans
            # İlişki puanı yüksekse veya belli özellikler varsa devam etme şansı artar
            continue_chance = 0.7  # Temel devam etme şansı
            
            # İlişki puanına göre düzenle
            relationship = initiator.get_relationship_with(partner.name)
            if relationship > 70:
                continue_chance += 0.2
            elif relationship < 30:
                continue_chance -= 0.2
                
            # Kişilik özelliklerine göre düzenle
            if "Karizmatik" in initiator.traits or "Karizmatik" in partner.traits:
                continue_chance += 0.1
            if "İlgisiz" in initiator.traits or "İlgisiz" in partner.traits:
                continue_chance -= 0.2
            if "Esprili" in initiator.traits or "Esprili" in partner.traits:
                continue_chance += 0.1
                
            # Sohbetin devam etme şansı
            if random.random() < continue_chance:
                # Başlatan kişinin tekrar yanıt vermesi için zamanlayıcı (5 saniye bekle)
                QTimer.singleShot(5000, lambda: self.initiator_respond(initiator, partner))
            else:
                # Sohbeti sonlandır
                QTimer.singleShot(3000, lambda: self.end_chat(initiator, partner, "Doğal sonlanma"))
            
            # Sohbet süresini 5 saniye artır (her konuşma için)
            initiator.chat_time += 5
            partner.chat_time += 5
            
        except Exception as e:
            print(f"HATA: Partner yanıt hatası: {e}")
            import traceback
            traceback.print_exc()

    def initiator_respond(self, initiator, partner):
        """Başlatan kişinin tekrar yanıt vermesi"""
        try:
            # Köylülerin hala sohbet ettiğini kontrol et
            if not initiator.is_chatting or not partner.is_chatting:
                return
                
            # Sohbet süresini kontrol et
            if initiator.chat_time > initiator.chat_duration:
                self.end_chat(initiator, partner, "Süre doldu")
                return
                
            # Sohbeti devam ettirme şansını kontrol et - konu değişimini de düşünelim
            topic_change_chance = 0.3  # %30 şans ile konu değişebilir
            
            # Şu andaki konuya bağlı olarak değişiklik şansını ayarla
            if initiator.chat_topic == "dedikodu":
                topic_change_chance = 0.4  # Dedikodu sonrası konu değişme olasılığı daha yüksek
            elif initiator.chat_topic == "şaka":
                topic_change_chance = 0.6  # Şaka sonrası konu değişme olasılığı çok yüksek
                
            # Konu değişimi gerçekleşti mi?
            if random.random() < topic_change_chance:
                # Yeni bir konu seç (mevcut konudan farklı olarak)
                available_topics = [t for t in initiator.CHAT_TOPICS if t != initiator.chat_topic and t != "selamlaşma"]
                if available_topics:
                    new_topic = random.choice(available_topics)
                    initiator.chat_topic = new_topic
                    partner.chat_topic = new_topic
                    
                    # Konu değişimini bildir
                    print(f"Konu değişti: {initiator.name} ve {partner.name} arasında yeni konu: {new_topic}")
            
            # Başlatan kişinin yanıt vermesi
            response_message = initiator.generate_chat_message(is_initiator=True)
            self.show_chat_message(initiator, response_message)
            
            # Sohbeti devam ettirme şansını kontrol et
            continue_chance = 0.6  # Temel devam etme şansı
            
            # İlişki puanına göre düzenle
            relationship = initiator.get_relationship_with(partner.name)
            if relationship > 70:
                continue_chance += 0.2
            elif relationship < 30:
                continue_chance -= 0.2
                
            # Kişilik özelliklerine göre düzenle
            if "Karizmatik" in initiator.traits or "Karizmatik" in partner.traits:
                continue_chance += 0.1
            if "İlgisiz" in initiator.traits or "İlgisiz" in partner.traits:
                continue_chance -= 0.2
            if "Esprili" in initiator.traits or "Esprili" in partner.traits:
                continue_chance += 0.1
                
            # Sohbetin devam etme şansı
            if random.random() < continue_chance:
                # Karşı tarafın yanıt vermesi için zamanlayıcı (5 saniye bekle)
                QTimer.singleShot(5000, lambda: self.partner_respond(initiator, partner))
            else:
                # Sohbeti sonlandır
                QTimer.singleShot(3000, lambda: self.end_chat(initiator, partner, "Doğal sonlanma"))
            
            # Sohbet süresini 5 saniye artır (her konuşma için)
            initiator.chat_time += 5
            partner.chat_time += 5
            
        except Exception as e:
            print(f"HATA: Başlatan yanıt hatası: {e}")
            import traceback
            traceback.print_exc()

    def end_chat(self, initiator, partner, reason="Bilinmeyen"):
        """Sohbeti sonlandır"""
        try:
            # Her iki köylü de artık konuşmuyor
            initiator.is_chatting = False
            initiator.chat_partner = None
            initiator.chat_topic = ""
            initiator.is_moving = False  # Hareket durumunu sıfırla
            
            partner.is_chatting = False
            partner.chat_partner = None
            partner.chat_topic = ""
            partner.is_moving = False  # Hareket durumunu sıfırla
            
            # İlişki puanlarını güncelle
            relationship_change = initiator.update_relationship_after_chat()
            
            # Sohbet sonrası bekleme süresi (cooldown)
            cooldown_time = random.uniform(20, 40)  # 20-40 saniye arası bekleme
            initiator.chat_cooldown = cooldown_time
            partner.chat_cooldown = cooldown_time
            
            # Durumlarını güncelle
            initiator.state = "Dolaşıyor"
            partner.state = "Dolaşıyor"
            
            # Yeni hedefler belirle
            QTimer.singleShot(1000, initiator.find_new_target)
            QTimer.singleShot(1500, partner.find_new_target)
            
            # Sohbet sonu bilgilerini logla
            print(f"Sohbet sonlandı: {initiator.name} ve {partner.name} arasında. Neden: {reason}, İlişki değişimi: {relationship_change}")
            
            # İstatistikleri güncelle
            self.completed_chats += 1
            
            return True
            
        except Exception as e:
            print(f"HATA: Sohbet sonlandırma hatası: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def apply_decision(self, villager, decision):
        """Köylünün kararını uygula"""
        if decision == "odun_kes":
            # En yakın ağacı bul
            nearest_tree = self.game_controller.find_nearest_available_tree(villager)
            if nearest_tree:
                villager.target_x = nearest_tree.x
                villager.state = "Ağaca Gidiyor"
                print(f"{villager.name} odun kesmeye gidiyor")
        
        elif decision == "ev_inşa_et":
            # Ev inşa etmek için uygun yer bul
            # Bu kısım oyun kontrolcüsünde uygulanacak
            villager.state = "Ev İnşa Etmeye Hazırlanıyor"
            print(f"{villager.name} ev inşa etmeye hazırlanıyor")
        
        elif decision == "avlan":
            # Av bölgesine git
            # Bu kısım oyun kontrolcüsünde uygulanacak
            villager.state = "Avlanmaya Gidiyor"
            print(f"{villager.name} avlanmaya gidiyor")
        
        elif decision == "devriye_gez":
            # Devriye gezme
            villager.state = "Devriye Geziyor"
            print(f"{villager.name} devriye geziyor")
        
        elif decision == "dua_et":
            # Dua etme
            villager.state = "Dua Ediyor"
            print(f"{villager.name} dua ediyor")
        
        elif decision == "dolaş":
            # Rastgele dolaşma
            if random.random() < 0.5:  # %50 şans
                # Yeni hedef belirle
                min_x = 100
                max_x = self.game_controller.window.width() - 100
                villager.target_x = random.randint(min_x, max_x)
                villager.state = "Dolaşıyor"
                print(f"{villager.name} yeni bir yere dolaşıyor: {villager.target_x}")
    
    def get_stats(self):
        """Etkileşim istatistiklerini döndür"""
        return {
            "total_interactions": self.total_interactions,
            "successful_interactions": self.successful_interactions,
            "failed_interactions": self.failed_interactions
        }

    def update_relationship(self, villager1, villager2, points, reason="Bilinmeyen"):
        """İki köylü arasındaki ilişkiyi güncelle"""
        try:
            # İlk köylünün ilişki puanı
            current_points = villager1.get_relationship_with(villager2.name)
            new_points = max(0, min(100, current_points + points))
            villager1.relationship_points[villager2.name] = new_points
            
            # İkinci köylünün ilişki puanı
            partner_current_points = villager2.get_relationship_with(villager1.name)
            partner_new_points = max(0, min(100, partner_current_points + points))
            villager2.relationship_points[villager1.name] = partner_new_points
            
            # İlişki değişiminin yönü ve büyüklüğü hakkında bilgi
            change_direction = "arttı" if points > 0 else "azaldı" if points < 0 else "değişmedi"
            change_magnitude = abs(points)
            change_desc = ""
            
            if change_magnitude > 5:
                change_desc = "önemli ölçüde"
            elif change_magnitude > 2:
                change_desc = "biraz"
            elif change_magnitude > 0:
                change_desc = "çok az"
                
            print(f"İlişki {change_desc} {change_direction}: {villager1.name} <-> {villager2.name}: {current_points} -> {new_points} ({points:+d}) - Neden: {reason}")
            
        except Exception as e:
            print(f"HATA - İlişki güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
            
    def can_chat(self, initiator, partner):
        """İki köylünün sohbet edip edemeyeceğini kontrol et"""
        try:
            # İki köylü de geçerli olmalı
            if not initiator or not partner:
                return False
                
            # Kendisiyle konuşamaz
            if initiator == partner:
                return False
                
            # İki köylü de şu anda sohbet etmemeli
            if initiator.is_chatting or partner.is_chatting:
                return False
                
            # İki köylü de konuşma bekleme süresinde olmamalı
            current_time = time.time()
            if hasattr(initiator, 'last_chat_time') and current_time - initiator.last_chat_time < initiator.chat_cooldown:
                return False
            if hasattr(partner, 'last_chat_time') and current_time - partner.last_chat_time < partner.chat_cooldown:
                return False
                
            # İki köylü arasındaki mesafe uygun olmalı
            distance = abs(initiator.x - partner.x)
            # Mesafeyi 200 pikselden 50 piksele düşürdük - yanyana olmalılar
            if distance > 50:  
                # Eğer mesafe 50 piksel üzerindeyse, konuşmak için yaklaşmaya çalışıyorlar mı kontrol et
                if initiator.state == f"{partner.name} ile Konuşmaya Gidiyor" or partner.state == f"{initiator.name} ile Konuşmaya Gidiyor":
                    return False  # Hala yaklaşıyorlar, şu an için sohbet etmesinler
                return False
                
            # Köylülerin durumu konuşmaya uygun olmalı
            if hasattr(initiator, 'state'):
                busy_states = ["Odun Kesiyor", "İnşaat Yapıyor", "Avlanıyor", "Eve Dönüyor", "Kaleye Dönüyor"]
                if initiator.state in busy_states:
                    return False
            
            if hasattr(partner, 'state'):
                busy_states = ["Odun Kesiyor", "İnşaat Yapıyor", "Avlanıyor", "Eve Dönüyor", "Kaleye Dönüyor"]
                if partner.state in busy_states:
                    return False
            
            # Temel konuşma şansı - azaltıldı
            chat_chance = 0.6  # %90'dan %60'a düşürüldü
            
            # Mesafe yakınsa şansı artır
            if distance < 30:
                chat_chance += 0.3
            
            # Karizmatik köylüler daha fazla konuşma şansına sahip
            if "Karizmatik" in initiator.traits:
                chat_chance += 0.1
            if "Esprili" in initiator.traits:
                chat_chance += 0.1
            if "İlgisiz" in initiator.traits:
                chat_chance -= 0.2
            if "Sinirli" in initiator.traits:
                chat_chance -= 0.1
            
            # İlişki puanı yüksekse şansı artır
            relationship = initiator.get_relationship_with(partner.name)
            if relationship > 70:
                chat_chance += 0.2
            elif relationship < 30:
                chat_chance -= 0.2
            
            # Yanına konuşmaya geldiyse şansı önemli ölçüde artır
            if initiator.state == f"{partner.name} ile Konuşmaya Gidiyor":
                chat_chance += 0.5
            if partner.state == f"{initiator.name} ile Konuşmaya Gidiyor":
                chat_chance += 0.5
            
            # Birbirlerine uyumlu özellikleri varsa şansı artır
            compatibility_score = initiator.check_trait_compatibility(partner)
            if compatibility_score > 0:
                chat_chance += 0.1 * compatibility_score
            elif compatibility_score < 0:
                chat_chance -= 0.1 * abs(compatibility_score)
            
            # Son 24 saatte konuştuklarsa şansı azalt (tekrarlayan konuşmaları azalt)
            recent_interactions = getattr(initiator, 'recent_chat_partners', {})
            if partner.name in recent_interactions:
                last_chat_time = recent_interactions[partner.name]
                hours_since_last_chat = (current_time - last_chat_time) / 3600
                if hours_since_last_chat < 24:  # Son 24 saat içinde
                    chat_chance -= 0.3  # Konuşma şansını önemli ölçüde azalt
            
            # Şans kontrolü
            if random.random() > chat_chance:
                return False
                
            # Son etkileşimleri kaydet
            if not hasattr(initiator, 'recent_chat_partners'):
                initiator.recent_chat_partners = {}
            initiator.recent_chat_partners[partner.name] = current_time
            
            if not hasattr(partner, 'recent_chat_partners'):
                partner.recent_chat_partners = {}
            partner.recent_chat_partners[initiator.name] = current_time
            
            # Konuşma durumlarını temizle
            initiator.state = "Sohbet Ediyor"
            partner.state = "Sohbet Ediyor"
            
            return True
            
        except Exception as e:
            print(f"HATA: Sohbet kontrol hatası: {e}")
            return False 

    def show_chat_message(self, villager, message):
        """Sohbet mesajını göster"""
        try:
            # Mesajı köylünün sohbet mesajı olarak ayarla
            villager.chat_message = message
            
            # Sohbet balonunu göster
            villager.chat_bubble_visible = True
            villager.chat_bubble_time = time.time()
            
            # Game Controller'a mesajı bildir
            if hasattr(self, 'game_controller') and self.game_controller:
                self.game_controller.chat_message.emit(villager, message)
                
            # Ek bilgi olarak logla
            print(f"📢 {villager.name}: {message}")
            
            # Sohbet kayıtlarına ekle
            self.chat_logs.append({
                'villager': villager.name,
                'message': message,
                'time': time.time(),
                'topic': villager.chat_topic if hasattr(villager, 'chat_topic') else "Bilinmeyen"
            })
            
            # Konu istatistiklerini güncelle
            if hasattr(villager, 'chat_topic') and villager.chat_topic:
                topic = villager.chat_topic
                if topic in self.chat_topics:
                    self.chat_topics[topic] += 1
                else:
                    self.chat_topics[topic] = 1
                    
        except Exception as e:
            print(f"HATA: Sohbet mesajı gösterme hatası: {e}")
            import traceback
            traceback.print_exc() 

    def check_active_chats(self):
        """Aktif sohbetleri kontrol et"""
        try:
            current_time = time.time()
            chats_to_end = []
            
            # Aktif sohbetleri kontrol et
            for chat_id, (initiator, partner, start_time, duration) in self.active_chats.items():
                # Sohbet süresi dolduysa
                if current_time - start_time > duration:
                    chats_to_end.append(chat_id)
                    
                # Sohbet eden köylülerden biri öldüyse
                if hasattr(initiator, 'is_dead') and initiator.is_dead or hasattr(partner, 'is_dead') and partner.is_dead:
                    chats_to_end.append(chat_id)
            
            # Sohbetleri sonlandır
            for chat_id in chats_to_end:
                initiator, partner, _, _ = self.active_chats[chat_id]
                self.end_chat(initiator, partner)
        except Exception as e:
            print(f"HATA: Aktif sohbet kontrolü hatası: {e}")
            import traceback
            traceback.print_exc()

    def create_random_interaction(self):
        """Rastgele bir etkileşim oluştur"""
        try:
            # Köylü listesi boşsa çık
            if not hasattr(self.game_controller, 'villagers') or not self.game_controller.villagers:
                return False
            
            # Rastgele iki köylü seç
            if len(self.game_controller.villagers) < 2:
                return False
                
            # Rastgele bir köylü seç
            initiator = random.choice(self.game_controller.villagers)
            
            # İlk köylü sohbet ediyorsa çık
            if initiator.is_chatting:
                return False
            
            # İlk köylü ölüyse çık
            if hasattr(initiator, 'is_dead') and initiator.is_dead:
                return False
            
            # Diğer köylüyü seç (aynı köylü olmamalı ve sohbet etmiyor olmalı)
            available_partners = [v for v in self.game_controller.villagers 
                                if v != initiator and not v.is_chatting and not (hasattr(v, 'is_dead') and v.is_dead)]
            
            if not available_partners:
                return False
            
            partner = random.choice(available_partners)
            
            # İki köylünün aralarındaki mesafeyi kontrol et
            distance = ((initiator.x - partner.x) ** 2 + (initiator.y - partner.y) ** 2) ** 0.5
            
            # Eğer mesafe fazlaysa ve rastgele değer 0.8'den küçükse etkileşimi başlatma
            if distance > 100 and random.random() < 0.8:
                return False
            
            # Sohbeti başlat
            return self.start_chat(initiator, partner)
            
        except Exception as e:
            print(f"HATA: Rastgele etkileşim oluşturma hatası: {e}")
            import traceback
            traceback.print_exc()
            return False

    def move_villagers_closer(self, initiator, partner):
        """İki köylüyü birbirine yaklaştır"""
        try:
            # İki köylü arasındaki mesafeyi hesapla
            distance = ((initiator.x - partner.x) ** 2 + (initiator.y - partner.y) ** 2) ** 0.5
            
            # Eğer mesafe fazlaysa (100 birimden fazla)
            if distance > 100:
                # İnitiator'ı partnere doğru yaklaştır
                direction_x = 1 if partner.x > initiator.x else -1
                
                # Hedef pozisyonu ayarla (partnerin 50 birim yanı)
                target_x = partner.x - (50 * direction_x)
                
                # Zemin seviyesini kontrol et
                ground_y = self.game_controller.ground_y if hasattr(self.game_controller, 'ground_y') else 400
                
                # Hedef pozisyonu ayarla
                initiator.target_x = target_x
                initiator.target_y = ground_y
                initiator.is_moving = True
                
                print(f"{initiator.name}, {partner.name} ile konuşmak için yaklaşıyor.")
        except Exception as e:
            print(f"HATA: Köylüleri yaklaştırma hatası: {e}")
            import traceback
            traceback.print_exc() 