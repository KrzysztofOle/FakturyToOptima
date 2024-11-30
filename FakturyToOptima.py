#
# Kod częściowo wygenerowany przez ChatGPT
#

from imapclient import IMAPClient
from dotenv import load_dotenv
import email
import os
import pdfplumber
import openai
from pydantic import BaseModel

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

# Odczyt danych logowania
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
DOWNLOAD_FOLDER = "./attachments"

# Ustawienie folderu zapisu
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def save_attachment(msg, folder):
    """Zapisuje załączniki z wiadomości e-mail do określonego folderu."""
    for part in msg.walk():
        if part.get_content_disposition() == "attachment":
            filename = part.get_filename()
            if filename:
                filepath = os.path.join(folder, filename)
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                print(f"Zapisano załącznik: {filepath}")
                return filepath


def fetch_unread_with_attachment():
    # Połączenie z serwerem IMAP
    with IMAPClient(IMAP_SERVER, port=993) as client:
        client.debug = 4  # Poziom debugowania
        client.login(EMAIL, PASSWORD)
        client.select_folder("INBOX")

        # Pobierz nieprzeczytane wiadomości
        messages = client.search(["UNSEEN"])
        print(f"Znaleziono {len(messages)} nieprzeczytanych wiadomości.")

        for msg_id in messages:
            raw_msg = client.fetch([msg_id], ["RFC822"])[msg_id][b"RFC822"]
            email_msg = email.message_from_bytes(raw_msg)

            # Wypisz podstawowe informacje
            subject = email_msg.get("Subject", "Brak tematu")
            print(f"Przetwarzanie wiadomości: {subject}")

            # Zapisz załączniki
            yield save_attachment(email_msg, DOWNLOAD_FOLDER)


def extract_from_pdf(sciezka_pdf):
    # Wczytanie pliku PDF
    with pdfplumber.open(sciezka_pdf) as pdf:
        text = ""
        for i, page in enumerate(pdf.pages):
            text += page.extract_text()
    return text


for filename in fetch_unread_with_attachment():
    print(f'do przetworzenia: {filename}')
    zawartosc = extract_from_pdf(filename)
    print(f'zawartość:\n {zawartosc}')
    print('\n\n==============================================')
