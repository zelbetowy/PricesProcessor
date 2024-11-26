import os
import pandas as pd
import requests
import numpy as np

# Ustal ścieżkę do katalogu, w którym znajduje się skrypt
script_dir = os.path.dirname(os.path.abspath(__file__))

# Ustal pełną ścieżkę do pliku Excel, bazując na lokalizacji skryptu
file_path = os.path.join(script_dir, "symbolstoBackend.xlsx")

# URL endpointa kontrolera Springa
url = "http://localhost:8080/symbols/add"
headers = {"Content-Type": "application/json"}

# Wczytaj plik Excel, używając kolumn od B do I, zamieniając NaN, inf i -inf na None
print('Hello, world!')
df = pd.read_excel(file_path, usecols="B:I")

# Zamiana inf i -inf na NaN, a potem wypełnianie NaN jako None
df.replace([np.inf, -np.inf], np.nan, inplace=True)

# Wypełnianie NaN jako None (pusty ciąg)
df = df.applymap(lambda x: None if pd.isna(x) else x)

# Iteracja przez każdy wiersz i wysyłanie danych do API
for _, row in df.iterrows():
    # Dynamiczna konwersja wiersza na słownik na podstawie nagłówków z Excela
    data = row.to_dict()

    # Wysyłanie żądania POST do API
    response = requests.post(url, json=data, headers=headers)

    # Sprawdzenie odpowiedzi
    if response.status_code == 200:
        print(f"Symbol {data.get('symbolFullName', 'unknown')} dodany pomyślnie.")
    else:
        print(f"Błąd przy dodawaniu symbolu: {response.text}")