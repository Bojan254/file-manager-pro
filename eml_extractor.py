import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from email.header import decode_header
import email
import os
import re

class EmlExtractorPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.place(relwidth=1, relheight=1)

        self.eml_files = []

        ctk.CTkLabel(self, text="Ekstrakcija EML attachmenata", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(18, 4))
        ctk.CTkLabel(self, text="Dodaj .eml fajlove i odaberi folder za cuvanje attachmenata", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 12))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 8))

        ctk.CTkButton(btn_frame, text="+ Dodaj EML fajlove", command=self.add_files, width=180).grid(row=0, column=0, padx=6)
        ctk.CTkButton(btn_frame, text="Ocisti listu", command=self.clear_list, width=130, fg_color="#555", hover_color="#444").grid(row=0, column=1, padx=6)

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
        bottom_frame.pack(pady=(0, 14), padx=20, fill="x")

        ctk.CTkButton(bottom_frame, text="Odaberi folder za cuvanje", command=self.select_output, width=220, fg_color="#2a6496", hover_color="#1f4f78").pack(side="left", padx=(0, 10))

        self.output_label = ctk.CTkLabel(bottom_frame, text="Nije odabran folder", text_color="gray", font=ctk.CTkFont(size=11))
        self.output_label.pack(side="left")

        ctk.CTkButton(self, text="Izvuci attachmente", command=self.extract, width=220, fg_color="#1a7a3c", hover_color="#145e2d", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(0, 14))

        self.output_folder = None

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("EML fajlovi", "*.eml")])
        for f in files:
            if f not in self.eml_files:
                self.eml_files.append(f)
                self.listbox.insert(tk.END, "  {}".format(os.path.basename(f)))

    def clear_list(self):
        self.eml_files.clear()
        self.listbox.delete(0, tk.END)

    def select_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.output_label.configure(text=folder, text_color="white")

    def clean_text(self, text):
        if not text:
            return "nepoznato"
        decoded_parts = decode_header(text)
        result = ""
        for decoded_bytes, charset in decoded_parts:
            if isinstance(decoded_bytes, bytes):
                result += decoded_bytes.decode(charset or "utf-8", errors="replace")
            else:
                result += decoded_bytes
        result = result.replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("\t", " ")
        result = re.sub(r' +', " ", result)
        result = re.sub(r'[\\/*?:"<>|]', "_", result).strip()
        result = result[:80]
        return result or "nepoznato"

    def get_sender_name(self, msg):
        from_raw = msg.get("From", "nepoznat_posiljalac")
        match = re.match(r'^(.*?)\s*<.*?>$', from_raw)
        if match:
            name = match.group(1).strip().strip('"')
        else:
            name = from_raw.split("@")[0]
        return self.clean_text(name)

    def extract(self):
        if not self.eml_files:
            messagebox.showwarning("Upozorenje", "Nisi dodao nijedan EML fajl.")
            return
        if not self.output_folder:
            messagebox.showwarning("Upozorenje", "Nisi odabrao folder za cuvanje.")
            return

        ukupno = 0
        greske = 0
        greske_detalji = []

        for eml_path in self.eml_files:
            try:
                with open(eml_path, "rb") as f:
                    msg = email.message_from_bytes(f.read())

                eml_naziv = os.path.splitext(os.path.basename(eml_path))[0]
                eml_naziv = self.clean_text(eml_naziv)
                posiljalac = self.get_sender_name(msg)
                naziv_foldera = "{} - {}".format(eml_naziv, posiljalac)
                subfolder = os.path.join(self.output_folder, naziv_foldera)
                os.makedirs(subfolder, exist_ok=True)

                for part in msg.walk():
                    content_type = part.get_content_type()
                    filename = part.get_filename()
                    disposition = str(part.get_content_disposition() or "")

                    # Preskacamo inline slike (logoi, potpisi)
                    if content_type.startswith("image/") and disposition != "attachment":
                        continue

                    if not filename:
                        if content_type in ("text/plain", "text/html", "multipart/mixed",
                                            "multipart/alternative", "multipart/related"):
                            continue
                        ext_map = {
                            "application/pdf": ".pdf",
                            "image/jpeg": ".jpg",
                            "image/png": ".png",
                            "image/gif": ".gif",
                            "application/msword": ".doc",
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
                            "application/vnd.ms-excel": ".xls",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
                        }
                        ext = ext_map.get(content_type, "")
                        if not ext:
                            continue
                        filename = "prilog_{}{}".format(ukupno + 1, ext)

                    filename_clean = self.clean_text(filename)
                    payload = part.get_payload(decode=True)

                    if not payload:
                        continue

                    # Preskacamo slike manje od 10KB - vjerovatno logoi
                    if content_type.startswith("image/") and len(payload) < 10240:
                        continue

                    filepath = os.path.join(subfolder, filename_clean)
                    counter = 1
                    base, ext = os.path.splitext(filepath)
                    while os.path.exists(filepath):
                        filepath = "{}_{}{}".format(base, counter, ext)
                        counter += 1

                    with open(filepath, "wb") as out:
                        out.write(payload)
                    ukupno += 1

            except Exception as e:
                greske += 1
                greske_detalji.append("Fajl: {}\nGreska: {}\n".format(os.path.basename(eml_path), str(e)))

        if greske_detalji:
            log_path = os.path.join(self.output_folder, "GRESKE_LOG.txt")
            with open(log_path, "w", encoding="utf-8") as log:
                log.write("\n---\n".join(greske_detalji))

        if greske == 0:
            messagebox.showinfo("Gotovo!", "Izvuceno {} fajlova\nSacuvano u podffolderima unutar:\n{}".format(ukupno, self.output_folder))
        else:
            messagebox.showwarning("Djelimicno gotovo", "Izvuceno: {}\nGreske: {}\nFolder: {}\n\nDetalji zapisani u GRESKE_LOG.txt".format(ukupno, greske, self.output_folder))