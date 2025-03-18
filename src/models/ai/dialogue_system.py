import random
import time
from enum import Enum
from typing import List, Dict, Optional, Any, Callable
from src.models.ai.behavior_tree import NodeStatus, BehaviorNode, ActionNode, ConditionNode

class DialogueType(Enum):
    """Diyalog türleri"""
    GREETING = 1       # Selamlaşma
    WEATHER = 2        # Hava durumu
    WORK = 3           # İş hakkında
    GOSSIP = 4         # Dedikodu
    PERSONAL = 5       # Kişisel konular
    COMPLAINT = 6      # Şikayet
    COMPLIMENT = 7     # İltifat
    JOKE = 8           # Şaka
    FAREWELL = 9       # Vedalaşma
    RANDOM = 10        # Rastgele konuşma
    RELATIONSHIP = 11  # İlişki hakkında

class EmotionType(Enum):
    """Duygu türleri"""
    HAPPY = 1          # Mutlu
    SAD = 2            # Üzgün
    ANGRY = 3          # Kızgın
    NEUTRAL = 4        # Nötr
    SURPRISED = 5      # Şaşkın
    AFRAID = 6         # Korkmuş
    EXCITED = 7        # Heyecanlı

class DialogueNode:
    """Bir diyalog cümlesi düğümü"""
    def __init__(self, 
                 text: str,
                 dialogue_type: DialogueType,
                 emotion: EmotionType = EmotionType.NEUTRAL,
                 min_relationship: int = 0,
                 condition: Callable = None,
                 next_nodes: List['DialogueNode'] = None):
        self.text = text  # Diyalog metni
        self.dialogue_type = dialogue_type  # Diyalog türü
        self.emotion = emotion  # Duygusal durum
        self.min_relationship = min_relationship  # Minimum ilişki puanı
        self.condition = condition  # Ek koşul fonksiyonu
        self.next_nodes = next_nodes or []  # Sonraki diyalog düğümleri
    
    def can_use(self, villager, partner) -> bool:
        """Bu diyalog düğümünün kullanılabilir olup olmadığını kontrol eder"""
        # İlişki puanı kontrolü
        relationship_points = villager.relationship_points.get(partner.name, 0)
        if relationship_points < self.min_relationship:
            return False
        
        # Ek koşul kontrolü
        if self.condition and not self.condition(villager, partner):
            return False
        
        return True
    
    def add_next(self, node: 'DialogueNode') -> 'DialogueNode':
        """Sonraki diyalog düğümünü ekler"""
        self.next_nodes.append(node)
        return node

class DialogueTopic:
    """Bir konuşma konusu (örn. hava durumu, meslek, günlük)"""
    def __init__(self, 
                 name: str, 
                 dialogue_type: DialogueType,
                 root_nodes: List[DialogueNode] = None,
                 condition: Callable = None,
                 min_relationship: int = 0,
                 max_relationship: int = 100,
                 priority: int = 1):
        self.name = name  # Konu adı
        self.dialogue_type = dialogue_type  # Diyalog türü
        self.root_nodes = root_nodes or []  # Kök diyalog düğümleri
        self.condition = condition  # Ek koşul fonksiyonu
        self.min_relationship = min_relationship  # Minimum ilişki puanı
        self.max_relationship = max_relationship  # Maksimum ilişki puanı
        self.priority = priority  # Öncelik (yüksek sayı = yüksek öncelik)
    
    def can_use(self, villager, partner) -> bool:
        """Bu konunun kullanılabilir olup olmadığını kontrol eder"""
        # İlişki puanı kontrolü
        relationship_points = villager.relationship_points.get(partner.name, 0)
        if relationship_points < self.min_relationship or relationship_points > self.max_relationship:
            return False
        
        # Ek koşul kontrolü
        if self.condition and not self.condition(villager, partner):
            return False
        
        return True
    
    def get_random_root_node(self, villager, partner) -> Optional[DialogueNode]:
        """Kullanılabilir rastgele bir kök diyalog düğümü döndürür"""
        available_nodes = [node for node in self.root_nodes if node.can_use(villager, partner)]
        if not available_nodes:
            return None
        
        return random.choice(available_nodes)
    
    def add_root_node(self, node: DialogueNode) -> DialogueNode:
        """Kök diyalog düğümü ekler"""
        self.root_nodes.append(node)
        return node

