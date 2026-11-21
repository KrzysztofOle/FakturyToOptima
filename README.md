# FakturyToOptima — eksperyment importu faktur z e-maila

**Status: prototyp badawczy, niezweryfikowany importer do Comarch ERP Optima.**

## Cel
Eksperyment z odbiorem załączników faktur przez IMAP, odczytem PDF/OCR i przygotowaniem danych do dalszego importu. Kod nie potwierdza bezpiecznej, kompletnej integracji z bazą Optimy.

## Składniki
- `FakturyToOptima.py` — IMAP, parsowanie e-mail, PDF i OCR;
- `faktury_ocr.py`, `faktury_ocr_refactored.py` — eksperymenty OCR;
- `sql_test.py`, `tabela_df.py`, `flags.py` — skrypty pomocnicze;
- `attachments/` i `faktury.csv` — lokalne artefakty/przykłady (przed publikacją sprawdzić, czy nie zawierają rzeczywistych danych);
- `activate.ps1`, `activate.sh` — historyczne skrypty aktywacji środowiska.

## Technologie
Python, IMAPClient, python-dotenv, pdfplumber, PyMuPDF (`fitz`), pytesseract, Pillow, Pydantic oraz biblioteka OpenAI. OCR wymaga osobnej instalacji Tesseract z danymi językowymi `pol`.

## Uruchomienie
Nie ma aktualnego manifestu wersji zależności ani sprawdzonego entrypointu produkcyjnego. Przed uruchomieniem należy założyć izolowane środowisko, przejrzeć kod i ustalić konfigurację IMAP oraz API **bez zapisywania haseł i danych klientów do Git**. Nie używać produkcyjnej skrzynki ani bazy Optimy w pierwszej próbie.

## Ograniczenia
Nie testowano importu, jakości OCR, zgodności JPK ani bezpieczeństwa poświadczeń. Ten projekt jest odrębny od `ksef-optima-connector`.
