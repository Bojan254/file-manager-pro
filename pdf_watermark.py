import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading

class PdfWatermarkPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.place(relwidth=1, relheight=1)

        self.files = []

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.scroll_frame, text="Dodavanje Watermark-a na PDF", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(18, 4))
        ctk.CTkLabel(self.scroll_frame, text="Dodaj tekst watermark na svaku stranicu PDF fajla", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 10))

        content_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        content_frame.pack(padx=20, pady=(0, 8), fill="x")
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)

        # LIJEVA STRANA - lista
        left_frame = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", corner_radius=8)
        left_frame.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(left_frame, text="PDF fajlovi", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 2))
        ctk.CTkLabel(left_frame,
            text="Dodaj PDF fajlove na koje zelis dodati watermark.\nWatermark ce biti dodan na svaku stranicu.",
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
            height=8
        )
        self.listbox.pack(padx=6, pady=6, fill="both")

        # DESNA STRANA - uputstvo
        right_frame = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", corner_radius=8)
        right_frame.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(right_frame, text="Kako koristiti?", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 8))

        uputstvo = (
            "Koraci:\n\n"
            "1) Dodaj PDF fajlove\n\n"
            "2) Unesi tekst\n"
            "   watermark-a\n\n"
            "3) Podesi poziciju,\n"
            "   velicinu i prozirnost\n\n"
            "4) Odaberi folder\n\n"
            "5) Klikni 'Dodaj'\n\n"
            "NAPOMENA:\n"
            "Tekst se automatski\n"
            "prilagodjava velicini\n"
            "stranice.\n\n"
            "Originalni fajlovi\n"
            "ostaju sacuvani."
        )

        ctk.CTkLabel(right_frame, text=uputstvo, font=ctk.CTkFont(size=11), text_color="#cccccc", justify="left").pack(padx=14, pady=(0, 14), anchor="w")

        # Podesavanja watermark-a
        wm_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        wm_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(wm_frame, text="Podesavanja watermark-a", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 4))

        opt_frame = ctk.CTkFrame(wm_frame, fg_color="transparent")
        opt_frame.pack(padx=20, pady=(0, 12), fill="x")
        opt_frame.columnconfigure(1, weight=1)

        # Tekst
        ctk.CTkLabel(opt_frame, text="Tekst:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", pady=8)
        self.wm_text = ctk.CTkEntry(opt_frame, placeholder_text="npr. POVJERLJIVO, DRAFT, naziv firme...", width=320, height=34)
        self.wm_text.grid(row=0, column=1, columnspan=2, sticky="w", padx=(10, 0), pady=8)

        # Pozicija
        ctk.CTkLabel(opt_frame, text="Pozicija:", font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", pady=8)
        self.pozicija_var = ctk.StringVar(value="Centar (dijagonalno)")
        pozicije = [
            "Centar (dijagonalno)",
            "Centar (horizontalno)",
            "Gore - centar",
            "Dolje - centar",
            "Gore - lijevo",
            "Gore - desno",
            "Dolje - lijevo",
            "Dolje - desno"
        ]
        ctk.CTkOptionMenu(opt_frame, variable=self.pozicija_var, values=pozicije, width=220).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=8)

        # Velicina fonta
        ctk.CTkLabel(opt_frame, text="Velicina teksta:", font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w", pady=8)
        self.font_size_var = ctk.StringVar(value="48")
        ctk.CTkOptionMenu(opt_frame, variable=self.font_size_var, values=["24", "36", "48", "60", "72", "96"], width=120).grid(row=2, column=1, sticky="w", padx=(10, 0), pady=8)
        ctk.CTkLabel(opt_frame, text="(automatski se prilagodjava ako je prevelik)", font=ctk.CTkFont(size=11), text_color="gray").grid(row=2, column=2, sticky="w", padx=(10, 0))

        # Prozirnost
        ctk.CTkLabel(opt_frame, text="Prozirnost:", font=ctk.CTkFont(size=12)).grid(row=3, column=0, sticky="w", pady=8)
        self.opacity_var = ctk.StringVar(value="15")
        ctk.CTkOptionMenu(opt_frame, variable=self.opacity_var, values=["5", "10", "15", "20", "30", "40", "50"], width=120).grid(row=3, column=1, sticky="w", padx=(10, 0), pady=8)
        ctk.CTkLabel(opt_frame, text="(manji broj = bledje)", font=ctk.CTkFont(size=11), text_color="gray").grid(row=3, column=2, sticky="w", padx=(10, 0))

        # Boja
        ctk.CTkLabel(opt_frame, text="Boja:", font=ctk.CTkFont(size=12)).grid(row=4, column=0, sticky="w", pady=8)
        self.boja_var = ctk.StringVar(value="Siva")
        ctk.CTkOptionMenu(opt_frame, variable=self.boja_var, values=["Siva", "Crvena", "Plava", "Zelena", "Crna"], width=120).grid(row=4, column=1, sticky="w", padx=(10, 0), pady=8)

        # Info
        info_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a3a1a", corner_radius=8)
        info_frame.pack(padx=20, pady=(0, 8), fill="x")
        ctk.CTkLabel(info_frame,
            text="Gdje se cuvaju fajlovi?\n"
                 "Fajlovi se cuvaju u folder koji odaberes pod istim nazivom kao original.\n"
                 "Originalni fajlovi ostaju nepromijenjeni.",
            font=ctk.CTkFont(size=11), text_color="#aaffaa", justify="left").pack(padx=14, pady=10, anchor="w")

        # Output folder
        output_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        output_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(output_frame, text="Folder za cuvanje", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 4))

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

        ctk.CTkButton(self.scroll_frame, text="Dodaj Watermark", command=self.add_watermark, width=220, height=40, fg_color="#1a7a3c", hover_color="#145e2d", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(4, 18))

        self.output_folder = None

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF fajlovi", "*.pdf")])
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.listbox.insert(tk.END, "  [PDF]  {}".format(os.path.basename(f)))

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

    def get_boja_rgb(self):
        boje = {
            "Siva":   (0.5, 0.5, 0.5),
            "Crvena": (0.8, 0.0, 0.0),
            "Plava":  (0.0, 0.0, 0.8),
            "Zelena": (0.0, 0.6, 0.0),
            "Crna":   (0.0, 0.0, 0.0),
        }
        return boje.get(self.boja_var.get(), (0.5, 0.5, 0.5))

    def fit_text(self, font, tekst, max_sirina, font_size):
        # Smanjuje font dok tekst ne stane u max_sirina
        while font_size > 8:
            if font.text_length(tekst, fontsize=font_size) <= max_sirina:
                break
            font_size -= 1
        return font_size

    def podijeli_tekst(self, rijeci, font, font_size, max_sirina):
        # Dijeli tekst u redove koji stanu u max_sirina
        redovi = []
        trenutni_red = []

        for rijec in rijeci:
            test = " ".join(trenutni_red + [rijec])
            if font.text_length(test, fontsize=font_size) <= max_sirina:
                trenutni_red.append(rijec)
            else:
                if trenutni_red:
                    redovi.append(" ".join(trenutni_red))
                trenutni_red = [rijec]

        if trenutni_red:
            redovi.append(" ".join(trenutni_red))

        return redovi

    def add_watermark(self):
        if not self.files:
            messagebox.showwarning("Upozorenje", "Nisi dodao nijedan PDF fajl.")
            return
        if not self.wm_text.get().strip():
            messagebox.showwarning("Upozorenje", "Nisi unio tekst watermark-a.")
            return
        if not self.output_folder:
            messagebox.showwarning("Upozorenje", "Nisi odabrao folder za cuvanje.")
            return
        thread = threading.Thread(target=self.run_watermark)
        thread.start()

    def run_watermark(self):
        import fitz
        import math

        tekst = self.wm_text.get().strip()
        pozicija = self.pozicija_var.get()
        font_size = int(self.font_size_var.get())
        opacity = int(self.opacity_var.get()) / 100
        boja = self.get_boja_rgb()
        margina = 25

        ukupno = len(self.files)
        uspjesno = 0
        greske = []

        self.progress.set(0)
        self.set_status("Dodavanje watermark-a u toku...", "#f0c040")

        for i, filepath in enumerate(self.files):
            naziv = os.path.basename(filepath)
            self.set_status("Obradjujem ({}/{}): {}".format(i+1, ukupno, naziv), "#f0c040")

            try:
                doc = fitz.open(filepath)

                for page in doc:
                    pw = page.rect.width
                    ph = page.rect.height
                    font = fitz.Font("helv")
                    rijeci = tekst.split()

                    if "dijagonalno" in pozicija:
                        # Za dijagonalu max duzina je 70% od manje dimenzije
                        max_sirina = min(pw, ph) * 0.70

                        # Smanjujemo font dok jedna rijec stane
                        fs = self.fit_text(font, max(rijeci, key=len), max_sirina, font_size)

                        # Dijelimo tekst u redove
                        redovi = self.podijeli_tekst(rijeci, font, fs, max_sirina)

                        cx = pw / 2
                        cy = ph / 2
                        razmak = fs * 1.4
                        ukupna_visina = razmak * len(redovi)

                        tw = fitz.TextWriter(page.rect)
                        for r_idx, red in enumerate(redovi):
                            w = font.text_length(red, fontsize=fs)
                            x = cx - w / 2
                            y = cy - ukupna_visina / 2 + r_idx * razmak + fs
                            tw.append(fitz.Point(x, y), red, font=font, fontsize=fs)

                        tw.write_text(page, color=boja, opacity=opacity,
                                      morph=(fitz.Point(cx, cy), fitz.Matrix(45)))

                    else:
                        # Za horizontalne pozicije max sirina je sirina stranice minus margine
                        max_sirina = pw - 2 * margina

                        # Smanjujemo font dok jedna rijec stane
                        fs = self.fit_text(font, max(rijeci, key=len), max_sirina, font_size)

                        # Dijelimo tekst u redove
                        redovi = self.podijeli_tekst(rijeci, font, fs, max_sirina)

                        razmak = fs * 1.4
                        ukupna_visina = razmak * len(redovi)

                        tw = fitz.TextWriter(page.rect)

                        for r_idx, red in enumerate(redovi):
                            w = font.text_length(red, fontsize=fs)

                            if pozicija == "Centar (horizontalno)":
                                x = pw / 2 - w / 2
                                y = ph / 2 - ukupna_visina / 2 + r_idx * razmak + fs

                            elif pozicija == "Gore - centar":
                                x = pw / 2 - w / 2
                                y = margina + r_idx * razmak + fs

                            elif pozicija == "Dolje - centar":
                                x = pw / 2 - w / 2
                                y = ph - ukupna_visina + r_idx * razmak - margina + fs

                            elif pozicija == "Gore - lijevo":
                                x = margina
                                y = margina + r_idx * razmak + fs

                            elif pozicija == "Gore - desno":
                                x = pw - w - margina
                                y = margina + r_idx * razmak + fs

                            elif pozicija == "Dolje - lijevo":
                                x = margina
                                y = ph - ukupna_visina + r_idx * razmak - margina + fs

                            else:  # Dolje - desno
                                x = pw - w - margina
                                y = ph - ukupna_visina + r_idx * razmak - margina + fs

                            tw.append(fitz.Point(x, y), red, font=font, fontsize=fs)

                        tw.write_text(page, color=boja, opacity=opacity)

                # Cuvamo
                output_path = os.path.join(self.output_folder, naziv)
                counter = 1
                base = os.path.join(self.output_folder, os.path.splitext(naziv)[0])
                while os.path.exists(output_path):
                    output_path = "{}_wm_{}.pdf".format(base, counter)
                    counter += 1

                doc.save(output_path)
                doc.close()
                uspjesno += 1

            except Exception as e:
                greske.append("{}: {}".format(naziv, str(e)))

            self.progress.set((i + 1) / ukupno)
            self.update_idletasks()

        if not greske:
            self.set_status("Watermark dodan na {} fajlova!".format(uspjesno), "#4caf50")
            messagebox.showinfo("Gotovo!", "Watermark uspjesno dodan na {} fajlova!\n\nSacuvano u:\n{}".format(
                uspjesno, self.output_folder))
        else:
            self.set_status("Gotovo sa greskama ({} od {} uspjesno)".format(uspjesno, ukupno), "#f0c040")
            messagebox.showwarning("Djelimicno gotovo", "Uspjesno: {} od {}\n\nGreske:\n{}".format(
                uspjesno, ukupno, "\n".join(greske)))