class DialogueManager:
    """Diyalogları yönetir"""
    def __init__(self):
        self.topics: Dict[str, DialogueTopic] = {}
        self.create_default_topics()
    
    def create_default_topics(self):
        """Varsayılan konuları oluşturur"""
        # Selamlaşma konusu
        greeting_topic = DialogueTopic("Selamlaşma", DialogueType.GREETING, priority=10)
        self.add_topic(greeting_topic)
        
        # Sabah selamlaşması
        good_morning = DialogueNode("Günaydın! Bugün nasılsın?", DialogueType.GREETING, EmotionType.HAPPY)
        greeting_topic.add_root_node(good_morning)
        
        good_morning_response1 = DialogueNode("İyiyim, teşekkür ederim. Sen nasılsın?", DialogueType.GREETING, EmotionType.HAPPY)
        good_morning.add_next(good_morning_response1)
        
        good_morning_response2 = DialogueNode("Çok yorgunum, iyi uyuyamadım.", DialogueType.GREETING, EmotionType.SAD)
        good_morning.add_next(good_morning_response2)
        
        # Akşam selamlaşması
        good_evening = DialogueNode("İyi akşamlar! Günün nasıl geçti?", DialogueType.GREETING, EmotionType.NEUTRAL)
        greeting_topic.add_root_node(good_evening)
        
        good_evening_response1 = DialogueNode("Harika bir gündü, çok iş başardım.", DialogueType.GREETING, EmotionType.EXCITED)
        good_evening.add_next(good_evening_response1)
        
        good_evening_response2 = DialogueNode("Çok yorucu bir gündü, dinlenmem gerek.", DialogueType.GREETING, EmotionType.TIRED)
        good_evening.add_next(good_evening_response2)
        
        # Hava durumu konusu
        weather_topic = DialogueTopic("Hava Durumu", DialogueType.WEATHER, priority=5)
        self.add_topic(weather_topic)
        
        # Güzel hava
        nice_weather = DialogueNode("Bugün hava çok güzel, değil mi?", DialogueType.WEATHER, EmotionType.HAPPY)
        weather_topic.add_root_node(nice_weather)
        
        nice_weather_response1 = DialogueNode("Evet, böyle güneşli günleri seviyorum.", DialogueType.WEATHER, EmotionType.HAPPY)
        nice_weather.add_next(nice_weather_response1)
        
        nice_weather_response2 = DialogueNode("Biraz fazla sıcak, gölgede kalmayı tercih ederim.", DialogueType.WEATHER, EmotionType.NEUTRAL)
        nice_weather.add_next(nice_weather_response2)
        
        # Kötü hava
        bad_weather = DialogueNode("Bu yağmur hiç kesilmeyecek gibi duruyor.", DialogueType.WEATHER, EmotionType.SAD)
        weather_topic.add_root_node(bad_weather)
        
        bad_weather_response1 = DialogueNode("Evet, ekinlerimiz için iyi olsa da işlerimizi zorlaştırıyor.", DialogueType.WEATHER, EmotionType.NEUTRAL)
        bad_weather.add_next(bad_weather_response1)
        
        bad_weather_response2 = DialogueNode("Ben yağmurlu havaları severim, huzur verici buluyorum.", DialogueType.WEATHER, EmotionType.HAPPY)
        bad_weather.add_next(bad_weather_response2)
        
        # İş konusu
        work_topic = DialogueTopic("İş Hakkında", DialogueType.WORK, priority=7)
        self.add_topic(work_topic)
        
        # Oduncu için
        woodcutter_talk = DialogueNode("Bugün kaç ağaç kestin?", DialogueType.WORK, EmotionType.NEUTRAL, 
                                      condition=lambda v, p: p.profession == "Oduncu")
        work_topic.add_root_node(woodcutter_talk)
        
        woodcutter_response1 = DialogueNode("Birkaç tane. Bugün biraz yavaş ilerliyorum.", DialogueType.WORK, EmotionType.NEUTRAL)
        woodcutter_talk.add_next(woodcutter_response1)
        
        woodcutter_response2 = DialogueNode("Çok fazla! Baltam neredeyse körelmek üzere.", DialogueType.WORK, EmotionType.EXCITED)
        woodcutter_talk.add_next(woodcutter_response2)
        
        # İnşaatçı için
        builder_talk = DialogueNode("Yeni ev inşaatı nasıl gidiyor?", DialogueType.WORK, EmotionType.NEUTRAL, 
                                   condition=lambda v, p: p.profession == "İnşaatçı")
        work_topic.add_root_node(builder_talk)
        
        builder_response1 = DialogueNode("İyi gidiyor, yakında bitecek.", DialogueType.WORK, EmotionType.HAPPY)
        builder_talk.add_next(builder_response1)
        
        builder_response2 = DialogueNode("Malzeme eksikliği yaşıyoruz, daha fazla oduna ihtiyacımız var.", DialogueType.WORK, EmotionType.WORRIED)
        builder_talk.add_next(builder_response2)
        
        # ... diğer meslekler için diyaloglar eklenebilir
        
        # Dedikodu konusu (ilişki puanı 30'dan fazla olanlar için)
        gossip_topic = DialogueTopic("Dedikodu", DialogueType.GOSSIP, min_relationship=30, priority=6)
        self.add_topic(gossip_topic)
        
        # Diğer köylüler hakkında dedikodu
        gossip_talk = DialogueNode("Duydun mu? Ahmet ve Ayşe çok yakınlaşmışlar son zamanlarda.", DialogueType.GOSSIP, EmotionType.EXCITED)
        gossip_topic.add_root_node(gossip_talk)
        
        gossip_response1 = DialogueNode("Gerçekten mi? Bu çok ilginç!", DialogueType.GOSSIP, EmotionType.SURPRISED)
        gossip_talk.add_next(gossip_response1)
        
        gossip_response2 = DialogueNode("Başkalarının işine burnumuzu sokmamalıyız.", DialogueType.GOSSIP, EmotionType.NEUTRAL)
        gossip_talk.add_next(gossip_response2)
    
    def add_topic(self, topic: DialogueTopic):
        """Yeni bir konu ekler"""
        self.topics[topic.name] = topic
    
    def get_available_topics(self, villager, partner) -> List[DialogueTopic]:
        """İki köylü arasında kullanılabilir konuları döndürür"""
        return [topic for topic in self.topics.values() if topic.can_use(villager, partner)]
    
    def get_topic_by_type(self, dialogue_type: DialogueType) -> Optional[DialogueTopic]:
        """Belirli türdeki bir konuyu döndürür"""
        for topic in self.topics.values():
            if topic.dialogue_type == dialogue_type:
                return topic
        return None
    
    def select_topic(self, villager, partner) -> Optional[DialogueTopic]:
        """İki köylü arasında bir konuşma konusu seçer"""
        available_topics = self.get_available_topics(villager, partner)
        if not available_topics:
            return None
        
        # Önceliğe göre sırala (en yüksek öncelik ilk)
        available_topics.sort(key=lambda x: x.priority, reverse=True)
        
        # %60 olasılıkla en yüksek öncelikli konuyu seç
        # %40 olasılıkla rastgele bir konu seç
        if random.random() < 0.6 and available_topics:
            return available_topics[0]
        else:
            return random.choice(available_topics)
    
    def start_dialogue(self, initiator, partner) -> Optional[DialogueNode]:
        """İki köylü arasında diyalog başlatır"""
        selected_topic = self.select_topic(initiator, partner)
        if not selected_topic:
            return None
        
        # Konunun kök düğümlerinden birini seç
        root_node = selected_topic.get_random_root_node(initiator, partner)
        if not root_node:
            return None
        
        # Seçilen kök düğümü döndür
        return root_node
    
    def get_response(self, dialogue_node: DialogueNode, responder, initiator) -> Optional[DialogueNode]:
        """Verilen diyalog düğümüne cevap diyalog düğümünü döndürür"""
        if not dialogue_node.next_nodes:
            # Cevap yoksa, yeni bir konuşma başlat
            return self.start_dialogue(responder, initiator)
        
        # Kullanılabilir cevapları filtrele
        available_responses = [node for node in dialogue_node.next_nodes if node.can_use(responder, initiator)]
        if not available_responses:
            # Kullanılabilir cevap yoksa, yeni bir konuşma başlat
            return self.start_dialogue(responder, initiator)
        
        # Rastgele bir cevap seç
        return random.choice(available_responses)

