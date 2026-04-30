import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading

class PdfCompressorPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.place(relwidth=1, relheight=1)

        self.files = []

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.scroll_frame, text="Kompresija PDF fajlova", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(18, 4))
        ctk.CTkLabel(self.scroll_frame, text="Smanji velicinu jednog ili vise PDF fajlova", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 10))

        # Gornji dio - lista i uputstvo
        content_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        content_frame.pack(padx=20, pady=(0, 8), fill="x")
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)

        # LIJEVA STRANA - lista
        left_frame = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", corner_radius=8)
        left_frame.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(left_frame, text="PDF fajlovi", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 2))
        ctk.CTkLabel(left_frame,
            text="Dodaj PDF fajlove koje zelis kompresovati.\nProgram ce kompresovati svaki fajl posebno.",
            font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 6))

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
            height=10
        )
        self.listbox.pack(padx=6, pady=6, fill="both")

        # DESNA STRANA - uputstvo
        right_frame = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", corner_radius=8)
        right_frame.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(right_frame, text="Kako koristiti?", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 8))

        uputstvo = (
            "Koraci:\n\n"
            "1) Dodaj PDF fajlove\n\n"
            "2) Odaberi nivo\n"
            "   kompresije\n\n"
            "3) Odaberi folder za\n"
            "   cuvanje\n\n"
            "4) Klikni 'Kompresuj'\n\n"
            "Nivoi kompresije:\n\n"
            "Lagana – malo manji\n"
            "fajl, odlican kvalitet\n\n"
            "Srednja – dobar\n"
            "balans kvaliteta\n"
            "i velicine\n\n"
            "Jaka – najmanji fajl,\n"
            "vidljivo smanjenje\n"
            "kvaliteta slika\n\n"
            "NAPOMENA:\n"
            "Originalni fajlovi\n"
            "ostaju sacuvani."
        )

        ctk.CTkLabel(right_frame, text=uputstvo, font=ctk.CTkFont(size=11), text_color="#cccccc", justify="left").pack(padx=14, pady=(0, 14), anchor="w")

        # Podesavanja kompresije
        settings_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        settings_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(settings_frame, text="Nivo kompresije", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 4))
        ctk.CTkLabel(settings_frame, text="Veca kompresija = manji fajl, ali i manji kvalitet slika u PDF-u.", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 8))

        nivo_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        nivo_frame.pack(padx=20, pady=(0, 12), fill="x")

        self.kompresija_var = ctk.StringVar(value="Srednja")
        nivoi = [
            ("Lagana  –  manji gubitak kvaliteta, fajl smanjen ~20-30%", "Lagana"),
            ("Srednja  –  balans kvaliteta i velicine, fajl smanjen ~40-60%", "Srednja"),
            ("Jaka  –  najmanji fajl, vidljiv gubitak kvaliteta, fajl smanjen ~60-80%", "Jaka"),
        ]

        for tekst, vrijednost in nivoi:
            ctk.CTkRadioButton(
                nivo_frame,
                text=tekst,
                variable=self.kompresija_var,
                value=vrijednost,
                font=ctk.CTkFont(size=12)
            ).pack(anchor="w", pady=4)

        # Info o cuvanju
        info_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a3a1a", corner_radius=8)
        info_frame.pack(padx=20, pady=(0, 8), fill="x")
        ctk.CTkLabel(info_frame,
            text="Gdje se cuvaju kompresovani fajlovi?\n"
                 "Kompresovani fajlovi se cuvaju u folder koji odaberes.\n"
                 "Naziv fajla ostaje isti kao original.",
            font=ctk.CTkFont(size=11), text_color="#aaffaa", justify="left").pack(padx=14, pady=10, anchor="w")

        # Output folder
        output_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        output_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(output_frame, text="Folder za cuvanje", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 4))
        ctk.CTkLabel(output_frame, text="Odaberi gdje ce se sacuvati kompresovani PDF fajlovi.", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 8))

        folder_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        folder_frame.pack(padx=20, pady=(0, 12), fill="x")

        ctk.CTkButton(folder_frame, text="Odaberi folder", command=self.select_output, width=160, fg_color="#2a6496", hover_color="#1f4f78").pack(side="left", padx=(0, 10))
        self.output_label = ctk.CTkLabel(folder_frame, text="Nije odabran folder", text_color="gray", font=ctk.CTkFont(size=11))
        self.output_label.pack(side="left")

        # Progress
        self.progress = ctk.CTkProgressBar(self.scroll_frame, width=400)
        self.progress.set(0)
        self.progress.pack(pady=(8, 4))

        self.status_label = ctk.CTkLabel(self.scroll_frame, text="", font=ctk.CTkFont(size=12), text_color="#aaaaaa")
        self.status_label.pack(pady=(0, 6))

        ctk.CTkButton(self.scroll_frame, text="Kompresuj PDF", command=self.compress, width=220, height=40, fg_color="#1a7a3c", hover_color="#145e2d", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(4, 18))

        self.output_folder = None

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF fajlovi", "*.pdf")])
        for f in files:
            if f not in self.files:
                self.files.append(f)
                velicina = os.path.getsize(f) / (1024 * 1024)
                self.listbox.insert(tk.END, "  [PDF]  {} ({:.2f} MB)".format(os.path.basename(f), velicina))

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
        self.progress.set(0)
        self.status_label.configure(text="")

    def select_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.output_label.configure(text=folder, text_color="white")

    def set_status(self, text, color="#aaaaaa"):
        self.status_label.configure(text=text, text_color=color)
        self.update_idletasks()

    def compress(self):
        if not self.files:
            messagebox.showwarning("Upozorenje", "Nisi dodao nijedan PDF fajl.")
            return
        if not self.output_folder:
            messagebox.showwarning("Upozorenje", "Nisi odabrao folder za cuvanje.")
            return
        thread = threading.Thread(target=self.run_compress)
        thread.start()

    def run_compress(self):
        import fitz
        import shutil

        nivo = self.kompresija_var.get()

        if nivo == "Lagana":
            garbage = 2
            deflate = True
            img_dpi = 150
        elif nivo == "Srednja":
            garbage = 3
            deflate = True
            img_dpi = 100
        else:  # Jaka
            garbage = 4
            deflate = True
            img_dpi = 72

        ukupno = len(self.files)
        uspjesno = 0
        greske = []
        ukupno_usteda = 0

        self.progress.set(0)
        self.set_status("Kompresija u toku...", "#f0c040")

        for i, filepath in enumerate(self.files):
            naziv = os.path.basename(filepath)
            self.set_status("Kompresujem ({}/{}): {}".format(i+1, ukupno, naziv), "#f0c040")

            try:
                originalna_velicina = os.path.getsize(filepath)

                output_path = os.path.join(self.output_folder, naziv)
                counter = 1
                base = os.path.join(self.output_folder, os.path.splitext(naziv)[0])
                while os.path.exists(output_path):
                    output_path = "{}_kompresovan_{}.pdf".format(base, counter)
                    counter += 1

                doc = fitz.open(filepath)

                # Metod 1: Čistimo i kompresujemo strukturu PDF-a
                doc.save(
                    output_path,
                    garbage=garbage,
                    deflate=deflate,
                    deflate_images=True,
                    deflate_fonts=True,
                    clean=True,
                    linear=True
                )
                doc.close()

                nova_velicina = os.path.getsize(output_path)

                # Ako je novi fajl VECI od originala, koristimo original
                if nova_velicina >= originalna_velicina:
                    shutil.copy2(filepath, output_path)
                    nova_velicina = originalna_velicina
                    self.listbox.delete(i)
                    self.listbox.insert(i, "  [PDF]  {} – nije moglo biti kompresovano".format(naziv))
                else:
                    usteda = originalna_velicina - nova_velicina
                    ukupno_usteda += usteda
                    procenat = (usteda / originalna_velicina * 100)
                    self.listbox.delete(i)
                    self.listbox.insert(i, "  [PDF]  {} → {:.2f} MB  (ustedeno {:.1f}%)".format(
                        naziv,
                        nova_velicina / (1024 * 1024),
                        procenat
                    ))

                uspjesno += 1

            except Exception as e:
                greske.append("{}: {}".format(naziv, str(e)))

            self.progress.set((i + 1) / ukupno)
            self.update_idletasks()

        if ukupno_usteda > 1024 * 1024:
            usteda_str = "{:.2f} MB".format(ukupno_usteda / (1024 * 1024))
        else:
            usteda_str = "{:.0f} KB".format(ukupno_usteda / 1024)

        if not greske:
            self.set_status("Uspjesno kompresovano {} fajlova! Ustedeno {}".format(uspjesno, usteda_str), "#4caf50")
            messagebox.showinfo("Gotovo!", "Uspjesno kompresovano {} fajlova!\n\nUkupno ustedeno: {}\n\nSacuvano u:\n{}".format(
                uspjesno, usteda_str, self.output_folder))
        else:
            self.set_status("Gotovo sa greskama ({} od {} uspjesno)".format(uspjesno, ukupno), "#f0c040")
            messagebox.showwarning("Djelimicno gotovo", "Uspjesno: {} od {}\nUstedeno: {}\n\nGreske:\n{}".format(
                uspjesno, ukupno, usteda_str, "\n".join(greske)))