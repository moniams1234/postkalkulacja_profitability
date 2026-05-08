import pandas as pd
from .helpers import find_col, batch_label

def add_basic_columns(df):
    df = df.copy()
    numer = find_col(df, ["Numer"])
    zam = find_col(df, ["Zamówienie", "Zamowienie"])
    qty = find_col(df, ["Zamawiana ilość", "Zamawiana ilosc"])

    if numer:
        df["Zlecenie produkcyjne"] = df[numer].astype(str).str.split("-", n=1).str[0].str.strip()
    else:
        df["Zlecenie produkcyjne"] = ""

    if zam:
        df["Lewy 10"] = df[zam].astype(str).str[:10]
    else:
        df["Lewy 10"] = ""

    if qty:
        df["Batch"] = df[qty].apply(batch_label)
    else:
        df["Batch"] = ""

    return df
