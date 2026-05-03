from data_utils import detect_month_columns
import pandas as pd
import re


def detect_intent(query):
    query = query.lower()

    if any(word in query for word in ["average", "mean"]):
        return "average"
    elif any(word in query for word in ["highest", "max"]):
        return "max"
    elif any(word in query for word in ["lowest", "min"]):
        return "min"
    elif any(word in query for word in ["total", "sum"]):
        return "sum"
    else:
        return "rag"


def find_best_row(df, keywords):

    best_row = None
    best_score = 0

    for _, row in df.iterrows():
        row_text = " ".join([str(v).lower() for v in row.values])

        score = sum(1 for k in keywords if k in row_text)

        if score > best_score:
            best_score = score
            best_row = row

    return best_row, best_score


def handle_calculation(df, query, intent):

    month_cols = detect_month_columns(df)

    if not month_cols:
        return None

    query = re.sub(r"[^\w\s]", "", query.lower())

    # SMART KEYWORD MAPPING
    keyword_map = {
        "pl": ["total", "revenue"],
        "pnl": ["total", "revenue"],
        "p&l": ["total", "revenue"],
        "summary": ["total", "revenue"],
        "overall": ["total", "revenue"],
        "revenue": ["revenue", "sales", "total"],
        "sales": ["sales", "revenue"],
        "profit": ["profit", "income"],
        "income": ["income", "profit"]
    }

    keywords = []

    for word in query.split():
        if word in keyword_map:
            keywords.extend(keyword_map[word])
        else:
            keywords.append(word)

    # Find best row
    best_row, best_score = find_best_row(df, keywords)

    # Fallback to TOTAL row
    if best_row is None or best_score == 0:
        for _, row in df.iterrows():
            first_col = str(row.iloc[0]).lower()
            if "total" in first_col:
                best_row = row
                break

    if best_row is None:
        return None

    try:
        values = best_row[month_cols]

        values = values.astype(str).str.replace(",", "").str.strip()
        values = pd.to_numeric(values, errors="coerce").dropna()

        if values.empty:
            return None

        if intent == "average":
            return values.mean()
        elif intent == "max":
            return values.max()
        elif intent == "min":
            return values.min()
        elif intent == "sum":
            return values.sum()
        else:
            return values

    except:
        return None