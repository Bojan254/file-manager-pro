import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import tempfile
import shutil

class PdfMergerPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.place(relwidth=1, relheight=1)

        self.files = []

        ctk.CTkLabel(self, text="Spajanje fajlova u PDF", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(18, 4))
        ctk.CTkLabel(self, text="Dodaj PDF, Word ili slike - program ce ih spojiti u jedan PDF", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 12))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 8))

        ctk.CTkButton(btn_frame, text="+ Dodaj fajlove", command=self.add_files, width=150).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Gore", command=self.move_up, width=80, fg_color="#555", hover_color="#444").grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_frame, text="Dolje", command=self.move_down, width=80, fg_color="#555", hover_color="#444").grid(row=0, column=2, padx=5)
        ctk.CTkButton(btn_frame, text="Ukloni", command=self.remove_selected, width=80, fg_color="#7a1a1a", hover_color="#5e1414").grid(row=0, column=3, padx=5)
        ctk.CTkButton(btn_frame, text="Ocisti sve", command=self.clear_list, width=90, fg_color="#555", hover_color="#444").grid(row=0, column=4, padx=5)

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

        ctk.CTkButton(bottom_frame, text="Odaberi lokaciju cuvanja", command=self.select_output, width=210, fg_color="#2a6496", hover_color="#1f4f78").pack(side="left", padx=(0, 10))
        self.output_label = ctk.CTkLabel(bottom_frame, text="Nije odabrana lokacija", text_color="gray", font=ctk.CTkFont(size=11))
        self.output_label.pack(side="left")

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), text_color="#aaaaaa")
        self.status_label.pack(pady=(0, 6))

        ctk.CTkButton(self, text="Spoji u PDF", command=self.merge, width=220, height=40, fg_color="#1a7a3c", hover_color="#145e2d", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 18))

        self.output_path = None

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[
            ("Podrzani fajlovi", "*.pdf *.doc *.docx *.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp *.gif"),
            ("PDF fajlovi", "*.pdf"),
            ("Word fajlovi", "*.doc *.docx"),
            ("Slike", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp *.gif"),
        ])
        for f in files:
            if f not in self.files:
                self.files.append(f)
                ext = os.path.splitext(f)[1].upper()
                self.listbox.insert(tk.END, "  [{}]  {}".format(ext.replace(".", ""), os.path.basename(f)))

    def move_up(self):
        idx = self.listbox.curselection()
        if not idx or idx[0] == 0:
            return
        i = idx[0]
        self.files[i], self.files[i-1] = self.files[i-1], self.files[i]
        text = self.listbox.get(i)
        self.listbox.delete(i)
        self.listbox.insert(i-1, text)
        self.listbox.select_set(i-1)

    def move_down(self):
        idx = self.listbox.curselection()
        if not idx or idx[0] == len(self.files) - 1:
            return
        i = idx[0]
        self.files[i], self.files[i+1] = self.files[i+1], self.files[i]
        text = self.listbox.get(i)
        self.listbox.delete(i)
        self.listbox.insert(i+1, text)
        self.listbox.select_set(i+1)

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
        self.status_label.configure(text="")

    def select_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF fajl", "*.pdf")],
            title="Sacuvaj spojeni PDF kao..."
        )
        if path:
            self.output_path = path
            self.output_label.configure(text=os.path.basename(path), text_color="white")

    def set_status(self, text, color="#aaaaaa"):
        self.status_label.configure(text=text, text_color=color)
        self.update_idletasks()

    def word_to_pdf_com(self, filepath, output_path, idx):
        import comtypes.client
        import pathlib

        temp_dir = "C:\\Temp"
        os.makedirs(temp_dir, exist_ok=True)

        safe_naziv = "merger_word_{}.docx".format(idx)
        safe_path = os.path.join(temp_dir, safe_naziv)
        tmp_pdf_path = os.path.join(temp_dir, "merger_out_{}.pdf".format(idx))

        word = None
        try:
            shutil.copy2(filepath, safe_path)
            abs_path = str(pathlib.Path(safe_path).resolve())
            abs_output = str(pathlib.Path(tmp_pdf_path).resolve())

            word = comtypes.client.CreateObject("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(abs_path)
            doc.SaveAs(abs_output, FileFormat=17)
            doc.Close()
            word.Quit()
            word = None

            shutil.move(tmp_pdf_path, output_path)
            return True, None

        except Exception as e:
            return False, str(e)

        finally:
            if word:
                try:
                    word.Quit()
                except:
                    pass
            for tmp in [safe_path, tmp_pdf_path]:
                if os.path.exists(tmp):
                    try:
                        os.remove(tmp)
                    except:
                        pass

    def merge(self):
        if not self.files:
            messagebox.showwarning("Upozorenje", "Nisi dodao nijedan fajl.")
            return
        if not self.output_path:
            messagebox.showwarning("Upozorenje", "Nisi odabrao lokaciju za cuvanje.")
            return
        thread = threading.Thread(target=self.run_merge)
        thread.start()

    def run_merge(self):
        import fitz

        self.set_status("Obrada u toku...", "#f0c040")

        temp_files = []
        pdf_paths = []
        greske = []

        try:
            for idx, filepath in enumerate(self.files):
                ext = os.path.splitext(filepath)[1].lower()

                if ext == ".pdf":
                    pdf_paths.append(filepath)

                elif ext in (".doc", ".docx"):
                    self.set_status("Konvertujem Word: {}".format(os.path.basename(filepath)), "#f0c040")
                    try:
                        # Koristimo COM metodu
                        tmp_path = os.path.join("C:\\Temp", "merger_pdf_{}.pdf".format(idx))
                        os.makedirs("C:\\Temp", exist_ok=True)
                        ok, greska = self.word_to_pdf_com(filepath, tmp_path, idx)
                        if ok:
                            pdf_paths.append(tmp_path)
                            temp_files.append(tmp_path)
                        else:
                            greske.append("{}: {}".format(os.path.basename(filepath), greska))
                    except Exception as e:
                        greske.append("{}: {}".format(os.path.basename(filepath), str(e)))

                elif ext in (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".gif"):
                    self.set_status("Konvertujem sliku: {}".format(os.path.basename(filepath)), "#f0c040")
                    try:
                        from PIL import Image
                        temp_dir = tempfile.gettempdir()
                        tmp_path = os.path.join(temp_dir, "merger_img_{}.pdf".format(idx))
                        img = Image.open(filepath)
                        if img.mode not in ("RGB", "L"):
                            img = img.convert("RGB")
                        img.save(tmp_path, "PDF", resolution=150)
                        img.close()
                        pdf_paths.append(tmp_path)
                        temp_files.append(tmp_path)
                    except Exception as e:
                        greske.append("{}: {}".format(os.path.basename(filepath), str(e)))

            if not pdf_paths:
                self.set_status("Nema fajlova za spajanje.", "#e05555")
                return

            self.set_status("Spajam {} fajlova...".format(len(pdf_paths)), "#f0c040")
            merged = fitz.open()
            for path in pdf_paths:
                doc = fitz.open(path)
                merged.insert_pdf(doc)
                doc.close()

            merged.save(self.output_path)
            merged.close()

            for tmp in temp_files:
                try:
                    os.remove(tmp)
                except:
                    pass

            if greske:
                self.set_status("Gotovo sa greskama ({} fajlova preskoceno)".format(len(greske)), "#f0c040")
                messagebox.showwarning("Djelimicno gotovo", "Spojeno, ali {} fajlova nije moglo biti konvertovano:\n\n{}".format(len(greske), "\n".join(greske)))
            else:
                self.set_status("Uspjesno spojeno!", "#4caf50")
                messagebox.showinfo("Gotovo!", "Fajlovi su uspjesno spojeni i sacuvani kao:\n{}".format(self.output_path))

        except Exception as e:
            self.set_status("Greska!", "#e05555")
            messagebox.showerror("Greska", "Doslo je do greske:\n{}".format(str(e)))