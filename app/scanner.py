from thefuzz import process
from app.cleaner import isim_temizle, liste_temizle
from app.skor_engine import skor_hesapla, risk_belirle, ORTA_ESIK, _turkce_normalize


def tek_liste_tara(aranan: str, liste: dict, liste_adi: str, esik: int = None) -> list:
    temiz_aranan = isim_temizle(aranan)
    isimler = list(liste.keys())
    temiz_liste = liste_temizle(isimler)
    
    temiz_aranan = _turkce_normalize(temiz_aranan)
    temiz_liste = [_turkce_normalize(isim) for isim in temiz_liste]
    
    gecerli_indeksler = []
    for i, isim in enumerate(temiz_liste):
        if not isim:
            continue
        kelimeler = isim.split()
        if any(len(kelime) >= 2 for kelime in kelimeler):
            gecerli_indeksler.append(i)
    temiz_liste = [temiz_liste[i] for i in gecerli_indeksler]
    isimler = [isimler[i] for i in gecerli_indeksler]
    
    aranan_kelime = len(temiz_aranan.split())
    sonuclar = []
    kullanilan = set()
    kullanilacak_esik = esik if esik is not None else ORTA_ESIK
    
    eslesmeler = process.extract(temiz_aranan, temiz_liste, limit=len(temiz_liste))
    
    for eslesen, ham in eslesmeler:
        if ham < kullanilacak_esik:
            continue
        
        idx = temiz_liste.index(eslesen)
        orijinal_isim = isimler[idx]
        
        if (orijinal_isim, liste_adi) in kullanilan:
            continue
        kullanilan.add((orijinal_isim, liste_adi))
        
        eslesen_kelime = len(eslesen.split())
        ortak = set(temiz_aranan.split()) & set(eslesen.split())
        
        if aranan_kelime == 1 and len(temiz_aranan) <= 6:
            hedef_kelimeler = eslesen.split()
            if not any(temiz_aranan.lower() in kelime.lower() for kelime in hedef_kelimeler):
             continue
        
        if aranan_kelime > 1:
            if eslesen_kelime >= aranan_kelime * 2 and len(ortak) <= 1:
                continue
            if len(ortak) / aranan_kelime < 0.5:
                continue
        
        s = skor_hesapla(temiz_aranan, eslesen)
        
        if s["nihai_skor"] < kullanilacak_esik:
            continue
        
        r = risk_belirle(s["nihai_skor"], liste_adi)
        
        ek = liste.get(orijinal_isim, {})
        
        sonuclar.append({
            "eslesen_isim": eslesen,
            "orijinal_isim": orijinal_isim,
            "skor": s["nihai_skor"],
            "guven": r["guven"],
            "risk": r["risk"],
            "aksiyon": r["aksiyon"],
            "detayli_skorlar": s["detay"],
            "kaynak": liste_adi,
            "ek_bilgiler": ek
        })
    
    sonuclar.sort(key=lambda x: x["skor"], reverse=True)
    return sonuclar


def tum_listeleri_tara(aranan: str, listeler: dict, esik: int = None) -> dict:
    temiz_aranan = isim_temizle(aranan)
    tum = []
    
    for ad, liste in listeler.items():
        tum.extend(tek_liste_tara(aranan, liste, ad, esik))
    
    tum.sort(key=lambda x: x["skor"], reverse=True)
    
    gorulen = set()
    benzersiz = []
    for s in tum:
        anahtar = (s["eslesen_isim"], s["kaynak"])
        if anahtar not in gorulen:
            gorulen.add(anahtar)
            benzersiz.append(s)
    
    yuksek = [s for s in benzersiz if s["guven"] == "high"]
    
    if yuksek:
        risk = "🔴 YUKSEK"
    elif benzersiz:
        risk = "🟡 ORTA"
    else:
        risk = "🟢 TEMİZ"
    
    return {
        "aranan": aranan,
        "temizlenmis": temiz_aranan,
        "toplam_eslesme": len(benzersiz),
        "yuksek_riskli_sayisi": len(yuksek),
        "genel_risk": risk,
        "eslesmeler": benzersiz
    }