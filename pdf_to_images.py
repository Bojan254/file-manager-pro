import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading

class PdfToImagesPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.place(relwidth=1, relheight=1)

        self.files = []

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.scroll_frame, text="PDF u Slike", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(18, 4))
        ctk.CTkLabel(self.scroll_frame, text="Konvertuj svaku stranicu PDF-a u sliku", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 10))

        content_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        content_frame.pack(padx=20, pady=(0, 8), fill="x")
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)

        # LIJEVA STRANA - lista
        left_frame = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", corner_radius=8)
        left_frame.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(left_frame, text="PDF fajlovi", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 2))
        ctk.CTkLabel(left_frame,
            text="Dodaj PDF fajlove koje zelis konvertovati u slike.\nSvaka stranica postaje posebna slika.",
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
            "2) Odaberi format slike\n"
            "   (JPG ili PNG)\n\n"
            "3) Odaberi kvalitet\n"
            "   (DPI)\n\n"
            "4) Odaberi folder\n\n"
            "5) Klikni 'Konvertuj'\n\n"
            "Imenovanje slika:\n\n"
            "NazivPDF_str_1.jpg\n"
            "NazivPDF_str_2.jpg\n"
            "NazivPDF_str_3.jpg\n\n"
            "NAPOMENA:\n"
            "Svaka stranica PDF-a\n"
            "postaje posebna slika.\n"
            "Veci DPI = bolji\n"
            "kvalitet, sporije."
        )

        ctk.CTkLabel(right_frame, text=uputstvo, font=ctk.CTkFont(size=11), text_color="#cccccc", justify="left").pack(padx=14, pady=(0, 14), anchor="w")

        # Podesavanja
        settings_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        settings_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(settings_frame, text="Podesavanja", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 4))

        opt_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        opt_frame.pack(padx=20, pady=(0, 12), fill="x")
        opt_frame.columnconfigure(1, weight=1)

        # Format
        ctk.CTkLabel(opt_frame, text="Format slike:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", pady=8)
        self.format_var = ctk.StringVar(value="JPG")
        ctk.CTkOptionMenu(opt_frame, variable=self.format_var, values=["JPG", "PNG"], width=120).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=8)
        ctk.CTkLabel(opt_frame, text="(PNG je veci fajl ali bez gubitka kvaliteta)", font=ctk.CTkFont(size=11), text_color="gray").grid(row=0, column=2, sticky="w", padx=(10, 0))

        # DPI
        ctk.CTkLabel(opt_frame, text="Kvalitet (DPI):", font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", pady=8)
        self.dpi_var = ctk.StringVar(value="150")
        ctk.CTkOptionMenu(opt_frame, variable=self.dpi_var, values=["72", "96", "150", "200", "300"], width=120).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=8)
        ctk.CTkLabel(opt_frame, text="(150 je dobar balans brzine i kvaliteta)", font=ctk.CTkFont(size=11), text_color="gray").grid(row=1, column=2, sticky="w", padx=(10, 0))

        # JPG kvalitet
        ctk.CTkLabel(opt_frame, text="JPG kvalitet:", font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w", pady=8)
        self.jpg_quality_var = ctk.StringVar(value="90")
        ctk.CTkOptionMenu(opt_frame, variable=self.jpg_quality_var, values=["60", "70", "80", "90", "95", "100"], width=120).grid(row=2, column=1, sticky="w", padx=(10, 0), pady=8)
        ctk.CTkLabel(opt_frame, text="(vazi samo za JPG format)", font=ctk.CTkFont(size=11), text_color="gray").grid(row=2, column=2, sticky="w", padx=(10, 0))

        # Info
        info_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a3a1a", corner_radius=8)
        info_frame.pack(padx=20, pady=(0, 8), fill="x")
        ctk.CTkLabel(info_frame,
            text="Gdje se cuvaju slike?\n"
                 "Za svaki PDF kreira se poseban podfolder u odabranom folderu.\n"
                 "Naziv podffoldera = naziv PDF fajla.\n"
                 "Naziv slike = NazivPDF_str_1.jpg, NazivPDF_str_2.jpg...",
            font=ctk.CTkFont(size=11), text_color="#aaffaa", justify="left").pack(padx=14, pady=10, anchor="w")

        # Output folder
        output_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        output_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(output_frame, text="Folder za cuvanje", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 4))
        ctk.CTkLabel(output_frame, text="Odaberi gdje ce se sacuvati konvertovane slike.", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 8))

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

        ctk.CTkButton(self.scroll_frame, text="Konvertuj u slike", command=self.convert, width=220, height=40, fg_color="#1a7a3c", hover_color="#145e2d", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(4, 18))

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

    def convert(self):
        if not self.files:
            messagebox.showwarning("Upozorenje", "Nisi dodao nijedan PDF fajl.")
            return
        if not self.output_folder:
            messagebox.showwarning("Upozorenje", "Nisi odabrao folder za cuvanje.")
            return
        thread = threading.Thread(target=self.run_convert)
        thread.start()

    def run_convert(self):
        import fitz
        from PIL import Image
        import io

        format_slike = self.format_var.get()
        dpi = int(self.dpi_var.get())
        jpg_quality = int(self.jpg_quality_var.get())

        ukupno = len(self.files)
        ukupno_slika = 0
        greske = []

        self.progress.set(0)
        self.set_status("Konverzija u toku...", "#f0c040")

        for i, filepath in enumerate(self.files):
            naziv = os.path.basename(filepath)
            ime_bez_ext = os.path.splitext(naziv)[0]
            self.set_status("Konvertujem ({}/{}): {}".format(i+1, ukupno, naziv), "#f0c040")

            try:
                doc = fitz.open(filepath)
                ukupno_stranica = len(doc)

                # Kreiramo poseban podfolder za ovaj PDF
                subfolder = os.path.join(self.output_folder, ime_bez_ext)
                os.makedirs(subfolder, exist_ok=True)

                for page_idx in range(ukupno_stranica):
                    self.set_status("Konvertujem stranicu {}/{} – {}".format(
                        page_idx+1, ukupno_stranica, naziv), "#f0c040")

                    page = doc[page_idx]
                    mat = fitz.Matrix(dpi/72, dpi/72)
                    pix = page.get_pixmap(matrix=mat)

                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                    # Naziv: NazivPDF_str_1.jpg
                    ext = ".jpg" if format_slike == "JPG" else ".png"
                    naziv_slike = "{}_str_{}{}".format(ime_bez_ext, page_idx + 1, ext)
                    output_path = os.path.join(subfolder, naziv_slike)

                    if format_slike == "JPG":
                        img.save(output_path, "JPEG", quality=jpg_quality, optimize=True)
                    else:
                        img.save(output_path, "PNG", optimize=True)

                    ukupno_slika += 1

                doc.close()

            except Exception as e:
                greske.append("{}: {}".format(naziv, str(e)))

            self.progress.set((i + 1) / ukupno)
            self.update_idletasks()

        if not greske:
            self.set_status("Uspjesno konvertovano {} stranica!".format(ukupno_slika), "#4caf50")
            messagebox.showinfo("Gotovo!", "Uspjesno konvertovano {} stranica u slike!\n\nSacuvano u:\n{}".format(
                ukupno_slika, self.output_folder))
        else:
            self.set_status("Gotovo sa greskama.", "#f0c040")
            messagebox.showwarning("Djelimicno gotovo", "Konvertovano {} stranica.\n\nGreske:\n{}".format(
                ukupno_slika, "\n".join(greske)))