from thefuzz import fuzz
import re
import unicodedata

KESIN_ESIK = 85
YUKSEK_ESIK = 70
ORTA_ESIK = 55


def _turkce_normalize(metin: str) -> str:
    if not metin:
        return ""
    metin = unicodedata.normalize('NFKC', metin)
    tr_to_ascii = {'ç': 'c', 'Ç': 'c', 'ğ': 'g', 'Ğ': 'g', 'ı': 'i', 'İ': 'i', 'ö': 'o', 'Ö': 'o', 'ş': 's', 'Ş': 's', 'ü': 'u', 'Ü': 'u'}
    for tr_char, ascii_char in tr_to_ascii.items():
        metin = metin.replace(tr_char, ascii_char)
    metin = metin.lower()
    metin = re.sub(r'[^a-z0-9\s\-\']', '', metin)
    metin = re.sub(r'\s+', ' ', metin).strip()
    return metin


def skor_hesapla(aranan: str, hedef: str) -> dict:
    aranan_norm = _turkce_normalize(aranan)
    hedef_norm = _turkce_normalize(hedef)
    
    r = fuzz.ratio(aranan_norm, hedef_norm)
    p = fuzz.partial_ratio(aranan_norm, hedef_norm)
    ts = fuzz.token_sort_ratio(aranan_norm, hedef_norm)
    tset = fuzz.token_set_ratio(aranan_norm, hedef_norm)
    
    aranan_kelimeler = aranan_norm.split()
    hedef_kelimeler = hedef_norm.split()
    aranan_kelime = len(aranan_kelimeler)
    hedef_kelime = len(hedef_kelimeler)
    aranan_set = set(aranan_kelimeler)
    hedef_set = set(hedef_kelimeler)
    
    # 1) Tam eşleşme
    if r == 100:
        nihai = 100
    # 2) Aynı kelimeler farklı sıra
    elif ts == 100:
        nihai = 98
    # 3) Aranan kelimelerin tamamı hedefte var
    elif aranan_set.issubset(hedef_set):
        nihai = 93
    # 4) Token set 100
    elif tset == 100:
        nihai = 90
    # 5) Token set yüksek
    elif tset >= 85:
        nihai = 80 + round((tset - 85) / 3)
    # 6) Partial ratio yüksek
    elif p >= 85:
        nihai = 75 + round((p - 85) / 3)
    # 7) Genel
    else:
        nihai = round(r * 0.15 + p * 0.25 + ts * 0.25 + tset * 0.35)
    
    nihai = min(nihai, 100)
    return {"nihai_skor": nihai, "detay": {"ratio": r, "partial_ratio": p, "token_sort_ratio": ts, "token_set_ratio": tset}}


def risk_belirle(skor: int, kaynak: str = "OFAC") -> dict:
    PEP_KAYNAKLARI = ['CIA Liderler', 'TBMM', 'Wikidata PEP']
    is_pep = kaynak in PEP_KAYNAKLARI
    if skor >= KESIN_ESIK:
        return {"eslesme": True, "guven": "high", "risk": "🔵 YÜKSEK EŞLEŞME" if is_pep else "🔴 YÜKSEK EŞLEŞME", "aksiyon": "manuel_kontrol", "kategori": "pep" if is_pep else "yaptirim"}
    elif skor >= YUKSEK_ESIK:
        return {"eslesme": True, "guven": "medium", "risk": "🔵 ORTA EŞLEŞME" if is_pep else "🟡 ORTA EŞLEŞME", "aksiyon": "manuel_kontrol", "kategori": "pep" if is_pep else "yaptirim"}
    elif skor >= ORTA_ESIK:
        return {"eslesme": True, "guven": "low", "risk": "🟢 DÜŞÜK EŞLEŞME", "aksiyon": "bilgi", "kategori": "pep" if is_pep else "yaptirim"}
    else:
        return {"eslesme": False, "guven": "none", "risk": "🟢 EŞLEŞME YOK", "aksiyon": "onayla", "kategori": "pep" if is_pep else "yaptirim"}