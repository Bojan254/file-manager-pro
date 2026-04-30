import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import zipfile
import re

class ZipExtractorPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.place(relwidth=1, relheight=1)

        self.files = []

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.scroll_frame, text="Otpakivanje ZIP arhiva", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(18, 4))
        ctk.CTkLabel(self.scroll_frame, text="Otpakuj jedan ili vise ZIP fajlova automatski", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 10))

        content_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        content_frame.pack(padx=20, pady=(0, 8), fill="x")
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)

        # LIJEVA STRANA - lista
        left_frame = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", corner_radius=8)
        left_frame.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(left_frame, text="ZIP fajlovi", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 2))
        ctk.CTkLabel(left_frame,
            text="Dodaj ZIP fajlove koje zelis otpakovati.\nProgram ce otpakovati svaki fajl posebno.",
            font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 6))

        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 6))
        ctk.CTkButton(btn_frame, text="+ Dodaj ZIP fajlove", command=self.add_files, width=160).grid(row=0, column=0, padx=4)
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
            "1) Dodaj ZIP fajlove\n\n"
            "2) Odaberi gdje ce se\n"
            "   otpakovati fajlovi\n\n"
            "3) Podesi opcije\n\n"
            "4) Klikni 'Otpakuj'\n\n"
            "Opcije:\n\n"
            "Poseban folder –\n"
            "svaki ZIP dobija\n"
            "svoj folder\n\n"
            "Rekurzivno –\n"
            "otpakuje ZIP unutar\n"
            "ZIP-a automatski\n"
            "(do 10 nivoa dubine)\n\n"
            "NAPOMENA:\n"
            "Program automatski\n"
            "rjesava probleme sa:\n"
            "- dugim putanjama\n"
            "- specijalnim znakovima\n"
            "- duplikatima\n"
            "- kodiranjem naziva\n"
            "- ZIP Slip napadima"
        )

        ctk.CTkLabel(right_frame, text=uputstvo, font=ctk.CTkFont(size=11), text_color="#cccccc", justify="left").pack(padx=14, pady=(0, 14), anchor="w")

        # Podesavanja
        settings_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        settings_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(settings_frame, text="Podesavanja", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 4))

        opt_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        opt_frame.pack(padx=20, pady=(0, 8), fill="x")
        opt_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(opt_frame, text="Nacin otpakivanja:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", pady=8)
        self.nacin_var = ctk.StringVar(value="Poseban folder za svaki ZIP")
        ctk.CTkOptionMenu(opt_frame,
            variable=self.nacin_var,
            values=[
                "Poseban folder za svaki ZIP",
                "Sve u jedan folder"
            ],
            width=240).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=8)

        ctk.CTkLabel(opt_frame,
            text="Poseban folder: svaki ZIP dobija svoj folder\nSve u jedan: svi fajlovi idu zajedno",
            font=ctk.CTkFont(size=11), text_color="gray").grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 8))

        check_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        check_frame.pack(padx=20, pady=(0, 12), fill="x")

        self.preskoci_duplikate = ctk.CTkCheckBox(
            check_frame,
            text="Preskoci ako fajl vec postoji (ne prepisuj)",
            font=ctk.CTkFont(size=12)
        )
        self.preskoci_duplikate.select()
        self.preskoci_duplikate.pack(anchor="w", pady=4)

        self.skrati_putanju = ctk.CTkCheckBox(
            check_frame,
            text="Automatski skrati preduge nazive fajlova (Windows limit 260 znakova)",
            font=ctk.CTkFont(size=12)
        )
        self.skrati_putanju.select()
        self.skrati_putanju.pack(anchor="w", pady=4)

        self.rekurzivno = ctk.CTkCheckBox(
            check_frame,
            text="Rekurzivno otpakuj (otpakuj ZIP unutar ZIP-a automatski)",
            font=ctk.CTkFont(size=12)
        )
        self.rekurzivno.select()
        self.rekurzivno.pack(anchor="w", pady=4)

        # Info
        info_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a3a1a", corner_radius=8)
        info_frame.pack(padx=20, pady=(0, 8), fill="x")
        ctk.CTkLabel(info_frame,
            text="Gdje se cuvaju otpakovani fajlovi?\n"
                 "Fajlovi se cuvaju u folder koji odaberes.\n"
                 "Ako je odabrano 'Poseban folder', kreira se podfolder sa nazivom ZIP fajla.\n"
                 "ZIP unutar ZIP-a se otpakuje u poseban podfolder i original ZIP se brise.",
            font=ctk.CTkFont(size=11), text_color="#aaffaa", justify="left").pack(padx=14, pady=10, anchor="w")

        # Output folder
        output_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        output_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(output_frame, text="Folder za otpakivanje", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 4))
        ctk.CTkLabel(output_frame, text="Odaberi gdje ce se sacuvati otpakovani fajlovi.", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 8))

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

        ctk.CTkButton(self.scroll_frame, text="Otpakuj ZIP", command=self.extract, width=220, height=40, fg_color="#1a7a3c", hover_color="#145e2d", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(4, 18))

        self.output_folder = None

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[
            ("ZIP arhive", "*.zip *.ZIP"),
        ])
        for f in files:
            if f not in self.files:
                self.files.append(f)
                velicina = os.path.getsize(f) / (1024 * 1024)
                self.listbox.insert(tk.END, "  [ZIP]  {} ({:.2f} MB)".format(os.path.basename(f), velicina))

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

    def ocisti_naziv(self, naziv):
        naziv = naziv.replace('/', os.sep).replace('\\', os.sep)
        naziv = re.sub(r'[<>:"|?*]', '_', naziv)
        naziv = re.sub(r'[\x00-\x1f\x7f]', '', naziv)
        dijelovi = naziv.split(os.sep)
        dijelovi = [d.rstrip('. ') for d in dijelovi if d]
        naziv = os.sep.join(dijelovi)
        return naziv

    def skrati_naziv(self, putanja, max_duzina=240):
        if len(putanja) <= max_duzina:
            return putanja
        folder = os.path.dirname(putanja)
        naziv = os.path.basename(putanja)
        ime, ext = os.path.splitext(naziv)
        slobodno = max_duzina - len(folder) - len(ext) - 2
        if slobodno < 8:
            slobodno = 8
        ime = ime[:slobodno]
        return os.path.join(folder, ime + ext)

    def decode_naziv(self, naziv):
        if isinstance(naziv, bytes):
            for enc in ['utf-8', 'cp1250', 'cp437', 'latin-1']:
                try:
                    return naziv.decode(enc)
                except Exception:
                    continue
            return naziv.decode('utf-8', errors='replace')
        return naziv

    def extract(self):
        if not self.files:
            messagebox.showwarning("Upozorenje", "Nisi dodao nijedan ZIP fajl.")
            return
        if not self.output_folder:
            messagebox.showwarning("Upozorenje", "Nisi odabrao folder za otpakivanje.")
            return
        thread = threading.Thread(target=self.run_extract)
        thread.start()

    def run_extract(self):
        nacin = self.nacin_var.get()
        preskoci = self.preskoci_duplikate.get()
        skrati = self.skrati_putanju.get()
        rekurzivno = self.rekurzivno.get()

        ukupno = len(self.files)
        self.ukupno_fajlova = 0
        self.preskoceno = 0
        self.greske = []

        self.progress.set(0)
        self.set_status("Otpakivanje u toku...", "#f0c040")

        for i, filepath in enumerate(self.files):
            naziv_zip = os.path.basename(filepath)
            ime_zip = os.path.splitext(naziv_zip)[0]
            self.set_status("Otpakujem ({}/{}): {}".format(i+1, ukupno, naziv_zip), "#f0c040")

            if nacin == "Poseban folder za svaki ZIP":
                output_dir = os.path.join(self.output_folder, ime_zip)
                os.makedirs(output_dir, exist_ok=True)
            else:
                output_dir = self.output_folder

            self.otpakuj_zip(filepath, output_dir, preskoci, skrati, rekurzivno, dubina=0)

            self.progress.set((i + 1) / ukupno)
            self.update_idletasks()

        poruka_dijelovi = ["Otpakovano {} fajlova.".format(self.ukupno_fajlova)]
        if self.preskoceno > 0:
            poruka_dijelovi.append("Preskoceno {} duplikata.".format(self.preskoceno))

        if not self.greske:
            self.set_status("Uspjesno otpakovano {} fajlova!".format(self.ukupno_fajlova), "#4caf50")
            messagebox.showinfo("Gotovo!", "{}\n\nSacuvano u:\n{}".format(
                "\n".join(poruka_dijelovi), self.output_folder))
        else:
            self.set_status("Gotovo sa napomenama – otpakovano {} fajlova.".format(self.ukupno_fajlova), "#f0c040")
            log_path = os.path.join(self.output_folder, "GRESKE_LOG.txt")
            try:
                with open(log_path, "w", encoding="utf-8") as log:
                    log.write("\n---\n".join(self.greske))
            except Exception:
                pass
            messagebox.showwarning("Gotovo sa napomenama",
                "{}\n\nNapomene: {}\n\nDetalji zapisani u GRESKE_LOG.txt".format(
                    "\n".join(poruka_dijelovi), len(self.greske)))

    def otpakuj_zip(self, filepath, output_dir, preskoci, skrati, rekurzivno, dubina=0):
        MAX_DUBINA = 10
        if dubina > MAX_DUBINA:
            self.greske.append("{}: Preskoceno - previse nivoa ZIP unutar ZIP-a (max {}).".format(
                os.path.basename(filepath), MAX_DUBINA))
            return

        naziv_zip = os.path.basename(filepath)

        try:
            if not zipfile.is_zipfile(filepath):
                self.greske.append("{}: Nije validan ZIP fajl.".format(naziv_zip))
                return

            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                lose = zip_ref.testzip()
                if lose:
                    self.greske.append("{}: Ostecen fajl unutar arhive: {}".format(naziv_zip, lose))

                for member in zip_ref.infolist():
                    try:
                        if member.flag_bits & 0x800:
                            clan_naziv = member.filename
                        else:
                            clan_naziv = self.decode_naziv(member.filename.encode('cp437'))

                        clan_naziv = self.ocisti_naziv(clan_naziv)
                        if not clan_naziv:
                            continue

                        puna_putanja = os.path.join(output_dir, clan_naziv)

                        # ZIP Slip zastita
                        abs_output = os.path.abspath(output_dir)
                        abs_putanja = os.path.abspath(puna_putanja)
                        if not abs_putanja.startswith(abs_output):
                            self.greske.append("{}: Preskocen zbog sigurnosti: {}".format(naziv_zip, clan_naziv))
                            continue

                        if skrati:
                            puna_putanja = self.skrati_naziv(puna_putanja)

                        if member.is_dir():
                            os.makedirs(puna_putanja, exist_ok=True)
                            continue

                        os.makedirs(os.path.dirname(puna_putanja), exist_ok=True)

                        if preskoci and os.path.exists(puna_putanja):
                            self.preskoceno += 1
                            continue

                        if not preskoci and os.path.exists(puna_putanja):
                            base, ext = os.path.splitext(puna_putanja)
                            counter = 1
                            while os.path.exists(puna_putanja):
                                puna_putanja = "{}_{}{}".format(base, counter, ext)
                                counter += 1

                        with zip_ref.open(member) as source:
                            with open(puna_putanja, 'wb') as target:
                                target.write(source.read())

                        self.ukupno_fajlova += 1

                        # Rekurzivno otpakivanje ZIP unutar ZIP-a
                        if rekurzivno and puna_putanja.lower().endswith('.zip'):
                            self.set_status("Otpakujem ZIP unutar ZIP-a (nivo {}): {}".format(
                                dubina+1, os.path.basename(puna_putanja)), "#f0c040")
                            sub_output = os.path.splitext(puna_putanja)[0]
                            os.makedirs(sub_output, exist_ok=True)
                            self.otpakuj_zip(puna_putanja, sub_output, preskoci, skrati, rekurzivno, dubina+1)
                            try:
                                os.remove(puna_putanja)
                            except Exception:
                                pass

                    except Exception as e:
                        self.greske.append("{} - {}: {}".format(naziv_zip, member.filename, str(e)))

        except zipfile.BadZipFile:
            self.greske.append("{}: Ostecena ili nevalidna ZIP arhiva.".format(naziv_zip))
        except PermissionError:
            self.greske.append("{}: Nema dozvole za pisanje u odabrani folder.".format(naziv_zip))
        except Exception as e:
            self.greske.append("{}: {}".format(naziv_zip, str(e)))