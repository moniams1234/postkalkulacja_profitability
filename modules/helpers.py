import re
import numpy as np
import pandas as pd

def normalize_col_name(name):
    return re.sub(r"\s+", " ", str(name).replace("\n", " ").replace("\r", " ")).strip()

def normalize_columns(df):
    if df is None:
        return None
    df = df.copy()
    df.columns = [normalize_col_name(c) for c in df.columns]
    return df

def find_col(df, candidates):
    if df is None:
        return None
    lookup = {normalize_col_name(c).lower(): c for c in df.columns}
    for cand in candidates:
        key = normalize_col_name(cand).lower()
        if key in lookup:
            return lookup[key]
    # relaxed contains
    for cand in candidates:
        key = normalize_col_name(cand).lower()
        for k, real in lookup.items():
            if key == k or key in k or k in key:
                return real
    return None

def safe_num(value):
    try:
        if value is None or value == "":
            return 0.0
        v = float(str(value).replace(" ", "").replace(",", "."))
        if np.isnan(v):
            return 0.0
        return v
    except Exception:
        return 0.0

def extract_invoice_fragment(order_text):
    """
    Example:
    KOH-34440-K659995 | 260220_Digital [K659995]
    -> 260220_Digital
    """
    if order_text is None:
        return ""
    txt = str(order_text)
    if "| " in txt:
        txt = txt.split("| ", 1)[1]
    elif "|" in txt:
        txt = txt.split("|", 1)[1].strip()
    if " [" in txt:
        txt = txt.split(" [", 1)[0]
    elif "[" in txt:
        txt = txt.split("[", 1)[0].strip()
    if "|" in txt:
        txt = txt.split("|", 1)[0].strip()
    return txt.strip()

def batch_label(qty):
    q = safe_num(qty)
    if q <= 0:
        return ""
    if q <= 50: return "0-50"
    if q <= 100: return "51-100"
    if q <= 200: return "101-200"
    if q <= 300: return "201-300"
    if q <= 500: return "301-500"
    if q <= 1000: return "501-1000"
    if q <= 1500: return "1001-1500"
    if q <= 2000: return "1501-2000"
    if q <= 3000: return "2001-3000"
    if q <= 10000: return "3001-10000"
    if q <= 20000: return "10001-20000"
    if q <= 30000: return "20001-30000"
    if q <= 100000: return "30001-100000"
    return "100001-1000000"
