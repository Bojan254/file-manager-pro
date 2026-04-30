import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import tempfile
import shutil

class WordToPdfPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.place(relwidth=1, relheight=1)

        self.files = []

        ctk.CTkLabel(self, text="Word u PDF", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(18, 4))
        ctk.CTkLabel(self, text="Dodaj Word fajlove i odaberi folder – program ce ih sve konvertovati u PDF", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 12))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 8))

        ctk.CTkButton(btn_frame, text="+ Dodaj Word fajlove", command=self.add_files, width=180).grid(row=0, column=0, padx=6)
        ctk.CTkButton(btn_frame, text="Ukloni", command=self.remove_selected, width=90, fg_color="#7a1a1a", hover_color="#5e1414").grid(row=0, column=1, padx=6)
        ctk.CTkButton(btn_frame, text="Ocisti sve", command=self.clear_list, width=100, fg_color="#555", hover_color="#444").grid(row=0, column=2, padx=6)

        self.listbox_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=8)
        self.listbox_frame.pack(padx=20, pady=(0, 10), fill="both", expand=True)

        self.listbox = tk.Listbox(
            self.listbox_frame,
            bg="#1e1e1e", fg="white",
            selectbackground="#1f6aa5",
            borderwidth=0, highlightthickness=0,
            font=("Segoe UI", 11),
            activestyle="none"
        )
        self.listbox.pack(padx=8, pady=8, fill="both", expand=True)

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(pady=(0, 10), padx=20, fill="x")

        ctk.CTkButton(bottom_frame, text="Odaberi folder za cuvanje", command=self.select_output, width=220, fg_color="#2a6496", hover_color="#1f4f78").pack(side="left", padx=(0, 10))
        self.output_label = ctk.CTkLabel(bottom_frame, text="Nije odabran folder", text_color="gray", font=ctk.CTkFont(size=11))
        self.output_label.pack(side="left")

        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.set(0)
        self.progress.pack(pady=(0, 4))

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), text_color="#aaaaaa")
        self.status_label.pack(pady=(0, 6))

        ctk.CTkButton(self, text="Konvertuj u PDF", command=self.convert, width=220, height=40, fg_color="#1a7a3c", hover_color="#145e2d", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(0, 18))

        self.output_folder = None

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Word fajlovi", "*.doc *.docx")])
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
            messagebox.showwarning("Upozorenje", "Nisi dodao nijedan Word fajl.")
            return
        if not self.output_folder:
            messagebox.showwarning("Upozorenje", "Nisi odabrao folder za cuvanje.")
            return
        thread = threading.Thread(target=self.run_convert)
        thread.start()

    def run_convert(self):
        import comtypes.client
        import pathlib

        ukupno = len(self.files)
        uspjesno = 0
        greske = []

        self.progress.set(0)
        self.set_status("Konverzija u toku...", "#f0c040")

        # Kreiramo C:\Temp folder
        temp_dir = "C:\\Temp"
        os.makedirs(temp_dir, exist_ok=True)

        word = None

        try:
            word = comtypes.client.CreateObject("Word.Application")
            word.Visible = False

            for i, filepath in enumerate(self.files):
                naziv = os.path.basename(filepath)
                self.set_status("Konvertujem ({}/{}): {}".format(i+1, ukupno, naziv), "#f0c040")

                safe_path = None
                tmp_pdf_path = None

                try:
                    # Kopiramo u C:\Temp da izbjegnemo probleme sa putanjom
                    safe_naziv = "word_tmp_{}.docx".format(i)
                    safe_path = os.path.join(temp_dir, safe_naziv)
                    shutil.copy2(filepath, safe_path)

                    tmp_pdf_path = os.path.join(temp_dir, "word_out_{}.pdf".format(i))

                    abs_path = str(pathlib.Path(safe_path).resolve())
                    abs_output = str(pathlib.Path(tmp_pdf_path).resolve())

                    # Otvaramo Word dokument
                    doc = word.Documents.Open(abs_path)
                    # 17 = wdFormatPDF
                    doc.SaveAs(abs_output, FileFormat=17)
                    doc.Close()

                    # Premjestamo na pravu lokaciju
                    ime_bez_ext = os.path.splitext(naziv)[0]
                    output_path = os.path.join(self.output_folder, ime_bez_ext + ".pdf")

                    counter = 1
                    base_path = os.path.join(self.output_folder, ime_bez_ext)
                    while os.path.exists(output_path):
                        output_path = "{}_{}{}".format(base_path, counter, ".pdf")
                        counter += 1

                    shutil.move(tmp_pdf_path, output_path)
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
            if word:
                try:
                    word.Quit()
                except:
                    pass

        if not greske:
            self.set_status("Uspjesno konvertovano {} fajlova!".format(uspjesno), "#4caf50")
            messagebox.showinfo("Gotovo!", "Svi fajlovi su uspjesno konvertovani!\n\nSacuvano u:\n{}".format(self.output_folder))
        else:
            self.set_status("Gotovo sa greskama ({} od {} uspjesno)".format(uspjesno, ukupno), "#f0c040")
            messagebox.showwarning("Djelimicno gotovo",
                "Uspjesno: {} od {}\n\nGreske:\n{}".format(uspjesno, ukupno, "\n".join(greske)))