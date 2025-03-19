from src.models.ai.behavior_tree import (
    NodeStatus, BehaviorNode, SequenceNode, SelectorNode, 
    ActionNode, ConditionNode, InverterNode, DelayNode,
    BlackboardNode, RandomSelectorNode
)
import random
import time
from PyQt5.QtCore import QTimer
from src.models.ai.dialogue.dialogue_manager import DialogueManager

# Köylü durumları için sabitler
IDLE = "Boşta"
WANDERING = "Dolaşıyor"
WORKING = "Çalışıyor"
CHATTING = "Sohbet Ediyor"
APPROACHING = "Yaklaşıyor"  # Köylüye yaklaşma durumu
RESTING = "Dinleniyor"
SLEEPING = "Uyuyor"
GOING_HOME = "Eve Gidiyor"

# Global Diyalog Yöneticisi örneği
dialogue_manager = DialogueManager()

def set_dialogue_manager(manager):
    """Global diyalog yöneticisini ayarla"""
    global dialogue_manager
    dialogue_manager = manager
    print("Diyalog yöneticisi başarıyla ayarlandı.")

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
    
    # Köylüye yakın mı kontrol et
    is_near_partner = ConditionNode("Köylü Yakın mı?",
                                  lambda v, dt: check_if_near_chat_partner(v))
    chat_sequence.add_child(is_near_partner)
    
    # Yakın değilse köylüye yaklaş
    approaching_selector = SelectorNode("Yaklaşma Seçici")
    
    # Yakın olma durumu
    near_partner_sequence = SequenceNode("Yakındaysa")
    near_partner_condition = ConditionNode("Zaten Yakın mı?", 
                                         lambda v, dt: check_if_near_chat_partner(v))
    near_partner_sequence.add_child(near_partner_condition)
    
    # Yakınsa konuşmaya devam et
    continue_chat = ActionNode("Konuşmaya Devam Et",
                              lambda v, dt: continue_chatting(v, v.chat_partner) if hasattr(v, 'chat_partner') else NodeStatus.FAILURE)
    near_partner_sequence.add_child(continue_chat)
    
    # Yaklaşma sekansı
    approach_sequence = SequenceNode("Yaklaş Sekansı")
    
    # Yakın değilse yaklaş
    not_near_condition = InverterNode("Yakın Değil mi?")
    is_near = ConditionNode("Yakın mı?", 
                          lambda v, dt: check_if_near_chat_partner(v))
    not_near_condition.add_child(is_near)
    approach_sequence.add_child(not_near_condition)
    
    # Köylüye yaklaş
    approach_action = ActionNode("Köylüye Yaklaş", 
                               lambda v, dt: approach_chat_partner(v, v.chat_partner) if hasattr(v, 'chat_partner') else NodeStatus.FAILURE)
    approach_sequence.add_child(approach_action)
    
    # Seçiciye sekansları ekle
    approaching_selector.add_child(near_partner_sequence)
    approaching_selector.add_child(approach_sequence)
    
    chat_sequence.add_child(approaching_selector)
    
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
                if distance < 50:  # 50 birim mesafe içinde (daha kısa mesafe)
                    # Köylü sohbet etmiyor olmalı - diğer köylüler ile konuşmamayı garantile
                    if not hasattr(other, 'is_chatting') or not other.is_chatting:
                        # Köylünün başka bir sohbeti yoksa
                        if not hasattr(other, 'chat_partner') or other.chat_partner is None:
                            return other
        
        return None
    except Exception as e:
        print(f"HATA: {villager.name} yakın köylü bulma hatası: {e}")
        import traceback
        traceback.print_exc()
        return None

