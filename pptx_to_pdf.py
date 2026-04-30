import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading

class PptxToPdfPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.place(relwidth=1, relheight=1)

        self.files = []

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.scroll_frame, text="PowerPoint u PDF", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(18, 4))
        ctk.CTkLabel(self.scroll_frame, text="Konvertuj PowerPoint prezentacije u PDF fajlove", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 10))

        content_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        content_frame.pack(padx=20, pady=(0, 8), fill="x")
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)

        # LIJEVA STRANA - lista
        left_frame = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", corner_radius=8)
        left_frame.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(left_frame, text="PowerPoint fajlovi", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 2))
        ctk.CTkLabel(left_frame,
            text="Dodaj .pptx fajlove koje zelis konvertovati u PDF.\nProgram ce konvertovati svaki fajl posebno.",
            font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 6))

        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 6))
        ctk.CTkButton(btn_frame, text="+ Dodaj PPTX fajlove", command=self.add_files, width=160).grid(row=0, column=0, padx=4)
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
            "1) Dodaj .pptx fajlove\n\n"
            "2) Odaberi broj slajdova\n"
            "   po stranici\n\n"
            "3) Odaberi folder\n\n"
            "4) Klikni 'Konvertuj'\n\n"
            "Raspored slajdova:\n\n"
            "1 po strani – jedan\n"
            "slajd po A4 stranici\n\n"
            "2 po strani – dva\n"
            "slajda jedan ispod\n"
            "drugog\n\n"
            "4 po strani – cetiri\n"
            "slajda u mrezi 2x2\n\n"
            "NAPOMENA:\n"
            "Potreban je instaliran\n"
            "Microsoft PowerPoint."
        )

        ctk.CTkLabel(right_frame, text=uputstvo, font=ctk.CTkFont(size=11), text_color="#cccccc", justify="left").pack(padx=14, pady=(0, 14), anchor="w")

        # Podesavanja
        settings_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        settings_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(settings_frame, text="Raspored slajdova", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 4))
        ctk.CTkLabel(settings_frame, text="Odaberi koliko slajdova ce biti prikazano na jednoj A4 stranici.", font=ctk.CTkFont(size=11), text_color="gray").pack(pady=(0, 8))

        self.slajdovi_var = ctk.StringVar(value="1")
        slajd_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        slajd_frame.pack(padx=20, pady=(0, 12))

        opcije = [
            ("1 po stranici  –  maksimalna citljivost", "1"),
            ("2 po stranici  –  kompaktniji prikaz", "2"),
            ("4 po stranici  –  pregled / handout", "4"),
        ]
        for tekst, vrijednost in opcije:
            ctk.CTkRadioButton(
                slajd_frame,
                text=tekst,
                variable=self.slajdovi_var,
                value=vrijednost,
                font=ctk.CTkFont(size=12)
            ).pack(anchor="w", pady=5)

        # Info
        info_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a3a1a", corner_radius=8)
        info_frame.pack(padx=20, pady=(0, 8), fill="x")
        ctk.CTkLabel(info_frame,
            text="Gdje se cuvaju konvertovani fajlovi?\n"
                 "PDF fajlovi se cuvaju u folder koji odaberes.\n"
                 "Naziv fajla ostaje isti kao original (.pdf ekstenzija).",
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

        ctk.CTkButton(self.scroll_frame, text="Konvertuj u PDF", command=self.convert, width=220, height=40, fg_color="#1a7a3c", hover_color="#145e2d", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(4, 18))

        self.output_folder = None

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PowerPoint fajlovi", "*.pptx")])
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.listbox.insert(tk.END, "  [PPTX]  {}".format(os.path.basename(f)))

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
            messagebox.showwarning("Upozorenje", "Nisi dodao nijedan PowerPoint fajl.")
            return
        if not self.output_folder:
            messagebox.showwarning("Upozorenje", "Nisi odabrao folder za cuvanje.")
            return
        thread = threading.Thread(target=self.run_convert)
        thread.start()

    def run_convert(self):
        import comtypes.client
        import shutil
        import tempfile

        slajdovi_po_strani = int(self.slajdovi_var.get())
        dpi = 150
        a4_w = int(8.27 * dpi)
        a4_h = int(11.69 * dpi)

        ukupno = len(self.files)
        uspjesno = 0
        greske = []

        self.progress.set(0)
        self.set_status("Konverzija u toku...", "#f0c040")

        temp_dir = "C:\\Temp"
        os.makedirs(temp_dir, exist_ok=True)

        powerpoint = None

        try:
            powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
            powerpoint.Visible = 1

            for i, filepath in enumerate(self.files):
                naziv = os.path.basename(filepath)
                self.set_status("Konvertujem ({}/{}): {}".format(i+1, ukupno, naziv), "#f0c040")

                safe_path = None
                tmp_pdf_path = None

                try:
                    import pathlib
                    safe_naziv = "pptx_{}.pptx".format(i)
                    safe_path = os.path.join(temp_dir, safe_naziv)
                    shutil.copy2(filepath, safe_path)

                    tmp_pdf_path = os.path.join(temp_dir, "output_{}.pdf".format(i))

                    abs_path = str(pathlib.Path(safe_path).resolve())
                    abs_output = str(pathlib.Path(tmp_pdf_path).resolve())

                    prezentacija = powerpoint.Presentations.Open(
                        abs_path,
                        ReadOnly=1,
                        Untitled=0,
                        WithWindow=1
                    )
                    prezentacija.SaveAs(abs_output, 32)
                    prezentacija.Close()

                    ime_bez_ext = os.path.splitext(naziv)[0]
                    output_path = os.path.join(self.output_folder, ime_bez_ext + ".pdf")

                    counter = 1
                    while os.path.exists(output_path):
                        output_path = os.path.join(self.output_folder, "{}_{}.pdf".format(ime_bez_ext, counter))
                        counter += 1

                    if slajdovi_po_strani == 1:
                        shutil.copy2(tmp_pdf_path, output_path)
                    else:
                        self.set_status("Rasporedjujem slajdove ({}/{}): {}".format(i+1, ukupno, naziv), "#f0c040")
                        self.arrange_slides(tmp_pdf_path, output_path, slajdovi_po_strani, dpi, a4_w, a4_h)

                    uspjesno += 1

                except Exception as e:
                    greske.append("{}: {}".format(naziv, str(e)))

                finally:
                    for tmp in [safe_path, tmp_pdf_path]:
                        if tmp and os.path.exists(tmp):
                            try:
                                os.remove(tmp)
                            except:
                                pass

                self.progress.set((i + 1) / ukupno)
                self.update_idletasks()

        finally:
            if powerpoint:
                try:
                    powerpoint.Quit()
                except:
                    pass

        if not greske:
            self.set_status("Uspjesno konvertovano {} fajlova!".format(uspjesno), "#4caf50")
            messagebox.showinfo("Gotovo!", "Uspjesno konvertovano {} fajlova!\n\nSacuvano u:\n{}".format(
                uspjesno, self.output_folder))
        else:
            self.set_status("Gotovo sa greskama ({} od {} uspjesno)".format(uspjesno, ukupno), "#f0c040")
            messagebox.showwarning("Djelimicno gotovo", "Uspjesno: {} od {}\n\nGreske:\n{}".format(
                uspjesno, ukupno, "\n".join(greske)))

    def arrange_slides(self, input_pdf, output_pdf, slajdovi_po_strani, dpi, a4_w, a4_h):
        import fitz
        from PIL import Image
        import io

        if slajdovi_po_strani == 2:
            cols, rows = 1, 2
        else:
            cols, rows = 2, 2

        margin = int(0.25 * dpi)
        slot_w = (a4_w - (cols + 1) * margin) // cols
        slot_h = (a4_h - (rows + 1) * margin) // rows

        src = fitz.open(input_pdf)
        ukupno_slajdova = len(src)
        novi_pdf = fitz.open()

        for page_start in range(0, ukupno_slajdova, slajdovi_po_strani):
            grupa = list(range(page_start, min(page_start + slajdovi_po_strani, ukupno_slajdova)))
            nova_str = novi_pdf.new_page(width=a4_w, height=a4_h)

            for idx, slajd_idx in enumerate(grupa):
                col = idx % cols
                row = idx // cols

                x = margin + col * (slot_w + margin)
                y = margin + row * (slot_h + margin)

                slajd = src[slajd_idx]
                mat = fitz.Matrix(dpi/72, dpi/72)
                pix = slajd.get_pixmap(matrix=mat)

                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                ratio = min(slot_w / img.width, slot_h / img.height)
                new_w = int(img.width * ratio)
                new_h = int(img.height * ratio)
                img = img.resize((new_w, new_h), Image.LANCZOS)

                x_center = x + (slot_w - new_w) // 2
                y_center = y + (slot_h - new_h) // 2

                img_buffer = io.BytesIO()
                img.save(img_buffer, format="JPEG", quality=92)
                img_bytes = img_buffer.getvalue()

                rect = fitz.Rect(x_center, y_center, x_center + new_w, y_center + new_h)
                nova_str.insert_image(rect, stream=img_bytes)
                nova_str.draw_rect(rect, color=(0.8, 0.8, 0.8), width=0.5)

        src.close()
        novi_pdf.save(output_pdf)
        novi_pdf.close()