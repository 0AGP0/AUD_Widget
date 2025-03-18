import random
import time
from typing import Dict, List, Tuple, Optional

class RuleBasedAI:
    """Köylüler için kural tabanlı yapay zeka sistemi"""
    
    def __init__(self):
        # Etkileşim sıklığını kontrol etmek için zaman aralıkları
        self.chat_cooldown = 60  # saniye (varsayılan: 60 saniye)
        self.decision_cooldown = 30  # saniye (varsayılan: 30 saniye)
        
        # Etkileşim şansları
        self.base_chat_chance = 0.20  # Temel sohbet başlatma şansı - 0.05'ten 0.20'ye yükseltildi
        
        # Karakteristik özelliklerin uyum grupları
        self.trait_compatibility_groups = {
            # Olumlu özellikler grubu
            "positive": [
                "Çalışkan", "Karizmatik", "Babacan", "Romantik", "Merhametli", 
                "Sabırlı", "Esprili", "Güvenilir", "Meraklı", "Dikkatli", 
                "İyimser", "Pratik", "Mantıklı", "Soğukkanlı", "Cömert"
            ],
            # Olumsuz özellikler grubu
            "negative": [
                "Tembel", "Sinirli", "Yobaz", "İnatçı", "Kurnaz", 
                "Sabırsız", "Karamsar", "Duygusal", "Kıskanç", "Merhametsiz", "İlgisiz"
            ],
            # Nötr özellikler grubu
            "neutral": [
                "Uykucu", "Hırslı"
            ]
        }
        
        # Birbiriyle iyi anlaşan özellik çiftleri
        self.compatible_trait_pairs = [
            ("Çalışkan", "Çalışkan"),
            ("Çalışkan", "Hırslı"),
            ("İyimser", "İyimser"),
            ("İyimser", "Esprili"),
            ("Romantik", "Merhametli"),
            ("Karizmatik", "Esprili"),
            ("Babacan", "Merhametli"),
            ("Güvenilir", "Sabırlı"),
            ("Meraklı", "Mantıklı"),
            ("Cömert", "Merhametli"),
            ("Tembel", "Tembel"),
            ("Uykucu", "Tembel"),
            ("Karamsar", "Karamsar"),
        ]
        
        # Birbiriyle zıt olan ve anlaşamayan özellik çiftleri
        self.incompatible_trait_pairs = [
            ("Çalışkan", "Tembel"),
            ("İyimser", "Karamsar"),
            ("Sabırlı", "Sabırsız"),
            ("Cömert", "Kıskanç"),
            ("Merhametli", "Merhametsiz"),
            ("Mantıklı", "Duygusal"),
            ("Güvenilir", "Kurnaz"),
            ("Sinirli", "Soğukkanlı"),
            ("Sinirli", "Esprili"),
            ("Yobaz", "Mantıklı"),
            ("Yobaz", "Meraklı"),
            ("İnatçı", "Sabırlı"),
            ("Tembel", "Hırslı"),
        ]
        
        # Kişilik özelliklerine göre etkileşim modifikatörleri
        self.trait_modifiers = {
            # Sohbet başlatma şansını etkileyen özellikler
            "chat_chance": {
                "Karizmatik": 0.15,  # Karizmatik köylüler daha fazla sohbet başlatır
                "Esprili": 0.10,
                "İlgisiz": -0.03,
                "Sinirli": -0.05,
                "Romantik": 0.08,
                "Merhametli": 0.05,
                "Yobaz": -0.02,
                "Kıskanç": 0.03,
                "Duygusal": 0.07,
                "Soğukkanlı": -0.03,
                "İlgisiz": -0.10
            },
            
            # İlişki puanı değişimini etkileyen özellikler
            "relationship_change": {
                "Karizmatik": 2,
                "Esprili": 2,
                "Sinirli": -2,
                "Romantik": 3,
                "Merhametli": 2,
                "Yobaz": -1,
                "Kıskanç": -2,
                "Merhametsiz": -3,
                "Duygusal": 1,
                "Güvenilir": 2,
                "Cömert": 2,
                "İlgisiz": -1
            }
        }
        
        # Konuşma konuları ve olasılıkları
        self.chat_topics = {
            "meslek": 0.25,
            "hava": 0.10,
            "dedikodu": 0.15,
            "şaka": 0.10,
            "ilişki": 0.15,
            "felsefe": 0.05,
            "yemek": 0.10,
            "ev": 0.10
        }
        
        # Kişilik özelliklerine göre tercih edilen konular
        self.trait_topic_preferences = {
            "Karizmatik": ["ilişki", "dedikodu"],
            "Esprili": ["şaka", "dedikodu"],
            "Sinirli": ["meslek", "hava"],
            "Romantik": ["ilişki", "felsefe"],
            "Merhametli": ["ilişki", "yemek"],
            "Yobaz": ["felsefe", "dedikodu"],
            "Kıskanç": ["dedikodu", "ilişki"],
            "Merhametsiz": ["meslek", "dedikodu"],
            "Duygusal": ["ilişki", "felsefe"],
            "Güvenilir": ["meslek", "ev"],
            "Cömert": ["yemek", "ev"],
            "İlgisiz": ["meslek", "hava"],
            "Tembel": ["yemek", "hava"],
            "Çalışkan": ["meslek", "ev"],
            "Hırslı": ["meslek", "ev"],
            "Sabırlı": ["felsefe", "meslek"],
            "İnatçı": ["meslek", "dedikodu"],
            "Kurnaz": ["dedikodu", "ilişki"],
            "Meraklı": ["dedikodu", "felsefe"],
            "Dikkatli": ["meslek", "hava"],
            "Sabırsız": ["meslek", "yemek"],
            "İyimser": ["şaka", "ilişki"],
            "Karamsar": ["hava", "meslek"],
            "Pratik": ["meslek", "ev"],
            "Mantıklı": ["meslek", "felsefe"],
            "Soğukkanlı": ["meslek", "hava"],
            "Babacan": ["ilişki", "yemek"],
            "Uykucu": ["yemek", "hava"]
        }
        
        # Son etkileşim zamanlarını takip etmek için sözlük
        self.last_chat_time = {}  # {villager_name: timestamp}
        self.last_decision_time = {}  # {villager_name: timestamp}
    
    def are_traits_compatible(self, traits1, traits2):
        """İki köylünün özellikleri arasındaki uyumu kontrol eder"""
        compatibility_score = 0
        
        # Uyumlu özellik çiftleri için puan ekle
        for trait1 in traits1:
            for trait2 in traits2:
                # Aynı gruptan özelliklere +1
                for group in ["positive", "negative", "neutral"]:
                    if trait1 in self.trait_compatibility_groups[group] and trait2 in self.trait_compatibility_groups[group]:
                        compatibility_score += 1
                
                # Özellikle uyumlu çiftlere +2
                if (trait1, trait2) in self.compatible_trait_pairs or (trait2, trait1) in self.compatible_trait_pairs:
                    compatibility_score += 2
                
                # Uyumsuz çiftlere -3
                if (trait1, trait2) in self.incompatible_trait_pairs or (trait2, trait1) in self.incompatible_trait_pairs:
                    compatibility_score -= 3
        
        return compatibility_score
        
    def should_initiate_chat(self, villager, potential_partners):
        """Köylünün sohbet başlatıp başlatmayacağını belirler"""
        # Gece ise sohbet başlatma
        if hasattr(villager, 'game_controller') and not villager.game_controller.is_daytime:
            return False, None
        
        # Zaten sohbet ediyorsa yeni sohbet başlatma
        if villager.is_chatting:
            return False, None
        
        # Sohbet bekleme süresi kontrolü
        current_time = time.time()
        if villager.name in self.last_chat_time:
            time_since_last_chat = current_time - self.last_chat_time[villager.name]
            if time_since_last_chat < self.chat_cooldown:
                return False, None
        
        # Temel sohbet şansını hesapla
        chat_chance = self.base_chat_chance
        
        # Kişilik özelliklerine göre şansı ayarla
        for trait in villager.traits:
            if trait in self.trait_modifiers["chat_chance"]:
                chat_chance += self.trait_modifiers["chat_chance"][trait]
        
        # Şans kontrolü
        if random.random() > chat_chance:
            return False, None
        
        # Potansiyel sohbet partnerleri arasından seçim yap
        available_partners = []
        
        for partner in potential_partners:
            # Kendisiyle sohbet etme
            if partner == villager:
                continue
            
            # Zaten sohbet eden köylülerle sohbet başlatma
            if partner.is_chatting:
                continue
            
            # Mesafe kontrolü - yakın köylüler arasında sohbet başlatma şansı
            # Mesafe sınırını 100 pikselden 200 piksele çıkarıyoruz
            distance = abs(villager.x - partner.x)
            if distance < 200:  # 200 piksel mesafe içinde
                # İlişki puanına göre sohbet şansını ayarla
                relationship = villager.get_relationship_with(partner.name)
                partner_weight = 1.0
                
                # İlişki puanı yüksekse daha fazla sohbet şansı
                if relationship > 70:
                    partner_weight = 2.0
                elif relationship < 30:
                    partner_weight = 0.5
                
                # Karşı cins ise ve romantik özelliği varsa ek şans
                if villager.gender != partner.gender and "Romantik" in villager.traits:
                    partner_weight *= 1.5
                
                # Aynı meslek grubundaysa ek şans
                if villager.profession == partner.profession:
                    partner_weight *= 1.2
                
                # Karakteristik özelliklerin uyumu
                trait_compatibility = self.are_traits_compatible(villager.traits, partner.traits)
                if trait_compatibility > 0:
                    partner_weight *= (1.0 + 0.1 * trait_compatibility)
                elif trait_compatibility < 0:
                    partner_weight *= max(0.1, 1.0 + 0.1 * trait_compatibility)
                
                # Partneri listeye ekle
                available_partners.append((partner, partner_weight))
        
        # Eğer potansiyel partner yoksa sohbet başlatma
        if not available_partners:
            return False, None
        
        # Ağırlıklı rastgele seçim yap
        total_weight = sum(weight for _, weight in available_partners)
        if total_weight <= 0:
            return False, None
            
        random_value = random.uniform(0, total_weight)
        current_weight = 0
        
        for partner, weight in available_partners:
            current_weight += weight
            if random_value <= current_weight:
                # Sohbet zamanını güncelle
                self.last_chat_time[villager.name] = current_time
                return True, partner
        
        return False, None
    
    def get_chat_topic(self, villager):
        """Köylünün konuşacağı konuyu belirler"""
        try:
            # Kişilik özelliklerine göre tercih edilen konuları al
            preferred_topics = []
            
            # Köylünün özelliklerine göre konuları ağırlıklandır
            topic_weights = {
                "selamlaşma": 0.05,  # Selamlaşma genelde başlangıçta kullanılır
                "günlük": 0.15,
                "meslek": 0.15,
                "hava": 0.10,
                "dedikodu": 0.10,
                "şaka": 0.10,
                "ilişki": 0.10,
                "felsefe": 0.05,
                "yemek": 0.10,
                "ev": 0.10
            }
            
            # Mesleğe göre ağırlıkları ayarla
            if villager.profession == "Oduncu":
                topic_weights["meslek"] += 0.1
                topic_weights["ev"] += 0.05
            elif villager.profession == "İnşaatçı":
                topic_weights["ev"] += 0.15
                topic_weights["meslek"] += 0.05
            elif villager.profession == "Avcı":
                topic_weights["meslek"] += 0.1
                topic_weights["yemek"] += 0.05
            elif villager.profession == "Gardiyan":
                topic_weights["dedikodu"] += 0.1
                topic_weights["meslek"] += 0.05
            elif villager.profession == "Papaz":
                topic_weights["felsefe"] += 0.15
                topic_weights["ilişki"] += 0.05
            
            # Kişilik özelliklerine göre ağırlıkları ayarla
            for trait in villager.traits:
                if trait in self.trait_topic_preferences:
                    for topic in self.trait_topic_preferences[trait]:
                        topic_weights[topic] = topic_weights.get(topic, 0) + 0.05
                        preferred_topics.append(topic)
            
            # Eğer sohbet partneri varsa, ilişki seviyesine göre konuları ayarla
            if hasattr(villager, 'chat_partner') and villager.chat_partner:
                partner = villager.chat_partner
                relationship = villager.get_relationship_with(partner.name)
                
                # Yakın ilişki (70+)
                if relationship > 70:
                    topic_weights["ilişki"] += 0.1
                    topic_weights["dedikodu"] += 0.05
                    topic_weights["şaka"] += 0.05
                    
                    # Karşı cins ise ve romantik özelliği varsa
                    if villager.gender != partner.gender and "Romantik" in villager.traits:
                        topic_weights["ilişki"] += 0.15
                
                # Orta ilişki (30-70)
                elif 30 <= relationship <= 70:
                    topic_weights["günlük"] += 0.05
                    topic_weights["hava"] += 0.05
                    topic_weights["meslek"] += 0.05
                
                # Uzak ilişki (30-)
                else:
                    topic_weights["hava"] += 0.1
                    topic_weights["günlük"] += 0.05
                    topic_weights["ilişki"] -= 0.05  # İlişki konusu daha az olasılıklı
            
            # Gündüz/gece durumuna göre konuları ayarla
            if hasattr(villager, 'is_daytime') and not villager.is_daytime:
                # Gece vakti daha derin konular
                topic_weights["felsefe"] += 0.1
                topic_weights["ilişki"] += 0.05
                topic_weights["hava"] -= 0.05
            
            # Ağırlıklara göre konu seç
            topics = list(topic_weights.keys())
            weights = [max(0.01, topic_weights[t]) for t in topics]  # Minimum 0.01 ağırlık
            
            # Ağırlıklı rastgele seçim
            selected_topic = random.choices(topics, weights=weights, k=1)[0]
            
            return selected_topic
            
        except Exception as e:
            print(f"HATA: Sohbet konusu belirleme hatası: {e}")
            import traceback
            traceback.print_exc()
            return "günlük"  # Hata durumunda varsayılan konu
    
    def calculate_relationship_change(self, villager1, villager2):
        """İki köylü arasındaki ilişki değişimini hesaplar"""
        # Temel ilişki değişimi
        base_change = random.randint(1, 3)  # 1-3 arası pozitif değişim
        
        # Kişilik özelliklerine göre değişimi ayarla
        for trait in villager1.traits:
            if trait in self.trait_modifiers["relationship_change"]:
                base_change += self.trait_modifiers["relationship_change"][trait]
        
        # Karşı tarafın özelliklerine göre değişimi ayarla
        for trait in villager2.traits:
            if trait in self.trait_modifiers["relationship_change"]:
                base_change += self.trait_modifiers["relationship_change"][trait] // 2  # Yarı etki
        
        # Rastgele negatif etkileşim şansı
        if random.random() < 0.15:  # %15 şans
            base_change = -base_change
            
        # Özelliklerin uyumu
        trait_compatibility = self.are_traits_compatible(villager1.traits, villager2.traits)
        base_change += trait_compatibility
        
        # Birbiriyle zıt olan ve anlaşamayan özellikler için ekstra negatif etki
        for trait1 in villager1.traits:
            for trait2 in villager2.traits:
                if (trait1, trait2) in self.incompatible_trait_pairs or (trait2, trait1) in self.incompatible_trait_pairs:
                    # Zıt özellikler için daha büyük bir negatif etki
                    base_change -= 1
                    # Anlaşmazlık şansını arttır
                    if random.random() < 0.3:  # %30 şans ile ek negatif etki
                        base_change -= 1
        
        # Benzer özelliklere sahip köylüler arasında ek pozitif etki
        for trait in villager1.traits:
            if trait in villager2.traits:
                base_change += 1
                # Anlaşma şansını arttır
                if random.random() < 0.3:  # %30 şans ile ek pozitif etki
                    base_change += 1
        
        return base_change
    
    def make_decision(self, villager):
        """Köylünün bir sonraki kararını belirler"""
        # Karar bekleme süresi kontrolü
        current_time = time.time()
        if villager.name in self.last_decision_time:
            time_since_last_decision = current_time - self.last_decision_time[villager.name]
            if time_since_last_decision < self.decision_cooldown:
                return None
        
        # Kararı güncelle
        self.last_decision_time[villager.name] = current_time
        
        # Köylünün mesleğine göre kararlar
        if villager.profession == "Oduncu":
            # Oduncu kararları
            if random.random() < 0.7:  # %70 şans
                return "odun_kes"
            else:
                return "dolaş"
                
        elif villager.profession == "İnşaatçı":
            # İnşaatçı kararları
            if hasattr(villager, 'game_controller') and villager.game_controller:
                # Kale envanterinde yeterli odun varsa ev inşa et
                castle = villager.game_controller.castle
                if castle and hasattr(castle, 'get_inventory'):
                    inventory = castle.get_inventory()
                    if inventory.get("odun", 0) >= 20:  # 20 odun gerekiyor
                        return "ev_inşa_et"
            
            return "dolaş"
            
        elif villager.profession == "Avcı":
            # Avcı kararları
            if random.random() < 0.8:  # %80 şans
                return "avlan"
            else:
                return "dolaş"
                
        elif villager.profession == "Gardiyan":
            # Gardiyan kararları
            return "devriye_gez"
            
        elif villager.profession == "Papaz":
            # Papaz kararları
            return "dua_et"
            
        else:
            # Diğer meslekler veya işsizler
            return "dolaş" 