def start_chat_with_nearby_villager(villager):
    """Yakındaki bir köylüyle sohbet başlatır"""
    try:
        # Eğer zaten sohbet ediyorsa, başka konuşma başlatılmaz
        if hasattr(villager, 'is_chatting') and villager.is_chatting:
            return NodeStatus.FAILURE
            
        # Konuşma cooldown kontrolü - eğer köylü yakın zamanda konuşmuşsa yeni bir konuşma başlatma
        current_time = time.time()
        if hasattr(villager, 'chat_cooldown') and current_time < villager.chat_cooldown:
            # Cooldown süresi dolmamış, konuşma başlatma
            remaining = int(villager.chat_cooldown - current_time)
            if remaining > 0 and remaining % 15 == 0:  # Her 15 saniyede bir mesaj
                print(f"{villager.name} konuşma için {remaining} saniye daha beklemeli.")
            return NodeStatus.FAILURE
        
        # Yakında köylü var mı bul
        nearby_villager = find_nearby_villager(villager)
        
        if not nearby_villager:
            # print(f"{villager.name} yakınında sohbet edecek köylü bulamadı.")
            return NodeStatus.FAILURE
        
        # Diğer köylünün de cooldown süresi kontrol edilir
        if hasattr(nearby_villager, 'chat_cooldown') and current_time < nearby_villager.chat_cooldown:
            # Diğer köylünün cooldown süresi dolmamış
            return NodeStatus.FAILURE
        
        # Diğer köylü zaten sohbet ediyorsa atla - çift kontrol
        if hasattr(nearby_villager, 'is_chatting') and nearby_villager.is_chatting:
            # print(f"{nearby_villager.name} zaten başka biriyle konuşuyor.")
            return NodeStatus.FAILURE
            
        # Köylünün kendisi de sohbet etmiyorsa - çift kontrol
        if hasattr(villager, 'is_chatting') and villager.is_chatting:
            return NodeStatus.FAILURE
        
        # Köylüler arasında ilişki kontrolü (eğer sevilmiyorsa konuşma şansı düşük)
        if dialogue_manager and hasattr(villager, 'relationships') and villager.name in nearby_villager.relationships:
            relationship = nearby_villager.relationships[villager.name]
            # Düşük ilişki düzeyinde konuşma olasılığı azalır
            if relationship == "Düşman" and random.random() < 0.9:  # %90 ihtimalle konuşma yok
                print(f"{nearby_villager.name}, {villager.name} ile konuşmak istemiyor (düşman).")
                return NodeStatus.FAILURE
            elif relationship == "Antipatik" and random.random() < 0.7:  # %70 ihtimalle konuşma yok
                print(f"{nearby_villager.name}, {villager.name} ile konuşmak istemiyor (antipatik).")
                return NodeStatus.FAILURE
        
        # Sohbeti başlat
        if start_chat(villager, nearby_villager):
            villager.state = CHATTING
            if hasattr(nearby_villager, 'state'):
                nearby_villager.state = CHATTING
            return NodeStatus.SUCCESS
        
        return NodeStatus.FAILURE
    except Exception as e:
        print(f"Sohbet başlatma hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        return NodeStatus.FAILURE

def check_if_near_chat_partner(villager):
    """Köylünün sohbet ortağına yakın olup olmadığını kontrol eder"""
    try:
        if hasattr(villager, 'chat_partner') and villager.chat_partner:
            # Mesafeyi hesapla
            distance = abs(villager.x - villager.chat_partner.x)
            return distance < 40  # 40 birimden yakınsa
        return False
    except Exception as e:
        print(f"HATA: Yakınlık kontrolü hatası: {e}")
        return False

def approach_chat_partner(villager, target_villager):
    """Köylünün hedefteki köylüye yaklaşmasını sağlar"""
    try:
        # Hedef köylü geçersizse çık
        if not target_villager:
            return NodeStatus.FAILURE
        
        # Diğer köylüye doğru yönelt ve yaklaşma mesafesini hesapla
        dx = target_villager.x - villager.x
        dy = target_villager.y - villager.y
        distance = (dx**2 + dy**2)**0.5
        
        # Konuşma mesafesi belirle (40 birim)
        CONVERSATION_DISTANCE = 40
        
        # Eğer yeteri kadar yakınsa durup konuşmaya başla
        if distance <= CONVERSATION_DISTANCE:
            # Her iki köylüyü de durdur
            if hasattr(villager, 'moving'):
                villager.moving = False
            if hasattr(target_villager, 'moving'):
                target_villager.moving = False
            
            # is_wandering bayrağını kapat
            if hasattr(villager, 'is_wandering'):
                villager.is_wandering = False
            if hasattr(target_villager, 'is_wandering'):
                target_villager.is_wandering = False
                
            # Hızları sıfırla
            if hasattr(villager, 'speed'):
                villager._original_speed = villager.speed
                villager.speed = 0
                
            if hasattr(target_villager, 'speed'):
                target_villager._original_speed = target_villager.speed
                target_villager.speed = 0
            
            # Hareket vektörlerini sıfırla
            if hasattr(villager, 'vx'):
                villager.vx = 0
                villager.vy = 0
            if hasattr(target_villager, 'vx'):
                target_villager.vx = 0
                target_villager.vy = 0
            
            # Birbirlerine baksınlar
            if hasattr(villager, 'direction'):
                villager.direction = calculate_direction(villager.x, villager.y, target_villager.x, target_villager.y)
            
            if hasattr(target_villager, 'direction'):
                target_villager.direction = calculate_direction(target_villager.x, target_villager.y, villager.x, villager.y)
            
            # Yön vektörlerini ayarla (eski stil)
            if hasattr(villager, 'direction_x'):
                villager.direction_x = 1 if villager.x < target_villager.x else -1
            
            if hasattr(target_villager, 'direction_x'):
                target_villager.direction_x = 1 if target_villager.x < villager.x else -1
            
            print(f"{villager.name} ve {target_villager.name} konuşma için tamamen durdular")
            
            # Konuşma başlat
            if start_chat(villager, target_villager):
                # Konuşma durumlarını güncelle
                villager.state = CHATTING
                if hasattr(target_villager, 'state'):
                    target_villager.state = CHATTING
                return NodeStatus.SUCCESS
            else:
                return NodeStatus.FAILURE
        else:
            # Hala yaklaşıyor, hareket etmeye devam et
            if hasattr(villager, 'move_towards'):
                villager.move_towards(target_villager.x)
                villager.state = APPROACHING
                return NodeStatus.RUNNING
            else:
                # move_towards fonksiyonu yoksa alternatif hareket
                normalize_factor = 1.0
                if distance > 0:
                    normalize_factor = 1.0 / distance
                
                if hasattr(villager, 'vx'):
                    villager.vx = dx * normalize_factor * villager.speed
                    villager.vy = dy * normalize_factor * villager.speed
                
                if hasattr(villager, 'moving'):
                    villager.moving = True
                
                if hasattr(villager, 'direction'):
                    villager.direction = calculate_direction(villager.x, villager.y, target_villager.x, target_villager.y)
                
                villager.state = APPROACHING
                return NodeStatus.RUNNING
    except Exception as e:
        print(f"Köylü yaklaşma hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        return NodeStatus.FAILURE

def calculate_direction(x1, y1, x2, y2):
    """İki nokta arasındaki yönü hesaplar (kuzey, güney, doğu, batı, vs.)"""
    dx = x2 - x1
    dy = y2 - y1
    
    if abs(dx) > abs(dy):
        return "east" if dx > 0 else "west"
    else:
        return "south" if dy > 0 else "north"

def continue_chatting(villager, target_villager):
    """Köylülerin sohbet etmeye devam etmesini sağlar"""
    try:
        current_time = time.time()
        
        # Konuşma durumlarını başlat
        if not hasattr(villager, 'chat_state'):
            villager.chat_state = 'GREETING'
            villager.chat_start_time = current_time
            villager.next_message_time = current_time
            villager.message_count = 0
            villager.max_messages = random.randint(4, 7)
            villager.last_speaker = None
            print(f"Yeni konuşma başladı: {villager.name} ve {target_villager.name}")
            
        # Son konuşan kişi kontrolü
        if villager.last_speaker == villager:
            return NodeStatus.RUNNING
            
        # Konuşma süresi kontrolü (maksimum 30 saniye)
        if current_time - villager.chat_start_time > 30:
            end_chat(villager, target_villager)
            return NodeStatus.SUCCESS
            
        # İnaktivite kontrolü (7 saniye)
        if current_time - villager.next_message_time > 7:
            print(f"İnaktivite nedeniyle sohbet sonlandırılıyor: {villager.name} ve {target_villager.name}")
            end_chat(villager, target_villager)
            return NodeStatus.SUCCESS
        
        # Durum makinesi
        if villager.chat_state == 'GREETING' and current_time >= villager.next_message_time:
            if villager.last_speaker is None:  # Sadece ilk selamlaşmada
                greeting = dialogue_manager.generate_greeting(villager, target_villager)
                if hasattr(villager, 'game_controller'):
                    villager.game_controller.create_dialogue_bubble(villager, greeting)
                dialogue_manager.log_dialogue(villager, target_villager, greeting)
                
                villager.chat_state = 'TALKING'
                villager.next_message_time = current_time + 3
                villager.message_count += 1
                villager.last_speaker = villager
                
        elif villager.chat_state == 'TALKING' and current_time >= villager.next_message_time:
            # Mesaj limiti kontrolü
            if villager.message_count >= villager.max_messages:
                villager.chat_state = 'FAREWELL'
                return NodeStatus.RUNNING
            
            # Konuşmacıyı belirle (sırayla konuşma)
            if villager.last_speaker != villager:
                speaker = villager
                listener = target_villager
                
                # Mesaj oluştur
                message = dialogue_manager.generate_dialogue_line(speaker, listener, random.choice(dialogue_manager.TOPICS))
                
                # Mesajı göster
                if hasattr(speaker, 'game_controller'):
                    speaker.game_controller.create_dialogue_bubble(speaker, message)
                dialogue_manager.log_dialogue(speaker, listener, message)
                
                # Sonraki mesaj için hazırlık
                villager.next_message_time = current_time + 3
                villager.message_count += 1
                villager.last_speaker = speaker
                
                # Soru-cevap kontrolü
                if "?" in message:
                    villager.next_message_time = current_time + 2
                
        elif villager.chat_state == 'FAREWELL' and current_time >= villager.next_message_time:
            if villager.last_speaker != villager:
                goodbye_phrases = [
                    "Hoşça kal!",
                    "Görüşmek üzere!",
                    "Seninle konuşmak güzeldi!",
                    "İyi günler!",
                    "Kendine iyi bak!"
                ]
                goodbye = random.choice(goodbye_phrases)
                
                if hasattr(villager, 'game_controller'):
                    villager.game_controller.create_dialogue_bubble(villager, goodbye)
                dialogue_manager.log_dialogue(villager, target_villager, goodbye)
                
                end_chat(villager, target_villager)
                return NodeStatus.SUCCESS
        
        # Birbirlerine bakmaya devam etsinler
        if hasattr(villager, 'direction'):
            villager.direction = calculate_direction(villager.x, villager.y, target_villager.x, target_villager.y)
        if hasattr(target_villager, 'direction'):
            target_villager.direction = calculate_direction(target_villager.x, target_villager.y, villager.x, villager.y)
        
        return NodeStatus.RUNNING
        
    except Exception as e:
        print(f"HATA: Sohbet devam ettirme hatası: {e}")
        import traceback
        traceback.print_exc()
        end_chat(villager, target_villager)
        return NodeStatus.FAILURE

def end_chat(villager, target_villager):
    """Sohbeti sonlandırır ve köylülerin hareketine izin verir"""
    try:
        # Hedef kontrolü
        if not target_villager:
            if hasattr(villager, 'chat_partner'):
                target_villager = villager.chat_partner
            if not target_villager:
                # Tek taraflı sonlandırma
                if hasattr(villager, 'is_chatting'):
                    villager.is_chatting = False
                
                # Köylünün tekrar hareket etmesine izin ver
                if hasattr(villager, 'moving'):
                    villager.moving = True
                    
                # Wandering bayrağını açarak dolaşmaya izin ver
                if hasattr(villager, 'is_wandering'):
                    villager.is_wandering = True
                    
                # Hızları geri yükle
                if hasattr(villager, 'speed'):
                    if hasattr(villager, '_original_speed'):
                        villager.speed = villager._original_speed
                    else:
                        villager.speed = 0.35  # Varsayılan hız
                
                # Rasgele bir yöne doğru hareket ettir
                if hasattr(villager, 'vx'):
                    villager.vx = random.uniform(-1, 1) * villager.speed
                    villager.vy = random.uniform(-1, 1) * villager.speed
                
                # Köylünün hedefini sıfırla
                villager.chat_partner = None
                
                # Köylünün durumunu güncelle
                villager.state = WANDERING
                
                # Cooldown ekle
                cooldown_time = random.uniform(60, 180)
                villager.chat_cooldown = time.time() + cooldown_time
                
                return NodeStatus.SUCCESS
        
        # Veda mesajı
        goodbye_phrases = [
            "Hoşça kal!",
            "Görüşmek üzere!",
            "Seninle konuşmak güzeldi, tekrar görüşelim!",
            "İyi günler!",
            "Sohbet için teşekkürler!",
            "Kendine iyi bak!"
        ]
        
        # Rastgele veda mesajı seç
        goodbye_message = random.choice(goodbye_phrases)
        
        # Vedalaşma mesajını göster
        if hasattr(villager, 'game_controller') and villager.game_controller:
            villager.game_controller.create_dialogue_bubble(villager, goodbye_message)
        
        # Veda mesajını kaydet
        if dialogue_manager:
            dialogue_manager.log_dialogue(villager, target_villager, goodbye_message)
        
        print(f"{villager.name} ve {target_villager.name} konuşmayı sonlandırdı: {goodbye_message}")
        
        # Sohbet durumlarını resetle
        if hasattr(villager, 'is_chatting'):
            villager.is_chatting = False
        if hasattr(target_villager, 'is_chatting'):
            target_villager.is_chatting = False
            
        # Köylülerin tekrar hareket etmesine izin ver
        if hasattr(villager, 'moving'):
            villager.moving = True
        if hasattr(target_villager, 'moving'):
            target_villager.moving = True
            
        # Wandering bayrağını açarak dolaşmaya izin ver
        if hasattr(villager, 'is_wandering'):
            villager.is_wandering = True
        if hasattr(target_villager, 'is_wandering'):
            target_villager.is_wandering = True
            
        # Hızları geri yükle
        if hasattr(villager, 'speed'):
            if hasattr(villager, '_original_speed'):
                villager.speed = villager._original_speed
            else:
                villager.speed = 0.35  # Varsayılan hız
                
        if hasattr(target_villager, 'speed'):
            if hasattr(target_villager, '_original_speed'):
                target_villager.speed = target_villager._original_speed
            else:
                target_villager.speed = 0.35  # Varsayılan hız
        
        # Köylüleri rasgele bir yöne doğru hareket ettir
        if hasattr(villager, 'vx'):
            villager.vx = random.uniform(-1, 1) * villager.speed
            villager.vy = random.uniform(-1, 1) * villager.speed
        
        if hasattr(target_villager, 'vx'):
            target_villager.vx = random.uniform(-1, 1) * target_villager.speed
            target_villager.vy = random.uniform(-1, 1) * target_villager.speed
        
        # Köylülerin hedeflerini sıfırla
        villager.chat_partner = None
        target_villager.chat_partner = None
        
        # Köylülerin durumlarını güncelle
        villager.state = WANDERING
        if hasattr(target_villager, 'state'):
            target_villager.state = WANDERING
        
        # ÖNEMLİ: Yeni bir konuşma başlatmadan önce daha uzun bekleme süresi (cooldown) ekle
        # Bu, köylülerin sürekli konuşmasını engelleyecek
        cooldown_time = random.uniform(60, 180)  # 1-3 dakika arası bekleme
        
        # Köylülere chat_cooldown değişkeni ekle
        villager.chat_cooldown = time.time() + cooldown_time
        target_villager.chat_cooldown = time.time() + cooldown_time
        
        print(f"{villager.name} ve {target_villager.name} {int(cooldown_time)} saniye boyunca başka konuşma başlatmayacak.")
        
        return NodeStatus.SUCCESS
    except Exception as e:
        print(f"Sohbet sonlandırma hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Hata durumunda da köylülerin durumunu reset et
        if hasattr(villager, 'is_chatting'):
            villager.is_chatting = False
        if target_villager and hasattr(target_villager, 'is_chatting'):
            target_villager.is_chatting = False
            
        # Hata olsa da köylülerin hareket etmesine izin ver
        try:
            if hasattr(villager, 'moving'):
                villager.moving = True
            if target_villager and hasattr(target_villager, 'moving'):
                target_villager.moving = True
        except:
            pass
            
        return NodeStatus.FAILURE

def start_chat(villager, target_villager):
    """İki köylü arasında sohbeti başlatır"""
    try:
        if not target_villager:
            return False
            
        # Eğer köylülerden biri zaten sohbet ediyorsa, başlatma
        if (hasattr(villager, 'is_chatting') and villager.is_chatting) or \
           (hasattr(target_villager, 'is_chatting') and target_villager.is_chatting):
            return False
            
        print(f"{villager.name}, {target_villager.name} ile sohbet başlatıyor.")
        
        # Konuşma durumlarını ayarla
        villager.is_chatting = True
        villager.chat_partner = target_villager
        villager.chat_state = 'GREETING'
        villager.last_speaker = None
        villager.last_topic = random.choice(dialogue_manager.TOPICS)
        villager.last_message_was_question = False
        villager.chat_start_time = time.time()
        villager.next_message_time = time.time()
        
        # Karşı köylünün durumunu da ayarla
        target_villager.is_chatting = True
        target_villager.chat_partner = villager
        target_villager.chat_state = 'GREETING'
        target_villager.last_speaker = None
        target_villager.last_topic = villager.last_topic
        target_villager.last_message_was_question = False
        target_villager.chat_start_time = villager.chat_start_time
        target_villager.next_message_time = villager.next_message_time
        
        # Orijinal hızları sakla ve hareketi durdur
        if hasattr(villager, 'speed'):
            villager._original_speed = villager.speed
            villager.speed = 0
        
        if hasattr(target_villager, 'speed'):
            target_villager._original_speed = target_villager.speed
            target_villager.speed = 0
        
        # Hareket bayrağını kapat
        if hasattr(villager, 'moving'):
            villager.moving = False
        if hasattr(target_villager, 'moving'):
            target_villager.moving = False
            
        # Rastgele sohbet süresi belirle (15-30 saniye arası)
        chat_duration = random.uniform(15, 30)
        villager.chat_end_time = time.time() + chat_duration
        target_villager.chat_end_time = villager.chat_end_time
        
        print(f"Sohbet başlatıldı: {villager.name} -> {target_villager.name}")
        return True
        
    except Exception as e:
        print(f"Sohbet başlatma hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Hata durumunda köylülerin durumunu reset et
        try:
            if hasattr(villager, 'is_chatting'):
                villager.is_chatting = False
            if hasattr(target_villager, 'is_chatting'):
                target_villager.is_chatting = False
        except:
            pass
            
        return False 