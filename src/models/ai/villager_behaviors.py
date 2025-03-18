from src.models.ai.behavior_tree import (
    NodeStatus, BehaviorNode, SequenceNode, SelectorNode, 
    ActionNode, ConditionNode, InverterNode, DelayNode,
    BlackboardNode, RandomSelectorNode
)
import random
import time
from PyQt5.QtCore import QTimer

# Köylü durumları için sabitler
IDLE = "Boşta"
WANDERING = "Dolaşıyor"
WORKING = "Çalışıyor"
CHATTING = "Sohbet Ediyor"
RESTING = "Dinleniyor"
SLEEPING = "Uyuyor"
GOING_HOME = "Eve Gidiyor"

def create_villager_behavior_tree(villager):
    """Köylü için ana davranış ağacını oluşturur"""
    # Ana seçici düğüm (en üst düzey karar verici)
    root = SelectorNode("Ana Davranış Seçici")
    
    # 1. Temel sohbet davranışı (basitleştirildi)
    chat_behavior = create_chat_behavior(villager)
    root.add_child(chat_behavior)
    
    # 2. Gece olduğunda eve gitme davranışı
    going_home_behavior = create_going_home_behavior(villager)
    root.add_child(going_home_behavior)
    
    # 3. Meslekle ilgili davranışlar
    profession_behavior = create_profession_behavior(villager)
    root.add_child(profession_behavior)
    
    # 4. Boş zaman davranışları (en düşük öncelik)
    idle_behavior = create_idle_behavior(villager)
    root.add_child(idle_behavior)
    
    return root

def create_chat_behavior(villager):
    """Köylü için basit sohbet davranışını oluşturur"""
    # Sohbet sekansı
    chat_sequence = SequenceNode("Sohbet Sekansı")
    
    # Sohbet ediyor mu kontrolü
    is_chatting = ConditionNode("Sohbet Ediyor mu?", 
                              lambda v, dt: hasattr(v, 'is_chatting') and v.is_chatting and
                                           hasattr(v, 'chat_partner') and v.chat_partner)
    chat_sequence.add_child(is_chatting)
    
    # Durum güncelleme eylemi
    update_state = ActionNode("Sohbet Durumu Güncelle", 
                            lambda v, dt: update_villager_state(v, CHATTING))
    chat_sequence.add_child(update_state)
    
    # Basit kalma eylemi - diyalog sistemi yerine basit bir bekleme ekliyoruz
    stay_in_place = ActionNode("Sohbet Sırasında Yerinde Kal", 
                            lambda v, dt: NodeStatus.RUNNING)
    chat_sequence.add_child(stay_in_place)
    
    return chat_sequence

def create_going_home_behavior(villager):
    """Köylü için eve gitme davranışını oluşturur"""
    # Eve gitme sekansı
    going_home_sequence = SequenceNode("Eve Gitme Sekansı")
    
    # Gece mi kontrolü
    is_night = ConditionNode("Gece mi?", 
                           lambda v, dt: hasattr(v, 'game_controller') and 
                                        not v.game_controller.is_daytime)
    going_home_sequence.add_child(is_night)
    
    # Eve gidiyor mu kontrolü (eğer zaten eve gidiyorsa tekrar başlatma)
    not_going_home = InverterNode("Eve Gidiyor mu?")
    is_already_going_home = ConditionNode("Zaten Eve Gidiyor mu?", 
                                       lambda v, dt: hasattr(v, 'state') and v.state == GOING_HOME)
    not_going_home.add_child(is_already_going_home)
    going_home_sequence.add_child(not_going_home)
    
    # Eve gitme eylemi
    go_home_action = ActionNode("Eve Git", 
                              lambda v, dt: start_going_home(v))
    going_home_sequence.add_child(go_home_action)
    
    return going_home_sequence

