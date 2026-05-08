from .loaders import read_post_list, read_excel_any, read_sheet_by_name
from .validators import missing_base_columns
from .transformations import add_basic_columns
from .calculations import add_time_costs, add_totals
from .prepress import classify_digital_offset, add_prepress_costs
from .offset import add_offset_costs
from .clicks import calculate_clicks
from .sales_value import add_sales_value_and_invoice_date

def build_profitability(files, settings):
    warnings = []
    base = read_post_list(files.get("base"))
    if base is None:
        return None, {"warnings": ["Brak pliku Baza."], "machine_cols": []}

    missing = missing_base_columns(base)
    if missing:
        warnings.append("Brakujące kolumny w Bazie: " + ", ".join(missing))

    df = add_basic_columns(base)

    df_czasy = read_excel_any(files.get("czasy")) if files.get("czasy") else None
    df = classify_digital_offset(df, df_czasy)
    df, df_czasy_out, machine_cols = add_time_costs(df, df_czasy, settings.get("rates", {}))
    if df_czasy is None:
        warnings.append("Brak pliku Czasy – Total DL nie zawiera kosztów maszyn.")

    df_farby = read_sheet_by_name(files.get("farby"), ["pivot", "farby"]) if files.get("farby") else None
    df = add_offset_costs(df, df_farby)
    if df_farby is None:
        warnings.append("Brak pliku Farby – Offset inks i Płyta offsetowa = 0.")

    df_inks = read_excel_any(files.get("inks")) if files.get("inks") else None
    df, df_kliki = calculate_clicks(df, df_inks, settings.get("click_costs", {}))
    if df_inks is None:
        warnings.append("Brak pliku Inks – Moje Kliki = 0.")

    df_zlec = read_excel_any(files.get("zlec")) if files.get("zlec") else None
    df_fry = read_excel_any(files.get("fry")) if files.get("fry") else None
    df = add_sales_value_and_invoice_date(df, df_zlec, df_fry)
    if df_zlec is None and df_fry is None:
        warnings.append("Brak plików faktur – Sales Value i Data faktury mogą być puste.")

    df = add_prepress_costs(
        df,
        settings.get("prepress", {}),
        settings.get("pp_digital", 10.0),
        settings.get("pp_offset", 40.0),
    )
    df = add_totals(df, machine_cols, settings.get("other_pct", 2.0))

    end_cols = ["Total DL", "Total Materials", "Sales Value", "Data faktury", "Miesiąc faktury", "TPM", "CM"]
    other = [c for c in df.columns if c not in end_cols]
    df = df[other + end_cols]

    return df, {
        "warnings": warnings,
        "df_czasy": df_czasy_out,
        "df_kliki": df_kliki,
        "df_farby": df_farby,
        "machine_cols": machine_cols,
    }
