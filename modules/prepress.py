from .helpers import safe_num

def classify_digital_offset(df_profit, df_czasy):
    df_profit = df_profit.copy()
    if df_czasy is None:
        df_profit["Digital/Offset"] = ""
        return df_profit

    cols = {c.lower(): c for c in df_czasy.columns}
    zp_col = next((v for k, v in cols.items() if "numer zlecenia produkcyjnego" in k), None)
    mach_col = next((v for k, v in cols.items() if "nazwa maszyny" in k), None)
    if not zp_col or not mach_col:
        df_profit["Digital/Offset"] = ""
        return df_profit

    tmp = df_czasy.copy()
    tmp["_zp"] = tmp[zp_col].astype(str).str.strip()
    tmp["_mach"] = tmp[mach_col].astype(str).str.lower().str.replace(r"\s+", " ", regex=True).str.strip()

    def classify(zp):
        sub = tmp[tmp["_zp"] == str(zp).strip()]
        if sub.empty:
            return ""
        machines = " | ".join(sub["_mach"].tolist())
        is_hp = any(x in machines for x in ["hp 35", "hp35", "hp 7", "hp7", "hp 1", "hp1"])
        is_heid = "heidelberg cx 104" in machines or "cx 104" in machines
        if is_hp:
            return "Digital"
        if is_heid:
            return "Offset"
        return "no printing"

    df_profit["Digital/Offset"] = df_profit["Zlecenie produkcyjne"].apply(classify)
    return df_profit

def add_prepress_costs(df, prepress_table=None, default_digital=10.0, default_offset=40.0):
    df = df.copy()
    prepress_table = prepress_table or {}
    klient_col = None
    for c in df.columns:
        if c.lower() in ["klient", "klient id"]:
            klient_col = c
            break

    def calc(row):
        klient = str(row.get(klient_col, "")).strip() if klient_col else ""
        offset_inks = safe_num(row.get("Offset inks", 0))
        pp = prepress_table.get(klient, {})
        if offset_inks > 0:
            return safe_num(pp.get("offset", default_offset))
        return safe_num(pp.get("digital", default_digital))

    df["Prepress costs"] = df.apply(calc, axis=1)
    return df