def create_profession_behavior(villager):
    """Köylü için mesleğe özel davranışları oluşturur"""
    # Meslek sekansı
    profession_sequence = SequenceNode("Meslek Sekansı")
    
    # Gündüz mü kontrolü
    is_day = ConditionNode("Gündüz mü?", 
                         lambda v, dt: hasattr(v, 'game_controller') and 
                                      v.game_controller.is_daytime)
    profession_sequence.add_child(is_day)
    
    # Meslek seçici
    profession_selector = SelectorNode("Meslek Seçici")
    
    # Oduncu davranışı
    woodcutter_sequence = SequenceNode("Oduncu Davranışı")
    is_woodcutter = ConditionNode("Oduncu mu?", 
                                lambda v, dt: hasattr(v, 'profession') and 
                                             v.profession == "Oduncu")
    woodcutter_sequence.add_child(is_woodcutter)
    
    # Günlük ağaç kesme limiti dolmamış mı?
    tree_limit_not_reached = ConditionNode("Ağaç Limiti Dolmadı mı?", 
                                         lambda v, dt: hasattr(v, 'trees_cut_today') and 
                                                      hasattr(v, 'max_trees_per_day') and
                                                      v.trees_cut_today < v.max_trees_per_day)
    woodcutter_sequence.add_child(tree_limit_not_reached)
    
    # Oduncu işini yap
    woodcutter_action = ActionNode("Oduncu İşi Yap", 
                                 lambda v, dt: handle_woodcutter_job(v))
    woodcutter_sequence.add_child(woodcutter_action)
    
    # İnşaatçı davranışı
    builder_sequence = SequenceNode("İnşaatçı Davranışı")
    is_builder = ConditionNode("İnşaatçı mı?", 
                             lambda v, dt: hasattr(v, 'profession') and 
                                          v.profession == "İnşaatçı")
    builder_sequence.add_child(is_builder)
    
    # Günlük bina inşa limiti dolmamış mı?
    building_limit_not_reached = ConditionNode("İnşaat Limiti Dolmadı mı?", 
                                            lambda v, dt: hasattr(v, 'buildings_built') and 
                                                         hasattr(v, 'max_buildings_per_day') and
                                                         v.buildings_built < v.max_buildings_per_day)
    builder_sequence.add_child(building_limit_not_reached)
    
    # İnşaatçı işini yap
    builder_action = ActionNode("İnşaatçı İşi Yap", 
                              lambda v, dt: handle_builder_job(v))
    builder_sequence.add_child(builder_action)
    
    # Avcı davranışı
    hunter_sequence = SequenceNode("Avcı Davranışı")
    is_hunter = ConditionNode("Avcı mı?", 
                            lambda v, dt: hasattr(v, 'profession') and 
                                         v.profession == "Avcı")
    hunter_sequence.add_child(is_hunter)
    
    # Günlük avlanma limiti dolmamış mı?
    hunting_limit_not_reached = ConditionNode("Avlanma Limiti Dolmadı mı?", 
                                           lambda v, dt: hasattr(v, 'animals_hunted') and 
                                                        hasattr(v, 'max_hunts_per_day') and
                                                        v.animals_hunted < v.max_hunts_per_day)
    hunter_sequence.add_child(hunting_limit_not_reached)
    
    # Avcı işini yap
    hunter_action = ActionNode("Avcı İşi Yap", 
                             lambda v, dt: handle_hunter_job(v))
    hunter_sequence.add_child(hunter_action)
    
    # Çiftçi davranışı
    farmer_sequence = SequenceNode("Çiftçi Davranışı")
    is_farmer = ConditionNode("Çiftçi mi?", 
                            lambda v, dt: hasattr(v, 'profession') and 
                                         v.profession == "Çiftçi")
    farmer_sequence.add_child(is_farmer)
    
    # Günlük hasat limiti dolmamış mı?
    harvest_limit_not_reached = ConditionNode("Hasat Limiti Dolmadı mı?", 
                                           lambda v, dt: hasattr(v, 'crops_harvested') and 
                                                        hasattr(v, 'max_harvests_per_day') and
                                                        v.crops_harvested < v.max_harvests_per_day)
    farmer_sequence.add_child(harvest_limit_not_reached)
    
    # Çiftçi işini yap
    farmer_action = ActionNode("Çiftçi İşi Yap", 
                             lambda v, dt: handle_farmer_job(v))
    farmer_sequence.add_child(farmer_action)
    
    # Gardiyan davranışı
    guard_sequence = SequenceNode("Gardiyan Davranışı")
    is_guard = ConditionNode("Gardiyan mı?", 
                           lambda v, dt: hasattr(v, 'profession') and 
                                        v.profession == "Gardiyan")
    guard_sequence.add_child(is_guard)
    
    # Günlük devriye limiti dolmamış mı?
    patrol_limit_not_reached = ConditionNode("Devriye Limiti Dolmadı mı?", 
                                          lambda v, dt: hasattr(v, 'patrol_count') and 
                                                       hasattr(v, 'max_patrols_per_day') and
                                                       v.patrol_count < v.max_patrols_per_day)
    guard_sequence.add_child(patrol_limit_not_reached)
    
    # Gardiyan işini yap
    guard_action = ActionNode("Gardiyan İşi Yap", 
                            lambda v, dt: handle_guard_job(v))
    guard_sequence.add_child(guard_action)
    
    # Meslekleri seçiciye ekle
    profession_selector.add_child(woodcutter_sequence)
    profession_selector.add_child(builder_sequence)
    profession_selector.add_child(hunter_sequence)
    profession_selector.add_child(farmer_sequence)
    profession_selector.add_child(guard_sequence)
    
    # Meslek seçiciyi sekansa ekle
    profession_sequence.add_child(profession_selector)
    
    return profession_sequence

