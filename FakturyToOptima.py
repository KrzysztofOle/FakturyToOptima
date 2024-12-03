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
import re
from datetime import datetime

# ocr
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io


# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()

# Odczyt danych logowania
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
DOWNLOAD_FOLDER = "./attachments"

# Ustawienie folderu zapisu
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

class Invoice(BaseModel):
    invoice_date: str
    company_name_from: str
    company_name_to: str
    invoice_number: str
    buyers_tax_identification_number: str

    # Typ dokumentu
    # NIP wystawiającego dokument
    # Numer dokumentu
    # Data wystawienia dokumentu
    # Data sprzedaży
    # Nip odbiorcy dokumentu
    # Wartość netto
    # stawki vat: 23%, 8%, 5%, 0% i zw
    # Stawka Vat
    # Kwoty Vat

    def format_date(self):
        self.invoice_date = datetime.strptime(self.invoice_date, "%Y-%m-%d")


# Funkcja do odczytywania tekstu ze skanów faktur w PDF
def odczytaj_fakture_ocr(pdf_path):
    wszystkie_teksty = []

    # Otwórz plik PDF
    with fitz.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf, start=1):
            # Ekstrakcja obrazów z każdej strony PDF
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]

                # Przetwórz obraz za pomocą PIL
                image = Image.open(io.BytesIO(image_bytes))

                # OCR na obrazie (ustaw język polski)
                tekst = pytesseract.image_to_string(image, lang="pol")

                wszystkie_teksty.append((page_num, img_index, tekst))

    result = ''
    for strona, obraz, tekst in wszystkie_teksty:
        result += tekst
    return result


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

def clean_text(text):
    # Zachowuje polskie znaki, litery łacińskie, cyfry i podstawowe znaki interpunkcyjne
    return re.sub(r"[^\w\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ.,;:!?\-\"\'\(\)\[\]\/]+", "", text)

def czy_pdf_zawiera_tekst(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tekst = page.extract_text()  # Pobiera tekst z warstwy tekstowej
            if tekst and tekst.strip():  # Sprawdza, czy tekst istnieje i nie jest pusty
                return True
    return False


def extract_from_pdf(sciezka_pdf):
    # Wczytanie pliku PDF
    with pdfplumber.open(sciezka_pdf) as pdf:
        text = ""
        for i, page in enumerate(pdf.pages):
            text += page.extract_text()
    return clean_text(text)


lista_faktur = []

client = openai.OpenAI()


for filename in fetch_unread_with_attachment():
    print('\n\n==============================================')
    # print(f'do przetworzenia: {filename}')
    zawartosc = ''
    try:
        zawartosc = extract_from_pdf(filename)
    except Exception as e:
        print(e)

    try:
        if zawartosc == '' or len(zawartosc)<10:
            zawartosc = odczytaj_fakture_ocr(filename)
        # print(f'zawartość:\n {zawartosc}')
    except Exception as e:
        print(e)

    if zawartosc == '':
        continue

    response = client.beta.chat.completions.parse(
        model='gpt-4o-mini',
        messages= [
            {'role': 'system', 'content': 'Prosze wyciągnij dane z faktur. '
                                          'Musze poznać date, nazwe firmy która wystawiła fakturę, '
                                          'nazwe firmy na jaką została wystawiona faktura oraz numer faktury, '
                                          'oraz nip nabywcy'
                                          'Daty formatuj jako YYYY-MM-DD'
            },
            {'role': 'user', 'content': zawartosc}
        ],
        response_format=Invoice
    )
    invoice = response.choices[0].message.parsed
    invoice.format_date()
    print(invoice)
    lista_faktur.append(invoice)
print('==============================================\n\n')
print('\n\n\n\n')
for ff in lista_faktur:
    print(ff)
