# test przetwarzania faktur korzystajac z OCR
# pierwotny kod wygenerowany prez chatGPT
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io


# Funkcja do odczytywania tekstu ze skanów faktur w PDF
def odczytaj_fakture(pdf_path):
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


# Przykład użycia
sciezka_pdf = "attachments/PKP SZYBKA KOLEJ  F.28.522.11.2024  108,00.PDF"
odczytane_dane = odczytaj_fakture(sciezka_pdf)

print(odczytane_dane)