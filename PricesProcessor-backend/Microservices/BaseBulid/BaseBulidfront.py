import pandas as pd
import requests

# Ścieżka do pliku Excel
file_path = "Symbols.xlsx"

# Endpoint Springowego kontrolera
url = "http://localhost:8080/executeSQL"
headers = {"Content-Type": "application/json"}

# Wczytaj plik Excel, używając pierwszego wiersza jako nagłówków
df = pd.read_excel(file_path, usecols="B:I", skiprows=0)

# Funkcja do zamiany pustych wartości na NULL
def prepare_value(value):
    return f"'{value}'" if pd.notna(value) else "NULL"

# Przetwarzanie każdego wiersza i wysyłanie zapytania SQL
for _, row in df.iterrows():
    sql = f"""
    INSERT INTO symbol (
        {', '.join(df.columns)}
    ) VALUES (
        {', '.join(prepare_value(row[col]) for col in df.columns)}
    );
    """
    
    # Wysyłanie zapytania SQL do endpointa
    response = requests.post(url, data=sql, headers=headers)
    
    # Sprawdzenie odpowiedzi
    if response.status_code == 200:
        print("SQL executed successfully.")
    else:
        print(f"Failed to execute SQL: {response.text}")