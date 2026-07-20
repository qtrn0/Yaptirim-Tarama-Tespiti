from pydantic import BaseModel, Field
from typing import List, Optional


class TaramaRequest(BaseModel):
    isim: str = Field(..., description="Taranacak kişi veya şirket adı", example="Vladimir Putin", min_length=1, max_length=200)
    tip: Optional[str] = Field(default="person", description="Tarama tipi: 'person' veya 'company'", example="person", pattern="^(person|company)$")
    kategori: Optional[str] = Field(default=None, description="Tarama kategorisi: 'yaptirim', 'pep' veya boş (tümü)", example="yaptirim", pattern="^(yaptirim|pep)$")
    listeler: Optional[List[str]] = Field(default=None, description="Taranacak liste isimleri (boşsa tümü)", example=["Masak", "OFAC SDN", "BM"])
    esik: Optional[int] = Field(default=None, description="Eşleşme eşiği (70-100). Varsayılan: 75", example=80, ge=70, le=100)


class TopluTaramaRequest(BaseModel):
    isimler: List[str] = Field(..., description="Taranacak isimlerin listesi (maks. 100)", example=["vladimir putin", "Vladimir Putin", "Ali Khamenei"], min_items=1, max_items=100)
    tip: Optional[str] = Field(default="person", description="Tarama tipi", example="person", pattern="^(person|company)$")
    kategori: Optional[str] = Field(default=None, description="Tarama kategorisi: 'yaptirim', 'pep' veya boş (tümü)", example="yaptirim", pattern="^(yaptirim|pep)$")
    listeler: Optional[List[str]] = Field(default=None, description="Taranacak liste isimleri (boşsa tümü)", example=["OFAC SDN", "BM", "Interpol"])
    esik: Optional[int] = Field(default=None, description="Eşleşme eşiği (70-100). Varsayılan: 75", example=80, ge=70, le=100)
    

class DetayliSkorlar(BaseModel):
    ratio: int = Field(..., ge=0, le=100)
    partial_ratio: int = Field(..., ge=0, le=100)
    token_sort_ratio: int = Field(..., ge=0, le=100)
    token_set_ratio: int = Field(..., ge=0, le=100)


class Eslesme(BaseModel):
    eslesen_isim: str
    skor: int = Field(..., ge=0, le=100)
    guven: str
    risk: str
    aksiyon: str
    detayli_skorlar: DetayliSkorlar
    kaynak: str
    uyruk: Optional[str] = None
    dogum_tarihi: Optional[str] = None
    ek_bilgiler: Optional[dict] = None


class TaramaResponse(BaseModel):
    aranan: str
    temizlenmis: str
    toplam_eslesme: int = Field(..., ge=0)
    yuksek_riskli_sayisi: int = Field(..., ge=0)
    genel_risk: str
    taranan_listeler: List[str]
    eslesmeler: List[Eslesme]
    yasal_uyari: str = "Bu sonuç bilgilendirme amaçlıdır. Nihai uyumluluk kararı ve yasal sorumluluk kullanıcıya aittir."


class TopluTaramaOge(BaseModel):
    aranan: str
    toplam_eslesme: int
    genel_risk: str
    yuksek_riskli_sayisi: int


class TopluTaramaResponse(BaseModel):
    toplam_sorgu: int
    riskli_sorgu_sayisi: int
    sonuclar: List[TopluTaramaOge]


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    aktif_listeler: List[str] = []
    toplam_kayit: int = 0


class ErrorResponse(BaseModel):
    hata: str
    detay: Optional[str] = None