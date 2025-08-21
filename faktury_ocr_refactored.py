"""
Moduł OCR/ekstrakcji tekstu z faktur PDF.

Funkcjonalność:
- Ekstrakcja tekstu z PDF-ów zawierających warstwę tekstową (PyMuPDF).
- OCR dla skanów (obrazy w PDF) przy użyciu Tesseract (pytesseract).
- Walidacja plików (rozmiar, rozszerzenie) i bezpieczne przetwarzanie partii plików.
- Współpraca z pipeline'em: pobranie załączników e-mail -> OCR/tekst -> analiza w ChatGPT -> eksport do Optimy.

Wymagania systemowe:
- `pymupdf` (fitz)
- `pytesseract` + zainstalowany binarny Tesseract w systemie
  oraz pakiet języka polskiego (np. `tesseract-ocr-pol` na Debian/Ubuntu).
- `Pillow`

Autor: (uzupełnij wg repo)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict

import io
import fitz  # PyMuPDF
import pytesseract
from PIL import Image


class EmptyPdfError(Exception):
    """Wyjątek sygnalizujący pusty plik PDF (rozmiar 0 lub brak poprawnych danych)."""


@dataclass(frozen=True)
class OcrConfig:
    """Konfiguracja OCR."""
    dpi: int = 300
    lang: str = "pol"   # zainstaluj pakiet językowy dla Tesseract
    psm: int | None = None  # Page Segmentation Mode; np. 6 lub 3
    oem: int | None = None  # OCR Engine Mode


def is_pdf_nonempty(path: Path) -> bool:
    """Sprawdza, czy plik istnieje, jest PDF-em i ma rozmiar > 0 bajtów."""
    return (
        isinstance(path, Path)
        and path.exists()
        and path.is_file()
        and path.suffix.lower() == ".pdf"
        and path.stat().st_size > 0
    )


def extract_text_pymupdf(pdf_path: Path) -> str:
    """
    Ekstrahuje tekst z PDF z warstwą tekstową.

    Zwraca pusty string, jeśli nie uda się wydobyć żadnego tekstu
    (np. gdy PDF to skan). Nie rzuca wyjątków dla typowych problemów
    poza błędami I/O i fitz.
    """
    teksty: List[str] = []
    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            t = page.get_text("text") or ""
            if t:
                teksty.append(t)
    return "\n".join(teksty).strip()


def extract_text_ocr(pdf_path: Path, cfg: OcrConfig | None = None) -> str:
    """
    Wykonuje OCR stron PDF jako obrazów i skleja wynik w jeden string.
    """
    cfg = cfg or OcrConfig()
    ocr_texts: List[str] = []

    tesseract_config = []
    if cfg.psm is not None:
        tesseract_config += [f"--psm {cfg.psm}"]
    if cfg.oem is not None:
        tesseract_config += [f"--oem {cfg.oem}"]
    tesseract_config_str = " ".join(tesseract_config) if tesseract_config else ""

    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            # Render strony do obrazu
            pix = page.get_pixmap(dpi=cfg.dpi)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            # OCR
            text = pytesseract.image_to_string(img, lang=cfg.lang, config=tesseract_config_str) or ""
            ocr_texts.append(text.strip())

    return "\n".join(ocr_texts).strip()


def extract_text_auto(pdf_path: Path, cfg: OcrConfig | None = None) -> str:
    """
    Próbuje najpierw wydobyć tekst natywnie (PyMuPDF). Jeśli brak wyników -> OCR.

    :return: pełny tekst z dokumentu (może być pusty, jeśli OCR i natywna ekstrakcja nic nie znalazły).
    """
    text = extract_text_pymupdf(pdf_path)
    if text:
        return text
    return extract_text_ocr(pdf_path, cfg=cfg)


def odczytaj_fakture(pdf_path: Path, cfg: OcrConfig | None = None) -> str:
    """
    Główna funkcja: zwraca tekst z faktury PDF.
    - Waliduje plik (istnienie, rozmiar, rozszerzenie).
    - Obsługuje PDF z tekstem i skany (OCR).

    :raises FileNotFoundError: gdy plik nie istnieje
    :raises IsADirectoryError: gdy ścieżka wskazuje katalog
    :raises EmptyPdfError: gdy plik ma 0 bajtów lub jest uszkodzony w sposób wykrywany przez fitz
    :return: tekst wyciągnięty z faktury
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"Brak pliku: {pdf_path}")
    if not pdf_path.is_file():
        raise IsADirectoryError(f"To nie jest plik: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Niepoprawne rozszerzenie (oczekiwano .pdf): {pdf_path}")
    if pdf_path.stat().st_size == 0:
        raise EmptyPdfError(f"Pusty plik PDF: {pdf_path}")

    try:
        return extract_text_auto(pdf_path, cfg=cfg)
    except fitz.EmptyFileError as e:
        # PyMuPDF zgłasza to, gdy nie potrafi otworzyć danych (np. uszkodzony lub faktycznie pusty plik)
        raise EmptyPdfError(f"Nie można otworzyć pustego/uszkodzonego PDF: {pdf_path}") from e


def list_nonempty_pdfs(folder: Path, recursive: bool = False) -> list[Path]:
    """
    Zwraca listę niepustych plików PDF w katalogu.

    :param folder: katalog wejściowy
    :param recursive: czy przeszukiwać rekurencyjnie
    """
    it = folder.rglob("*.pdf") if recursive else folder.glob("*.pdf")
    return [p for p in it if is_pdf_nonempty(p)]


def process_folder(folder: Path, recursive: bool = False, cfg: OcrConfig | None = None) -> Dict[Path, str]:
    """
    Przetwarza wszystkie niepuste PDF-y w folderze i zwraca mapę: Path -> tekst.
    Błędy dla pojedynczych plików są łapane i wypisywane na stdout; pozostałe pliki są kontynuowane.
    """
    results: Dict[Path, str] = {}
    for pdf in list_nonempty_pdfs(folder, recursive=recursive):
        try:
            results[pdf] = odczytaj_fakture(pdf, cfg=cfg)
        except Exception as e:  # noqa: BLE001 - intencjonalnie szeroko, by nie zatrzymywać batcha
            print(f"[WARN] {pdf.name}: {e}")
    return results


if __name__ == "__main__":
    # Przykład użycia: przetwórz folder 'attachments/' rekursywnie
    base = Path("attachments")
    if base.exists():
        wyniki = process_folder(base, recursive=True, cfg=OcrConfig(dpi=300, lang="pol"))
        for p, t in wyniki.items():
            print(f"\n=== {p.name} ===\n{t[:1000]}\n...")
    else:
        print("Brak folderu 'attachments' – pomiń przykład.")