class DialogueAction(ActionNode):
    """Diyalog eylemi için davranış ağacı düğümü"""
    def __init__(self, name: str, dialogue_manager: DialogueManager):
        super().__init__(name, self._execute_dialogue)
        self.dialogue_manager = dialogue_manager
    
    def _execute_dialogue(self, villager, dt: float) -> NodeStatus:
        # Köylünün konuşma durumunu kontrol et
        if not hasattr(villager, 'is_chatting') or not villager.is_chatting:
            return NodeStatus.FAILURE
        
        # Konuşma partnerini kontrol et
        if not hasattr(villager, 'chat_partner') or not villager.chat_partner:
            return NodeStatus.FAILURE
        
        # Konuşma süresini kontrol et
        if not hasattr(villager, 'chat_time'):
            villager.chat_time = 0
        
        if not hasattr(villager, 'chat_duration'):
            villager.chat_duration = random.uniform(15, 30)  # 15-30 saniye arası konuşma
        
        villager.chat_time += dt
        
        # Konuşma süresi dolduysa
        if villager.chat_time >= villager.chat_duration:
            if hasattr(villager, 'end_chat'):
                villager.end_chat()
            return NodeStatus.SUCCESS
        
        # Son mesaj zamanını kontrol et
        if not hasattr(villager, 'last_message_time'):
            villager.last_message_time = 0
        
        # 2 saniye aralıkla konuşma
        if villager.chat_time - villager.last_message_time >= 2.0:
            # Sohbet başlatma veya devam ettirme durumunu kontrol et
            is_initiator = hasattr(villager, 'is_chat_initiator') and villager.is_chat_initiator
            
            # Aktif diyalog düğümünü kontrol et
            current_dialogue = BlackboardNode.get_data(villager, 'current_dialogue')
            
            if current_dialogue is None and is_initiator:
                # Yeni bir diyalog başlat
                new_dialogue = self.dialogue_manager.start_dialogue(villager, villager.chat_partner)
                if new_dialogue:
                    BlackboardNode.set_data(villager, 'current_dialogue', new_dialogue)
                    # Diyalog metnini baloncuk içinde göster
                    villager.show_chat_message(new_dialogue.text)
                    villager.last_message_time = villager.chat_time
            elif not is_initiator:
                # Partner cevap versin
                partner_dialogue = BlackboardNode.get_data(villager.chat_partner, 'current_dialogue')
                if partner_dialogue:
                    response = self.dialogue_manager.get_response(partner_dialogue, villager, villager.chat_partner)
                    if response:
                        BlackboardNode.set_data(villager, 'current_dialogue', response)
                        # Diyalog metnini baloncuk içinde göster
                        villager.show_chat_message(response.text)
                        villager.last_message_time = villager.chat_time
        
        return NodeStatus.RUNNING

# Diyalog ağacı örnekleri için yardımcı fonksiyonlar
def create_dialogue_system():
    """Diyalog sistemini oluşturur ve varsayılan diyaloglarla doldurur"""
    return DialogueManager()

def create_chat_behavior_tree(villager):
    """Köylünün sohbet davranış ağacını oluşturur"""
    from src.models.ai.behavior_tree import SequenceNode, ConditionNode, ActionNode, SelectorNode
    
    # Diyalog yöneticisini oluştur
    if not hasattr(villager, 'dialogue_manager'):
        villager.dialogue_manager = create_dialogue_system()
    
    # Sohbet davranış ağacını oluştur
    chat_tree = SequenceNode("Sohbet Davranışı")
    
    # Sohbet ediyor mu kontrolü
    is_chatting = ConditionNode("Sohbet Ediyor mu?", 
                              lambda v, dt: hasattr(v, 'is_chatting') and v.is_chatting and hasattr(v, 'chat_partner') and v.chat_partner)
    chat_tree.add_child(is_chatting)
    
    # Diyalog eylemi
    dialogue_action = DialogueAction("Diyalog Eylemi", villager.dialogue_manager)
    chat_tree.add_child(dialogue_action)
    
    return chat_tree 