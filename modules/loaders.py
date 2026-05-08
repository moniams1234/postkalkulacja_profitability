import io
import pandas as pd
from .helpers import normalize_columns

def read_excel_any(uploaded, sheet_name=0, header="auto"):
    if uploaded is None:
        return None
    raw = uploaded.read()
    uploaded.seek(0)
    if header == "auto":
        probe = pd.read_excel(io.BytesIO(raw), sheet_name=sheet_name, header=None, nrows=12)
        header_row = 0
        for i, row in probe.iterrows():
            vals = [str(v).strip() for v in row.dropna().tolist()]
            if len(vals) >= 3:
                header_row = i
                break
        df = pd.read_excel(io.BytesIO(raw), sheet_name=sheet_name, header=header_row)
    else:
        df = pd.read_excel(io.BytesIO(raw), sheet_name=sheet_name, header=header)
    return normalize_columns(df)

def read_post_list(uploaded):
    if uploaded is None:
        return None
    raw = uploaded.read()
    uploaded.seek(0)
    # post_list zwykle ma nagłówki w 4. wierszu, ale jeśli nie pasuje, próbuj auto
    try:
        df = pd.read_excel(io.BytesIO(raw), header=3)
        df = normalize_columns(df)
        if len(df.columns) < 3:
            raise ValueError("too few columns")
        return df
    except Exception:
        return read_excel_any(uploaded, header="auto")

def read_sheet_by_name(uploaded, preferred_names):
    if uploaded is None:
        return None
    raw = uploaded.read()
    uploaded.seek(0)
    xf = pd.ExcelFile(io.BytesIO(raw))
    sheet = xf.sheet_names[0]
    for s in xf.sheet_names:
        sl = s.lower()
        if any(p.lower() in sl for p in preferred_names):
            sheet = s
            break
    return read_excel_any(uploaded, sheet_name=sheet, header="auto")
