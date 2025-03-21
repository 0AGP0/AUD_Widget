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
        
        # Günlük olaylar listesi
        self.daily_events = [
            "Köye yeni bir tüccar geldi",
            "Köy meydanında festival hazırlıkları başladı",
            "Ormanda yeni bir maden bulundu",
            "Köyün doğusuna yeni evler inşa ediliyor",
            "Yakındaki nehirde balık miktarı arttı",
            "Köy pazarında yeni ürünler satışa çıktı",
            "Köy konseyi yeni kararlar aldı",
            "Hasat zamanı yaklaşıyor",
            "Kış hazırlıkları başladı",
            "Komşu köyden misafirler geldi",
            "Köy okulunda yeni eğitim dönemi başladı",
            "Köy kütüphanesi için yeni kitaplar geldi",
            "Köy meydanına yeni bir çeşme yapılıyor",
            "Bahçelerde yeni sebzeler ekildi",
            "Köy korosunun yeni gösterisi yaklaşıyor",
            "Zanaatkarlar yeni ürünler üretmeye başladı",
            "Köy değirmeninde tadilat yapılıyor",
            "Yeni bir sağlık ocağı açılıyor",
            "Köy girişine yeni bir kapı inşa ediliyor",
            "Köy merkezinde yeni bir park yapılıyor"
        ]
        
        self.current_daily_event = None
        self.last_event_change = 0
        self.event_change_interval = 86400  # 24 saat (saniye cinsinden)
        
        # Diyalog senaryoları
        self.dialogue_scenarios = {
            "GREETING": {
                "DOST": {
                    "questions": [
                        "Canım dostum, nasılsın bakalım? Seni görmeyeli çok oldu!",
                        "Hey dostum! Bugün çok iyi görünüyorsun, neler yapıyorsun?",
                        "Sevgili dostum, ailecek nasılsınız? Özledim sizi!"
                    ],
                    "responses": [
                        "Seni gördüm, daha da iyi oldum! Biraz yoğunum ama keyifli işler yapıyorum.",
                        "Çok şükür iyiyiz dostum, sen nasılsın? Biz de seni özledik.",
                        "Harika görünüyorsun! Biz de iyiyiz, çoluk çocuk selamlar gönderiyor."
                    ]
                },
                "ARKADAŞ": {
                    "questions": [
                        "Selam! Nasıl gidiyor işler?",
                        "Merhaba! Bugün oldukça enerjik görünüyorsun, neler yapıyorsun?",
                        "Hey! Uzun zamandır görüşemedik, nasılsın?"
                    ],
                    "responses": [
                        "İyiyim teşekkürler, biraz yoğun ama keyifli!",
                        "Sağol, bugün gerçekten enerjik hissediyorum. Sen nasılsın?",
                        "Özlemişim seni! Ben de iyiyim, çok şükür."
                    ]
                },
                "NÖTR": {
                    "questions": [
                        "Merhaba, nasılsınız?",
                        "İyi günler, nasıl gidiyor?",
                        "Selamlar, bugün nasılsınız?"
                    ],
                    "responses": [
                        "İyiyim teşekkür ederim, siz nasılsınız?",
                        "Çok şükür iyiyim, sağolun.",
                        "İyiyim, teşekkür ederim."
                    ]
                },
                "ANTİPATİK": {
                    "questions": [
                        "Merhaba...",
                        "İyi günler.",
                        "Selamlar."
                    ],
                    "responses": [
                        "İyiyim.",
                        "İdare ediyoruz.",
                        "Fena değil."
                    ]
                }
            },
            "DAILY_EVENT": {
                "DOST": {
                    "questions": [
                        "{olay} diye duydum, sen de duydun mu dostum? Ne düşünüyorsun?",
                        "Dostum, {olay}! İnanabiliyor musun? Nasıl buldun bu gelişmeyi?",
                        "Canım dostum, {olay} haberini aldın mı? Heyecan verici değil mi?"
                    ],
                    "responses": [
                        "Evet dostum, harika bir gelişme! Köyümüz için çok iyi olacak.",
                        "Duydum tabii! Çok sevindim bu habere, birlikte katkıda bulunalım.",
                        "Muhteşem bir haber! Senin de fikirlerini almak isterim bu konuda."
                    ]
                },
                "ARKADAŞ": {
                    "questions": [
                        "{olay}, ne düşünüyorsun bu konuda?",
                        "Duydun mu? {olay}! Nasıl buldun?",
                        "{olay} haberini aldın mı? İlginç değil mi?"
                    ],
                    "responses": [
                        "Evet, duydum! Bence çok iyi olacak.",
                        "Harika bir gelişme! Desteklememiz gerekiyor.",
                        "İyi olmuş, köyümüz için güzel bir adım."
                    ]
                },
                "NÖTR": {
                    "questions": [
                        "{olay}, siz ne düşünüyorsunuz?",
                        "Bu gelişmeyi duydunuz mu? {olay}",
                        "{olay} konusunda ne dersiniz?"
                    ],
                    "responses": [
                        "Evet, duydum. Umarım hayırlısı olur.",
                        "Faydalı olacağını düşünüyorum.",
                        "Güzel bir gelişme olmuş."
                    ]
                },
                "ANTİPATİK": {
                    "questions": [
                        "{olay}... Ne diyorsunuz?",
                        "Duydunuz mu? {olay}",
                        "{olay} konusunda..."
                    ],
                    "responses": [
                        "Duydum...",
                        "Bakalım...",
                        "Göreceğiz..."
                    ]
                }
            },
            "WORK": {
                "DOST": {
                    "questions": [
                        "İşler nasıl gidiyor canım dostum? Yardıma ihtiyacın var mı?",
                        "{meslek} işleri yoğun mu dostum? Beraber çalışalım istersen!",
                        "Sevgili dostum, bugün neler yaptın? Anlat bakalım!"
                    ],
                    "responses": [
                        "Sağol dostum, senin gibi bir dostum olduğu için çok şanslıyım! İşler yoğun ama keyifli.",
                        "Biraz yoğun ama senin desteğinle her şey daha kolay! Yarın beraber çalışalım.",
                        "Bugün çok verimli bir gündü! Seninle çalışmak ister misin?"
                    ]
                },
                "ARKADAŞ": {
                    "questions": [
                        "{meslek} işleri nasıl gidiyor? Yardım lazım mı?",
                        "Bugün işler yoğun muydu? Neler yaptın?",
                        "İşler nasıl? Desteğe ihtiyacın var mı?"
                    ],
                    "responses": [
                        "İyiyim, sağol! Biraz yoğun ama hallediyorum.",
                        "Bugün çok çalıştım ama değdi. Sen nasılsın?",
                        "İşler iyi gidiyor, teşekkür ederim ilgin için."
                    ]
                },
                "NÖTR": {
                    "questions": [
                        "İşleriniz nasıl gidiyor?",
                        "{meslek} olarak bugün neler yaptınız?",
                        "Çalışmalar nasıl ilerliyor?"
                    ],
                    "responses": [
                        "İyi gidiyor, teşekkür ederim.",
                        "Çok şükür, işler yolunda.",
                        "Normal seyrinde devam ediyor."
                    ]
                },
                "ANTİPATİK": {
                    "questions": [
                        "İşler nasıl?",
                        "Çalışıyor musunuz?",
                        "Ne var ne yok?"
                    ],
                    "responses": [
                        "İdare ediyoruz.",
                        "Çalışıyoruz işte.",
                        "Aynı..."
                    ]
                }
            },
            "FAMILY": {
                "DOST": {
                    "questions": [
                        "Ailen nasıl dostum? Çocuklar büyümüş müdür?",
                        "Eşin nasıl? Geçen gördüğümde biraz hastaydı.",
                        "Çocuklar okula alıştı mı dostum? Bizimkilerle iyi anlaşıyorlar mı?"
                    ],
                    "responses": [
                        "Çok şükür hepsi iyi dostum! Çocuklar büyüdü, okula başladılar. Seninkiler nasıl?",
                        "Sağol dostum, eşim çok daha iyi. Sizin ev halkı nasıl?",
                        "Evet, çok iyi anlaşıyorlar! Bu hafta sonu bizde toplansak mı?"
                    ]
                },
                "ARKADAŞ": {
                    "questions": [
                        "Evdekiler nasıl? Hepsi iyi mi?",
                        "Çocuklar nasıl? Okul nasıl gidiyor?",
                        "Aile nasıl? Her şey yolunda mı?"
                    ],
                    "responses": [
                        "İyiler sağol, seninkilere selam söyle!",
                        "Okul iyi gidiyor, çocuklar çalışkan. Seninkiler nasıl?",
                        "Herkes iyi, teşekkür ederim. Selamlar!"
                    ]
                },
                "NÖTR": {
                    "questions": [
                        "Aileniz nasıl?",
                        "Evde herkes iyi mi?",
                        "Çocuklar nasıl?"
                    ],
                    "responses": [
                        "İyiler, teşekkür ederim.",
                        "Herkes iyi, sağolun.",
                        "Çok şükür, iyiler."
                    ]
                },
                "ANTİPATİK": {
                    "questions": [
                        "Ev nasıl?",
                        "Çoluk çocuk?",
                        "Evdekiler?"
                    ],
                    "responses": [
                        "İyiler.",
                        "İdare ediyorlar.",
                        "Fena değiller."
                    ]
                }
            },
            "WEATHER": {
                "DOST": {
                    "questions": [
                        "Bugün hava çok güzel dostum, biraz yürüyüşe çıkalım mı?",
                        "Bu havada çalışmak zor olmalı, sana yardım edeyim mi?",
                        "Hava tam pikniklik, ailecek gitsek mi dostum?"
                    ],
                    "responses": [
                        "Harika fikir dostum! Biraz temiz hava iyi gelir.",
                        "Sağol canım dostum, senin yardımınla her iş kolay!",
                        "Muhteşem olur! Bizimkilere de söyleyelim, güzel bir gün geçiririz!"
                    ]
                },
                "ARKADAŞ": {
                    "questions": [
                        "Hava güzel, biraz yürüyelim mi?",
                        "Bu havada çalışmak nasıl gidiyor?",
                        "Hava güzelken bir şeyler yapalım mı?"
                    ],
                    "responses": [
                        "Olur, biraz temiz hava iyi gelir.",
                        "Biraz zor ama idare ediyoruz.",
                        "İyi fikir, ne yapalım?"
                    ]
                },
                "NÖTR": {
                    "questions": [
                        "Hava bugün nasıl sizce?",
                        "Bu havada çalışmak zor olmalı?",
                        "Hava durumu işlerinizi etkiliyor mu?"
                    ],
                    "responses": [
                        "Evet, güzel bir gün.",
                        "İdare ediyoruz.",
                        "Çok etkilemiyor."
                    ]
                },
                "ANTİPATİK": {
                    "questions": [
                        "Hava nasıl?",
                        "Çalışılıyor mu bu havada?",
                        "Hava sıcak değil mi?"
                    ],
                    "responses": [
                        "Normal.",
                        "Çalışıyoruz mecburen.",
                        "Biraz."
                    ]
                }
            },
            "FUTURE_PLANS": {
                "DOST": {
                    "questions": [
                        "Dostum, gelecek için ne planların var? Heyecan verici projeler düşünüyor musun?",
                        "Bu yıl için güzel hedefler koymuşsun, nasıl gidiyor? Yardıma ihtiyacın var mı?",
                        "Hayalini kurduğun o iş için ne düşünüyorsun dostum? Başlayalım mı?"
                    ],
                    "responses": [
                        "Seninle konuşmak iyi geldi dostum! Evet, büyük planlarım var ve senin desteğine ihtiyacım olacak!",
                        "Hedeflerime doğru ilerliyorum, senin yardımınla daha da hızlanacak!",
                        "Tam da seninle konuşmak istiyordum bu konuyu! Harika fikirlerim var!"
                    ]
                },
                "ARKADAŞ": {
                    "questions": [
                        "Gelecek için planların neler?",
                        "Yeni projeler düşünüyor musun?",
                        "Bu yıl için hedeflerin var mı?"
                    ],
                    "responses": [
                        "Birkaç güzel fikrim var, sonra detaylı konuşalım.",
                        "Evet, yeni şeyler düşünüyorum. Sen ne dersin?",
                        "Hedeflerim var, ilerliyorum yavaş yavaş."
                    ]
                },
                "NÖTR": {
                    "questions": [
                        "İleride neler yapmayı düşünüyorsunuz?",
                        "Planlarınız neler?",
                        "Yeni hedefleriniz var mı?"
                    ],
                    "responses": [
                        "Birkaç planım var.",
                        "Düşünüyorum bazı şeyler.",
                        "Bakalım, zaman gösterecek."
                    ]
                },
                "ANTİPATİK": {
                    "questions": [
                        "Ne yapacaksınız?",
                        "Plan var mı?",
                        "Hedef?"
                    ],
                    "responses": [
                        "Var bir şeyler.",
                        "Düşünüyorum.",
                        "Bakarız."
                    ]
                }
            }
        }
        
        # Daha fazla senaryo kategorisi eklenecek...
        
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
        """Konuşma içeriği üretir"""
        try:
            # Konu belirtilmemişse rastgele konu seç
            if not topic:
                # Son konuşulan konuları takip et
                if not hasattr(self, 'recent_topics'):
                    self.recent_topics = []
                
                # Son 5 konunun dışında bir konu seç
                available_topics = [t for t in self.TOPICS if t not in self.recent_topics]
                if not available_topics:  # Eğer tüm konular kullanıldıysa
                    available_topics = self.TOPICS
                
                topic = random.choice(available_topics)
                
                # Seçilen konuyu son konular listesine ekle
                self.recent_topics.append(topic)
                if len(self.recent_topics) > 5:
                    self.recent_topics.pop(0)
            
            # Kişilik ve ilişki kontrolü
            relationship_type = self.get_relationship_type(speaker, listener)
            
            # Selamlaşma tekrarlanıyor mu kontrol et
            is_greeting_repetitive = False
            
            # Son diyalogları kontrol et
            if hasattr(speaker, 'last_dialogue_lines') and speaker.last_dialogue_lines:
                # Son 3 mesajda selamlaşma var mı?
                greeting_count = 0
                for line in speaker.last_dialogue_lines[-3:]:
                    if any(greeting in line.lower() for greeting in ["merhaba", "selam", "hey", "nasılsın"]):
                        greeting_count += 1
                
                # Eğer son 3 mesajdan 2'si selamlaşma içeriyorsa
                if greeting_count >= 2:
                    is_greeting_repetitive = True
            else:
                # last_dialogue_lines özelliği yoksa oluştur
                speaker.last_dialogue_lines = []
            
            # Temaya göre olası diyalog satırları
            dialogue_options = []
            
            # Son söylenen mesajlar
            last_messages = getattr(speaker, 'last_dialogue_lines', [])
            
            # Önce özel ilişki tipine göre konuşma oluştur
            if relationship_type in self.RELATIONSHIP_DIALOGUE:
                # Tekrar etmeyen diyalog bul
                relationship_dialogues = self.RELATIONSHIP_DIALOGUE[relationship_type]
                # Son kullanılan mesajlar dışında seçenekler
                filtered_dialogues = [d for d in relationship_dialogues if d not in last_messages]
                if filtered_dialogues:
                    dialogue_options.extend(filtered_dialogues)
                else:
                    dialogue_options.extend(relationship_dialogues)
            
            # Sonra konuya göre konuşma oluştur
            if topic in self.TOPIC_DIALOGUE:
                topic_dialogues = self.TOPIC_DIALOGUE[topic]
                # Son kullanılan mesajlar dışında seçenekler
                filtered_topic = [d for d in topic_dialogues if d not in last_messages]
                if filtered_topic:
                    dialogue_options.extend(filtered_topic)
                else: 
                    dialogue_options.extend(topic_dialogues)
            
            # Meslek bazlı diyaloglar
            if hasattr(speaker, 'profession') and speaker.profession:
                profession_dialogues = {
                    'Çiftçi': [
                        f"Bu yıl hasat çok iyi olacak gibi görünüyor.",
                        f"Tarlada ürünler gayet iyi büyüyor.",
                        f"Yağmur mevsimi geldi, ekinler için harika bir haber.",
                        f"Bu topraklar daha iyi günler görmüştü.",
                        f"Son zamanlarda tarımda yeni teknikler denedim."
                    ],
                    'Demirci': [
                        f"Dün çok güzel bir kılıç yaptım, görmen lazım.",
                        f"Metal işleme sanatında kendimi geliştiriyorum.",
                        f"Ocağın başında geçirdiğim saatler beni dinlendiriyor.",
                        f"Yeni bir silah tasarımı üzerinde çalışıyorum.",
                        f"İyi bir demirci olmak sabır işidir."
                    ],
                    'Tüccar': [
                        f"Son kervanla gelen mallar çok kaliteli.",
                        f"Ticaret yolları güvenli değil son zamanlarda.",
                        f"Bu mevsim satışlar yavaş gidiyor.",
                        f"Komşu köylerle ticaret anlaşması imzaladık.",
                        f"İyi bir pazarlık her zaman iki tarafı da memnun eder."
                    ],
                    'Bekçi': [
                        f"Dün gece devriye sırasında bir şey fark ettim.",
                        f"Köy sınırlarında güvenlik önlemlerini artırdık.",
                        f"Son zamanlarda eşkiyalar bölgede kol geziyor.",
                        f"Gece nöbetleri çok yorucu ama köyün güvenliği önemli.",
                        f"Yeni bir muhafız alayı yakında köyümüze gelecek."
                    ],
                    'Avcı': [
                        f"Dağlarda inanılmaz bir hayvan gördüm.",
                        f"Avlanmanın püf noktası sabırdır.",
                        f"Bu mevsim geyikler çok bereketli.",
                        f"Ormanda yeni bir patika keşfettim.",
                        f"Yay kullanma teknikleri üzerine çalışıyorum."
                    ],
                    'Şifacı': [
                        f"Şifalı otlardan yeni bir karışım hazırladım.",
                        f"Bu mevsim hastalıklar artıyor, dikkatli ol.",
                        f"İyileştirme sanatı uzun yıllar alır.",
                        f"Dağlardaki nadir bitkiler hastalıklara çare oluyor.",
                        f"Her derde deva bir reçetem var."
                    ]
                }
                
                # Konuşan kişinin mesleğine göre diyalog ekle
                if speaker.profession in profession_dialogues:
                    prof_dialogues = profession_dialogues[speaker.profession]
                    # Son kullanılan mesajlar dışında seçenekler
                    filtered_prof = [d for d in prof_dialogues if d not in last_messages]
                    if filtered_prof:
                        dialogue_options.extend(filtered_prof)
                    else:
                        dialogue_options.extend(prof_dialogues)
            
            # Kişilik özelliklerine göre konuşma biçimini belirle
            personality_modifiers = []
            
            if hasattr(speaker, 'personality_traits'):
                # Kişilik özelliklerine göre ek diyaloglar
                if 'Neşeli' in speaker.personality_traits:
                    personality_modifiers.extend([
                        "Bugün hava ne kadar güzel, değil mi?",
                        "Her şey yolunda gidiyor gibi hissediyorum!",
                        "Hayat ne güzel!"
                    ])
                    
                if 'Asabi' in speaker.personality_traits:
                    personality_modifiers.extend([
                        "Bugün de herkes sinirimi bozuyor.",
                        "Bu işler hep bana mı kalıyor?",
                        "Hiçbir şey yolunda gitmiyor."
                    ])
                    
                if 'Utangaç' in speaker.personality_traits:
                    personality_modifiers.extend([
                        "Şey... sana bir şey sormak istiyordum...",
                        "Rahatsız etmek istemem ama...",
                        "Acaba... bir dakikan var mı?"
                    ])
                
                if 'Bilge' in speaker.personality_traits:
                    personality_modifiers.extend([
                        "Hayat yolculuğunda sabır en önemli erdemdir.",
                        "Gerçek bilgelik, bilmediğini bilmektir.",
                        "Her zorluk bize yeni bir ders öğretir."
                    ])
                    
                if 'Meraklı' in speaker.personality_traits:
                    personality_modifiers.extend([
                        "Son zamanlarda ilginç bir şey keşfettin mi?",
                        "O olay hakkında ne düşünüyorsun?",
                        "Bana daha fazla anlatır mısın?"
                    ])
                
                # Kişilik özelliklerine göre diyalog eklenmesi
                dialogue_options.extend(personality_modifiers)
            
            # Ruh haline göre konuşma biçimini düzenle
            mood_dialogues = []
            if hasattr(speaker, 'mood'):
                if speaker.mood == "Mutlu":
                    mood_dialogues = [
                        "Bugün kendimi harika hissediyorum!",
                        "Hayat ne güzel değil mi?", 
                        "Bu güzel günde seninle konuşmak çok iyi.",
                        "Bugün her şey yolunda gidiyor."
                    ]
                elif speaker.mood == "Üzgün":
                    mood_dialogues = [
                        "Son günlerde kendimi iyi hissetmiyorum...",
                        "Bazen her şey çok zor geliyor.",
                        "Bugün biraz moralim bozuk.",
                        "Keşke bazı şeyler farklı olsaydı."
                    ]
                elif speaker.mood == "Kızgın":
                    mood_dialogues = [
                        "İnsanlar beni çok sinirlendiriyor!",
                        "Bugün kimseyle uğraşacak halim yok.",
                        "Bazen her şey kontrolden çıkıyor.",
                        "Son olaylar canımı çok sıktı."
                    ]
                elif speaker.mood == "Yorgun":
                    mood_dialogues = [
                        "Bugün çok yorgunum...",
                        "Biraz dinlenmeye ihtiyacım var.",
                        "Son zamanlarda çok çalışıyorum.",
                        "Gece iyi uyuyamadım."
                    ]
                elif speaker.mood == "Endişeli":
                    mood_dialogues = [
                        "Son zamanlarda çok endişeliyim.",
                        "Gelecek hakkında kaygılarım var.",
                        "Belirsizlik beni huzursuz ediyor.",
                        "Bu durumda ne yapacağımı bilmiyorum."
                    ]
                
                # Ruh haline göre diyalog eklenmesi
                dialogue_options.extend(mood_dialogues)
            
            # Selamlaşma çok tekrarlanıyorsa, selamlaşma dışı bir mesaj seç
            if is_greeting_repetitive:
                # Selamlaşma ifadelerini filtrele
                non_greeting_options = [opt for opt in dialogue_options if not any(
                    greeting in opt.lower() for greeting in ["merhaba", "selam", "hey", "nasılsın"])]
                
                # Eğer selamlaşma dışı mesajlar varsa, onlardan seç
                if non_greeting_options:
                    dialogue_options = non_greeting_options
            
            # Eğer diyalog seçeneği yoksa, jenerik mesajlar kullan
            if not dialogue_options:
                dialogue_options = [
                    f"Bugün hava nasıl?",
                    f"Köyde yeni bir şey var mı?",
                    f"Son zamanlarda nasıl gidiyor?",
                    f"Duyduğuma göre yakında bir festival olacakmış.",
                    f"Aileniz nasıl?"
                ]
            
            # Rastgele bir diyalog satırı seç
            dialogue_line = random.choice(dialogue_options)
            
            # Diyalog satırını son diyaloglar listesine ekle
            speaker.last_dialogue_lines.append(dialogue_line)
            
            # En fazla son 10 mesajı tut
            if len(speaker.last_dialogue_lines) > 10:
                speaker.last_dialogue_lines.pop(0)
            
            # Dinleyicinin ismini ekle
            if random.random() < 0.3 and hasattr(listener, 'name'):
                if "?" in dialogue_line:
                    # Soru cümlesine isim ekle (cümlenin sonuna)
                    dialogue_line = dialogue_line.replace("?", f", {listener.name}?")
                else:
                    # Rastgele isim ekle (cümlenin başına veya sonuna)
                    if random.random() < 0.5:
                        dialogue_line = f"{listener.name}, {dialogue_line}"
                    else:
                        dialogue_line = f"{dialogue_line}, {listener.name}"
            
            return dialogue_line
            
        except Exception as e:
            print(f"Yanıt üretirken hata: {e}")
            import traceback
            traceback.print_exc()
            return "Anlayamadım, tekrar eder misin?"
            
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
    
    def generate_response(self, asker, responder):
        """Soruya yanıt üretir"""
        try:
            # Yanıt üretmek için bilgileri kontrol et
            if not hasattr(asker, 'last_dialogue') or not asker.last_dialogue:
                print(f"HATA: {asker.name}'nin son mesajı bulunamadı - last_dialogue yok veya boş")
                
                # Genel bir soru varsayalım ve cevap verelim
                question = "Günün nasıl geçiyor?"
                print(f"Varsayılan soru kullanılıyor: '{question}'")
                
                # Köylünün last_dialogue özelliğini ayarla
                asker.last_dialogue = question
            else:
                # Soruyu al
                question = asker.last_dialogue
            
            # Son soruların takibi
            if not hasattr(self, 'recent_questions'):
                self.recent_questions = []
            
            # Aynı soru son zamanlarda soruldu mu?
            if question in self.recent_questions:
                print(f"UYARI: '{question}' sorusu tekrarlanıyor, farklı bir cevap verilecek")
                alternative_responses = [
                    "Bu konuyu az önce konuştuk.",
                    "Bunu zaten sordun bence.",
                    "Farklı bir şey konuşalım mı?",
                    "Başka bir konu açalım, ne dersin?",
                    "Konuyu değiştirelim mi?"
                ]
                
                # Son soruları güncelle ama yeniden ekleme
                return random.choice(alternative_responses)
            else:
                # Soruyu son sorulara ekle
                self.recent_questions.append(question)
                # Son 10 soruyu tut
                if len(self.recent_questions) > 10:
                    self.recent_questions.pop(0)
            
            # Dinleyicinin özellikleri ve ilişkileri
            personality = "Nötr"
            profession = "Köylü"
            mood = "Normal"
            
            if hasattr(responder, 'personality_traits') and responder.personality_traits:
                if isinstance(responder.personality_traits, list) and responder.personality_traits:
                    personality = responder.personality_traits[0]
                elif isinstance(responder.personality_traits, str):
                    personality = responder.personality_traits
            
            if hasattr(responder, 'profession') and responder.profession:
                profession = responder.profession
                
            if hasattr(responder, 'mood') and responder.mood:
                mood = responder.mood
            
            # İlişki durumu
            relationship = ""
            try:
                relationship = self.get_relationship_type(responder, asker)
            except:
                relationship = "Nötr"  # Hata durumunda varsayılan ilişki
            
            # Düşük ilişki varsa olumsuz cevaplar
            negative_responses = [
                "Seninle konuşmak istemiyorum.",
                "Beni rahat bırak.",
                "Sana ne?",
                "Hmm, bilmiyorum.",
                "..."
            ]
            
            # Eğer ilişki kötüyse %30 ihtimalle olumsuz cevap ver
            if relationship == "Düşman" or relationship == "Kötü":
                if random.random() < 0.3:
                    return random.choice(negative_responses)
            
            # Sorunun içeriğine göre cevap ver
            if "nasılsın" in question.lower() or "nasıl gidiyor" in question.lower():
                # Ruh haline göre yanıtlar
                responses = {
                    "Mutlu": [
                        "Harika hissediyorum, teşekkür ederim!",
                        "Bugün çok güzel bir gün, sen nasılsın?",
                        "Kendimi hiç olmadığım kadar iyi hissediyorum.",
                        "Her şey yolunda, sen nasılsın?"
                    ],
                    "Üzgün": [
                        "İdare ediyorum... Sorduğun için teşekkürler.",
                        "Çok iyi değilim açıkçası...",
                        "Zor günler geçiriyorum.",
                        "Biraz moralim bozuk."
                    ],
                    "Kızgın": [
                        "Sinirlerim biraz gergin, sorma.",
                        "İyi değilim ve konuşmak istemiyorum.",
                        "Bugün beni rahat bıraksan iyi olur.",
                        "Çok sinirli hissediyorum."
                    ],
                    "Yorgun": [
                        "Çok yorgunum, biraz dinlenmeye ihtiyacım var.",
                        "Uykusuz geçen gecelerden sonra bitkin durumdayım.",
                        "Bugün çok çalıştım, yorgunum.",
                        "Biraz dinlensem iyi olacak."
                    ],
                    "Normal": [
                        "İyiyim, teşekkür ederim.",
                        "Her zamanki gibi işte.",
                        "Şikâyet edemem, sen nasılsın?",
                        "Fena değil, sorduğun için sağol."
                    ],
                    "Endişeli": [
                        "Biraz endişeliyim...",
                        "Son zamanlarda kafam karışık.",
                        "Çok düşünüyorum, biliyorsun.",
                        "Bazı şeyler beni rahatsız ediyor."
                    ]
                }
                
                # Mesleğe göre ek cevaplar
                profession_responses = {
                    "Çiftçi": [
                        "Tarlada işler yoğun, ama iyiyim.",
                        "Hasat zamanı yaklaşıyor, biraz telaşlıyım."
                    ],
                    "Demirci": [
                        "Ocağın başında ter döküyorum ama keyifli.",
                        "Yeni siparişlerle uğraşıyorum, yoğunum."
                    ],
                    "Tüccar": [
                        "Ticaret iyi gidiyor, şikayetim yok.",
                        "Yeni mallar geldi, onlarla meşgulüm."
                    ],
                    "Bekçi": [
                        "Nöbetler yorucu ama köyün güvenliği için değer.",
                        "Gözlerim devamlı tetikte, tehlike her an gelebilir."
                    ],
                    "Avcı": [
                        "Bugün güzel avlar yakaladım, keyfim yerinde.",
                        "Ormanda yeni izler keşfettim, heyecanlıyım."
                    ],
                    "Şifacı": [
                        "Hastalarımla ilgileniyorum, yoğun bir gün.",
                        "Yeni şifalı karışımlar hazırlıyorum."
                    ]
                }
                
                # Mood yoksa Normal olarak kabul et
                mood_to_use = mood if mood in responses else "Normal"
                
                # Temel cevaplar
                mood_resp = responses[mood_to_use]
                
                # Meslek cevapları varsa ekle
                if profession in profession_responses:
                    profession_resp = profession_responses[profession]
                    all_responses = mood_resp + profession_resp
                else:
                    all_responses = mood_resp
                
                return random.choice(all_responses)
                
            elif "ne yapıyorsun" in question.lower() or "ne ile meşgulsün" in question.lower():
                # Mesleğe göre yanıtlar
                profession_activities = {
                    "Çiftçi": [
                        "Tarlada çalışıyordum.",
                        "Ekinleri kontrol ediyordum.",
                        "Tohumları ekmeye hazırlanıyordum."
                    ],
                    "Demirci": [
                        "Yeni bir kılıç yapıyordum.",
                        "Ocağı yakıyordum.",
                        "Metal dövüyordum."
                    ],
                    "Tüccar": [
                        "Malları düzenliyordum.",
                        "Fiyatları hesaplıyordum.",
                        "Yeni bir ticaret anlaşması üzerinde çalışıyordum."
                    ],
                    "Bekçi": [
                        "Devriye geziyordum.",
                        "Köy sınırlarını kontrol ediyordum.",
                        "Silahımı temizliyordum."
                    ],
                    "Avcı": [
                        "Av için hazırlanıyordum.",
                        "Tuzakları kontrol ediyordum.",
                        "Avladığım hayvanları işliyordum."
                    ],
                    "Şifacı": [
                        "Şifalı otları topluyordum.",
                        "Hastaları kontrol ediyordum.",
                        "Yeni bir iksir hazırlıyordum."
                    ]
                }
                
                # Jenerik aktiviteler
                generic_activities = [
                    "Biraz dinleniyordum.",
                    "Etrafı seyrediyordum.",
                    "Düşünüyordum sadece.",
                    "Yürüyüş yapıyordum."
                ]
                
                # Mesleğe özel yanıt varsa kullan, yoksa jenerik yanıt
                if profession in profession_activities:
                    activity_responses = profession_activities[profession]
                else:
                    activity_responses = generic_activities
                
                return random.choice(activity_responses)
                
            elif "hava" in question.lower() and ("nasıl" in question.lower() or "güzel mi" in question.lower()):
                # Hava durumu hakkında yanıtlar
                weather_responses = [
                    "Bugün hava oldukça güzel.",
                    "Biraz rüzgarlı ama güneşli.",
                    "Sanırım yağmur yağacak.",
                    "Hava çok sıcak bugün.",
                    "Soğuk bir gün, kendine dikkat et."
                ]
                return random.choice(weather_responses)
                
            elif "köyde" in question.lower() and "yeni" in question.lower():
                # Köy dedikodular
                gossip_responses = [
                    "Yeni bir tüccar kervanı gelecekmiş yakında.",
                    "Duyduğuma göre şehirden yeni bir aile taşınıyormuş.",
                    "Hiçbir yenilik yok, her şey aynı.",
                    "Son günlerde köy meydanında yeni bir yapı inşa ediliyor.",
                    "Çiftçi Ahmet'in tarlasında garip bir olay olmuş, herkes bundan bahsediyor."
                ]
                return random.choice(gossip_responses)
                
            elif any(word in question.lower() for word in ["sever misin", "hoşlanır mısın", "ne düşünüyorsun"]):
                # Tercihler hakkında yanıtlar
                preference_responses = [
                    "Evet, gerçekten seviyorum.",
                    "Pek sayılmaz, benim tarzım değil.",
                    "Bazen keyif alıyorum.",
                    "Çok iyi bilmiyorum, deneyimim az.",
                    "Bu konuda karışık duygularım var."
                ]
                return random.choice(preference_responses)
                
            # Soruyu anlayamadıysa jenerik bir yanıt
            generic_responses = [
                f"Hmm, bu ilginç bir soru.",
                f"Bunu daha önce hiç düşünmemiştim.",
                f"Sanırım... evet, öyle diyebilirim.",
                f"Bu konuda çok bilgim yok açıkçası.",
                f"İyi bir soru, biraz düşünmem lazım."
            ]
            
            # Kişilik özelliklerine göre yanıt biçimini ayarla
            if personality == "Neşeli":
                return random.choice(generic_responses) + " 😊"
            elif personality == "Asabi":
                return random.choice(generic_responses) + "... Başka?"
            elif personality == "Utangaç":
                return "Şey... " + random.choice(generic_responses).lower()
            elif personality == "Bilge":
                return random.choice(generic_responses) + " Ancak her şey göründüğü gibi değildir."
            else:
                return random.choice(generic_responses)
                
        except Exception as e:
            print(f"Yanıt üretirken hata: {e}")
            import traceback
            traceback.print_exc()
            return "Anlayamadım, tekrar eder misin?"

    def get_daily_event(self) -> str:
        """Günün olayını döndürür, gerekirse yeni olay seçer"""
        current_time = time.time()
        
        # Eğer olay yoksa veya değişim zamanı geldiyse yeni olay seç
        if (self.current_daily_event is None or 
            current_time - self.last_event_change >= self.event_change_interval):
            self.current_daily_event = random.choice(self.daily_events)
            self.last_event_change = current_time
            
        return self.current_daily_event

    def get_dialogue(self, category: str, relationship: str, context: Dict = None) -> Tuple[str, str]:
        """Belirli bir kategori ve ilişki durumu için soru ve cevap döndürür"""
        if category not in self.dialogue_scenarios or relationship not in self.dialogue_scenarios[category]:
            return None, None
            
        scenario = self.dialogue_scenarios[category]
        relationship_dialogue = scenario[relationship]
        
        question = random.choice(relationship_dialogue["questions"])
        response = random.choice(relationship_dialogue["responses"])
        
        # Eğer bağlam varsa, metinleri formatla
        if context:
            question = question.format(**context)
            response = response.format(**context)
            
        return question, response

    def create_conversation(self, villager1, villager2) -> List[Tuple[str, str, str]]:
        """İki köylü arasında tam bir konuşma oluşturur"""
        conversation = []
        relationship = villager1.relationships.get(villager2.name, "NÖTR")
        
        # Konuşma uzunluğunu belirle (3-4 arası konu)
        num_topics = random.randint(3, 4)
        
        # Kullanılabilir kategoriler
        categories = ["GREETING", "DAILY_EVENT", "WORK", "FAMILY", "WEATHER", "FUTURE_PLANS"]
        
        # Selamlaşma ile başla (zorunlu)
        greeting_q, greeting_r = self.get_dialogue("GREETING", relationship)
        conversation.append((villager1.name, villager2.name, greeting_q))
        conversation.append((villager2.name, villager1.name, greeting_r))
        
        # Günün olayı hakkında konuşma (zorunlu)
        daily_event = self.get_daily_event()
        event_q, event_r = self.get_dialogue("DAILY_EVENT", relationship, {"olay": daily_event})
        conversation.append((villager1.name, villager2.name, event_q))
        conversation.append((villager2.name, villager1.name, event_r))
        
        # Diğer konular için rastgele kategoriler seç
        available_categories = [cat for cat in categories if cat not in ["GREETING", "DAILY_EVENT"]]
        selected_categories = random.sample(available_categories, min(num_topics - 2, len(available_categories)))
        
        for category in selected_categories:
            context = {"meslek": villager2.profession} if category == "WORK" else None
            q, r = self.get_dialogue(category, relationship, context)
            
            if q and r:
                conversation.append((villager1.name, villager2.name, q))
                conversation.append((villager2.name, villager1.name, r))
        
        return conversation 

    def get_relationship_type(self, villager1, villager2):
        """İki köylü arasındaki ilişki tipini döndürür"""
        try:
            # Köylünün ilişkiler sözlüğünü kontrol et
            if not hasattr(villager1, 'relationships'):
                print(f"UYARI: {villager1.name} köylüsünün relationships özelliği bulunamadı")
                return "Nötr"
            
            # İlişki puanını al
            relationship_score = villager1.relationships.get(villager2.name, 0)
            
            # İlişki tipini belirle
            if relationship_score <= -75:
                return "Düşman"
            elif relationship_score <= -25:
                return "Hoşlanmıyor"
            elif relationship_score < 25:
                return "Nötr"
            elif relationship_score < 75:
                return "İyi"
            else:
                return "Dost"
        except Exception as e:
            print(f"İlişki tipi belirlenirken hata: {e}")
            return "Nötr"  # Varsayılan 