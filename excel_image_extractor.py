import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import zipfile
import shutil
import re

class ExcelImageExtractorPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.place(relwidth=1, relheight=1)

        self.files = []

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.scroll_frame, text="Ekstrakcija slika iz Excela", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(18, 4))
        ctk.CTkLabel(self.scroll_frame, text="Izvlaci slike zalijepljene u Excel fajlove i cuva ih kao JPG", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 10))

        content_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        content_frame.pack(padx=20, pady=(0, 8), fill="x")
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)

        # LIJEVA STRANA - lista
        left_frame = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", corner_radius=8)
        left_frame.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(left_frame, text="Excel fajlovi", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 2))
        ctk.CTkLabel(left_frame,
            text="Dodaj Excel fajlove iz kojih zelis izvuci slike.\nProgram ce pronaci sve slike u svakom fajlu.",
            font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 6))

        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 6))
        ctk.CTkButton(btn_frame, text="+ Dodaj Excel fajlove", command=self.add_files, width=160).grid(row=0, column=0, padx=4)
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
            "1) Dodaj Excel fajlove\n"
            "   (.xlsx format)\n\n"
            "2) Odaberi folder gdje\n"
            "   ce se sacuvati slike\n\n"
            "3) Klikni dugme za\n"
            "   ekstrakciju\n\n"
            "Imenovanje slika:\n\n"
            "NazivFajla_NazivSheeta\n"
            "_redniBroj.jpg\n\n"
            "Primjer:\n"
            "Izvjestaj_Sheet1_1.jpg\n"
            "Izvjestaj_Sheet1_2.jpg\n"
            "Izvjestaj_Sheet2_1.jpg\n\n"
            "NAPOMENA:\n"
            "Radi samo sa .xlsx\n"
            "formatom fajlova."
        )

        ctk.CTkLabel(right_frame, text=uputstvo, font=ctk.CTkFont(size=11), text_color="#cccccc", justify="left").pack(padx=14, pady=(0, 14), anchor="w")

        # Info
        info_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a3a1a", corner_radius=8)
        info_frame.pack(padx=20, pady=(0, 8), fill="x")
        ctk.CTkLabel(info_frame,
            text="Kako se cuvaju slike?\n"
                 "Naziv slike = NazivExcelFajla_NazivSheeta_RedniBroj.jpg\n"
                 "Sve slike se cuvaju u odabrani folder.",
            font=ctk.CTkFont(size=11), text_color="#aaffaa", justify="left").pack(padx=14, pady=10, anchor="w")

        # Output folder
        output_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        output_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(output_frame, text="Folder za cuvanje slika", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 4))
        ctk.CTkLabel(output_frame, text="Odaberi folder u koji ce se sacuvati sve izvucene slike.", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 8))

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

        ctk.CTkButton(self.scroll_frame, text="Izvuci slike", command=self.extract, width=220, height=40, fg_color="#1a7a3c", hover_color="#145e2d", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(4, 18))

        self.output_folder = None

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Excel fajlovi", "*.xlsx")])
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.listbox.insert(tk.END, "  [XLSX]  {}".format(os.path.basename(f)))

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

    def extract(self):
        if not self.files:
            messagebox.showwarning("Upozorenje", "Nisi dodao nijedan Excel fajl.")
            return
        if not self.output_folder:
            messagebox.showwarning("Upozorenje", "Nisi odabrao folder za cuvanje.")
            return
        thread = threading.Thread(target=self.run_extract)
        thread.start()

    def run_extract(self):
        from PIL import Image
        import io
        import xml.etree.ElementTree as ET

        ukupno = len(self.files)
        ukupno_slika = 0
        greske = []

        self.progress.set(0)
        self.set_status("Ekstrakcija u toku...", "#f0c040")

        for i, filepath in enumerate(self.files):
            naziv_fajla = os.path.splitext(os.path.basename(filepath))[0]
            self.set_status("Obrada ({}/{}): {}".format(i+1, ukupno, os.path.basename(filepath)), "#f0c040")

            try:
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    svi_fajlovi = zip_ref.namelist()

                    # Citamo nazive sheetova
                    sheet_names = {}
                    try:
                        with zip_ref.open("xl/workbook.xml") as wb_file:
                            tree = ET.parse(wb_file)
                            root = tree.getroot()
                            ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                            for j, sheet in enumerate(root.findall('.//ns:sheet', ns), start=1):
                                sheet_names[j] = sheet.get('name', 'Sheet{}'.format(j))
                    except Exception:
                        sheet_names = {}

                    # Mapiramo slike na sheetove kroz drawings
                    media_to_sheet = {}
                    for sheet_idx, sheet_name in sheet_names.items():
                        sheet_rels = "xl/worksheets/_rels/sheet{}.xml.rels".format(sheet_idx)
                        if sheet_rels not in svi_fajlovi:
                            continue
                        try:
                            with zip_ref.open(sheet_rels) as rels_file:
                                rels_tree = ET.parse(rels_file)
                                rels_root = rels_tree.getroot()
                                drawing_rels = []
                                for rel in rels_root:
                                    target = rel.get('Target', '')
                                    rel_type = rel.get('Type', '')
                                    if 'drawing' in rel_type.lower() or 'drawing' in target.lower():
                                        drawing_name = target.split('/')[-1]
                                        drawing_rels.append(drawing_name)

                            for drawing_name in drawing_rels:
                                drawing_rels_path = "xl/drawings/_rels/{}.rels".format(drawing_name)
                                if drawing_rels_path not in svi_fajlovi:
                                    continue
                                with zip_ref.open(drawing_rels_path) as drels_file:
                                    drels_tree = ET.parse(drels_file)
                                    drels_root = drels_tree.getroot()
                                    for rel in drels_root:
                                        target = rel.get('Target', '')
                                        rel_type = rel.get('Type', '')
                                        if 'image' in rel_type.lower() or '../media/' in target:
                                            media_path = "xl/media/" + target.split('/')[-1]
                                            if media_path in svi_fajlovi:
                                                media_to_sheet[media_path] = sheet_name
                        except Exception:
                            continue

                    # Uzimamo SVE slike iz xl/media/ - pouzdana metoda
                    media_fajlovi = [
                        f for f in svi_fajlovi
                        if f.startswith("xl/media/") and not f.endswith("/")
                    ]

                    if not media_fajlovi:
                        greske.append("{}: Nisu pronadjene slike u ovom fajlu.".format(naziv_fajla))
                        self.progress.set((i + 1) / ukupno)
                        self.update_idletasks()
                        continue

                    # Brojaci po sheetu
                    sheet_counter = {}

                    for media_fajl in media_fajlovi:
                        try:
                            with zip_ref.open(media_fajl) as img_file:
                                img_data = img_file.read()

                            img = Image.open(io.BytesIO(img_data))

                            if img.mode not in ("RGB", "L"):
                                img = img.convert("RGB")

                            # Naziv sheeta
                            if media_fajl in media_to_sheet:
                                sheet_name = media_to_sheet[media_fajl]
                            else:
                                sheet_name = "Sheet1"

                            sheet_clean = re.sub(r'[\\/*?:"<>|]', "_", sheet_name).strip()

                            # Redni broj za ovaj sheet
                            if sheet_clean not in sheet_counter:
                                sheet_counter[sheet_clean] = 1
                            else:
                                sheet_counter[sheet_clean] += 1

                            br = sheet_counter[sheet_clean]

                            # NazivFajla_NazivSheeta_1.jpg
                            output_naziv = "{}_{}_{}.jpg".format(naziv_fajla, sheet_clean, br)
                            output_path = os.path.join(self.output_folder, output_naziv)

                            counter = 1
                            while os.path.exists(output_path):
                                output_naziv = "{}_{}_{}_{}.jpg".format(naziv_fajla, sheet_clean, br, counter)
                                output_path = os.path.join(self.output_folder, output_naziv)
                                counter += 1

                            img.save(output_path, "JPEG", quality=95)
                            img.close()
                            ukupno_slika += 1

                        except Exception as e:
                            greske.append("{} - {}: {}".format(naziv_fajla, os.path.basename(media_fajl), str(e)))

            except Exception as e:
                greske.append("{}: {}".format(os.path.basename(filepath), str(e)))

            self.progress.set((i + 1) / ukupno)
            self.update_idletasks()

        if ukupno_slika > 0 and not greske:
            self.set_status("Uspjesno izvuceno {} slika!".format(ukupno_slika), "#4caf50")
            messagebox.showinfo("Gotovo!", "Uspjesno izvuceno {} slika!\n\nSacuvano u:\n{}".format(ukupno_slika, self.output_folder))
        elif ukupno_slika > 0 and greske:
            self.set_status("Gotovo sa napomenama – izvuceno {} slika.".format(ukupno_slika), "#f0c040")
            messagebox.showwarning("Gotovo sa napomenama",
                "Izvuceno {} slika.\n\nNapomene:\n{}".format(ukupno_slika, "\n".join(greske)))
        else:
            self.set_status("Nisu pronadjene slike.", "#e05555")
            messagebox.showwarning("Nema slika", "Nisu pronadjene slike ni u jednom Excel fajlu.\n\nNapomene:\n{}".format("\n".join(greske)))