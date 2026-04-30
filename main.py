import customtkinter as ctk
from zip_extractor import ZipExtractorPanel
from pdf_watermark import PdfWatermarkPanel
from pdf_to_images import PdfToImagesPanel
from pptx_to_pdf import PptxToPdfPanel
from pdf_compressor import PdfCompressorPanel
from excel_image_extractor import ExcelImageExtractorPanel
from image_to_pdf import ImageToPdfPanel
from pdf_extractor import PdfExtractorPanel
from file_renamer import FileRenamerPanel
from word_to_pdf import WordToPdfPanel
from eml_extractor import EmlExtractorPanel
from pdf_merger import PdfMergerPanel

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("File Manager Pro")
        self.geometry("750x600")
        self.minsize(750, 600)
        self.resizable(True, True)

        # Naslov
        self.label_title = ctk.CTkLabel(self, text="File Manager Pro", font=ctk.CTkFont(size=22, weight="bold"))
        self.label_title.pack(pady=(20, 5))

        # Podnaslov
        self.label_sub = ctk.CTkLabel(self, text="Odaberi funkciju iz menija", font=ctk.CTkFont(size=13), text_color="gray")
        self.label_sub.pack(pady=(0, 15))

        # Padajuci meni
        self.selected_function = ctk.StringVar(value="-- Odaberi funkciju --")
        self.dropdown = ctk.CTkOptionMenu(
            self,
            variable=self.selected_function,
            values=[
                "Ekstrakcija EML attachmenata",
                "Spajanje PDF fajlova",
                "Word u PDF",
                "Slike u PDF",
                "PowerPoint u PDF",
                "PDF u Slike",
                "Kompresija PDF fajlova",
                "Watermark na PDF",
                "Otpakivanje ZIP arhiva",
                "Preimenovanje fajlova",
                "Ekstrakcija stranica iz PDF-a",
                "Ekstrakcija slika iz Excela"
            ],
            command=self.on_function_selected,
            width=300,
            font=ctk.CTkFont(size=13)
        )
        self.dropdown.pack(pady=(0, 20))

        # Glavni okvir - sad se razvlaci sa prozorom
        self.main_frame = ctk.CTkFrame(self, corner_radius=12)
        self.main_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        # Pocetna poruka
        self.placeholder = ctk.CTkLabel(
            self.main_frame,
            text="Odaberi funkciju iz padajuceg menija\nda bi se prikazao odgovarajuci interfejs.",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def on_function_selected(self, choice):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        if choice == "Ekstrakcija EML attachmenata":
            EmlExtractorPanel(self.main_frame)
        elif choice == "Spajanje PDF fajlova":
            PdfMergerPanel(self.main_frame)
        elif choice == "Word u PDF":
            WordToPdfPanel(self.main_frame)
        elif choice == "Preimenovanje fajlova":
            FileRenamerPanel(self.main_frame)
        elif choice == "Ekstrakcija stranica iz PDF-a":
            PdfExtractorPanel(self.main_frame)
        elif choice == "Slike u PDF":
            ImageToPdfPanel(self.main_frame)
        elif choice == "Ekstrakcija slika iz Excela":
            ExcelImageExtractorPanel(self.main_frame)
        elif choice == "Kompresija PDF fajlova":
            PdfCompressorPanel(self.main_frame)
        elif choice == "PowerPoint u PDF":
            PptxToPdfPanel(self.main_frame)
        elif choice == "PDF u Slike":
            PdfToImagesPanel(self.main_frame)
        elif choice == "Watermark na PDF":
            PdfWatermarkPanel(self.main_frame)
        elif choice == "Otpakivanje ZIP arhiva":
            ZipExtractorPanel(self.main_frame)

    def load_placeholder(self, naziv):
        label = ctk.CTkLabel(
            self.main_frame,
            text="Modul: {}\n\n(uskoro...)".format(naziv),
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        label.place(relx=0.5, rely=0.5, anchor="center")

if __name__ == "__main__":
    app = App()
    app.mainloop()