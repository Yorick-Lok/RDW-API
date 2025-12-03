import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
from datetime import datetime

class RDW_API:

    API_KEY = "KkgXpxzWQXJDRMfel4H3OKyxi"
    BASE_URL = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"

    OPCENTEN = {
        "Groningen": 0.957,
        "Friesland": 0.921,
        "Drenthe": 0.920,
        "Overijssel": 0.822,
        "Flevoland": 0.839,
        "Gelderland": 1.012,
        "Utrecht": 0.842,
        "Noord-Holland": 0.774,
        "Zuid-Holland": 1.015,
        "Zeeland": 0.844,
        "Noord-Brabant": 0.849,
        "Limburg": 0.858
    }

    CATEGORY_FIELDS = {
        "Kenteken": ["kenteken"],
        "Merk": ["merk", "handelsbenaming"],
        "Kleur": ["eerste_kleur", "tweede_kleur"],
        "Voertuigsoort": ["voertuigsoort"],
        "Massa's": [
            "toegestane_maximum_massa_voertuig",
            "maximum_massa_trekken_ongeremd",
            "maximum_trekken_massa_geremd",
            "massa_ledig_voertuig",
            "massa_rijklaar",
            "vermogen_massarijklaar",
            "technische_max_massa_voertuig",
            "variant",
            "uitvoering",
            "maximum_massa_samenstelling"
        ],
        "Specificaties": [
            "inrichting", "aantal_zitplaatsen", "aantal_cilinders",
            "aantal_deuren", "aantal_wielen", "export_indicator",
            "taxi_indicator", "plaats_chassisnummer",
            "openstaande_terugroepactie_indicator", "wielbasis",
            "cilinderinhoud", "europese_voertuigcategorie",
            "type", "breedte", "aanhangwagen_middenas_geremd",
            "aanhangwagen_autonoom_geremd", "laadvermogen"
        ],
        "Datums": [
            "vervaldatum_apk", "vervaldatum_apk_dt",
            "datum_eerste_toelating", "datum_eerste_toelating_dt",
            "datum_tenaamstelling", "datum_tenaamstelling_dt",
            "datum_eerste_tenaamstelling_in_nederland",
            "datum_eerste_tenaamstelling_in_nederland_dt",
            "jaar_laatste_registratie_tellerstand"
        ],
        "Keuringen": [
            "typegoedkeuringsnummer",
            "volgnummer_wijziging_eu_typegoedkeuring",
            "wacht_op_keuren",
            "zuinigheidsclassificatie",
            "tenaamstellen_mogelijk",
            "tellerstandoordeel",
            "code_toelichting_tellerstandoordeel"
        ],
        "Financieel": ["bruto_bpm", "catalogusprijs", "wam_verzekerd"]
    }

    MRB_1995_TABLE = [
        (0, 549, 0), (550, 649, 13), (650, 759, 35), (750, 849, 62),
        (850, 949, 92), (950, 1049, 125), (1050, 1149, 163), (1150, 1249, 205),
        (1250, 1349, 251), (1350, 1449, 301), (1450, 1549, 355), (1550, 1649, 412),
        (1650, 1749, 473), (1750, 1849, 537), (1850, 1949, 604), (1950, 2049, 675),
        (2050, 2149, 749), (2150, 2249, 826), (2250, 2349, 906), (2350, 2449, 989),
        (2450, 2549, 1075), (2550, 2649, 1164)
    ]

    DIESEL_SURCHARGE_TABLE = [
        (0, 900, 0), (901, 1000, 64), (1001, 1100, 70), (1101, 1200, 77),
        (1201, 1300, 84), (1301, 1400, 91), (1401, 1500, 98), (1501, 1600, 105),
        (1601, 1700, 112), (1701, 1800, 119), (1801, 1900, 126), (1901, 2000, 133),
        (2001, 2100, 140), (2101, 2200, 147), (2201, 2300, 154), (2301, 2400, 161),
        (2401, 2500, 168), (2501, 2600, 175), (2601, 2700, 182)
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("RDW API")
        self.root.geometry("750x900")
        self.car_cache = None
        self.create_widgets()

    def create_widgets(self):
        self.instruction_label = tk.Label(self.root, text="Vul het kenteken hier in.")
        self.instruction_label.pack(pady=10)

        self.license_plate_entry = tk.Entry(self.root, width=10)
        self.license_plate_entry.pack()

        self.province_label = tk.Label(self.root, text="Kies provincie voor MRB berekening:")
        self.province_label.pack()

        self.province_var = tk.StringVar()
        self.province_dropdown = tk.OptionMenu(self.root, self.province_var, *self.OPCENTEN.keys())
        self.province_var.trace("w", lambda *args: threading.Thread(target=self.update_mrb_only, daemon=True).start())
        self.province_dropdown.pack(pady=5)

        self.filters_frame = tk.Frame(self.root)
        self.filters_frame.pack(pady=10)

        tk.Label(self.filters_frame, text="Kies welke informatie je wilt tonen:").grid(row=0, column=0, columnspan=2)

        self.show_brand = tk.BooleanVar(value=True)
        tk.Checkbutton(self.filters_frame, text="Merk", variable=self.show_brand).grid(row=1, column=0, sticky='w')
        self.show_color = tk.BooleanVar(value=True)
        tk.Checkbutton(self.filters_frame, text="Kleur", variable=self.show_color).grid(row=1, column=1, sticky='w')
        self.show_vehicle_type = tk.BooleanVar(value=True)
        tk.Checkbutton(self.filters_frame, text="Voertuigsoort", variable=self.show_vehicle_type).grid(row=2, column=0, sticky='w')
        self.show_mass = tk.BooleanVar(value=False)
        tk.Checkbutton(self.filters_frame, text="Massa's", variable=self.show_mass).grid(row=2, column=1, sticky='w')
        self.show_specifications = tk.BooleanVar(value=False)
        tk.Checkbutton(self.filters_frame, text="Specificaties", variable=self.show_specifications).grid(row=3, column=0, sticky='w')
        self.show_dates = tk.BooleanVar(value=False)
        tk.Checkbutton(self.filters_frame, text="Datums", variable=self.show_dates).grid(row=3, column=1, sticky='w')
        self.show_inspections = tk.BooleanVar(value=False)
        tk.Checkbutton(self.filters_frame, text="Keuringen", variable=self.show_inspections).grid(row=4, column=0, sticky='w')
        self.show_financial = tk.BooleanVar(value=False)
        tk.Checkbutton(self.filters_frame, text="Financieel", variable=self.show_financial).grid(row=4, column=1, sticky='w')

        self.view_button = tk.Button(self.root, text="Informatie bekijken", command=self.license_plate_search)
        self.view_button.pack(pady=10)

        self.output_area = scrolledtext.ScrolledText(self.root, width=70, height=40, wrap=tk.WORD)
        self.output_area.pack(pady=10)

    def license_plate_search(self):
        kenteken = self.license_plate_entry.get().upper().replace("-", "")
        if not kenteken:
            messagebox.showerror("Fout", "Vul een kenteken in")
            return
        threading.Thread(target=self.fetch_and_display, args=(kenteken,), daemon=True).start()

    def fetch_and_display(self, kenteken):
        self.output_area.delete("1.0", tk.END)  # clear output

        params = {"kenteken": kenteken}
        headers = {"X-App-Token": self.API_KEY}
        self.output_area.insert(tk.END, f"Gegevens ophalen voor {kenteken}...\n")

        try:
            response = requests.get(self.BASE_URL, headers=headers, params=params)
            response.raise_for_status()
        except Exception as e:
            self.output_area.insert(tk.END, f"\nFout tijdens ophalen: {e}\n")
            return

        data = response.json()
        if not data:
            self.output_area.insert(tk.END, "Geen gegevens gevonden.")
            return

        self.car_cache = data[0]

        fuel = self.fetch_fuel_data(kenteken)
        self.car_cache["brandstof_omschrijving"] = fuel
        car = self.car_cache

        for category, fields in self.CATEGORY_FIELDS.items():
            show = {
                "Kenteken": True,
                "Merk": self.show_brand.get(),
                "Kleur": self.show_color.get(),
                "Voertuigsoort": self.show_vehicle_type.get(),
                "Massa's": self.show_mass.get(),
                "Specificaties": self.show_specifications.get(),
                "Datums": self.show_dates.get(),
                "Keuringen": self.show_inspections.get(),
                "Financieel": self.show_financial.get()
            }.get(category, True)

            if not show:
                continue

            items = []
            for key in fields:
                if key in car:
                    value = car[key]
                    if key.endswith("_dt") and value:
                        value = value.split("T")[0]
                    items.append(f"{key}: {value}")

            if category == "Financieel":
                province = self.province_var.get()
                if province:
                    mrb = self.calculate_mrb(car, province)
                    if mrb.get("oldtimer"):
                        items.append("===== Motorrijtuigbelasting =====")
                        items.append("Vrijstelling 40+ oldtimer: €0")
                    else:
                        items.append("===== Motorrijtuigbelasting =====")
                        items.append(f"MRB basis (1995): €{mrb['base']}")
                        items.append(f"MRB diesel toeslag: €{mrb['diesel']}")
                        items.append(f"MRB opcenten ({province}): €{mrb['opcenten']:.2f}")
                        items.append(f"MRB totaal: €{mrb['total']:.2f}")

            if not items:
                continue

            self.output_area.insert(tk.END, f"---------- {category} ----------\n")
            for line in items:
                self.output_area.insert(tk.END, line + "\n")
            self.output_area.insert(tk.END, "------------------------------\n\n")

        self.root.after(0, self.update_mrb_only)

    def calculate_opcenten(self, base_hoofdsom_year, province):
        rate = self.OPCENTEN.get(province)
        if rate is None:
            raise ValueError(f"Unknown province: {province}")
        return base_hoofdsom_year * rate

    def calculate_mrb(self, car, province):
        try:
            weight = int(car.get("massa_rijklaar") or car.get("massa_ledig_voertuig") or 0)
        except:
            weight = 0

        # Check 40+ oldtimer
        oldtimer = False
        date_str = car.get("datum_eerste_toelating")
        if date_str:
            try:
                d = datetime.strptime(date_str, "%Y%m%d")
                age = (datetime.now() - d).days / 365.25
                if age >= 40:
                    oldtimer = True
            except:
                pass

        if oldtimer:
            return {
                "weight": weight,
                "base": 0,
                "diesel": 0,
                "opcenten": 0,
                "total": 0,
                "oldtimer": True
            }

        base_hoofdsom_year = self.get_base_hoofdsom(weight)
        is_diesel = car.get("brandstof_omschrijving", "").lower() == "diesel"
        diesel_surcharge = 0
        if is_diesel:
            for low, high, amount in self.DIESEL_SURCHARGE_TABLE:
                if low <= weight <= high:
                    diesel_surcharge = amount
                    break
        provincial_surcharge = self.calculate_opcenten(base_hoofdsom_year, province)
        total = base_hoofdsom_year + diesel_surcharge + provincial_surcharge
        return {
            "weight": weight,
            "base": base_hoofdsom_year,
            "diesel": diesel_surcharge,
            "opcenten": provincial_surcharge,
            "total": total
        }

    def update_mrb_only(self):
        if not self.car_cache:
            return
        province = self.province_var.get()
        if not province:
            return

        mrb = self.calculate_mrb(self.car_cache, province)
        content = self.output_area.get("1.0", tk.END)

        if "===== Motorrijtuigbelasting =====" not in content:
            return

        # Replace old MRB block
        start = content.index("===== Motorrijtuigbelasting =====")
        end = content.find("------------------------------", start)
        if end == -1:
            end = len(content)
        else:
            end += len("------------------------------")

        if mrb.get("oldtimer"):
            new_mrb_text = "===== Motorrijtuigbelasting =====\nVrijstelling 40+ oldtimer: €0"
        else:
            new_mrb_text = (
                "===== Motorrijtuigbelasting =====\n"
                f"MRB basis (1995): €{mrb['base']}\n"
                f"MRB diesel toeslag: €{mrb['diesel']}\n"
                f"MRB opcenten ({province}): €{mrb['opcenten']:.2f}\n"
                f"MRB totaal: €{mrb['total']:.2f}"
            )

        refreshed = content[:start] + new_mrb_text + content[end:]
        yview = self.output_area.yview()
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert("1.0", refreshed)
        self.output_area.yview_moveto(yview[0])

    def get_base_hoofdsom(self, weight):
        for low, high, amount in self.MRB_1995_TABLE:
            if low <= weight <= high:
                return amount
        return 0

    def fetch_fuel_data(self, kenteken):
        url = "https://opendata.rdw.nl/resource/8ys7-d773.json"
        params = {"kenteken": kenteken}
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return data[0].get("brandstof_omschrijving", "")
        except:
            pass
        return ""

root = tk.Tk()
app = RDW_API(root)
root.mainloop()
