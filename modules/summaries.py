import pandas as pd
from .helpers import find_col

def customer_summary(df, month=None):
    data = df.copy()
    if month and month != "Wszystkie":
        data = data[data["Miesiąc faktury"] == month]
    klient = find_col(data, ["Klient", "Klient ID"]) or "Zlecenie produkcyjne"
    if klient not in data.columns:
        data[klient] = "(brak)"

    rows = []
    for k, g in data.groupby(klient, dropna=False):
        sv = g["Sales Value"].sum()
        tpm = g["TPM"].sum()
        cm = g["CM"].sum()
        rows.append({
            "Klient": k,
            "Miesiąc faktury": month or "Wszystkie",
            "Suma sprzedaży": sv,
            "Suma TPM": tpm,
            "TPM %": tpm / sv if sv else 0,
            "Suma CM": cm,
            "CM %": cm / sv if sv else 0,
            "Liczba zamówień": len(g),
            "Digital": (g["Digital/Offset"] == "Digital").sum(),
            "Offset": (g["Digital/Offset"] == "Offset").sum(),
            "no printing": (g["Digital/Offset"] == "no printing").sum(),
        })
    return pd.DataFrame(rows)

def batch_summary(df, month=None):
    data = df.copy()
    if month and month != "Wszystkie":
        data = data[data["Miesiąc faktury"] == month]
    klient = find_col(data, ["Klient", "Klient ID"]) or "Zlecenie produkcyjne"
    if "Batch" not in data.columns:
        return pd.DataFrame(columns=["Klient", "Batch", "Liczba zamówień"])
    return data.groupby([klient, "Batch"], dropna=False).size().reset_index(name="Liczba zamówień").rename(columns={klient: "Klient"})
