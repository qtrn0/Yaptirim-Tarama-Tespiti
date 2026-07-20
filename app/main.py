import os
import time
from collections import defaultdict
from typing import Optional, List
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.security import APIKeyHeader
from starlette.responses import JSONResponse

from app.models import (
    TaramaRequest,
    TaramaResponse,
    TopluTaramaRequest,
    TopluTaramaResponse,
    TopluTaramaOge,
    HealthResponse,
    Eslesme,
    DetayliSkorlar,
)
from app.scanner import tum_listeleri_tara
from app.data_loader import verileri_yukle

API_KEY = os.getenv("API_KEY", "demo-key-2026")
api_key_header = APIKeyHeader(name="X-API-Key")

def api_key_dogrula(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Geçersiz veya eksik API anahtarı.")
    return api_key

rate_limit_store = defaultdict(list)

def rate_limiter(client_ip: str, max_requests: int = 100, window: int = 60):
    now = time.time()
    rate_limit_store[client_ip] = [t for t in rate_limit_store[client_ip] if now - t < window]
    if len(rate_limit_store[client_ip]) >= max_requests:
        raise HTTPException(status_code=429, detail="Rate limit aşıldı. Dakikada maksimum 100 istek.")
    rate_limit_store[client_ip].append(now)

app = FastAPI(
    title="🛡️ Yaptırım Tarama Tespiti API",
    description="""
    ## Sanctions Screening & PEP Detection
    
    12 uluslararası veritabanında fuzzy string matching ile yaptırım ve PEP taraması.
    
    ### 📊 Veritabanları
    **Yaptırım (9):** Masak, OFAC SDN, OFAC Non-SDN, BM, AB, Interpol, UK, İçişleri Terör, ABD Terör
    
    **PEP (3):** CIA Liderler, TBMM, Wikidata PEP
    
    ### 🔑 Kimlik Doğrulama
    Tüm tarama endpoint'leri `X-API-Key` header'ı gerektirir. Varsayılan: `demo-key-2026`
    """,
    version="2.0.0",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

LISTELER = verileri_yukle()
LISTE_ADLARI = list(LISTELER.keys())
YASAL_UYARI = (
    "Bu sonuç bilgilendirme amaçlıdır. Nihai uyumluluk kararı ve yasal sorumluluk "
    "kullanıcıya aittir. Manuel kontrol önerilir. Durum Tarama Tespitçisi, yanlış pozitif "
    "veya yanlış negatif sonuçlardan doğacak zararlardan sorumlu tutulamaz."
)


@app.get("/", response_model=HealthResponse)
def root():
    return HealthResponse(status="operational", version="2.0.0", aktif_listeler=LISTE_ADLARI)


@app.get("/health", response_model=HealthResponse)
def health():
    toplam = sum(len(v) for v in LISTELER.values())
    return HealthResponse(status="ok", version="2.0.0", aktif_listeler=list(LISTELER.keys()), toplam_kayit=toplam)


@app.post("/screen", response_model=TaramaResponse)
def screen(request: TaramaRequest, req: Request, api_key: str = Depends(api_key_dogrula)):
    rate_limiter(req.client.host)
    
    if not request.isim or not request.isim.strip():
        raise HTTPException(status_code=400, detail="İsim alanı boş olamaz.")
    
    filtrelenmis = {k: v for k, v in LISTELER.items() if k in request.listeler} if request.listeler else LISTELER
    
    ham_sonuc = tum_listeleri_tara(request.isim, filtrelenmis, request.esik)
    
    eslesmeler = []
    for es in ham_sonuc["eslesmeler"]:
        detay = es["detayli_skorlar"]
        ek = es.get("ek_bilgiler", {})
        eslesmeler.append(Eslesme(
            eslesen_isim=es["eslesen_isim"],
            skor=es["skor"],
            guven=es["guven"],
            risk=es["risk"],
            aksiyon=es["aksiyon"],
            detayli_skorlar=DetayliSkorlar(
                ratio=detay["ratio"], partial_ratio=detay["partial_ratio"],
                token_sort_ratio=detay["token_sort_ratio"], token_set_ratio=detay["token_set_ratio"],
            ),
            kaynak=es["kaynak"],
            uyruk=ek.get("Nationality", ek.get("NATIONALITY", ek.get("Citizenship", ""))),
            dogum_tarihi=ek.get("BirthDate", ""),
            ek_bilgiler=ek
        ))
    
    return TaramaResponse(
        aranan=ham_sonuc["aranan"], temizlenmis=ham_sonuc["temizlenmis"],
        toplam_eslesme=ham_sonuc["toplam_eslesme"], yuksek_riskli_sayisi=ham_sonuc["yuksek_riskli_sayisi"],
        genel_risk=ham_sonuc["genel_risk"], taranan_listeler=list(filtrelenmis.keys()),
        eslesmeler=eslesmeler, yasal_uyari=YASAL_UYARI,
    )


@app.post("/screen/batch", response_model=TopluTaramaResponse)
def screen_batch(request: TopluTaramaRequest, req: Request, api_key: str = Depends(api_key_dogrula)):
    rate_limiter(req.client.host)
    
    if not request.isimler:
        raise HTTPException(status_code=400, detail="İsim listesi boş olamaz.")
    
    filtrelenmis = {k: v for k, v in LISTELER.items() if k in request.listeler} if request.listeler else LISTELER
    
    sonuclar = []
    riskli_sayisi = 0
    
    for isim in request.isimler:
        if not isim or not isim.strip():
            continue
        ham = tum_listeleri_tara(isim, filtrelenmis, request.esik)
        if ham["toplam_eslesme"] > 0:
            riskli_sayisi += 1
        sonuclar.append(TopluTaramaOge(
            aranan=ham["aranan"], toplam_eslesme=ham["toplam_eslesme"],
            genel_risk=ham["genel_risk"], yuksek_riskli_sayisi=ham["yuksek_riskli_sayisi"],
        ))
    
    return TopluTaramaResponse(toplam_sorgu=len(request.isimler), riskli_sorgu_sayisi=riskli_sayisi, sonuclar=sonuclar)