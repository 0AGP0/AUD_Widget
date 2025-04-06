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
    # Meslek seçici düğümü oluştur
    profession_sequence = SequenceNode("Meslek Davranışı")

    # Mesleğe özel davranışları kontrol et
    profession_selector = SelectorNode("Meslek Seçici")
    profession_sequence.add_child(profession_selector)
    
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
    
    # İnşaatçı davranışı - En Yüksek Önceliğe Taşıyalım
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
    harvesting_limit_not_reached = ConditionNode("Hasat Limiti Dolmadı mı?", 
                                              lambda v, dt: hasattr(v, 'crops_harvested') and 
                                                           hasattr(v, 'max_harvests_per_day') and
                                                           v.crops_harvested < v.max_harvests_per_day)
    farmer_sequence.add_child(harvesting_limit_not_reached)
    
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
    
    # Meslekleri öncelikli olarak ekle - en üst öncelikli İnşaatçı olsun
    profession_selector.add_child(builder_sequence)
    profession_selector.add_child(woodcutter_sequence)
    profession_selector.add_child(hunter_sequence)
    profession_selector.add_child(farmer_sequence)
    profession_selector.add_child(guard_sequence)
    
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
    """İnşaatçı işini yap"""
    try:
        print(f"DEBUG: {villager.name} inşaatçı işini yapıyor")
        
        # İnşaatçının oyun kontrolcüsü var mı kontrol et
        if not hasattr(villager, 'game_controller') or not villager.game_controller:
            print(f"DEBUG: {villager.name} için game_controller bulunamadı")
            return NodeStatus.FAILURE
        
        game_controller = villager.game_controller
        
        # Kale ve envanterini kontrol et
        if not hasattr(game_controller, 'castle') or not game_controller.castle:
            print(f"DEBUG: İNŞAATÇI HATA: {villager.name} kaleyi bulamadı!")
            return NodeStatus.FAILURE
        
        castle = game_controller.castle
        wood_amount = castle.get_inventory().get('odun', 0)
        print(f"DEBUG: Kale envanterinde {wood_amount} odun var. İnşaat için 30 odun gerekiyor.")
        
        # İnşaatçı zaten inşaat yapıyor mu?
        if hasattr(villager, 'is_building') and villager.is_building:
            print(f"DEBUG: {villager.name} zaten inşaat yapıyor")
            if hasattr(villager, 'target_building_site') and villager.target_building_site:
                # İnşaat alanına yaklaş
                building_site = villager.target_building_site
                distance = abs(building_site.x - villager.x)
                print(f"DEBUG: {villager.name} inşaat alanına mesafesi: {distance}")
                
                if distance > 20:
                    # İnşaat alanına doğru hareket et
                    if villager.x < building_site.x:
                        villager.direction = 1  # Sağa
                    else:
                        villager.direction = -1  # Sola
                    
                    # İnşaat alanına hareket et
                    villager.target_x = building_site.x
                    villager.target_y = building_site.y
                    villager.state = "İnşaat Alanına Gidiyor"
                    print(f"DEBUG: {villager.name} inşaat alanına gidiyor. Hedef: ({building_site.x}, {building_site.y})")
                    
                    # Hareketi başlat
                    villager.is_moving = True
                    villager.is_wandering = False
                    return NodeStatus.RUNNING
                    
                # İnşaat alanında, inşaat devam ediyor
                villager.state = "İnşaat Yapıyor"
                progress = building_site.progress if hasattr(building_site, 'progress') else 0
                print(f"DEBUG: {villager.name} inşaata devam ediyor. İlerleme: {progress:.1f}%")
                return NodeStatus.RUNNING
            else:
                # İnşaat alanı kayboldu
                villager.is_building = False
                villager.state = "İnşaat Alanı Kayboldu"
                print(f"DEBUG: {villager.name} için inşaat alanı kayboldu!")
                return NodeStatus.FAILURE
        
        # Yeterli odun var mı kontrol et (30 odun)
        if wood_amount >= 30:
            print(f"DEBUG: Yeterli odun var: {wood_amount}/30")
            # Köylünün günlük inşa limiti dolmadı mı?
            if not hasattr(villager, 'buildings_built') or not hasattr(villager, 'max_buildings_per_day'):
                # Özellikler eksik, varsayılan değerleri ayarla
                villager.buildings_built = 0
                villager.max_buildings_per_day = 1
                print(f"DEBUG: {villager.name} için eksik özellikler atandı. İnşaat sayısı: 0, Limit: 1")
            
            print(f"DEBUG: {villager.name} bugün {villager.buildings_built}/{villager.max_buildings_per_day} inşaat yapmış.")
            if villager.buildings_built >= villager.max_buildings_per_day:
                # Günlük limit doldu
                villager.state = "Günlük İnşaat Limiti Doldu"
                print(f"DEBUG: {villager.name} günlük inşaat limitine ulaştı! Limit: {villager.max_buildings_per_day}")
                return NodeStatus.FAILURE
            
            # Otomatik inşaat kontrolü
            print(f"DEBUG: {villager.name} otomatik inşaat kontrolü başlatıyor...")
            
            # Game Controller'ın potansiyel inşaat yerlerini bulup bulamadığını kontrol et
            potential_locations = game_controller.find_potential_building_locations()
            print(f"DEBUG: {len(potential_locations)} potansiyel inşaat lokasyonu bulundu: {potential_locations[:3] if potential_locations else 'Yok'}")
            
            # İnşaat başlatmayı dene
            success = game_controller.check_for_auto_building()
            
            if success:
                # İnşaat başlatıldı
                print(f"DEBUG: {villager.name} için inşaat başlatıldı!")
                return NodeStatus.SUCCESS
            else:
                # İnşaat başlatılamadı
                print(f"DEBUG: {villager.name} için inşaat başlatılamadı! Ev sayısı: {len(game_controller.houses)}, Mevcut inşaatlar: {len(game_controller.building_sites)}")
                # İnşaat için uygun yer bulunamadıysa, daha dar mesafe ile tekrar dene
                if not potential_locations:
                    print(f"DEBUG: {villager.name} daha küçük mesafe ile inşaat yeri arıyor...")
                    potential_locations = game_controller.find_potential_building_locations(min_distance=60)
                    if potential_locations:
                        # Uygun bir yer bulduk, rastgele seç
                        building_x = random.choice(potential_locations)
                        # İnşaat alanı oluştur ve başlat
                        building_site = game_controller.create_building_site(building_x, game_controller.ground_y, min_distance=60)
                        if building_site and building_site.start_construction(villager):
                            villager.is_building = True
                            villager.target_building_site = building_site
                            villager.state = "İnşaat Yapıyor"
                            print(f"DEBUG: {villager.name} alternatif konumda inşaat başlattı: {building_x}")
                            return NodeStatus.SUCCESS
                
                return NodeStatus.FAILURE
        else:
            # Yeterli odun yok, bekleyecek
            villager.state = "Odun Bekliyor"
            print(f"DEBUG: Yeterli odun yok: {wood_amount}/30 - {villager.name} odun bekliyor")
            return NodeStatus.FAILURE
    
    except Exception as e:
        print(f"HATA: İnşaatçı davranışı: {e}")
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
            print(f"UYARI: {villager.name} için game_controller bulunamadı!")
            return None
        
        print(f"DEBUG: {villager.name} yakındaki köylü arıyor...")
        
        # Tüm köylüleri kontrol et
        for other in villager.game_controller.villagers:
            # Kendisi değilse ve yakındaysa
            if other != villager:
                # Mesafeyi hesapla
                distance = ((villager.x - other.x) ** 2 + (villager.y - other.y) ** 2) ** 0.5
                if distance < 80:  # Mesafeyi artır - 80 birim mesafe içinde
                    print(f"DEBUG: {villager.name} ve {other.name} arası mesafe: {distance}")
                    # Köylü sohbet etmiyor olmalı - diğer köylüler ile konuşmamayı garantile
                    if not hasattr(other, 'is_chatting') or not other.is_chatting:
                        # Köylünün başka bir sohbeti yoksa
                        if not hasattr(other, 'chat_partner') or other.chat_partner is None:
                            print(f"BULUNDU: {villager.name}, {other.name} ile konuşabilir!")
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
            print(f"{villager.name} yakınında sohbet edecek köylü bulamadı.")
            return NodeStatus.FAILURE
        
        # Diğer köylünün de cooldown süresi kontrol edilir
        if hasattr(nearby_villager, 'chat_cooldown') and current_time < nearby_villager.chat_cooldown:
            # Diğer köylünün cooldown süresi dolmamış
            print(f"{nearby_villager.name}'nin konuşma cooldown süresi dolmamış.")
            return NodeStatus.FAILURE
        
        # Diğer köylü zaten sohbet ediyorsa atla - çift kontrol
        if hasattr(nearby_villager, 'is_chatting') and nearby_villager.is_chatting:
            print(f"{nearby_villager.name} zaten başka biriyle konuşuyor.")
            return NodeStatus.FAILURE
            
        # Köylünün kendisi de sohbet etmiyorsa - çift kontrol
        if hasattr(villager, 'is_chatting') and villager.is_chatting:
            return NodeStatus.FAILURE
        
        # Köylüler arasında ilişki kontrolü (eğer sevilmiyorsa konuşma şansı düşük)
        if dialogue_manager and hasattr(villager, 'relationships') and nearby_villager.name in villager.relationships:
            relationship = villager.relationships[nearby_villager.name]
            # Düşük ilişki düzeyinde konuşma olasılığı azalır
            if relationship == "Düşman" and random.random() < 0.9:  # %90 ihtimalle konuşma yok
                print(f"{villager.name}, {nearby_villager.name} ile konuşmak istemiyor (düşman).")
                return NodeStatus.FAILURE
            elif relationship == "Antipatik" and random.random() < 0.7:  # %70 ihtimalle konuşma yok
                print(f"{villager.name}, {nearby_villager.name} ile konuşmak istemiyor (antipatik).")
                return NodeStatus.FAILURE
        
        print(f"BAŞLATILIYOR: {villager.name} ve {nearby_villager.name} arasında sohbet başlatılıyor!")
        
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
        # Hata durumunda köylüleri serbest bırak
        try:
            villager.moving = True
            if hasattr(villager, 'chat_partner'):
                villager.chat_partner.moving = True
            villager.is_wandering = True
            if hasattr(villager, 'chat_partner'):
                villager.chat_partner.is_wandering = True
        except:
            pass
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
            print(f"YAKLAŞMA: {villager.name} ve {target_villager.name} konuşma mesafesinde ({distance:.1f})")
            
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
                
            # Hızları sıfırla ve orijinal hızları sakla
            if hasattr(villager, 'speed'):
                if not hasattr(villager, '_original_speed'):
                    villager._original_speed = villager.speed
                villager.speed = 0
                
            if hasattr(target_villager, 'speed'):
                if not hasattr(target_villager, '_original_speed'):
                    target_villager._original_speed = target_villager.speed
                target_villager.speed = 0
            
            # Hareket vektörlerini sıfırla
            if hasattr(villager, 'vx'):
                villager.vx = 0
                villager.vy = 0
            if hasattr(target_villager, 'vx'):
                target_villager.vx = 0
                target_villager.vy = 0
            
            # Birbirlerine baksınlar - yönlerini ayarla
            if hasattr(villager, 'direction'):
                villager.direction = calculate_direction(villager.x, villager.y, target_villager.x, target_villager.y)
            
            if hasattr(target_villager, 'direction'):
                target_villager.direction = calculate_direction(target_villager.x, target_villager.y, villager.x, villager.y)
            
            # Yön vektörlerini ayarla (eski stil)
            if hasattr(villager, 'direction_x'):
                villager.direction_x = 1 if villager.x < target_villager.x else -1
            
            if hasattr(target_villager, 'direction_x'):
                target_villager.direction_x = 1 if target_villager.x < villager.x else -1
            
            print(f"DURUŞ: {villager.name} ve {target_villager.name} tamamen durdular ve birbirlerine bakıyorlar")
            
            # Konuşma başlat
            if start_chat(villager, target_villager):
                # Konuşma durumlarını güncelle
                villager.state = CHATTING
                if hasattr(target_villager, 'state'):
                    target_villager.state = CHATTING
                return NodeStatus.SUCCESS
            else:
                # Konuşma başlatılamazsa köylüleri serbest bırak
                print(f"HATA: Konuşma başlatılamadı, köylüler serbest bırakılıyor")
                villager.moving = True
                target_villager.moving = True
                villager.is_wandering = True
                target_villager.is_wandering = True
                villager.speed = villager._original_speed if hasattr(villager, '_original_speed') else 0.35
                target_villager.speed = target_villager._original_speed if hasattr(target_villager, '_original_speed') else 0.35
                return NodeStatus.FAILURE
        else:
            # Yaklaşma mesafesini göster
            if hasattr(villager, 'last_approach_log_time'):
                log_interval = 1.0  # 1 saniyede bir log göster
                current_time = time.time()
                if current_time - villager.last_approach_log_time >= log_interval:
                    print(f"YAKLAŞIYOR: {villager.name} -> {target_villager.name} mesafe: {distance:.1f}, hedef mesafe: {CONVERSATION_DISTANCE}")
                    villager.last_approach_log_time = current_time
            else:
                villager.last_approach_log_time = time.time()
                
            # Hala yaklaşıyor, hareket etmeye devam et
            if hasattr(villager, 'move_towards'):
                villager.move_towards(target_villager.x, target_villager.y)  # Hedefin x,y koordinatlarına doğru hareket et
                villager.state = APPROACHING
                return NodeStatus.RUNNING
            else:
                # move_towards fonksiyonu yoksa alternatif hareket
                normalize_factor = 1.0
                if distance > 0:
                    normalize_factor = 1.0 / distance
                
                # Hedefe doğru vektörü ayarla ve hızını normalize et
                if hasattr(villager, 'vx'):
                    # Hareket hızı
                    movement_speed = villager.speed if hasattr(villager, 'speed') else 0.5
                    
                    # Hareket vektörünü hesapla
                    villager.vx = dx * normalize_factor * movement_speed
                    villager.vy = dy * normalize_factor * movement_speed
                
                # Hareket bayrağını ayarla
                if hasattr(villager, 'moving'):
                    villager.moving = True
                
                # Villager'ın yönünü hedefe çevir
                if hasattr(villager, 'direction'):
                    villager.direction = calculate_direction(villager.x, villager.y, target_villager.x, target_villager.y)
                
                # Durumu güncelle
                villager.state = APPROACHING
                return NodeStatus.RUNNING
    except Exception as e:
        print(f"Köylü yaklaşma hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        # Hata durumunda köylüleri serbest bırak
        try:
            villager.moving = True
            target_villager.moving = True
            villager.is_wandering = True
            target_villager.is_wandering = True
            villager.speed = villager._original_speed if hasattr(villager, '_original_speed') else 0.35
            target_villager.speed = target_villager._original_speed if hasattr(target_villager, '_original_speed') else 0.35
        except:
            pass
        return NodeStatus.FAILURE

def calculate_direction(x1, y1, x2, y2):
    """İki nokta arasındaki yönü hesaplar (kuzey, güney, doğu, batı, vs.)"""
    dx = x2 - x1
    dy = y2 - y1
    
    if abs(dx) > abs(dy):
        return "east" if dx > 0 else "west"
    else:
        return "south" if dy > 0 else "north"

def start_chat(villager, target_villager):
    """İki köylü arasında sohbet başlatır"""
    try:
        # Hedef köylü geçersizse başarısız
        if not target_villager:
            return False
            
        print(f"CHAT BAŞLATILIYOR: {villager.name} ve {target_villager.name} arasında sohbet...")
            
        # Her iki köylünün de konuşma durumunu güncelle
        villager.is_chatting = True
        target_villager.is_chatting = True
        
        # Chat partnerları ayarla
        villager.chat_partner = target_villager
        target_villager.chat_partner = villager
        
        # Sohbet süresini ayarla (10-30 saniye arası)
        chat_duration = random.uniform(10, 30)
        end_time = time.time() + chat_duration
        
        villager.chat_end_time = end_time
        target_villager.chat_end_time = end_time
        
        # Sonraki chat için cooldown ayarla (30-120 saniye)
        cooldown_duration = random.uniform(30, 120)
        cooldown_end_time = end_time + cooldown_duration
        
        villager.chat_cooldown = cooldown_end_time
        target_villager.chat_cooldown = cooldown_end_time
        
        # Son konuşma mesaj zamanını sıfırla
        villager.last_chat_message_time = time.time()
        target_villager.last_chat_message_time = time.time()
        
        # Sohbet durumunu güncelle
        villager.state = CHATTING
        target_villager.state = CHATTING
        
        # Köylülerin aktif diyalog baloncuklarını temizle
        clear_all_dialogue_bubbles(villager)
        clear_all_dialogue_bubbles(target_villager)
        
        # Soru-cevap mekanizması için bayraklar
        villager.last_message_was_question = False
        target_villager.last_message_was_question = False
        
        # Diyalog konusunu sıfırla
        if hasattr(villager, 'last_topic'):
            delattr(villager, 'last_topic')
            
        if hasattr(target_villager, 'last_topic'):
            delattr(target_villager, 'last_topic')
            
        # Konuşma sayacı - sohbet ilerlemesini takip etmek için
        villager.conversation_counter = 0
        target_villager.conversation_counter = 0
        
        # Son konuşan kişiyi sıfırla
        villager.last_speaker = None
        target_villager.last_speaker = None
        
        # Selamlaşma mesajı ile başla
        if dialogue_manager:
            greeting = dialogue_manager.generate_greeting(villager, target_villager)
            
            # Diyalog baloncuğunu göster
            if hasattr(villager, 'game_controller') and villager.game_controller:
                bubble = villager.game_controller.create_dialogue_bubble(villager, greeting)
                
                # Baloncuğu geri döndürdüğünden emin ol
                if bubble:
                    # Baloncuğu takip etmek için kaydet
                    villager.current_bubble = bubble
                    villager.active_bubble = True
                    villager.bubble_start_time = time.time()
                    
                    print(f"{villager.name}'nin selamlaşma baloncuğu gösterildi")
            
            # Diyaloğu kaydet
            dialogue_manager.log_dialogue(villager, target_villager, greeting)
        
        return True
    except Exception as e:
        print(f"Sohbet başlatma hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def continue_chatting(villager, target_villager):
    """Köylülerin sohbet etmeye devam etmesini sağlar"""
    try:
        # Hedef köylü geçersizse çık
        if not target_villager:
            # Sohbeti sonlandır
            if hasattr(villager, 'is_chatting') and villager.is_chatting:
                end_chat(villager, None)
            return NodeStatus.FAILURE
            
        # İki köylü arasındaki mesafeyi kontrol et
        dx = target_villager.x - villager.x
        dy = target_villager.y - villager.y
        distance = (dx**2 + dy**2)**0.5
        
        CONVERSATION_DISTANCE = 40
        
        # Eğer çok uzaklaştılarsa konuşmayı sonlandır
        if distance > CONVERSATION_DISTANCE * 1.5:
            print(f"{villager.name} ve {target_villager.name} arasındaki mesafe çok açıldı, konuşma sonlandırılıyor.")
            end_chat(villager, target_villager)
            return NodeStatus.SUCCESS
            
        # Hareket etmeyi kesinlikle engelle
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
            villager.speed = 0
        if hasattr(target_villager, 'speed'):
            target_villager.speed = 0
            
        # Hareket vektörlerini sıfırla
        if hasattr(villager, 'vx'):
            villager.vx = 0
            villager.vy = 0
        if hasattr(target_villager, 'vx'):
            target_villager.vx = 0
            target_villager.vy = 0
        
        # Şu anki zamanı al
        current_time = time.time()
        
        # Baloncuk sistemini kontrol et - eğer baloncuk görünme süresi dolduysa kaldır
        # Not: QTimer'ın yerine zamanlama sistemini düzgün bir şekilde kontrol ediyoruz
        if hasattr(villager, 'active_bubble') and villager.active_bubble:
            if hasattr(villager, 'bubble_start_time') and villager.current_bubble:
                bubble_duration = current_time - villager.bubble_start_time
                if bubble_duration >= 3:  # 3 saniye geçtiyse baloncuğu sil
                    print(f"{villager.name}'nin baloncuğu 3 saniye doldu, siliniyor...")
                    force_remove_bubble(villager, villager.current_bubble)
                    
        if hasattr(target_villager, 'active_bubble') and target_villager.active_bubble:
            if hasattr(target_villager, 'bubble_start_time') and target_villager.current_bubble:
                bubble_duration = current_time - target_villager.bubble_start_time
                if bubble_duration >= 3:  # 3 saniye geçtiyse baloncuğu sil
                    print(f"{target_villager.name}'nin baloncuğu 3 saniye doldu, siliniyor...")
                    force_remove_bubble(target_villager, target_villager.current_bubble)
        
        # Aktif konuşma balonu var mı kontrol et (şu anda konuşan var mı?)
        # Eğer herhangi bir baloncuk hala aktifse, yeni konuşma başlatma
        if hasattr(villager, 'active_bubble') and villager.active_bubble:
            return NodeStatus.RUNNING
            
        if hasattr(target_villager, 'active_bubble') and target_villager.active_bubble:
            return NodeStatus.RUNNING
        
        # Konuşma zamanı kontrolü
        if not hasattr(villager, 'last_chat_message_time'):
            villager.last_chat_message_time = 0
            
        # Konuşma zamanını kontrol et - son mesajdan sonra belirli bir zaman geçmiş mi?
        message_time_passed = current_time - villager.last_chat_message_time
        
        # Konuşma arası bekleme süresini, konuşmanın ilerleme durumuna göre ayarla
        if not hasattr(villager, 'conversation_counter'):
            villager.conversation_counter = 0
        
        # Konuşmanın ilk kısmı hızlı, sonrası daha yavaş olsun
        wait_time = 3.0 if villager.conversation_counter < 2 else random.uniform(4, 8)
        
        if message_time_passed >= wait_time:
            # Diyalog balonunun görünür kalma süresi (konuşma içeriğine bağlı)
            message_display_time = 3  # 3 saniye
            
            # ÖNEMLİ: Soru-cevap dinamiğini kontrol et
            # Soru sorulduğunda cevaplama mekanizması çalışmazsa konuşmalar kilitlenebilir
            if hasattr(villager, 'last_message_was_question') and villager.last_message_was_question:
                print(f"SORU ALGILANDI: {villager.name}'nin sorusuna {target_villager.name} cevap verecek")
                
                # Eğer bu köylü son soru soran ise, karşı taraf cevap vermeli
                if dialogue_manager:
                    # Cevap oluşturma - köylünün geçerli ruh halini kontrol et
                    mood = "Sakin"  # Varsayılan ruh hali
                    if hasattr(target_villager, 'mood'):
                        mood = target_villager.mood
                        
                    profession = ""  # Varsayılan meslek
                    if hasattr(target_villager, 'profession'):
                        profession = target_villager.profession
                    
                    # Varsayılan cevaplar (eğer generate_response çalışmazsa)
                    default_responses = [
                        "Bugün çok güzel bir gün.", 
                        "İyi gidiyor, teşekkür ederim.",
                        "Her zamanki gibi işte.",
                        "Çok çalışıyorum bu aralar.",
                        "Biraz yorgunum ama iyiyim."
                    ]
                    
                    # Son soruyu karşı tarafın last_dialogue'una ayarla
                    if hasattr(villager, 'last_question_text') and villager.last_question_text:
                        # Son soruyu al
                        target_villager.last_dialogue = villager.last_question_text
                        print(f"Son soru hedef köylüye atandı: {target_villager.last_dialogue}")
                    else:
                        # Soru yoksa varsayılan soru ata
                        target_villager.last_dialogue = "Günün nasıl geçiyor?"
                        print(f"Varsayılan soru kullanılıyor: {target_villager.last_dialogue}")
                    
                    # Diyalog yöneticisinden cevap almaya çalış
                    try:
                        # Cevap üret
                        response = dialogue_manager.generate_response(villager, target_villager)
                        if not response:  # Boş cevap geldiyse
                            response = random.choice(default_responses)
                    except Exception as response_err:
                        print(f"Cevap oluşturma hatası: {response_err}")
                        response = random.choice(default_responses)
                    
                    print(f"CEVAP: {target_villager.name} -> {villager.name}: {response}")
                    
                    # Son cevapları takip et - tekrarı önle
                    if not hasattr(target_villager, 'last_responses'):
                        target_villager.last_responses = []
                        
                    # Son 5 cevabı kontrol et, tekrar olmamasını sağla
                    while response in target_villager.last_responses and len(target_villager.last_responses) > 0:
                        # Farklı bir cevap bul
                        response = dialogue_manager.generate_response(villager, target_villager)
                        if not response or response in target_villager.last_responses:
                            # Yeni bir cevap bulunamadıysa default'lardan al
                            filtered_defaults = [r for r in default_responses if r not in target_villager.last_responses]
                            if filtered_defaults:
                                response = random.choice(filtered_defaults)
                            else:
                                response = random.choice(default_responses)
                                break  # Son çare olarak

                    # Cevabı son cevaplar listesine ekle
                    target_villager.last_responses.append(response)
                    if len(target_villager.last_responses) > 5:
                        target_villager.last_responses.pop(0)
                    
                    # Uzun yanıtlar için daha uzun görünme süresi
                    if len(response) > 50:
                        message_display_time = 5  # 5 saniye
                    
                    # Aktif baloncuk kaydı - baloncuğun yok edilmesini takip etmek için
                    target_villager.active_bubble = True
                    target_villager.bubble_start_time = current_time
                    
                    # Diyalog baloncuğunu göster
                    if hasattr(target_villager, 'game_controller') and target_villager.game_controller:
                        bubble = target_villager.game_controller.create_dialogue_bubble(target_villager, response)
                        
                        # Baloncuğu geri döndürdüğünden emin ol
                        if bubble:
                            # Baloncuğun kaldırılması - baloncuk referansını koru
                            target_villager.current_bubble = bubble
                            
                            # QTimer artık kullanmıyoruz, bunun yerine bubble_start_time kullanıyoruz
                            # ve her framedeki kontrol sistemi baloncukları yönetiyor
                            print(f"{target_villager.name}'nin baloncuğu gösterildi, {message_display_time} saniye sonra silinecek")
                        else:
                            # Baloncuk oluşturulamadıysa aktif bayrak temizle
                            target_villager.active_bubble = False
                    else:
                        # Game controller yok veya bubble oluşturulamadı
                        target_villager.active_bubble = False
                    
                    # Diyaloğu kaydet
                    dialogue_manager.log_dialogue(target_villager, villager, response)
                    
                    # Soru cevaplanmış olarak işaretle
                    villager.last_message_was_question = False
                    if hasattr(target_villager, 'last_message_was_question'):
                        target_villager.last_message_was_question = False
                        
                    # Konuşma sayacını artır
                    villager.conversation_counter += 1
                else:
                    # Diyalog yöneticisi yoksa soruyu zorla sıfırla - kilitleme sorunu çözümü
                    print("Diyalog yöneticisi bulunamadı, soru bayrağı sıfırlanıyor")
                    villager.last_message_was_question = False
            else:
                # Normal diyaloğa devam et
                # 15'ten fazla replik söylendiyse konuşmayı bitirelim
                if hasattr(villager, 'conversation_counter') and villager.conversation_counter >= 15:
                    print(f"Yeterince konuşuldu ({villager.conversation_counter} replik), konuşma sonlandırılıyor.")
                    end_chat(villager, target_villager)
                    return NodeStatus.SUCCESS
                
                if random.random() < 0.85:  # %85 konuşma şansı - daha sık konuşsunlar
                    # Konuşan kişi olarak sırayı alacak kişiyi belirle 
                    # Sıralı konuşmayı garanti et, son konuşandan sonra diğeri konuşsun
                    if hasattr(villager, 'last_speaker') and villager.last_speaker == villager.name:
                        speaker = target_villager
                    else:
                        speaker = villager
                        
                    listener = target_villager if speaker == villager else villager
                    
                    # Son konuşan kişiyi kaydet
                    villager.last_speaker = speaker.name
                    
                    # Rastgele bir konu seçme olasılığı
                    if not hasattr(villager, 'conversation_topic') or random.random() < 0.4:
                        topic = random.choice(dialogue_manager.TOPICS)
                        villager.conversation_topic = topic
                    else:
                        # Mevcut konuya devam et
                        topic = villager.conversation_topic
                    
                    # Diyalog satırı üret
                    message = dialogue_manager.generate_dialogue_line(speaker, listener, topic)
                    
                    # Uzun mesajlar için daha uzun görünme süresi
                    if len(message) > 50:
                        message_display_time = 5  # 5 saniye
                    
                    # Soru mu kontrolü (daha sık soru sorulsun %40)
                    is_question = "?" in message or random.random() < 0.3
                    speaker.last_message_was_question = is_question
                    
                    # Eğer mesaj soru içermiyorsa ve soru olarak işaretlendiyse, soru eki ekle
                    if is_question and "?" not in message:
                        # Rastgele soru ekle
                        question_suffixes = [
                            ", değil mi?", 
                            ", sence de öyle mi?", 
                            ", sen ne düşünüyorsun?", 
                            ", senin fikrin nedir?",
                            "... Peki senin durumun nasıl?"
                        ]
                        message += random.choice(question_suffixes)
                        print(f"SORU EKLENDİ: {message}")
                    
                    if is_question:
                        print(f"YENİ SORU: {speaker.name} -> {listener.name}: '{message}'")
                        # Soruyu sakla - cevap vermek için kullanılacak
                        speaker.last_question_text = message
                    
                    # Aktif baloncuk kaydı
                    speaker.active_bubble = True
                    speaker.bubble_start_time = current_time
                    
                    # Diyalog baloncuğunu göster
                    if hasattr(speaker, 'game_controller') and speaker.game_controller:
                        bubble = speaker.game_controller.create_dialogue_bubble(speaker, message)
                        
                        # Baloncuğu geri döndürdüğünden emin ol
                        if bubble:
                            # Baloncuğun kaldırılması - baloncuk referansını koru
                            speaker.current_bubble = bubble
                            
                            # QTimer artık kullanmıyoruz, bunun yerine bubble_start_time kullanıyoruz
                            # ve her framedeki kontrol sistemi baloncukları yönetiyor
                            print(f"{speaker.name}'nin baloncuğu gösterildi, {message_display_time} saniye sonra silinecek")
                        else:
                            # Baloncuk oluşturulamadıysa aktif bayrak temizle
                            speaker.active_bubble = False
                    else:
                        # Game controller yok veya bubble oluşturulamadı
                        speaker.active_bubble = False
                    
                    # Diyaloğu kaydet
                    dialogue_manager.log_dialogue(speaker, listener, message)
                    
                    print(f"{speaker.name} -> {listener.name}: {message}")
                    
                    # İki köylü arasındaki ilişkiyi güncelle (her 3 mesajda bir)
                    if random.random() < 0.3:
                        dialogue_manager.update_relationship(speaker, listener)
                        
                    # Konuşma sayacını artır
                    villager.conversation_counter += 1
            
            # Son mesaj zamanını güncelle
            villager.last_chat_message_time = current_time
        
        # Sohbet süresini kontrol et
        if hasattr(villager, 'chat_end_time'):
            # Sohbet süresi dolduysa konuşmayı sonlandır
            if current_time > villager.chat_end_time:
                # Tüm baloncukların silindiğinden emin ol
                clear_all_dialogue_bubbles(villager)
                clear_all_dialogue_bubbles(target_villager)
                
                # Sohbeti sonlandır
                end_chat(villager, target_villager)
                return NodeStatus.SUCCESS
            
            # Sohbet süresi dolmamışsa, herhangi bir takılma var mı kontrol et
            elif hasattr(villager, 'last_message_was_question') and villager.last_message_was_question:
                # Son sorunun üzerinden çok zaman geçti mi?
                if hasattr(villager, 'last_chat_message_time') and current_time - villager.last_chat_message_time > 15:
                    # 15 saniyeden fazla bir soru takılı kaldıysa, otomatik sıfırla
                    print(f"UYARI: {villager.name}'nin sorusu 15 saniyeden fazla takılı kaldı, otomatik sıfırlanıyor")
                    villager.last_message_was_question = False
                    # Zorunlu konuşma değişikliği
                    villager.last_chat_message_time = current_time - 10
        
        # Takılı kalma kontrolü (acil çözüm) - Konuşma başladı ama uzun süredir devam etmiyorsa
        if hasattr(villager, 'last_chat_message_time'):
            # 60 saniyeden uzun süredir hiç konuşma olmadıysa, acil durum çözümü uygula
            if current_time - villager.last_chat_message_time > 60:
                print(f"UYARI: {villager.name} ve {target_villager.name} arasında 60 saniyedir konuşma yok - konuşma sonlandırılıyor")
                end_chat(villager, target_villager)
                return NodeStatus.SUCCESS
                    
        return NodeStatus.RUNNING
    except Exception as e:
        print(f"HATA: Sohbet devam ettirme hatası: {e}")
        import traceback
        traceback.print_exc()
        
        # Hata durumunda bile takılmayı önle
        try:
            if hasattr(villager, 'last_message_was_question'):
                villager.last_message_was_question = False
                
            # Kritik hata durumunda acil çözüm
            emergency_reset_villager(villager)
            if target_villager:
                emergency_reset_villager(target_villager)
        except:
            pass
            
        return NodeStatus.FAILURE

def end_chat(villager, target_villager):
    """Sohbeti sonlandırır ve köylülerin hareketine izin verir"""
    try:
        print(f"{villager.name} ve {target_villager.name if target_villager else 'Bilinmeyen'} arasındaki sohbet sonlandırılıyor.")
        
        # Her iki köylünün diyalog baloncuklarını temizle
        clear_all_dialogue_bubbles(villager)
        if target_villager:
            clear_all_dialogue_bubbles(target_villager)
        
        # Villager'ı resetle
        villager.is_chatting = False
        villager.chat_partner = None
        villager.state = WANDERING
        
        # Hareket etmeyi tekrar etkinleştir
        if hasattr(villager, 'moving'):
            villager.moving = True
        if hasattr(villager, 'is_wandering'):
            villager.is_wandering = True
            
        # Hızları geri yükle
        if hasattr(villager, 'speed') and hasattr(villager, '_original_speed'):
            villager.speed = villager._original_speed
        else:
            villager.speed = 0.35  # Varsayılan hız
            
        # Soru-cevap mekanizması bayrağını sıfırla
        if hasattr(villager, 'last_message_was_question'):
            villager.last_message_was_question = False
            
        # Konuşma sayacını sıfırla
        if hasattr(villager, 'conversation_counter'):
            villager.conversation_counter = 0
            
        # Son konuşan kişiyi sıfırla
        if hasattr(villager, 'last_speaker'):
            villager.last_speaker = None
            
        # Konuşma konusunu sıfırla
        if hasattr(villager, 'conversation_topic'):
            delattr(villager, 'conversation_topic')
        
        # Target villager'ı da güncelle
        if target_villager:
            target_villager.is_chatting = False
            target_villager.chat_partner = None
            target_villager.state = WANDERING
            
            # Hareket etmeyi tekrar etkinleştir
            if hasattr(target_villager, 'moving'):
                target_villager.moving = True
            if hasattr(target_villager, 'is_wandering'):
                target_villager.is_wandering = True
                
            # Hızları geri yükle
            if hasattr(target_villager, 'speed') and hasattr(target_villager, '_original_speed'):
                target_villager.speed = target_villager._original_speed
            else:
                target_villager.speed = 0.35  # Varsayılan hız
                
            # Soru-cevap mekanizması bayrağını sıfırla
            if hasattr(target_villager, 'last_message_was_question'):
                target_villager.last_message_was_question = False
                
            # Konuşma sayacını sıfırla
            if hasattr(target_villager, 'conversation_counter'):
                target_villager.conversation_counter = 0
                
            # Son konuşan kişiyi sıfırla
            if hasattr(target_villager, 'last_speaker'):
                target_villager.last_speaker = None
                
            # Konuşma konusunu sıfırla
            if hasattr(target_villager, 'conversation_topic'):
                delattr(target_villager, 'conversation_topic')
            
        # Rasgele yönlerde hareket et
        if hasattr(villager, 'vx'):
            villager.vx = random.uniform(-1, 1) * villager.speed
            villager.vy = random.uniform(-1, 1) * villager.speed
            
        if target_villager and hasattr(target_villager, 'vx'):
            target_villager.vx = random.uniform(-1, 1) * target_villager.speed
            target_villager.vy = random.uniform(-1, 1) * target_villager.speed
            
        return NodeStatus.SUCCESS
    except Exception as e:
        print(f"Sohbet sonlandırma hatası: {e}")
        import traceback
        traceback.print_exc()
        
        # Hata durumunda yine de en azından köylüleri serbest bırak
        try:
            if villager:
                villager.is_chatting = False
                villager.moving = True
                villager.state = WANDERING
                
            if target_villager:
                target_villager.is_chatting = False
                target_villager.moving = True
                target_villager.state = WANDERING
        except:
            pass
            
        return NodeStatus.FAILURE

def emergency_reset_villager(villager):
    """Takılı kalmış köylüyü acil durumda serbest bırakır"""
    try:
        print(f"ACİL DURUM: {villager.name} zorla serbest bırakılıyor.")
        
        # Tüm konuşma ve hareket verilerini sıfırla
        villager.is_chatting = False
        villager.chat_partner = None
        villager.moving = True
        villager.is_wandering = True
        villager.speed = 0.35
        villager.state = WANDERING
        
        # Tüm diyalog balonlarını temizle
        clear_all_dialogue_bubbles(villager)
        
        # Hareket vektörlerini sıfırla
        if hasattr(villager, 'vx'):
            villager.vx = random.uniform(-1, 1) * villager.speed
            villager.vy = random.uniform(-1, 1) * villager.speed
            
        # Diğer durumları sıfırla
        if hasattr(villager, 'active_bubble'):
            villager.active_bubble = False
        if hasattr(villager, 'current_bubble'):
            villager.current_bubble = None
        if hasattr(villager, 'last_message_was_question'):
            villager.last_message_was_question = False
        if hasattr(villager, 'conversation_data'):
            delattr(villager, 'conversation_data')
            
        return True
    except Exception as e:
        print(f"Acil durum kurtarma hatası: {e}")
        return False

def clear_all_dialogue_bubbles(villager):
    """Köylünün tüm aktif diyalog baloncuklarını temizler"""
    try:
        # Mevcut baloncuğu temizle
        if hasattr(villager, 'current_bubble') and villager.current_bubble:
            force_remove_bubble(villager, villager.current_bubble)
            
        # Game controller üzerinden tüm baloncukları temizle
        if hasattr(villager, 'game_controller') and villager.game_controller:
            villager.game_controller.clear_dialogue_bubbles(villager)
            
        # Aktif baloncuk bayrağını kapat
        if hasattr(villager, 'active_bubble'):
            villager.active_bubble = False
            
        # Baloncuk başlangıç zamanını sıfırla
        if hasattr(villager, 'bubble_start_time'):
            villager.bubble_start_time = 0
    except Exception as e:
        print(f"Baloncuk temizleme hatası: {e}")
        
def end_chat(villager, target_villager):
    """İki köylü arasındaki sohbeti sonlandırır"""
    try:
        print(f"{villager.name} ve {target_villager.name if target_villager else 'Bilinmeyen'} arasındaki sohbet sonlandırılıyor.")
        
        # Her iki köylünün diyalog baloncuklarını temizle
        clear_all_dialogue_bubbles(villager)
        if target_villager:
            clear_all_dialogue_bubbles(target_villager)
        
        # Villager'ı resetle
        villager.is_chatting = False
        villager.chat_partner = None
        villager.state = WANDERING
        
        # Hareket etmeyi tekrar etkinleştir
        if hasattr(villager, 'moving'):
            villager.moving = True
        if hasattr(villager, 'is_wandering'):
            villager.is_wandering = True
            
        # Hızları geri yükle
        if hasattr(villager, 'speed') and hasattr(villager, '_original_speed'):
            villager.speed = villager._original_speed
        else:
            villager.speed = 0.35  # Varsayılan hız
            
        # Soru-cevap mekanizması bayrağını sıfırla
        if hasattr(villager, 'last_message_was_question'):
            villager.last_message_was_question = False
            
        # Konuşma sayacını sıfırla
        if hasattr(villager, 'conversation_counter'):
            villager.conversation_counter = 0
            
        # Son konuşan kişiyi sıfırla
        if hasattr(villager, 'last_speaker'):
            villager.last_speaker = None
            
        # Konuşma konusunu sıfırla
        if hasattr(villager, 'conversation_topic'):
            delattr(villager, 'conversation_topic')
        
        # Target villager'ı da güncelle
        if target_villager:
            target_villager.is_chatting = False
            target_villager.chat_partner = None
            target_villager.state = WANDERING
            
            # Hareket etmeyi tekrar etkinleştir
            if hasattr(target_villager, 'moving'):
                target_villager.moving = True
            if hasattr(target_villager, 'is_wandering'):
                target_villager.is_wandering = True
                
            # Hızları geri yükle
            if hasattr(target_villager, 'speed') and hasattr(target_villager, '_original_speed'):
                target_villager.speed = target_villager._original_speed
            else:
                target_villager.speed = 0.35  # Varsayılan hız
                
            # Soru-cevap mekanizması bayrağını sıfırla
            if hasattr(target_villager, 'last_message_was_question'):
                target_villager.last_message_was_question = False
                
            # Konuşma sayacını sıfırla
            if hasattr(target_villager, 'conversation_counter'):
                target_villager.conversation_counter = 0
                
            # Son konuşan kişiyi sıfırla
            if hasattr(target_villager, 'last_speaker'):
                target_villager.last_speaker = None
                
            # Konuşma konusunu sıfırla
            if hasattr(target_villager, 'conversation_topic'):
                delattr(target_villager, 'conversation_topic')
            
        # Rasgele yönlerde hareket et
        if hasattr(villager, 'vx'):
            villager.vx = random.uniform(-1, 1) * villager.speed
            villager.vy = random.uniform(-1, 1) * villager.speed
            
        if target_villager and hasattr(target_villager, 'vx'):
            target_villager.vx = random.uniform(-1, 1) * target_villager.speed
            target_villager.vy = random.uniform(-1, 1) * target_villager.speed
            
        return NodeStatus.SUCCESS
    except Exception as e:
        print(f"Sohbet sonlandırma hatası: {e}")
        import traceback
        traceback.print_exc()
        
        # Hata durumunda yine de en azından köylüleri serbest bırak
        try:
            if villager:
                villager.is_chatting = False
                villager.moving = True
                villager.state = WANDERING
                
            if target_villager:
                target_villager.is_chatting = False
                target_villager.moving = True
                target_villager.state = WANDERING
        except:
            pass
            
        return NodeStatus.FAILURE

def emergency_reset_villager(villager):
    """Köylüyü acil durumda serbest bırak"""
    try:
        print(f"ACİL DURUM: {villager.name} zorla serbest bırakılıyor!")
        
        # Tüm baloncukları temizle
        clear_all_dialogue_bubbles(villager)
        
        # Tüm bayrakları sıfırla
        if hasattr(villager, 'is_chatting'):
            villager.is_chatting = False
        if hasattr(villager, 'chat_partner'):
            villager.chat_partner = None
        if hasattr(villager, 'moving'):
            villager.moving = True
        if hasattr(villager, 'is_wandering'):
            villager.is_wandering = True
        if hasattr(villager, 'speed'):
            if hasattr(villager, '_original_speed'):
                villager.speed = villager._original_speed
            else:
                villager.speed = 0.35  # Varsayılan hız
        if hasattr(villager, 'state'):
            villager.state = WANDERING
        if hasattr(villager, 'last_message_was_question'):
            villager.last_message_was_question = False
        if hasattr(villager, 'vx'):
            villager.vx = 0
        if hasattr(villager, 'vy'):
            villager.vy = 0
            
        # Cooldown zamanını 5 saniye sonrasına ayarla
        villager.chat_cooldown = time.time() + 5
            
        return True
    except Exception as e:
        print(f"ACİL DURUM RESET HATASI: {e}")
        return False

# Diyalog baloncuklarını temizlemek için fonksiyonlar

def force_remove_bubble(villager, bubble):
    """Baloncuğu zorla kaldırır"""
    try:
        if hasattr(villager, 'game_controller') and villager.game_controller:
            if hasattr(villager.game_controller, 'remove_dialogue_bubble'):
                # Baloncuğu kaldır
                villager.game_controller.remove_dialogue_bubble(bubble)
            
        # Aktif bayrağı ve mevcut baloncuğu temizle
        villager.active_bubble = False
        villager.current_bubble = None
        
        print(f"{villager.name}'nin baloncuğu zorla kaldırıldı")
    except Exception as e:
        print(f"Baloncuk kaldırma hatası: {e}")

def clear_all_dialogue_bubbles(villager):
    """Köylünün tüm aktif diyalog baloncuklarını temizler"""
    try:
        # Mevcut baloncuğu varsa kaldır
        if hasattr(villager, 'current_bubble') and villager.current_bubble:
            force_remove_bubble(villager, villager.current_bubble)
        
        # Ekstra güvenlik - aktif bayrağı temizleme
        if hasattr(villager, 'active_bubble'):
            villager.active_bubble = False
        
        print(f"{villager.name}'nin tüm baloncukları temizlendi")
    except Exception as e:
        print(f"Tüm baloncukları temizleme hatası: {e}")

def remove_dialogue_bubble(villager, bubble):
    """Diyalog baloncuğunu kaldırır"""
    try:
        # Baloncuk geçerli mi kontrol et
        if not bubble:
            return
            
        # Game controller mevcut mu kontrol et
        if not hasattr(villager, 'game_controller') or not villager.game_controller:
            return
            
        # Fonksiyon mevcut mu kontrol et
        if hasattr(villager.game_controller, 'remove_dialogue_bubble'):
            # Lambda yöntemiyle doğru işlev referansını geçir
            # Bu, kapanma (closure) ile doğru şekilde çalışmasını sağlar
            villager.game_controller.remove_dialogue_bubble(bubble)
            
            # Temizleme işlemi tamamlandı
            villager.active_bubble = False
            villager.current_bubble = None
            
    except Exception as e:
        print(f"Baloncuk kaldırma hatası: {e}")
        # Hata olsa bile bayrağı temizlemeye çalış
        if hasattr(villager, 'active_bubble'):
            villager.active_bubble = False