def create_idle_behavior(villager):
    """Köylü için boş zaman davranışlarını oluşturur"""
    # Boş zaman seçici
    idle_selector = SelectorNode("Boş Zaman Seçici")
    
    # Rastgele sohbet başlatma davranışı
    random_chat_sequence = SequenceNode("Rastgele Sohbet Başlatma")
    
    # Belirli bir olasılıkla (düşük) rastgele sohbet başlat
    random_chat_chance = ConditionNode("Sohbet Şansı", 
                                     lambda v, dt: random.random() < 0.05)  # %5 olasılık
    random_chat_sequence.add_child(random_chat_chance)
    
    # Yakında başka bir köylü var mı kontrol et
    nearby_villager_condition = ConditionNode("Yakında Köylü Var mı?", 
                                           lambda v, dt: find_nearby_villager(v) is not None)
    random_chat_sequence.add_child(nearby_villager_condition)
    
    # Sohbet başlat
    start_chat_action = ActionNode("Sohbet Başlat", 
                                 lambda v, dt: start_chat_with_nearby_villager(v))
    random_chat_sequence.add_child(start_chat_action)
    
    # Dolaşma davranışı
    wandering_sequence = SequenceNode("Dolaşma")
    
    # Dolaşma eylemi
    wander_action = ActionNode("Dolaş", 
                             lambda v, dt: handle_wandering(v))
    wandering_sequence.add_child(wander_action)
    
    # Boş zaman davranışlarını ekle
    idle_selector.add_child(random_chat_sequence)
    idle_selector.add_child(wandering_sequence)
    
    return idle_selector

# Davranış eylem fonksiyonları
def update_villager_state(villager, state):
    """Köylünün durumunu günceller"""
    if hasattr(villager, 'state'):
        villager.state = state
    return NodeStatus.SUCCESS

def start_going_home(villager):
    """Köylünün eve gitme sürecini başlatır"""
    try:
        if hasattr(villager, 'go_home'):
            villager.go_home()
            villager.state = GOING_HOME
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
    except Exception as e:
        print(f"HATA: {villager.name} eve gitme hatası: {e}")
        import traceback
        traceback.print_exc()
        return NodeStatus.FAILURE

def handle_woodcutter_job(villager):
    """Oduncu işi yap eylemi"""
    try:
        # Günlük kesim limitini kontrol et
        if hasattr(villager, 'trees_cut_today') and hasattr(villager, 'max_trees_per_day'):
            if villager.trees_cut_today >= villager.max_trees_per_day:
                # Limit doldu, dolaşmaya devam et
                if hasattr(villager, 'wander'):
                    villager.wander()
                    villager.state = "Günlük Kesim Limiti Doldu"
                return NodeStatus.SUCCESS
        
        # Oduncu işi yap
        if hasattr(villager, 'handle_woodcutter'):
            villager.handle_woodcutter()
            
            # Ağaç kesme durumunda animasyonu güncelle
            if hasattr(villager, 'update_animation'):
                villager.update_animation()
            
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
    except Exception as e:
        print(f"HATA: {villager.name} için oduncu işi yaparken hata: {e}")
        import traceback
        traceback.print_exc()
        return NodeStatus.FAILURE

