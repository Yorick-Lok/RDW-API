import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading


class RDWRecallsApp:

    BASE_MERK_TYPE = "https://opendata.rdw.nl/resource/mu2x-mu5e.json"
    BASE_RECALLS = "https://opendata.rdw.nl/resource/j9yg-7rg9.json"

    def __init__(self, root):
        self.root = root
        self.root.title("RDW Terugroepacties per Merk")
        self.root.geometry("950x850")
        self.create_widgets()

    # ---------------- UI ---------------- #
    def create_widgets(self):
        tk.Label(
            self.root, text="Zoek RDW terugroepacties per merk", font=("Arial", 14)
        ).pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        tk.Label(frame, text="Merk:").pack(side=tk.LEFT)
        self.brand_entry = tk.Entry(frame, width=25)
        self.brand_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(self.root, text="Zoeken", command=self.start_search).pack(pady=10)

        self.output = scrolledtext.ScrolledText(self.root, width=110, height=40)
        self.output.pack(pady=10)

    # ---------------- Threading ---------------- #
    def start_search(self):
        brand = self.brand_entry.get().strip().upper()
        if not brand:
            messagebox.showwarning("Fout", "Voer een merk in.")
            return

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, f"Zoeken naar terugroepacties voor merk: {brand}\n\n")

        threading.Thread(target=self.search_recalls, args=(brand,), daemon=True).start()

    # ---------------- Logic ---------------- #
    def search_recalls(self, brand):
        try:
            # Stap 1: haal merk-type + referentiecode op
            types = self.get_types_by_brand(brand)
            if not types:
                self.write_output("Geen types gevonden voor dit merk.\n")
                return

            self.write_output(f"Gevonden {len(types)} type-invoer(s).\n\n")

            for t in types:
                ref_code = t.get("referentiecode_rdw")
                merk = t.get("merk", brand)
                model_type = t.get("type", "Onbekend")

                if not ref_code:
                    continue

                # Stap 2: haal terugroepacties op
                recalls = self.get_recall_details(ref_code)
                for r in recalls:
                    # Datum aankondiging, truncate bij T
                    datum = r.get('datum_aankondiging_producent_dt', 'Onbekend')
                    if datum and 'T' in datum:
                        datum = datum.split('T')[0]

                    # Categorie gebrek
                    categorie = r.get('categorie_defect') or "Onbekend"

                    # Risk: only display if field exists
                    gevaar = r.get('mogelijk_gevaar')
                    gevaar_line = f"Mogelijk risico: {gevaar}\n" if gevaar and gevaar.strip() != "" else ""

                    # Model/Type uit recall, fallback naar type
                    model = r.get('handelsbenaming') or model_type

                    line = (
                        f"Merk: {r.get('merk', merk)}\n"
                        f"Type/Model: {model}\n"
                        f"Categorie gebrek: {categorie}\n"
                        f"{gevaar_line}"
                        f"Datum aankondiging: {datum}\n"
                        + "-"*110 + "\n"
                    )
                    self.write_output(line)

        except Exception as e:
            self.write_output(f"Fout:\n{e}\n")

    # ---------------- API ---------------- #
    def get_types_by_brand(self, brand):
        params = {"merk": brand}
        r = requests.get(self.BASE_MERK_TYPE, params=params)
        r.raise_for_status()
        return r.json()

    def get_recall_details(self, code):
        params = {"referentiecode_rdw": code, "$limit": 50}
        r = requests.get(self.BASE_RECALLS, params=params)
        r.raise_for_status()
        return r.json()

    # ---------------- Thread-safe UI write ---------------- #
    def write_output(self, text):
        self.root.after(0, lambda: self.output.insert(tk.END, text))


# ---------------- Run app ---------------- #
if __name__ == "__main__":
    root = tk.Tk()
    app = RDWRecallsApp(root)
    root.mainloop()
