import pandas as pd

# Ścieżka do pliku Excel
file_path = "Symbols.xlsx"
output_sql_file = "insert_data.sql"

# Wczytaj plik Excel, używając pierwszego wiersza jako nagłówków
df = pd.read_excel(file_path, usecols="B:I", skiprows=0)

# Funkcja do zamiany pustych wartości na NULL
def prepare_value(value):
    return f"'{value}'" if pd.notna(value) else "NULL"

# Tworzenie pliku SQL
with open(output_sql_file, "w") as file:
    file.write("-- Insert data into symbols table\n")
    for _, row in df.iterrows():
        sql = f"""
        INSERT INTO symbol (
            {', '.join(df.columns)}
        ) VALUES (
            {', '.join(prepare_value(row[col]) for col in df.columns)}
        );
        """
        file.write(sql + "\n")
    print(f"Plik SQL został wygenerowany: {output_sql_file}")