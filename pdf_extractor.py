import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os

class PdfExtractorPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.place(relwidth=1, relheight=1)

        self.files = []

        # Scrollable glavni frame
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.scroll_frame, text="Ekstrakcija stranica iz PDF-a", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(18, 4))
        ctk.CTkLabel(self.scroll_frame, text="Izvadi odredjene stranice iz jednog ili vise PDF fajlova", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 10))

        # Gornji dio - lista i uputstvo
        content_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        content_frame.pack(padx=20, pady=(0, 8), fill="x")
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)

        # LIJEVA STRANA - lista fajlova
        left_frame = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", corner_radius=8)
        left_frame.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(left_frame, text="PDF fajlovi", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 2))
        ctk.CTkLabel(left_frame, text="Dodaj jedan ili vise PDF fajlova iz kojih ces vaditi stranice.\nIsti uslov stranica primjenjuje se na sve fajlove.", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 6))

        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 6))
        ctk.CTkButton(btn_frame, text="+ Dodaj PDF fajlove", command=self.add_files, width=160).grid(row=0, column=0, padx=4)
        ctk.CTkButton(btn_frame, text="Ukloni", command=self.remove_selected, width=90, fg_color="#7a1a1a", hover_color="#5e1414").grid(row=0, column=1, padx=4)
        ctk.CTkButton(btn_frame, text="Ocisti sve", command=self.clear_list, width=90, fg_color="#555", hover_color="#444").grid(row=0, column=2, padx=4)

        listbox_wrap = ctk.CTkFrame(left_frame, fg_color="#1e1e1e", corner_radius=6)
        listbox_wrap.pack(padx=8, pady=(0, 10), fill="both")

        self.listbox = tk.Listbox(
            listbox_wrap,
            bg="#1e1e1e", fg="white",
            selectbackground="#1f6aa5",
            borderwidth=0, highlightthickness=0,
            font=("Segoe UI", 10),
            activestyle="none",
            height=8
        )
        self.listbox.pack(padx=6, pady=6, fill="both")

        # DESNA STRANA - uputstvo
        right_frame = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", corner_radius=8)
        right_frame.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(right_frame, text="Kako koristiti?", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 8))

        uputstvo = (
            "Nacini unosa stranica:\n\n"
            "1) Pojedinacne stranice:\n"
            "   Unesi brojeve odvojene\n"
            "   zarezom.\n"
            "   Primjer:  1, 3, 5, 8\n\n"
            "2) Raspon stranica:\n"
            "   Unesi pocetak i kraj\n"
            "   sa crticom izmedju.\n"
            "   Primjer:  5-30\n\n"
            "3) Kombinacija:\n"
            "   Mozes kombinovati\n"
            "   oboje zajedno.\n"
            "   Primjer:  1, 3, 5-10, 15\n\n"
            "NAPOMENA:\n"
            "Stranice se broje od 1.\n"
            "Isti uslov vazi za sve\n"
            "dodane fajlove."
        )

        ctk.CTkLabel(right_frame, text=uputstvo, font=ctk.CTkFont(size=11), text_color="#cccccc", justify="left").pack(padx=14, pady=(0, 14), anchor="w")

        # Unos stranica
        pages_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        pages_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(pages_frame, text="Stranice za ekstrakciju", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 4))
        ctk.CTkLabel(pages_frame, text="Unesi koje stranice zelis izvaditi. Primjeri: '1, 3, 5'  ili  '5-30'  ili  '1, 3, 5-10, 15'", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 8))

        entry_frame = ctk.CTkFrame(pages_frame, fg_color="transparent")
        entry_frame.pack(pady=(0, 12))

        ctk.CTkLabel(entry_frame, text="Stranice:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=(0, 8))
        self.pages_entry = ctk.CTkEntry(entry_frame, placeholder_text="npr. 1, 3, 5-10, 15", width=300, height=36, font=ctk.CTkFont(size=13))
        self.pages_entry.grid(row=0, column=1)

        ctk.CTkButton(entry_frame, text="Provjeri unos", command=self.check_input, width=130, fg_color="#555", hover_color="#444").grid(row=0, column=2, padx=(10, 0))

        # Status provjere unosa
        self.check_label = ctk.CTkLabel(pages_frame, text="", font=ctk.CTkFont(size=11))
        self.check_label.pack(pady=(0, 10))

        # Preview
        preview_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        preview_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(preview_frame, text="Pregled - sta ce biti izvuceno:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(8, 4))
        ctk.CTkLabel(preview_frame, text="Prikazuje koji fajlovi ce biti obradjeni i koliko stranica ce biti izvuceno iz svakog.", font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", padx=10, pady=(0, 4))

        preview_wrap = ctk.CTkFrame(preview_frame, fg_color="#1e1e1e", corner_radius=6)
        preview_wrap.pack(padx=8, pady=(0, 8), fill="x")

        self.preview_listbox = tk.Listbox(
            preview_wrap,
            bg="#1e1e1e", fg="#aaffaa",
            borderwidth=0, highlightthickness=0,
            font=("Segoe UI", 10),
            activestyle="none",
            height=4
        )
        self.preview_listbox.pack(padx=6, pady=6, fill="x")

        ctk.CTkButton(self.scroll_frame, text="Pregledaj", command=self.show_preview, width=160, fg_color="#555", hover_color="#444").pack(pady=(0, 8))

        # Info o cuvanju
        info_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a3a1a", corner_radius=8)
        info_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(info_frame,
            text="Gdje se cuvaju novi fajlovi?\n"
                 "Program automatski kreira folder 'Izvucene stranice' na istoj lokaciji gdje su originalni fajlovi.\n"
                 "Novi fajlovi dobijaju isti naziv kao originali.",
            font=ctk.CTkFont(size=11), text_color="#aaffaa", justify="left").pack(padx=14, pady=10, anchor="w")

        # Dugme
        ctk.CTkButton(self.scroll_frame, text="Izvuci stranice", command=self.extract, width=220, height=40, fg_color="#1a7a3c", hover_color="#145e2d", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(4, 18))

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF fajlovi", "*.pdf")])
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.listbox.insert(tk.END, "  {}".format(os.path.basename(f)))

    def remove_selected(self):
        idx = self.listbox.curselection()
        if not idx:
            return
        i = idx[0]
        self.files.pop(i)
        self.listbox.delete(i)

    def clear_list(self):
        self.files.clear()
        self.listbox.delete(0, tk.END)
        self.preview_listbox.delete(0, tk.END)
        self.check_label.configure(text="")

    def parse_pages(self, unos, max_page=99999):
        # Parsira unos tipa "1, 3, 5-10, 15" u listu brojeva stranica
        stranice = set()
        dijelovi = unos.replace(" ", "").split(",")
        for dio in dijelovi:
            if not dio:
                continue
            if "-" in dio:
                parts = dio.split("-")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    start = int(parts[0])
                    end = int(parts[1])
                    if start > end:
                        start, end = end, start
                    for p in range(start, end + 1):
                        stranice.add(p)
                else:
                    return None, "Neispavan raspon: '{}'".format(dio)
            elif dio.isdigit():
                stranice.add(int(dio))
            else:
                return None, "Neispravan unos: '{}'".format(dio)

        if not stranice:
            return None, "Nisi unio nijednu stranicu."

        # Filtriramo stranice koje su vece od max
        stranice = sorted([p for p in stranice if 1 <= p <= max_page])
        return stranice, None

    def check_input(self):
        unos = self.pages_entry.get().strip()
        if not unos:
            self.check_label.configure(text="Unesi stranice da bi provjerio.", text_color="gray")
            return
        stranice, greska = self.parse_pages(unos)
        if greska:
            self.check_label.configure(text="Greska: {}".format(greska), text_color="#ff6666")
        else:
            self.check_label.configure(text="OK – Unos je ispravan. Ukupno {} stranica oznaceno.".format(len(stranice)), text_color="#aaffaa")

    def show_preview(self):
        import fitz
        self.preview_listbox.delete(0, tk.END)

        if not self.files:
            self.preview_listbox.insert(tk.END, "  Nema fajlova.")
            return

        unos = self.pages_entry.get().strip()
        if not unos:
            self.preview_listbox.insert(tk.END, "  Unesi stranice pa klikni Pregledaj.")
            return

        for filepath in self.files:
            naziv = os.path.basename(filepath)
            try:
                doc = fitz.open(filepath)
                ukupno_stranica = len(doc)
                doc.close()

                stranice, greska = self.parse_pages(unos, ukupno_stranica)
                if greska:
                    self.preview_listbox.insert(tk.END, "  {} – Greska: {}".format(naziv, greska))
                else:
                    vazi = [p for p in stranice if p <= ukupno_stranica]
                    preskoceno = len(stranice) - len(vazi)
                    info = "  {} – izvlaci {} od {} str.".format(naziv, len(vazi), ukupno_stranica)
                    if preskoceno > 0:
                        info += "  (upozorenje: {} str. ne postoji)".format(preskoceno)
                    self.preview_listbox.insert(tk.END, info)
            except Exception as e:
                self.preview_listbox.insert(tk.END, "  {} – Greska: {}".format(naziv, str(e)))

    def extract(self):
        import fitz

        if not self.files:
            messagebox.showwarning("Upozorenje", "Nisi dodao nijedan PDF fajl.")
            return

        unos = self.pages_entry.get().strip()
        if not unos:
            messagebox.showwarning("Upozorenje", "Nisi unio stranice za ekstrakciju.")
            return

        uspjesno = 0
        greske = []

        for filepath in self.files:
            naziv = os.path.basename(filepath)
            original_folder = os.path.dirname(filepath)

            try:
                doc = fitz.open(filepath)
                ukupno_stranica = len(doc)

                stranice, greska = self.parse_pages(unos, ukupno_stranica)
                if greska:
                    greske.append("{}: {}".format(naziv, greska))
                    doc.close()
                    continue

                # Filtriramo stranice koje postoje u dokumentu
                vazi = [p for p in stranice if p <= ukupno_stranica]
                if not vazi:
                    greske.append("{}: Nijedna od navedenih stranica ne postoji u ovom fajlu (ukupno {} str.)".format(naziv, ukupno_stranica))
                    doc.close()
                    continue

                # Kreiramo output folder
                output_folder = os.path.join(original_folder, "Izvucene stranice")
                os.makedirs(output_folder, exist_ok=True)

                # Novi dokument sa izvucenim stranicama
                novi_doc = fitz.open()
                for br in vazi:
                    novi_doc.insert_pdf(doc, from_page=br-1, to_page=br-1)

                # Cuvamo pod istim nazivom
                output_path = os.path.join(output_folder, naziv)
                counter = 1
                base = os.path.join(output_folder, os.path.splitext(naziv)[0])
                ext = ".pdf"
                while os.path.exists(output_path):
                    output_path = "{}_{}{}".format(base, counter, ext)
                    counter += 1

                novi_doc.save(output_path)
                novi_doc.close()
                doc.close()
                uspjesno += 1

            except Exception as e:
                greske.append("{}: {}".format(naziv, str(e)))

        if not greske:
            messagebox.showinfo("Gotovo!", "Uspjesno izvucene stranice iz {} fajlova!\n\nSacuvano u folderu 'Izvucene stranice' pored originalnih fajlova.".format(uspjesno))
        else:
            messagebox.showwarning("Djelimicno gotovo", "Uspjesno: {} od {}\n\nGreske:\n{}".format(
                uspjesno, len(self.files), "\n".join(greske)))