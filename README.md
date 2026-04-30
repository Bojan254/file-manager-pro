# File Manager Pro

> Sveobuhvatni desktop alat za automatizaciju svakodnevnih zadataka vezanih za dokumente, slike i arhive.

---

## O programu

**File Manager Pro** je desktop aplikacija razvijena u Pythonu koja ujedinjuje 12 korisnih alata u jednom modernom interfejsu. Namijenjena je svima koji svakodnevno rade sa PDF fajlovima, Word dokumentima, Excel tabelama, slikama i arhivama, a žele da uštede vrijeme automatizacijom ponavljajućih zadataka.

Program ne zahtijeva instalaciju – dovoljno je pokrenuti `.exe` fajl.

---

## Funkcionalnosti

| # | Modul | Opis |
|---|-------|------|
| 01 | **Ekstrakcija EML Attachmenata** | Automatski izvlači attachmente iz .eml fajlova i organizuje ih u podfoldere |
| 02 | **Spajanje fajlova u PDF** | Spaja PDF, Word i slike u jedan PDF dokument |
| 03 | **Word u PDF** | Batch konverzija .doc/.docx fajlova u PDF |
| 04 | **Slike u PDF** | Konvertuje slike (JPG, PNG, WEBP...) u PDF fajlove |
| 05 | **Preimenovanje fajlova** | Batch preimenovanje sa prefiksom, brojevnim nizom i sufiksom |
| 06 | **Ekstrakcija stranica iz PDF-a** | Izvlači odabrane stranice iz jednog ili više PDF fajlova |
| 07 | **Ekstrakcija slika iz Excela** | Izvlači slike zalijepljene u .xlsx fajlove i čuva ih kao JPG |
| 08 | **Kompresija PDF-a** | Smanjuje veličinu PDF fajlova sa tri nivoa kompresije |
| 09 | **PowerPoint u PDF** | Konvertuje .pptx u PDF sa opcijom 1, 2 ili 4 slajda po stranici |
| 10 | **PDF u slike** | Konvertuje svaku stranicu PDF-a u JPG ili PNG |
| 11 | **Watermark na PDF** | Dodaje tekstualni watermark na svaku stranicu PDF-a |
| 12 | **Otpakivanje ZIP arhiva** | Batch otpakivanje ZIP fajlova sa podrškom za rekurzivno otpakivanje |

---

## Tehnologije

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-1f6aa5)
![PyMuPDF](https://img.shields.io/badge/PDF-PyMuPDF-red)
![Pillow](https://img.shields.io/badge/Images-Pillow-yellow)

- **GUI:** CustomTkinter
- **PDF operacije:** PyMuPDF (fitz), pypdf
- **Konverzija dokumenata:** Windows COM (Word, PowerPoint)
- **Slike:** Pillow
- **Excel:** zipfile + xml.etree
- **Pakovanje:** PyInstaller

---

## Sistemski zahtjevi

- Windows 10 / Windows 11
- Microsoft Office (potreban za Word i PowerPoint konverziju)
- Minimalno 4 GB RAM

---

## Instalacija i pokretanje

### Kao gotova aplikacija (.exe)
Preuzmite `File Manager Pro.exe` i pokrenite ga direktno – bez instalacije.

> **Napomena:** Windows Defender može pokazati upozorenje. Kliknite **"More info" → "Run anyway"**.

### Kao Python projekat
```bash
# Klonirajte repozitorij
git clone https://github.com/vas-username/file-manager-pro.git
cd file-manager-pro

# Instalirajte zavisnosti
pip install customtkinter pypdf pymupdf docx2pdf pyinstaller pillow aspose.slides python-pptx comtypes

# Pokrenite program
python main.py
```

### Pakovanje u .exe
```bash
pyinstaller --noconfirm --onefile --windowed --icon="ikonica.ico" --name="File Manager Pro" main.py
```
