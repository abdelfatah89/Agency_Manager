import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from generate_keys import generate_keypair
from license_generator import issue_license


class AdminLicenseGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KONACH Admin License Tool")
        self.geometry("920x760")
        self.minsize(860, 680)

        self.request_code_var = tk.StringVar()
        self.customer_var = tk.StringVar()
        self.days_var = tk.StringVar(value="365")
        self.status_var = tk.StringVar(value="active")
        self.private_key_var = tk.StringVar(value=str(Path("keys") / "private_key.pem"))
        self.client_public_key_var = tk.StringVar(value=str(Path("config") / "license_public_key.pem"))
        self.output_var = tk.StringVar(value="license.json")
        self.keys_dir_var = tk.StringVar(value="keys")

        self._configure_style()
        self._build_ui()

    def _configure_style(self):
        style = ttk.Style(self)
        available = style.theme_names()
        if "vista" in available:
            style.theme_use("vista")
        elif "clam" in available:
            style.theme_use("clam")

        style.configure("Root.TFrame", padding=12)
        style.configure("Card.TLabelframe", padding=10)
        style.configure("Card.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Primary.TButton", padding=(14, 8), font=("Segoe UI", 9, "bold"))
        style.configure("TButton", padding=(10, 7))
        style.configure("TLabel", font=("Segoe UI", 9))
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))

    def _build_ui(self):
        root = ttk.Frame(self, style="Root.TFrame")
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(4, weight=1)

        ttk.Label(root, text="License Issuance Workspace", style="Header.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 8),
        )

        request_frame = ttk.LabelFrame(root, text="Request Code", style="Card.TLabelframe")
        request_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        request_frame.columnconfigure(0, weight=1)
        self.request_code_text = scrolledtext.ScrolledText(request_frame, height=8, font=("Consolas", 10))
        self.request_code_text.grid(row=0, column=0, sticky="nsew")

        details = ttk.LabelFrame(root, text="License Details", style="Card.TLabelframe")
        details.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        details.columnconfigure(1, weight=1)
        details.columnconfigure(3, weight=1)
        details.columnconfigure(5, weight=1)

        ttk.Label(details, text="Customer").grid(row=0, column=0, sticky="w")
        ttk.Entry(details, textvariable=self.customer_var).grid(row=0, column=1, sticky="ew", padx=(6, 14))

        ttk.Label(details, text="Days").grid(row=0, column=2, sticky="w")
        ttk.Entry(details, textvariable=self.days_var, width=10).grid(row=0, column=3, sticky="w", padx=(6, 14))

        ttk.Label(details, text="Status").grid(row=0, column=4, sticky="w")
        ttk.Combobox(
            details,
            textvariable=self.status_var,
            values=("active", "revoked", "suspended"),
            state="readonly",
            width=14,
        ).grid(row=0, column=5, sticky="w", padx=(6, 0))

        files = ttk.LabelFrame(root, text="Files", style="Card.TLabelframe")
        files.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        files.columnconfigure(1, weight=1)

        ttk.Label(files, text="Private Key").grid(row=0, column=0, sticky="w")
        ttk.Entry(files, textvariable=self.private_key_var).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(files, text="Browse", command=self._browse_private_key).grid(row=0, column=2, sticky="w")

        ttk.Label(files, text="Output License File").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(files, textvariable=self.output_var).grid(row=1, column=1, sticky="ew", padx=6, pady=(6, 0))
        ttk.Button(files, text="Browse", command=self._browse_output).grid(row=1, column=2, sticky="w", pady=(6, 0))

        ttk.Label(files, text="Client Public Key").grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(files, textvariable=self.client_public_key_var).grid(row=2, column=1, sticky="ew", padx=6, pady=(6, 0))
        ttk.Button(files, text="Browse", command=self._browse_client_public_key).grid(row=2, column=2, sticky="w", pady=(6, 0))

        ttk.Label(files, text="Keys Directory").grid(row=3, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(files, textvariable=self.keys_dir_var).grid(row=3, column=1, sticky="ew", padx=6, pady=(6, 0))
        ttk.Button(files, text="Browse", command=self._browse_keys_dir).grid(row=3, column=2, sticky="w", pady=(6, 0))

        actions = ttk.Frame(root)
        actions.grid(row=4, column=0, sticky="nsew")
        actions.columnconfigure(0, weight=1)
        actions.rowconfigure(2, weight=1)

        button_bar = ttk.Frame(actions)
        button_bar.grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Button(button_bar, text="Generate Keys", command=self._generate_keys).pack(side="left")
        ttk.Button(button_bar, text="Issue License", style="Primary.TButton", command=self._issue_license).pack(
            side="left",
            padx=8,
        )
        ttk.Button(button_bar, text="Copy License JSON", command=self._copy_license).pack(side="left")

        ttk.Label(actions, text="Generated License JSON", style="Header.TLabel").grid(row=1, column=0, sticky="w")
        self.output_text = scrolledtext.ScrolledText(actions, height=14, font=("Consolas", 10))
        self.output_text.grid(row=2, column=0, sticky="nsew", pady=(4, 0))

    def _browse_private_key(self):
        path = filedialog.askopenfilename(
            title="Select private_key.pem",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")],
        )
        if path:
            self.private_key_var.set(path)

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Save license as",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            self.output_var.set(path)

    def _browse_client_public_key(self):
        path = filedialog.askopenfilename(
            title="Select client public key",
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")],
        )
        if path:
            self.client_public_key_var.set(path)

    def _browse_keys_dir(self):
        path = filedialog.askdirectory(title="Select keys directory")
        if path:
            self.keys_dir_var.set(path)

    def _generate_keys(self):
        try:
            private_path, public_path = generate_keypair(Path(self.keys_dir_var.get().strip() or "keys"))
            self.private_key_var.set(str(private_path))
            messagebox.showinfo(
                "Keys Generated",
                f"Private key: {private_path}\nPublic key: {public_path}\n\n"
                "If you use this new private key, deploy the matching public key to the client first.",
            )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _issue_license(self):
        request_code = self.request_code_text.get("1.0", "end").strip()
        customer = self.customer_var.get().strip()
        days_text = self.days_var.get().strip() or "0"
        status = self.status_var.get().strip()
        private_key_path = Path(self.private_key_var.get().strip())
        client_public_key_path = Path(self.client_public_key_var.get().strip())
        out_path = Path(self.output_var.get().strip() or "license.json")

        if not request_code:
            messagebox.showwarning("Missing Data", "Request code is required")
            return
        if not customer:
            messagebox.showwarning("Missing Data", "Customer is required")
            return

        try:
            days = int(days_text)
        except ValueError:
            messagebox.showwarning("Invalid Value", "Days must be an integer")
            return

        try:
            _, blob = issue_license(
                request_code=request_code,
                customer=customer,
                days=days,
                status=status,
                private_key_path=private_key_path,
                expected_public_key_path=client_public_key_path,
                out_path=out_path,
            )
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", blob)
            messagebox.showinfo("Success", f"License generated: {out_path}")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _copy_license(self):
        blob = self.output_text.get("1.0", "end").strip()
        if not blob:
            messagebox.showwarning("No Data", "No license JSON to copy")
            return
        self.clipboard_clear()
        self.clipboard_append(blob)
        messagebox.showinfo("Copied", "License JSON copied to clipboard")


if __name__ == "__main__":
    app = AdminLicenseGUI()
    app.mainloop()
