from .helpers import find_col

BASE_REQUIRED = [
    "Numer", "Zamówienie", "Zamawiana ilość",
    "Papier [16]", "Klej [17]", "Lakiery [20]",
    "Opakowania zbiorcze [24]", "Kliki [48]"
]

def missing_base_columns(df):
    missing = []
    for c in BASE_REQUIRED:
        if find_col(df, [c]) is None:
            missing.append(c)
    if find_col(df, ["Klient", "Klient ID"]) is None:
        missing.append("Klient lub Klient ID")
    return missing
