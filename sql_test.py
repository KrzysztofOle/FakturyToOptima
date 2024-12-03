import mysql.connector


from dotenv import load_dotenv
import imaplib
import os

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

# Odczyt danych logowania
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DP_PASSWORD = os.getenv("DP_PASSWORD")
DP_DATABASE = os.getenv("DP_DATABASE")

def create_invoices_table():
    conn = mysql.connector.connect(
        host=DB_HOST,           # Adres serwera (np. 'db.example.com')
        user=DB_USER,           # Twoja nazwa użytkownika
        password=DP_PASSWORD,   # Twoje hasło
        database=DP_DATABASE    # Nazwa bazy danych
    )
    cursor = conn.cursor()

    # Tworzenie tabeli
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Faktury (
        id INT AUTO_INCREMENT PRIMARY KEY,
        message_id VARCHAR(255) NOT NULL,
        nazwa_zalacznika VARCHAR(255) NOT NULL,
        numer_faktury VARCHAR(100) NOT NULL,
        data_wystawienia_faktury DATE NOT NULL,
        UNIQUE (message_id)
    )
    """)

    conn.commit()  # Zapisz zmiany
    conn.close()  # Zamknięcie połączenia

# Wywołanie funkcji
create_invoices_table()