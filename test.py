from dotenv import load_dotenv
import imaplib
import os

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

# Odczyt danych logowania
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
DOWNLOAD_FOLDER = "./attachments"
FOLDER_TO_CHECK = 'INBOX'

mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL, PASSWORD)


def fetch_message_ids(server, email, password, folder):
    # Połączenie z serwerem IMAP
    mail = imaplib.IMAP4_SSL(server)
    mail.login(email, password)

    message_ids = []
    try:
        # Wybór folderu (np. INBOX)
        result, data = mail.select(folder)
        if result != 'OK':
            print(f"Nie udało się wybrać folderu: {folder}")
            return []

        # Pobranie listy wiadomości
        result, data = mail.search(None, 'ALL')
        if result != 'OK':
            print("Nie udało się pobrać wiadomości.")
            return []

        msg_ids = data[0].split()  # Lista ID wiadomości
        for msg_id in msg_ids:
            # Pobranie Message-ID dla każdej wiadomości
            result, data = mail.fetch(msg_id, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
            if result == 'OK' and data:
                raw_message_id = data[0][1].decode().strip()  # Pobierz i dekoduj Message-ID
                message_ids.append(raw_message_id)
    finally:
        mail.logout()

    return message_ids


# Wywołanie funkcji
message_ids = fetch_message_ids(IMAP_SERVER, EMAIL, PASSWORD, FOLDER_TO_CHECK)

print("Pobrane Message-ID:")
for mid in message_ids:
    print(mid)
