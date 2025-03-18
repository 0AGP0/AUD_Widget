import random
import time
from typing import List, Dict, Tuple, Optional, Any

class DialogueManager:
    """Köylüler arası diyalogları yöneten sınıf"""
    
    # İyi özellikler
    GOOD_TRAITS = [
        "Çalışkan", "Karizmatik", "Babacan", "Romantik", "Merhametli", 
        "Sabırlı", "Esprili", "Güvenilir", "Meraklı", "Dikkatli", 
        "İyimser", "Pratik", "Mantıklı", "Soğukkanlı", "Cömert"
    ]
    
    # Kötü özellikler
    BAD_TRAITS = [
        "Tembel", "Sinirli", "Yobaz", "İnatçı", "Kurnaz", "Hırslı", 
        "Sabırsız", "Karamsar", "Duygusal", "Kıskanç", "Merhametsiz", 
        "İlgisiz"
    ]
    
    # Konuşma konuları
    TOPICS = [
        "hava_durumu", "hasat", "dedikodu", "aile", "yemek", 
        "köy_hayatı", "politika", "din", "savaş", "evlilik",
        "ticaret", "hayvanlar", "hobi", "gelenek", "tarih"
    ]
    
    # İlişki seviyelerine göre diyalog tipleri
    RELATIONSHIP_DIALOGUE = {
        "Düşman": [
            "Benden uzak dur, {name}!",
            "Yine mi sen? Görmek istemiyorum seni.",
            "Seninle konuşacak bir şeyim yok.",
            "Kaybol gözümün önünden!",
            "Seni gördüğüme sevinemedim, {name}."
        ],
        "Hoşlanmıyor": [
            "Hmm, merhaba {name}.",
            "Ne istiyorsun?",
            "Acelem var şu an.",
            "Başka zaman konuşalım mı?",
            "Bugün pek havamda değilim."
        ],
        "Nötr": [
            "Merhaba {name}, nasılsın?",
            "Selam, bugün hava çok güzel.",
            "İşler nasıl gidiyor?",
            "Günün nasıl geçiyor?",
            "Bu aralar neler yapıyorsun?"
        ],
        "İyi": [
            "Selam dostum, seni görmek güzel!",
            "Nasılsın bakalım {name}?",
            "Bugün çok iyi görünüyorsun.",
            "Seninle konuşmak her zaman keyifli.",
            "Seni yine görmek güzel oldu."
        ],
        "Dost": [
            "{name}! Dostum, ne kadar özledim seni!",
            "İşte benim en iyi arkadaşım geldi!",
            "Nasılsın canım arkadaşım?",
            "Seni gördüğüme çok sevindim!",
            "Harika görünüyorsun bugün, ne oldu?"
        ]
    }
    
    # Ruh haline göre diyaloglar
    MOOD_DIALOGUE = {
        "Mutlu": [
            "Bugün harika bir gün!",
            "Kendimi çok iyi hissediyorum!",
            "Bu köyde yaşamak çok güzel.",
            "Her şey harika gidiyor!",
            "Gülümsemeden duramıyorum bugün."
        ],
        "Üzgün": [
            "Bugün kendimi pek iyi hissetmiyorum...",
            "Dün gece hiç uyuyamadım.",
            "Bazen hayat çok zor.",
            "Son zamanlarda biraz kederli hissediyorum.",
            "Umarım yarın daha iyi olurum."
        ],
        "Sinirli": [
            "Bugün herkes beni sinirlendiriyor.",
            "Bu işlerden bıktım artık!",
            "Şu kale muhafızları hiçbir işe yaramıyor.",
            "Hiçbir şey yolunda gitmiyor.",
            "Kimseyle uğraşacak havamda değilim."
        ],
        "Sakin": [
            "Her şey yolunda, telaşa gerek yok.",
            "Bugün huzurlu bir gün.",
            "Sakin olmak en iyisi.",
            "Hayat akıp gidiyor işte.",
            "Bu güzel günün tadını çıkaralım."
        ]
    }
    
    # Mesleklere göre diyaloglar
    PROFESSION_DIALOGUE = {
        "Oduncu": [
            "Bugün beş ağaç kestim.",
            "Baltam eski ama hâlâ keskin.",
            "Kışa hazırlık için daha çok odun kesmeliyiz.",
            "Bu ormanda çalışmak huzur veriyor.",
            "Sırtım ağrıyor, çok çalıştım bugün."
        ],
        "İnşaatçı": [
            "Yeni bir ev inşa etmeye başladım.",
            "Taş temeller en sağlam olanlardır.",
            "Bu köy giderek büyüyor.",
            "Dayanıklı evler inşa etmek için iyi malzeme şart.",
            "Çekiç kullanmakta üstüme yoktur."
        ],
        "Avcı": [
            "Dün kocaman bir geyik avladım.",
            "Yayım ve oklarım her zaman yanımda.",
            "Ormanın tehlikelerini iyi bilirim.",
            "Av mevsimi yaklaşıyor.",
            "Bu bölgedeki hayvanları iyi tanırım."
        ],
        "Çiftçi": [
            "Ekinler bu yıl çok bereketli.",
            "Yağmur yağmazsa mahsul zarar görecek.",
            "Toprak, emeğini her zaman ödüllendirir.",
            "Baharda yeni tohum ekmeliyiz.",
            "Tarla sürme zamanı geldi."
        ],
        "Gardiyan": [
            "Köyümüzü her türlü tehlikeden koruyacağım.",
            "Dün gece şüpheli biri gördüm.",
            "Silahımı her zaman yanımda taşırım.",
            "Devriye gezmek yorucu ama gerekli.",
            "Huzur içinde uyuyabilirsiniz, ben nöbetteyim."
        ],
        "Papaz": [
            "Tanrı hepimizi korusun.",
            "Bugün tapınakta dua ettim.",
            "İnancımız bize güç verir.",
            "Ruhunuzun huzuru için dua etmeyi unutmayın.",
            "Bu hafta yeni bir ayin düzenleyeceğim."
        ],
        "": [  # İşsizler için
            "Kendime bir meslek arıyorum.",
            "Bu köyde iş bulmak zor.",
            "Belki de başka bir köye gitmeliyim.",
            "Yeteneklerimi gösterebileceğim bir iş istiyorum.",
            "Para kazanmanın bir yolunu bulmalıyım."
        ]
    }
    
    # Konulara göre diyaloglar
    TOPIC_DIALOGUE = {
        "hava_durumu": [
            "Bugün hava çok güzel, değil mi?",
            "Yağmur yağacak gibi görünüyor.",
            "Bu sıcaklar beni bunaltıyor.",
            "Kış yaklaşıyor, hazırlık yapmalıyız.",
            "Rüzgar bugün çok sert esiyor."
        ],
        "hasat": [
            "Bu yılki hasat nasıl görünüyor?",
            "Ürünler olgunlaşmaya başladı.",
            "Çiftçiler çok çalışıyor bu günlerde.",
            "Ambarları doldurmanın zamanı geldi.",
            "Buğdaylar altın gibi parlıyor tarlada."
        ],
        "dedikodu": [
            "Duydun mu? {random_name} ve {random_name2} görüşüyormuş.",
            "Kale muhafızı dün sarhoş yakalanmış.",
            "Yeni gelen tüccar bence güvenilmez biri.",
            "{random_name}'in yeni evi çok gösterişli olmuş.",
            "Dün gece köyün dışında garip sesler duyulmuş."
        ],
        "aile": [
            "Çocukların nasıl?",
            "Ailenle vakit geçirmek güzeldir.",
            "Büyükbabam bana hep hikayeler anlatırdı.",
            "Aile bağları en kıymetli şeydir.",
            "Annem harika yemekler yapardı."
        ],
        "yemek": [
            "Akşam yemeği için ne pişirdin?",
            "Taze ekmek kokusu en güzelidir.",
            "Av etini nasıl pişirirsin?",
            "Bu yörenin özel yemekleri çok lezzetli.",
            "Mantar toplamayı severim, lezzetli olurlar."
        ],
        "köy_hayatı": [
            "Bu köyde yaşamak huzur verici.",
            "Şehir hayatı karmaşık, burada olmak daha iyi.",
            "Köy meydanında yapılan şenlikler çok eğlenceli.",
            "Komşular birbirine yardım eder burada.",
            "Köy hayatının zorlukları da var tabii."
        ],
        "politika": [
            "Lord'un yeni kararları hakkında ne düşünüyorsun?",
            "Vergiler giderek artıyor.",
            "Krallık bu savaştan galip çıkacak mı?",
            "Yeni kanunlar köylüleri zorluyor.",
            "Liderlerimiz bizi düşünüyor mu gerçekten?"
        ],
        "din": [
            "Dün tapınağa gittin mi?",
            "İnancın insana güç verir.",
            "Tanrılar bizi korusun.",
            "Bu yıl hasat festivali görkemli olacak.",
            "Dua etmek ruhumu dinlendiriyor."
        ],
        "savaş": [
            "Sınırdaki çatışmalar devam ediyormuş.",
            "Gençlerimizi savaşa gönderiyorlar.",
            "Savaş hiçbir sorunu çözmez.",
            "Barış zamanı geri gelecek mi?",
            "Askerler köyden geçerken gördün mü?"
        ],
        "evlilik": [
            "Evlilik hayatı nasıl gidiyor?",
            "Doğru eşi bulmak önemli.",
            "Düğün hazırlıkları başladı mı?",
            "Evlenmek için doğru zaman ne zamandır?",
            "Bir aile kurmak istiyorum."
        ],
        "ticaret": [
            "Pazarda fiyatlar sürekli artıyor.",
            "Gezgin tüccarlar ne zaman gelecek?",
            "İyi bir alışveriş yaptım bugün.",
            "Mallarını satabildin mi?",
            "Komşu köylerdeki mallar daha ucuz."
        ],
        "hayvanlar": [
            "İneklerim süt vermekte zorlanıyor bu aralar.",
            "Vahşi hayvanlar sürülerime saldırdı.",
            "İyi bir av köpeği edinmek istiyorum.",
            "Atım hastalandı, endişeliyim.",
            "Kış için hayvanları ahıra almalıyız."
        ],
        "hobi": [
            "Boş zamanlarımda ağaç oymacılığı yapıyorum.",
            "Balık tutmak beni rahatlatıyor.",
            "Şarkı söylemeyi severim, sen de katılır mısın?",
            "Hikaye anlatma gecesi düzenlemeliyiz.",
            "El işi yapmak için malzeme arıyorum."
        ],
        "gelenek": [
            "Atalarımızın geleneklerini yaşatmalıyız.",
            "Hasat festivali yaklaşıyor, hazırlanıyor musun?",
            "Köyümüzün dans gösterileri meşhurdur.",
            "Bu ritüeli nasıl yapacağımızı hatırlamıyorum.",
            "Geleneklerimiz bizi bir arada tutar."
        ],
        "tarih": [
            "Büyük savaştan sonra köyümüz yeniden inşa edildi.",
            "Atalarımız bu topraklara nasıl gelmiş biliyor musun?",
            "Eski kale kalıntılarını ziyaret ettin mi hiç?",
            "Köyümüzün tarihi çok eskilere dayanır.",
            "Yaşlı bilge bize geçmişten hikayeler anlatırdı."
        ]
    }
    
    def __init__(self):
        self.dialogue_history = []
        self.chat_logs = []
        self.pending_responses = {}
        self.game_controller = None
        
    def set_game_controller(self, game_controller):
        """Oyun kontrolcüsünü ayarla"""
        self.game_controller = game_controller
        
    def generate_greeting(self, speaker: 'Villager', listener: 'Villager') -> str:
        """İki köylü arasındaki selamlaşma diyaloğunu oluşturur"""
        try:
            # İlişki seviyesine göre selamlaşma mesajı
            relationship = speaker.get_relationship_with(listener)
            greetings = self.RELATIONSHIP_DIALOGUE.get(relationship, self.RELATIONSHIP_DIALOGUE["Nötr"])
            
            # İsim formatlaması
            greeting = random.choice(greetings).format(name=listener.name)
            return greeting
            
        except Exception as e:
            print(f"HATA: Selamlaşma mesajı oluşturma hatası: {e}")
            return f"Merhaba {listener.name}."
    
    def generate_dialogue_line(self, speaker: 'Villager', listener: 'Villager', topic: str = None) -> str:
        """İki köylü arasındaki bir diyalog satırını oluşturur"""
        try:
            # Konu belirlenmemişse rastgele seç
            if not topic:
                topic = random.choice(self.TOPICS)
            
            # Diyalog oluşturma şansları
            chances = {
                "relationship": 0.3,  # İlişki durumu
                "mood": 0.3,          # Ruh hali
                "profession": 0.2,    # Meslek
                "topic": 0.2          # Genel konu
            }
            
            # Rastgele diyalog tipi seç
            dialogue_type = random.choices(
                list(chances.keys()), 
                weights=list(chances.values()),
                k=1
            )[0]
            
            if dialogue_type == "relationship":
                relationship = speaker.get_relationship_with(listener)
                dialogues = self.RELATIONSHIP_DIALOGUE.get(relationship, self.RELATIONSHIP_DIALOGUE["Nötr"])
                dialogue = random.choice(dialogues)
                
            elif dialogue_type == "mood":
                dialogues = self.MOOD_DIALOGUE.get(speaker.mood, self.MOOD_DIALOGUE["Sakin"])
                dialogue = random.choice(dialogues)
                
            elif dialogue_type == "profession":
                dialogues = self.PROFESSION_DIALOGUE.get(speaker.profession, self.PROFESSION_DIALOGUE[""])
                dialogue = random.choice(dialogues)
                
            else:  # topic
                random_names = []
                if "random_name" in str(self.TOPIC_DIALOGUE.get(topic, [""])[0]):
                    if hasattr(speaker, 'game_controller') and speaker.game_controller:
                        villagers = speaker.game_controller.villagers
                        if len(villagers) >= 2:
                            random_names = random.sample([v.name for v in villagers if v != speaker and v != listener], 
                                                         min(2, len(villagers)-2))
                            
                            # Eğer yeterli köylü yoksa, köylü isimlerini oluştur
                            while len(random_names) < 2:
                                fake_names = ["Ahmet", "Mehmet", "Ayşe", "Fatma", "Ali", "Veli", "Zeynep", "Elif"]
                                random_names.append(random.choice(fake_names))
                
                dialogues = self.TOPIC_DIALOGUE.get(topic, self.TOPIC_DIALOGUE["köy_hayatı"])
                dialogue = random.choice(dialogues)
                
                # Random isimleri ekle
                if random_names and "{random_name}" in dialogue:
                    dialogue = dialogue.format(random_name=random_names[0], 
                                             random_name2=random_names[1] if len(random_names) > 1 else random_names[0])
            
            # İsim formatlaması (eğer gerekiyorsa)
            dialogue = dialogue.format(name=listener.name)
            return dialogue
            
        except Exception as e:
            print(f"HATA: Diyalog satırı oluşturma hatası: {e}")
            return f"Bugün nasılsın {listener.name}?"
            
    def calculate_relationship_change(self, speaker: 'Villager', listener: 'Villager') -> int:
        """İki köylü arasındaki ilişki değişimini hesaplar"""
        try:
            # Temel değişim
            base_change = 0
            
            # Ruh haline göre değişim
            mood_effect = {
                "Mutlu": 5,     # Mutlu köylü ilişkiyi olumlu etkiler
                "Üzgün": -2,    # Üzgün köylü ilişkiyi biraz olumsuz etkiler
                "Sinirli": -5,  # Sinirli köylü ilişkiyi olumsuz etkiler
                "Sakin": 2      # Sakin köylü ilişkiyi biraz olumlu etkiler
            }
            
            # Köylülerin ruh hallerine göre değişimi hesapla
            base_change += mood_effect.get(speaker.mood, 0)
            base_change += mood_effect.get(listener.mood, 0)
            
            # Ortak özellik sayısı
            compatible_traits = 0
            incompatible_traits = 0
            
            # İyi ve kötü özelliklerin uyumluluğunu kontrol et
            for trait in speaker.traits:
                if trait in self.GOOD_TRAITS and trait in listener.traits:
                    compatible_traits += 1
                elif trait in self.BAD_TRAITS and trait in listener.traits:
                    compatible_traits += 1  # Benzer kötü özellikler de uyumlu sayılır
                elif trait in self.GOOD_TRAITS and any(t in self.BAD_TRAITS for t in listener.traits):
                    incompatible_traits += 1
            
            # Uyumlu ve uyumsuz özelliklere göre değişim
            base_change += compatible_traits * 3
            base_change -= incompatible_traits * 2
            
            # Aynı meslekteyse bonus
            if speaker.profession == listener.profession and speaker.profession:
                base_change += 2
            
            # Mevcut ilişki seviyesine göre ayarla
            current_relationship = speaker.relationships.get(listener.name, 0)
            if current_relationship >= 50:  # Zaten iyi bir ilişki varsa, değişim daha az
                base_change = max(0, int(base_change * 0.7))
            elif current_relationship <= -50:  # Zaten kötü bir ilişki varsa, değişim daha az
                base_change = min(0, int(base_change * 0.7))
            
            # Rastgele değişim ekle (-2 ile +2 arası)
            base_change += random.randint(-2, 2)
            
            return base_change
            
        except Exception as e:
            print(f"HATA: İlişki değişimi hesaplama hatası: {e}")
            return 0
    
    def update_relationship(self, speaker: 'Villager', listener: 'Villager'):
        """İki köylü arasındaki ilişkiyi günceller"""
        try:
            # İlişki değişimini hesapla
            change = self.calculate_relationship_change(speaker, listener)
            
            # İlişkiyi güncelle
            if change > 0:
                speaker.increase_relationship(listener)
                listener.increase_relationship(speaker)
                print(f"{speaker.name} ve {listener.name} arasındaki ilişki olumlu yönde gelişti (+{change})")
            elif change < 0:
                speaker.decrease_relationship(listener)
                listener.decrease_relationship(speaker)
                print(f"{speaker.name} ve {listener.name} arasındaki ilişki olumsuz yönde gelişti ({change})")
            
        except Exception as e:
            print(f"HATA: İlişki güncelleme hatası: {e}")
    
    def log_dialogue(self, speaker: 'Villager', listener: 'Villager', message: str):
        """Diyaloğu kayıt altına alır"""
        try:
            dialogue_entry = {
                'speaker': speaker.name,
                'listener': listener.name,
                'message': message,
                'time': time.time(),
                'relationship': speaker.get_relationship_with(listener)
            }
            
            self.dialogue_history.append(dialogue_entry)
            
            # Son 100 diyaloğu tut
            if len(self.dialogue_history) > 100:
                self.dialogue_history = self.dialogue_history[-100:]
            
            # Oyun kontrolcüsüne ilet
            if self.game_controller and hasattr(self.game_controller, 'control_panel'):
                try:
                    self.game_controller.control_panel.add_dialogue_to_chat(
                        speaker.name,
                        listener.name,
                        message,
                        speaker.get_relationship_with(listener)
                    )
                except Exception as e:
                    print(f"HATA: Diyalog kontrolcüye iletilemedi: {e}")
                
        except Exception as e:
            print(f"HATA: Diyalog kaydetme hatası: {e}")
    
    def get_recent_dialogues(self, count: int = 10) -> List[Dict]:
        """Son diyalogları döndürür"""
        try:
            return self.dialogue_history[-count:] if self.dialogue_history else []
        except Exception as e:
            print(f"HATA: Son diyalogları alma hatası: {e}")
            return []
    
    def generate_response(self, question_asker: 'Villager', responder: 'Villager', topic: str = None) -> str:
        """Sorulan soruya cevap oluşturur"""
        try:
            # Son sorulan soruyu bul
            last_message = ""
            
            # Önce doğrudan diyalog geçmişinden bakalım
            for entry in reversed(self.dialogue_history):
                if entry['speaker'] == question_asker.name and entry['listener'] == responder.name:
                    last_message = entry['message']
                    break
            
            # Eğer son mesaj bulunamadıysa veya boşsa default mesaj kullan
            if not last_message:
                last_message = "Nasılsın?"
                print(f"Uyarı: Son mesaj bulunamadı, varsayılan soru kullanılıyor.")
            
            print(f"CEVAP ÜRETME: {question_asker.name}'nin sorusu: '{last_message}' cevaplanıyor...")
            
            # Konu belirlenmemişse rastgele seç
            if not topic:
                topic = random.choice(self.TOPICS)
            
            # Gelen soruya özel cevaplar (basit kelime eşleştirmesi yapıyoruz)
            if "nasılsın" in last_message.lower():
                mood_responses = {
                    "Mutlu": ["Çok iyiyim, teşekkür ederim!", "Harika hissediyorum bugün!", "Mükemmel!", "Kendimi hiç olmadığım kadar iyi hissediyorum."],
                    "Üzgün": ["İdare ediyorum...", "Daha iyi olabilirdim.", "Biraz keyfim yok bugün.", "Zor günler geçiriyorum."],
                    "Sinirli": ["Sorma, çok sinirliyim.", "Kötü, bugün her şey ters gidiyor.", "Sabrımı zorlayan bazı şeyler oldu."],
                    "Sakin": ["İyiyim, teşekkürler.", "Huzurluyum, teşekkür ederim.", "Sakin bir gün geçiriyorum.", "Her zamanki gibi."]
                }
                mood = responder.mood if hasattr(responder, 'mood') and responder.mood else "Sakin"
                return random.choice(mood_responses.get(mood, mood_responses["Sakin"]))
            
            elif "ne yapıyorsun" in last_message.lower() or "neler yapıyorsun" in last_message.lower():
                profession_responses = {
                    "Oduncu": ["Ormanda odun kesiyordum.", "Baltamı biliyordum.", "Kışa hazırlık için odun topluyordum."],
                    "İnşaatçı": ["Yeni ev planları yapıyordum.", "Köyün batı tarafına bir ev inşa ediyorum.", "İnşaat malzemeleri arıyordum."],
                    "Avcı": ["Avdan yeni döndüm.", "Yarın büyük bir av için hazırlanıyorum.", "Av ekipmanlarımı tamir ediyordum."],
                    "Çiftçi": ["Tarlada çalışıyordum.", "Ekinleri suluyordum.", "Hasat hazırlıkları yapıyordum."],
                    "Gardiyan": ["Devriye geziyordum.", "Köy sınırlarını kontrol ediyordum.", "Silahımı bakımdan geçiriyordum."],
                    "Papaz": ["Dualar okuyordum.", "Tapınağı temizliyordum.", "İbadetimi yerine getiriyordum."],
                    "": ["Dolaşıyordum.", "Köyde vakit geçiriyordum.", "Kendime yapacak bir şeyler arıyordum."]
                }
                profession = responder.profession if hasattr(responder, 'profession') and responder.profession else ""
                return random.choice(profession_responses.get(profession, profession_responses[""])) 
            
            elif "hava" in last_message.lower() and "nasıl" in last_message.lower():
                weather_responses = ["Bugün hava çok güzel.", 
                                   "Biraz serin ama güneşli.", 
                                   "Yağmur yağacak gibi görünüyor.", 
                                   "Böyle güzel havalar çok sürmez.",
                                   "Bulutlu ama yağmur beklemiyorum."]
                return random.choice(weather_responses)
            
            elif "ne düşünüyorsun" in last_message.lower() or "fikrin ne" in last_message.lower():
                topic_opinions = {
                    "hava_durumu": ["Bu mevsimde hava hep böyle değişken olur.", "Yağmur yağarsa ekinler için iyi olur."],
                    "hasat": ["Bu yıl hasat bereketli görünüyor.", "Geçen yıla göre daha iyi bir hasat bekliyorum."],
                    "dedikodu": ["İnsanların arkasından konuşmayı doğru bulmuyorum.", "Köyde her zaman ilginç söylentiler dolaşır."],
                    "aile": ["Aile her şeyden önemlidir.", "Ailemi çok özlüyorum."],
                    "yemek": ["Avlanmış taze et kadar güzeli yoktur.", "İyi bir yemek ruhun gıdasıdır."],
                    "köy_hayatı": ["Köy hayatı zor ama huzurlu.", "Şehir hayatı bana göre değil, köyü seviyorum."],
                    "politika": ["Liderlerimiz bazen bizi unutuyor.", "Vergiler çok yüksek, köylüler zorlanıyor."],
                    "din": ["İnançlı olmak insana güç verir.", "Tanrılar bizi koruyor, şükretmeliyiz."],
                    "savaş": ["Savaşlar sadece acı getirir.", "Barış içinde yaşamak en güzeli."],
                    "evlilik": ["Doğru kişiyi bulmak önemli.", "Evlilik büyük sorumluluk gerektirir."],
                    "ticaret": ["Adil ticaret herkes için iyidir.", "Tüccarlar bazen fazla kâr peşinde koşuyor."],
                    "hayvanlar": ["Hayvanlar en sadık dostlarımızdır.", "Doğayla uyum içinde yaşamalıyız."],
                    "hobi": ["Boş zamanlarımda el işi yapmayı seviyorum.", "Herkesin bir hobisi olmalı."],
                    "gelenek": ["Geleneklerimiz bizi biz yapar.", "Bazı gelenekler çağın gerisinde kalıyor."],
                    "tarih": ["Geçmişten ders almalıyız.", "Atalarımızın hikayeleri önemli."]
                }
                return random.choice(topic_opinions.get(topic, topic_opinions["köy_hayatı"]))
            
            elif "merhaba" in last_message.lower() or "selam" in last_message.lower():
                greetings_back = ["Ben de seni gördüğüme sevindim.", 
                                "Selam, nasılsın?", 
                                "Merhaba, bugün nasıl gidiyor?",
                                "Seninle karşılaşmak güzel oldu.",
                                "Selam, işlerin nasıl gidiyor?"]
                return random.choice(greetings_back)
            
            elif "mesleğin" in last_message.lower() or "ne iş yap" in last_message.lower():
                profession = responder.profession if hasattr(responder, 'profession') and responder.profession else ""
                if profession:
                    return f"Ben bir {profession}im. {random.choice(['Bu işi seviyorum.', 'Zor ama tatmin edici bir iş.', 'Bu mesleği ailemden öğrendim.'])}"
                else:
                    return "Henüz bir mesleğim yok, kendime uygun bir iş arıyorum."
            
            elif "aile" in last_message.lower() or "çocuk" in last_message.lower():
                family_responses = ["Ailem başka bir köyde yaşıyor.", 
                                   "Henüz çocuğum yok, belki ilerde.", 
                                   "Ailem benim için çok önemli.", 
                                   "Büyük bir ailem var, beş kardeşiz.",
                                   "Annem ve babam hala hayatta, onları sık görüyorum."]
                return random.choice(family_responses)
            
            # Daha genel soru algılama için
            elif "?" in last_message:
                # Eğer spesifik bir konu hakkında soru varsa bul
                detected_topic = None
                for key_topic in self.TOPICS:
                    if key_topic.replace("_", " ") in last_message.lower():
                        detected_topic = key_topic
                        break
                
                # Eğer konu algılandıysa onu kullan, yoksa varsayılanı
                topic_to_use = detected_topic if detected_topic else topic
                
                # Genel sorular için konuya bağlı cevaplar
                general_responses = {
                    "hava_durumu": ["Bence bugün yağmur yağmayacak.", "Havalar yakında soğuyacak gibi.", "Bu mevsimde hava çok değişken."],
                    "hasat": ["Ekinler iyi görünüyor bu yıl.", "Hasat zamanı yaklaşıyor, hazır olmalıyız.", "Geçen yıldan daha iyi bir hasat bekliyorum."],
                    "dedikodu": ["Söylentilere pek kulak asmam.", "Köyde her zaman ilginç dedikodular dolaşır.", "Başkalarının işine karışmamaya çalışırım."],
                    "aile": ["Aile bağları çok önemlidir.", "Her ailenin kendine özgü zorlukları vardır.", "Sevdiklerinizle vakit geçirmek en güzeli."],
                    "yemek": ["İyi bir yemek için taze malzeme şart.", "Annemin tarifleri hâlâ favorim.", "Yemek yapmayı ben de severim."],
                    "köy_hayatı": ["Köy hayatı zor ama huzur verici.", "Şehirde yaşayamazdım.", "Doğayla iç içe olmak güzel."],
                    "politika": ["Siyasetten pek anlamam.", "Liderler hep kendi çıkarlarını düşünüyor.", "Daha adil bir yönetim olmalı."],
                    "din": ["İnancım bana güç veriyor.", "Herkes istediğine inanmakta özgür olmalı.", "Düzenli olarak tapınağa giderim."],
                    "savaş": ["Savaş hiçbir sorunu çözmez.", "Barış içinde yaşamak dileğim.", "Çatışmadan uzak durmak en iyisi."],
                    "evlilik": ["Evlilik büyük bir adım.", "Doğru kişiyi bulmak önemli.", "Her evlilikte zorluklar olur."],
                    "ticaret": ["Dürüst ticaret herkes için iyidir.", "Pazarda iyi pazarlık yaparım.", "Ticarette güven önemlidir."],
                    "hayvanlar": ["Hayvanlarla arası iyi olan insanları severim.", "Her hayvanın kendine özgü bir karakteri vardır.", "Doğayla uyum içinde yaşamalıyız."],
                    "hobi": ["Boş zamanımda ağaç oymacılığı yaparım.", "Hobilerimiz bizi mutlu eder.", "Yeni şeyler öğrenmek için hiçbir zaman geç değil."],
                    "gelenek": ["Geleneklerimiz köklerimizi hatırlatır.", "Bazı gelenekler değişmeli.", "Festival zamanlarını severim."],
                    "tarih": ["Tarihten ders almalıyız.", "Geçmiş, geleceğimize ışık tutar.", "Yaşlıların hikayeleri hazine değerindedir."],
                }
                
                # Köy hayatı konusunu varsayılan olarak kullan
                response = random.choice(general_responses.get(topic_to_use, general_responses["köy_hayatı"]))
                print(f"CEVAP: {responder.name} şunu cevapladı: '{response}'")
                return response
                
            # "Nasıl gidiyor" gibi sorular için
            elif "nasıl" in last_message.lower() and any(word in last_message.lower() for word in ["gidiyor", "gidiyorsun", "günün"]):
                day_responses = [
                    "Bugün oldukça iyi gidiyor.", 
                    "Yoğun bir gün geçiriyorum.", 
                    "Her zamanki gibi işte.",
                    "Bugün biraz yorgunum ama iyiyim.",
                    "Güzel bir gün geçiriyorum, teşekkür ederim."
                ]
                return random.choice(day_responses)
                
            else:
                # İçinde soru işareti olmayan mesajlar için genel cevaplar
                general_responses = [
                    "Anladım.",
                    "Bu gerçekten ilginç.",
                    "Bunu daha önce düşünmemiştim.",
                    "Haklı olabilirsin.",
                    "Biraz daha anlat lütfen.",
                    "Bu konuda ne hissettiğini anlıyorum.",
                    "Seni dinliyorum.",
                    "Bunu duymak ilginç.",
                    "Ne demek istediğini anlıyorum.",
                    "Evet, katılıyorum."
                ]
                
                # Son mesaj bir soru gibi görünüyor mu?
                if last_message.strip().endswith("?") or "mi" in last_message.lower() or "mu" in last_message.lower():
                    # Genel evet/hayır sorularına cevaplar
                    yes_no_responses = [
                        "Evet, kesinlikle.",
                        "Hayır, sanmıyorum.",
                        "Belki de öyledir.",
                        "Bu konuda emin değilim.",
                        "Olabilir.",
                        "Muhtemelen evet.",
                        "Bence öyle değil.",
                        "Bu konuda düşünmem gerek."
                    ]
                    return random.choice(yes_no_responses)
                    
                return random.choice(general_responses)
                
        except Exception as e:
            print(f"HATA: Cevap oluşturma hatası: {e}")
            import traceback
            traceback.print_exc()
            
            # Hata durumunda bile basit bir cevap ver
            fallback_responses = ["Anlıyorum.", "Hmm, ilginç.", "Devam et.", "Peki.", "Evet."]
            return random.choice(fallback_responses) 