# test przetwarzania faktur korzystajac z OCR
# pierwotny kod wygenerowany prez chatGPT
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from pathlib import Path

# Funkcja do odczytywania tekstu ze skanów faktur w PDF
def odczytaj_fakture(pdf_path: Path):
    wszystkie_teksty = []
    teksty = []

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
                if tekst.strip():
                    wszystkie_teksty.append((page_num, img_index, tekst))
                
            txt = page.get_text("text")
            if txt.strip():
                    wszystkie_teksty.append((page_num, -1, txt))
            

    result = ''
    for strona, obraz, tekst in wszystkie_teksty:
        result += tekst
    return result


if __name__ == "__main__":
    folder = Path("attachments")
    pliki = [p for p in folder.iterdir() if p.is_file()]
    
    for plik in pliki:
        if plik.suffix.lower() == '.pdf':
            print("\n\n")
            print("-" * 40)
            print("-" * 40)
            print("\n")
            print(f"Odczytuję fakturę: {plik.name}")
            if not plik.exists() or not plik.is_file() or plik.stat().st_size == 0:
                print(f"Plik {plik.name} nie istnieje lub pusty.")
                continue
            # Odczytaj tekst z faktury
            tekst_faktury = odczytaj_fakture(plik)
            print(f"Tekst z faktury {plik.name}:\n{tekst_faktury}\n\n\n")
    

    # # Przykład użycia
    # sciezka_pdf = Path("attachments/GD.ZARZAD DRÓG I ZIELENI  15673  13,00.PDF")
    # odczytane_dane = odczytaj_fakture(sciezka_pdf)

    # print(odczytane_dane)


