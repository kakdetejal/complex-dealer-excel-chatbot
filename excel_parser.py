import pandas as pd

def load_all_sheets(file):

    xls = pd.ExcelFile(file)
    sheets = {}

    for sheet in xls.sheet_names:

        df = pd.read_excel(file, sheet_name=sheet, header=None)

        # STEP 1: Find header row dynamically
        header_row = None

        for i in range(len(df)):
            row_text = " ".join([str(v).lower() for v in df.iloc[i].values])

            if any(month in row_text for month in ["jan", "feb", "mar", "apr"]):
                header_row = i
                break

        # fallback
        if header_row is None:
            header_row = 0

        # 🔥 STEP 2: Set header properly
        df.columns = df.iloc[header_row]
        df = df[header_row + 1:]

        # 🔥 STEP 3: Clean dataframe
        df = df.dropna(how='all')
        df.columns = [str(col).strip() for col in df.columns]

        # 🔥 STEP 4: Convert numeric
        df = df.apply(pd.to_numeric, errors='ignore')

        sheets[sheet] = df

    return sheets