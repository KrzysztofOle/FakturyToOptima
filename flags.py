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

# Połączenie z serwerem IMAP
mail = imaplib.IMAP4_SSL(IMAP_SERVER)

try:
    # Logowanie
    mail.login(EMAIL, PASSWORD)

    # Sprawdzenie możliwości serwera
    result, capabilities = mail.capability()
    if result == 'OK':
        print("Możliwości serwera:", capabilities)
    else:
        print("Błąd przy sprawdzaniu możliwości serwera.")

    # # Tworzenie folderu
    # result, data = mail.create('NowyTest')
    # if result == 'OK':
    #     print("Folder 'NowyTest' został utworzony.")
    # else:
    #     print("Błąd przy tworzeniu folderu.")

    # Pobranie listy folderów
    result, data = mail.list()

    if result == 'OK':


        print("Lista folderów:")
        for folder in data:
            print(folder.decode())  # Dekodowanie bajtów do tekstu



        # Przeszukanie listy folderów
        folder_exists = any(FOLDER_TO_CHECK in folder.decode() for folder in data)

        if folder_exists:
            print(f"Folder '{FOLDER_TO_CHECK}' istnieje.")
        else:
            print(f"Folder '{FOLDER_TO_CHECK}' nie istnieje.")
    else:
        print("Nie udało się pobrać listy folderów.")


    # Wybór folderu (np. INBOX)
    mail.select(FOLDER_TO_CHECK)

    # Pobranie UID wiadomości o ID 1
    result, data = mail.fetch('1', '(UID)')
    if result == 'OK':
        # Parsowanie danych odpowiedzi
        # data[0] może wyglądać np. tak: (b'1 (UID 12345)',)
        print(f"Surowa odpowiedź fetch: {data}")
        try:
            raw_response = data[0][0].decode()  # Dekodowanie bajtów do tekstu
            uid = raw_response.split('UID ')[1].split(')')[0]  # Pobranie UID
            print(f"UID wiadomości: {uid}")
        except Exception as e:
            print(e)
            pass

finally:
    # Zamknięcie połączenia
    mail.logout()