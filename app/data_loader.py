import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _safe(val):
    """NaN değerleri boş string'e çevir."""
    try:
        if pd.isna(val):
            return ""
        return str(val).strip()
    except:
        return str(val).strip() if val else ""


def verileri_yukle() -> dict:
    listeler = {}

    # 1. MASAK
    try:
        df = pd.read_csv(os.path.join(DATA_DIR, "masak.csv"), encoding='iso-8859-9', sep=';')
        isim_dict = {}
        for i, row in df.iterrows():
            isim_dict[str(row.iloc[1])] = {"Örgütü": _safe(row.iloc[10]) if df.shape[1] > 10 else ""}
        listeler["Masak"] = isim_dict
        print(f"Masak yuklendi: {len(isim_dict)}")
    except Exception as e:
        print(f"Masak hata: {e}"); listeler["Masak"] = {}

    # 2. OFAC SDN
    try:
        df = pd.read_excel(os.path.join(DATA_DIR, "ofacsdn.xlsx"))
        isim_dict = {}
        for i, row in df.iterrows():
            isim_dict[_safe(row["Name"])] = {}
        listeler["OFAC SDN"] = isim_dict
        print(f"OFAC SDN yuklendi: {len(isim_dict)}")
    except Exception as e:
        print(f"OFAC SDN hata: {e}"); listeler["OFAC SDN"] = {}

    # 3. OFAC Non-SDN
    try:
        df = pd.read_excel(os.path.join(DATA_DIR, "ofacnosdn.xlsx"))
        isim_dict = {}
        for i, row in df.iterrows():
            isim_dict[_safe(row["Name"])] = {
                "Type": _safe(row.get("Type")),
                "Country": _safe(row.get("Country"))
            }
        listeler["OFAC Non-SDN"] = isim_dict
        print(f"OFAC Non-SDN yuklendi: {len(isim_dict)}")
    except Exception as e:
        print(f"OFAC Non-SDN hata: {e}"); listeler["OFAC Non-SDN"] = {}

    # 4. BM
    try:
        df = pd.read_excel(os.path.join(DATA_DIR, "un.xlsx"))
        isim_dict = {}
        for i, row in df.iterrows():
            first = _safe(row.get("FIRST_NAME"))
            second = _safe(row.get("SECOND_NAME"))
            tam = f"{first} {second}".strip()
            if tam:
                isim_dict[tam] = {
                    "GENDER": _safe(row.get("GENDER")),
                    "NATIONALITY": _safe(row.get("NATIONALITY"))
                }
        listeler["BM"] = isim_dict
        print(f"BM yuklendi: {len(isim_dict)}")
    except Exception as e:
        print(f"BM hata: {e}"); listeler["BM"] = {}

    # 5. AB
    try:
        df = pd.read_excel(os.path.join(DATA_DIR, "eu.xlsx"))
        isim_dict = {}
        for i, row in df.iterrows():
            country = _safe(row.get("properties country"))
            country = country.replace("[", "").replace("]", "").replace("'", "").replace('"', "").strip()
            isim_dict[_safe(row["Name"])] = {
                "Type": _safe(row.get("Type")),
                "Country": country
            }
        listeler["AB"] = isim_dict
        print(f"AB yuklendi: {len(isim_dict)}")
    except Exception as e:
        print(f"AB hata: {e}"); listeler["AB"] = {}

    # 6. Interpol
    try:
        df = pd.read_excel(os.path.join(DATA_DIR, "interpol.xlsx"))
        isim_dict = {}
        for i, row in df.iterrows():
            isim_dict[_safe(row["Name"])] = {
                "BirthPlace": _safe(row.get("BirthPlace")),
                "Nationality": _safe(row.get("Nationality")),
                "BirthDate": _safe(row.get("BirthDate")),
                "Gender": _safe(row.get("Gender"))
            }
        listeler["Interpol"] = isim_dict
        print(f"Interpol yuklendi: {len(isim_dict)}")
    except Exception as e:
        print(f"Interpol hata: {e}"); listeler["Interpol"] = {}

    # 7. UK
    try:
        df = pd.read_excel(os.path.join(DATA_DIR, "ukhmtofsi.xlsx"))
        isim_dict = {}
        for i, row in df.iterrows():
            isim_dict[_safe(row["Name"])] = {}
        listeler["UK"] = isim_dict
        print(f"UK yuklendi: {len(isim_dict)}")
    except Exception as e:
        print(f"UK hata: {e}"); listeler["UK"] = {}

    # 8. İçişleri Terör
    try:
        df = pd.read_excel(os.path.join(DATA_DIR, "icisleriteroraranan.xlsx"))
        isim_dict = {}
        for i, row in df.iterrows():
            isim_dict[_safe(row["Name"])] = {
                "BirthDate": _safe(row.get("BirthDate")),
                "List": _safe(row.get("List")),
                "BirthPlace": _safe(row.get("BirthPlace")),
                "Organization": _safe(row.get("Organization"))
            }
        listeler["Icisleri Teror"] = isim_dict
        print(f"Icisleri Teror yuklendi: {len(isim_dict)}")
    except Exception as e:
        print(f"Icisleri Teror hata: {e}"); listeler["Icisleri Teror"] = {}

    # 9. ABD Terör
    try:
        df = pd.read_excel(os.path.join(DATA_DIR, "usterorism.xlsx"))
        isim_dict = {}
        for i, row in df.iterrows():
            isim_dict[_safe(row["Name"])] = {
                "Alias": _safe(row.get("Alias"))
            }
        listeler["ABD Teror"] = isim_dict
        print(f"ABD Teror yuklendi: {len(isim_dict)}")
    except Exception as e:
        print(f"ABD Teror hata: {e}"); listeler["ABD Teror"] = {}

    # 10. CIA Liderler
    try:
        df = pd.read_excel(os.path.join(DATA_DIR, "ciaworldleaders.xlsx"))
        isim_dict = {}
        for i, row in df.iterrows():
            isim_dict[_safe(row["Name"])] = {
                "Role 0": _safe(row.get("Role 0")),
                "Role 1": _safe(row.get("Role 1")),
                "Citizenship": _safe(row.get("Citizenship"))
            }
        listeler["CIA Liderler"] = isim_dict
        print(f"CIA Liderler yuklendi: {len(isim_dict)}")
    except Exception as e:
        print(f"CIA Liderler hata: {e}"); listeler["CIA Liderler"] = {}

    # 11. TBMM
    try:
        df = pd.read_excel(os.path.join(DATA_DIR, "tbmm.xlsx"))
        isim_dict = {}
        for i, row in df.iterrows():
            isim_dict[_safe(row["Name"])] = {
                "BirthDate": _safe(row.get("BirthDate")),
                "Party": _safe(row.get("Party")),
                "BirthPlace": _safe(row.get("BirthPlace"))
            }
        listeler["TBMM"] = isim_dict
        print(f"TBMM yuklendi: {len(isim_dict)}")
    except Exception as e:
        print(f"TBMM hata: {e}"); listeler["TBMM"] = {}

    # 12. Wikidata PEP
    try:
        df = pd.read_excel(os.path.join(DATA_DIR, "wikidatapep.xlsx"))
        isim_dict = {}
        for i, row in df.iterrows():
            isim_dict[_safe(row["Name"])] = {
                "Type": _safe(row.get("Type"))
            }
        listeler["Wikidata PEP"] = isim_dict
        print(f"Wikidata PEP yuklendi: {len(isim_dict)}")
    except Exception as e:
        print(f"Wikidata PEP hata: {e}"); listeler["Wikidata PEP"] = {}

    return listeler