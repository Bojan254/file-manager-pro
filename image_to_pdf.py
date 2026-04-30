import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading

PODRZANI_FORMATI = (
    ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif",
    ".webp", ".gif", ".ico", ".ppm", ".pgm", ".pbm"
)

class ImageToPdfPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.place(relwidth=1, relheight=1)

        self.files = []

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.scroll_frame, text="Slike u PDF", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(18, 4))
        ctk.CTkLabel(self.scroll_frame, text="Konvertuj slike u PDF fajlove – svaka slika postaje poseban PDF", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 10))

        # Gornji dio - lista i uputstvo
        content_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        content_frame.pack(padx=20, pady=(0, 8), fill="x")
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)

        # LIJEVA STRANA - lista
        left_frame = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", corner_radius=8)
        left_frame.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(left_frame, text="Slike za konverziju", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 2))
        ctk.CTkLabel(left_frame,
            text="Dodaj slike koje zelis konvertovati u PDF.\nSvaka slika ce postati poseban PDF fajl.",
            font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 6))

        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 6))

        ctk.CTkButton(btn_frame, text="+ Dodaj slike", command=self.add_files, width=140).grid(row=0, column=0, padx=4)
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
            "1) Dodaj slike klikom na\n"
            "   '+ Dodaj slike'\n\n"
            "2) Odaberi folder u koji\n"
            "   ce se sacuvati PDF-ovi\n\n"
            "3) Klikni 'Konvertuj u PDF'\n\n"
            "Podrzani formati:\n"
            "JPG, JPEG, PNG, BMP,\n"
            "TIFF, TIF, WEBP, GIF,\n"
            "ICO, PPM, PGM, PBM\n\n"
            "NAPOMENA:\n"
            "Svaka slika postaje\n"
            "poseban PDF fajl.\n"
            "Novi fajlovi dobijaju\n"
            "isti naziv kao slike."
        )

        ctk.CTkLabel(right_frame, text=uputstvo, font=ctk.CTkFont(size=11), text_color="#cccccc", justify="left").pack(padx=14, pady=(0, 14), anchor="w")

        # Podesavanja kvaliteta
        settings_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        settings_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(settings_frame, text="Podesavanja", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 4))

        opt_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        opt_frame.pack(padx=20, pady=(0, 12), fill="x")
        opt_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(opt_frame, text="Kvalitet (DPI):", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", pady=6)
        self.dpi_var = ctk.StringVar(value="150")
        dpi_menu = ctk.CTkOptionMenu(opt_frame, variable=self.dpi_var, values=["72", "96", "150", "200", "300"], width=120)
        dpi_menu.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=6)
        ctk.CTkLabel(opt_frame, text="(veci DPI = bolji kvalitet, veci fajl)", font=ctk.CTkFont(size=11), text_color="gray").grid(row=0, column=2, sticky="w", padx=(10, 0))

        ctk.CTkLabel(opt_frame, text="Orijentacija:", font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", pady=6)
        self.orient_var = ctk.StringVar(value="Automatski")
        orient_menu = ctk.CTkOptionMenu(opt_frame, variable=self.orient_var, values=["Automatski", "Portrait", "Landscape"], width=120)
        orient_menu.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=6)
        ctk.CTkLabel(opt_frame, text="(Automatski prepoznaje na osnovu slike)", font=ctk.CTkFont(size=11), text_color="gray").grid(row=1, column=2, sticky="w", padx=(10, 0))

        # Output folder
        output_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        output_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(output_frame, text="Folder za cuvanje", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 4))
        ctk.CTkLabel(output_frame, text="Odaberi gdje ce se sacuvati konvertovani PDF fajlovi.", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 8))

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

        ctk.CTkButton(self.scroll_frame, text="Konvertuj u PDF", command=self.convert, width=220, height=40, fg_color="#1a7a3c", hover_color="#145e2d", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(4, 18))

        self.output_folder = None

    def add_files(self):
        tipovi = " ".join(["*{}".format(f) for f in PODRZANI_FORMATI])
        files = filedialog.askopenfilenames(filetypes=[
            ("Slike", tipovi),
            ("JPG", "*.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("BMP", "*.bmp"),
            ("TIFF", "*.tiff *.tif"),
            ("Ostali formati", "*.webp *.gif *.ico *.ppm *.pgm *.pbm"),
        ])
        for f in files:
            if f not in self.files:
                self.files.append(f)
                ext = os.path.splitext(f)[1].upper()
                self.listbox.insert(tk.END, "  [{}]  {}".format(ext.replace(".", ""), os.path.basename(f)))

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
            messagebox.showwarning("Upozorenje", "Nisi dodao nijednu sliku.")
            return
        if not self.output_folder:
            messagebox.showwarning("Upozorenje", "Nisi odabrao folder za cuvanje.")
            return
        thread = threading.Thread(target=self.run_convert)
        thread.start()

    def run_convert(self):
        from PIL import Image

        ukupno = len(self.files)
        uspjesno = 0
        greske = []

        self.progress.set(0)
        self.set_status("Konverzija u toku...", "#f0c040")

        dpi = int(self.dpi_var.get())
        orijentacija = self.orient_var.get()

        for i, filepath in enumerate(self.files):
            naziv = os.path.basename(filepath)
            self.set_status("Konvertujem ({}/{}): {}".format(i+1, ukupno, naziv), "#f0c040")

            try:
                img = Image.open(filepath)

                # Konvertujemo u RGB ako je potrebno
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")

                # Orijentacija
                w, h = img.size
                if orijentacija == "Portrait" and w > h:
                    img = img.rotate(90, expand=True)
                elif orijentacija == "Landscape" and h > w:
                    img = img.rotate(90, expand=True)

                # Naziv output fajla
                ime_bez_ext = os.path.splitext(naziv)[0]
                output_path = os.path.join(self.output_folder, ime_bez_ext + ".pdf")

                counter = 1
                base_path = os.path.join(self.output_folder, ime_bez_ext)
                while os.path.exists(output_path):
                    output_path = "{}_{}{}".format(base_path, counter, ".pdf")
                    counter += 1

                img.save(output_path, "PDF", resolution=dpi)
                img.close()
                uspjesno += 1

            except Exception as e:
                greske.append("{}: {}".format(naziv, str(e)))

            self.progress.set((i + 1) / ukupno)
            self.update_idletasks()

        if not greske:
            self.set_status("Uspjesno konvertovano {} slika!".format(uspjesno), "#4caf50")
            messagebox.showinfo("Gotovo!", "Sve slike su uspjesno konvertovane u PDF!\n\nSacuvano u:\n{}".format(self.output_folder))
        else:
            self.set_status("Gotovo sa greskama ({} od {} uspjesno)".format(uspjesno, ukupno), "#f0c040")
            messagebox.showwarning("Djelimicno gotovo", "Uspjesno: {} od {}\n\nGreske:\n{}".format(
                uspjesno, ukupno, "\n".join(greske)))