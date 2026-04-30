import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil

class FileRenamerPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.place(relwidth=1, relheight=1)

        self.files = []

        # Scrollable glavni frame
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

        ctk.CTkLabel(self.scroll_frame, text="Preimenovanje fajlova", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(18, 4))
        ctk.CTkLabel(self.scroll_frame, text="Dodaj fajlove, podesi format i pregledaj prije preimenovanja", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 10))

        content_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        content_frame.pack(padx=20, pady=(0, 8), fill="x")
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)

        # LIJEVA STRANA - lista fajlova
        left_frame = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", corner_radius=8)
        left_frame.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(left_frame, text="Fajlovi", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 4))

        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 6))
        ctk.CTkButton(btn_frame, text="+ Dodaj", command=self.add_files, width=100).grid(row=0, column=0, padx=4)
        ctk.CTkButton(btn_frame, text="Gore", command=self.move_up, width=70, fg_color="#555", hover_color="#444").grid(row=0, column=1, padx=4)
        ctk.CTkButton(btn_frame, text="Dolje", command=self.move_down, width=70, fg_color="#555", hover_color="#444").grid(row=0, column=2, padx=4)

        btn_frame2 = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame2.pack(pady=(0, 6))
        ctk.CTkButton(btn_frame2, text="Ukloni", command=self.remove_selected, width=100, fg_color="#7a1a1a", hover_color="#5e1414").grid(row=0, column=0, padx=4)
        ctk.CTkButton(btn_frame2, text="Ocisti sve", command=self.clear_list, width=100, fg_color="#555", hover_color="#444").grid(row=0, column=1, padx=4)

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

        # DESNA STRANA - podesavanja
        right_frame = ctk.CTkFrame(content_frame, fg_color="#1a1a1a", corner_radius=8)
        right_frame.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(right_frame, text="Podesavanja", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 8))

        settings_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        settings_frame.pack(padx=14, fill="x")

        ctk.CTkLabel(settings_frame, text="Tekstualni prefiks:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", pady=5)
        self.text_prefix = ctk.CTkEntry(settings_frame, placeholder_text="npr. FA-2025-", width=160)
        self.text_prefix.grid(row=0, column=1, padx=(8, 0), pady=5)

        ctk.CTkLabel(settings_frame, text="Broj pocetak:", font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", pady=5)
        self.num_start = ctk.CTkEntry(settings_frame, placeholder_text="npr. 1", width=160)
        self.num_start.grid(row=1, column=1, padx=(8, 0), pady=5)

        ctk.CTkLabel(settings_frame, text="Korak brojanja:", font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w", pady=5)
        self.num_step = ctk.CTkEntry(settings_frame, placeholder_text="npr. 1", width=160)
        self.num_step.grid(row=2, column=1, padx=(8, 0), pady=5)

        ctk.CTkLabel(settings_frame, text="Broj cifara:", font=ctk.CTkFont(size=12)).grid(row=3, column=0, sticky="w", pady=5)
        self.num_padding = ctk.CTkEntry(settings_frame, placeholder_text="npr. 3 za 001", width=160)
        self.num_padding.grid(row=3, column=1, padx=(8, 0), pady=5)

        ctk.CTkLabel(settings_frame, text="Separator:", font=ctk.CTkFont(size=12)).grid(row=4, column=0, sticky="w", pady=5)
        self.separator = ctk.CTkEntry(settings_frame, placeholder_text="npr. _ ili -", width=160)
        self.separator.grid(row=4, column=1, padx=(8, 0), pady=5)

        ctk.CTkLabel(settings_frame, text="Sufiks (na kraju):", font=ctk.CTkFont(size=12)).grid(row=5, column=0, sticky="w", pady=5)
        self.suffix = ctk.CTkEntry(settings_frame, placeholder_text="npr. -FINAL", width=160)
        self.suffix.grid(row=5, column=1, padx=(8, 0), pady=5)

        check_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        check_frame.pack(padx=14, pady=(8, 0), fill="x")

        self.use_number = ctk.CTkCheckBox(check_frame, text="Dodaj broj u naziv", font=ctk.CTkFont(size=12))
        self.use_number.select()
        self.use_number.pack(anchor="w", pady=3)

        self.copy_mode = ctk.CTkCheckBox(check_frame, text="Sacuvaj originale (kopiraj u 'Preimenovano')", font=ctk.CTkFont(size=12))
        self.copy_mode.select()
        self.copy_mode.pack(anchor="w", pady=3)

        ctk.CTkButton(right_frame, text="Pregledaj promjene", command=self.show_preview, width=200, fg_color="#555", hover_color="#444").pack(pady=(12, 10))

        # PREVIEW lista
        preview_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a1a", corner_radius=8)
        preview_frame.pack(padx=20, pady=(0, 8), fill="x")

        ctk.CTkLabel(preview_frame, text="Pregled novih naziva:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(8, 4))

        preview_wrap = ctk.CTkFrame(preview_frame, fg_color="#1e1e1e", corner_radius=6)
        preview_wrap.pack(padx=8, pady=(0, 8), fill="x")

        self.preview_listbox = tk.Listbox(
            preview_wrap,
            bg="#1e1e1e", fg="#aaffaa",
            borderwidth=0, highlightthickness=0,
            font=("Segoe UI", 10),
            activestyle="none",
            height=5
        )
        self.preview_listbox.pack(padx=6, pady=6, fill="x")

        # Dugme na dnu
        ctk.CTkButton(self.scroll_frame, text="Preimenuj fajlove", command=self.rename, width=220, height=40, fg_color="#1a7a3c", hover_color="#145e2d", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(4, 18))

    def add_files(self):
        files = filedialog.askopenfilenames()
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.listbox.insert(tk.END, "  {}".format(os.path.basename(f)))

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
        self.preview_listbox.delete(0, tk.END)

    def build_new_name(self, original_name, index):
        ime, ext = os.path.splitext(original_name)
        tekst_prefiks = self.text_prefix.get().strip()
        sufiks = self.suffix.get().strip()
        separator = self.separator.get()
        use_num = self.use_number.get()

        prefiks = tekst_prefiks

        if use_num:
            try:
                start = int(self.num_start.get()) if self.num_start.get().strip() else 1
                step = int(self.num_step.get()) if self.num_step.get().strip() else 1
                padding = int(self.num_padding.get()) if self.num_padding.get().strip() else 0
            except ValueError:
                start, step, padding = 1, 1, 0

            broj = start + (index * step)
            broj_str = str(broj).zfill(padding) if padding > 0 else str(broj)
            prefiks = "{}{}".format(tekst_prefiks, broj_str)

        if prefiks:
            novi_naziv = "{}{}{}{}{}".format(prefiks, separator, ime, sufiks, ext)
        else:
            novi_naziv = "{}{}{}".format(ime, sufiks, ext)

        return novi_naziv

    def show_preview(self):
        self.preview_listbox.delete(0, tk.END)
        if not self.files:
            self.preview_listbox.insert(tk.END, "  Nema fajlova za pregled.")
            return
        for i, filepath in enumerate(self.files):
            original = os.path.basename(filepath)
            novi = self.build_new_name(original, i)
            self.preview_listbox.insert(tk.END, "  {} -> {}".format(original, novi))

    def rename(self):
        if not self.files:
            messagebox.showwarning("Upozorenje", "Nisi dodao nijedan fajl.")
            return

        copy = self.copy_mode.get()
        uspjesno = 0
        greske = []

        for i, filepath in enumerate(self.files):
            original_naziv = os.path.basename(filepath)
            original_folder = os.path.dirname(filepath)
            novi_naziv = self.build_new_name(original_naziv, i)

            try:
                if copy:
                    output_folder = os.path.join(original_folder, "Preimenovano")
                    os.makedirs(output_folder, exist_ok=True)
                    dest = os.path.join(output_folder, novi_naziv)
                    counter = 1
                    base, ext = os.path.splitext(dest)
                    while os.path.exists(dest):
                        dest = "{}_{}{}".format(base, counter, ext)
                        counter += 1
                    shutil.copy2(filepath, dest)
                else:
                    dest = os.path.join(original_folder, novi_naziv)
                    os.rename(filepath, dest)
                uspjesno += 1
            except Exception as e:
                greske.append("{}: {}".format(original_naziv, str(e)))

        if not greske:
            if copy:
                poruka = "Uspjesno kopirano i preimenovano {} fajlova!\n\nSacuvano u folderu 'Preimenovano' pored originalnih fajlova.".format(uspjesno)
            else:
                poruka = "Uspjesno preimenovano {} fajlova na originalnoj lokaciji!".format(uspjesno)
            messagebox.showinfo("Gotovo!", poruka)
        else:
            messagebox.showwarning("Djelimicno gotovo", "Uspjesno: {} od {}\n\nGreske:\n{}".format(
                uspjesno, len(self.files), "\n".join(greske)))