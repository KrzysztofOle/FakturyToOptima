

import pandas as pd

# Tworzenie DataFrame z przykładowymi danymi
data = {
    'message_id': ['<12345abc@example.com>', '<67890def@example.com>'],
    'nazwa_zalacznika': ['faktura_123.pdf', 'faktura_124.pdf'],
    'numer_faktury': ['FV123/2024', 'FV124/2024'],
    'data_wystawienia_faktury': ['2024-12-03', '2024-12-04']
}

df = pd.DataFrame(data)

# Wyświetlenie danych
print(df)

# Zapisz do pliku CSV
df.to_csv('faktury.csv', index=False)