def handle_builder_job(villager):
    """İnşaatçı işi yap eylemi"""
    try:
        # İnşaatçı işi yap
        if hasattr(villager, 'handle_builder'):
            villager.handle_builder()
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
    except Exception as e:
        print(f"HATA: {villager.name} için inşaatçı işi yaparken hata: {e}")
        import traceback
        traceback.print_exc()
        return NodeStatus.FAILURE

def handle_hunter_job(villager):
    """Avcı işi yap eylemi"""
    try:
        # Avcı işi yap
        if hasattr(villager, 'handle_hunter'):
            villager.handle_hunter()
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
    except Exception as e:
        print(f"HATA: {villager.name} için avcı işi yaparken hata: {e}")
        import traceback
        traceback.print_exc()
        return NodeStatus.FAILURE

def handle_farmer_job(villager):
    """Çiftçi işi yap eylemi"""
    try:
        # Çiftçi işi yap
        if hasattr(villager, 'handle_farmer'):
            villager.handle_farmer()
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
    except Exception as e:
        print(f"HATA: {villager.name} için çiftçi işi yaparken hata: {e}")
        import traceback
        traceback.print_exc()
        return NodeStatus.FAILURE

def handle_guard_job(villager):
    """Gardiyan işi yap eylemi"""
    try:
        # Gardiyan işi yap
        if hasattr(villager, 'handle_guard'):
            villager.handle_guard()
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
    except Exception as e:
        print(f"HATA: {villager.name} için gardiyan işi yaparken hata: {e}")
        import traceback
        traceback.print_exc()
        return NodeStatus.FAILURE

def handle_wandering(villager):
    """Dolaşma eylemi"""
    try:
        # Dolaş
        if hasattr(villager, 'wander'):
            villager.wander()
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
    except Exception as e:
        print(f"HATA: {villager.name} için dolaşma işlemi yaparken hata: {e}")
        import traceback
        traceback.print_exc()
        return NodeStatus.FAILURE

def find_nearby_villager(villager):
    """Yakındaki başka bir köylüyü bulur"""
    try:
        if not hasattr(villager, 'game_controller') or not villager.game_controller:
            return None
        
        # Tüm köylüleri kontrol et
        for other in villager.game_controller.villagers:
            # Kendisi değilse ve yakındaysa
            if other != villager:
                # Mesafeyi hesapla
                distance = ((villager.x - other.x) ** 2 + (villager.y - other.y) ** 2) ** 0.5
                if distance < 100:  # 100 birim mesafe içinde
                    return other
        
        return None
    except Exception as e:
        print(f"HATA: {villager.name} yakın köylü bulma hatası: {e}")
        import traceback
        traceback.print_exc()
        return None

def start_chat_with_nearby_villager(villager):
    """Yakındaki bir köylüyle basit etkileşim başlatır"""
    try:
        # Yakında köylü var mı bul
        nearby_villager = find_nearby_villager(villager)
        
        if not nearby_villager:
            print(f"{villager.name} yakınında etkileşim kuracak köylü bulamadı.")
            return NodeStatus.FAILURE
            
        print(f"{villager.name}, {nearby_villager.name} ile selamlaştı.")
        
        # Basit bir selamlama mesajı göster
        if hasattr(villager, 'game_controller') and villager.game_controller:
            message = f"Selam {nearby_villager.name}!"
            # Diyalog baloncuğunu göster
            bubble = villager.game_controller.create_dialogue_bubble(villager, message)
            if bubble:
                # 5 saniye sonra baloncuğu kaldır
                QTimer.singleShot(5000, lambda: villager.game_controller.remove_dialogue_bubble(bubble))
        
        return NodeStatus.SUCCESS
        
    except Exception as e:
        print(f"Etkileşim başlatılırken hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return NodeStatus.FAILURE 