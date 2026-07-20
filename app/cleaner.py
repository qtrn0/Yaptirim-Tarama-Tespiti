import re


def isim_temizle(metin: str) -> str:
    """
    Ham ismi alır, temizler ve standart formata dönüştürür.
    
    Yaptıkları:
    - Küçük harfe çevirir
    - Kişi unvanlarını siler (Dr., Mr., Prof. vb.)
    - Şirket eklerini siler (Ltd., Inc., Corp. vb.)
    - Noktalama işaretlerini kaldırır
    - Fazla boşlukları temizler
    
    Örnek:
    "Dr. Vladimir Putin" -> "vladimir putin"
    "Wagner Group Ltd." -> "wagner group"
    """
    if not metin or not isinstance(metin, str):
        return ""
    
    # 1. Küçük harf ve baş/son boşluk temizliği
    metin = metin.lower().strip()
    
    # 2. Kişi unvanları
    metin = re.sub(
        r'\b(dr|mr|mrs|ms|prof|gen|lt|col|capt|cmdr|sir|lord|lady)\.?\b',
        '',
        metin
    )
    
    # 3. Şirket ekleri
    metin = re.sub(
        r'\b(ltd|llc|inc|corp|corporation|limited|company|co|gmbh|ag|sa|as|plc|llp|lp)\.?\b',
        '',
        metin
    )
    
    # 4. Parantez içindekileri sil (açıklamalar, eski isimler)
    metin = re.sub(r'\([^)]*\)', '', metin)
    
    # 5. Noktalama işaretlerini sil (harf, rakam, boşluk dışındakiler)
    metin = re.sub(r'[^\w\s]', '', metin)
    
    # 6. Fazla boşlukları tek boşluğa indir
    metin = re.sub(r'\s+', ' ', metin).strip()
    
    return metin


def liste_temizle(isim_listesi: list) -> list:
    """
    İsim listesindeki tüm isimleri temizler.
    None veya boş string'leri filtreler.
    """
    return [isim_temizle(i) for i in isim_listesi if i]


def yaptirim_listesi_temizle(liste: list) -> list:
    """
    OFAC/UK/EU formatındaki ham listeyi temizler.
    Virgülle ayrılmış "Soyad, Ad" formatını "Ad Soyad" yapar.
    """
    temiz_liste = []
    for isim in liste:
        if not isim:
            continue
        isim = isim_temizle(isim)
        # "soyad, ad" -> "ad soyad"
        if ',' in isim:
            parcalar = isim.split(',')
            isim = ' '.join(p.strip() for p in reversed(parcalar))
        temiz_liste.append(isim)
    return temiz_liste