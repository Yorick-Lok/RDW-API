import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading

class RDW_API:
    """Class for the RDW_API app."""

    API_KEY = "KkgXpxzWQXJDRMfel4H3OKyxi"
    BASE_URL = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"

    FIELDS_TO_HIDE = [
        "api_gekentekende_voertuigen_assen",
        "api_gekentekende_voertuigen_brandstof",
        "api_gekentekende_voertuigen_carrosserie",
        "api_gekentekende_voertuigen_carrosserie_specifiek",
        "api_gekentekende_voertuigen_voertuigklasse"
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("RDW API")
        self.root.geometry("700x800")
        self.create_widgets()
    

    def create_widgets(self):
        """Create the widgets here."""
        self.instruction_label = tk.Label(self.root, text="Vul het kenteken hier in.")
        self.instruction_label.pack(pady=10)

        self.license_plate_entry = tk.Entry(self.root, width=10)
        self.license_plate_entry.pack()

        # --- FILTER CHECKBOXES ---
        self.filters_frame = tk.Frame(self.root)
        self.filters_frame.pack(pady=10)

        tk.Label(self.filters_frame, text="Kies welke informatie je wilt tonen:").grid(
            row=0, column=0, columnspan=2
        )
        
        self.show_brand = tk.BooleanVar(value=True)
        tk.Checkbutton(self.filters_frame, text="Merk", variable=self.show_brand
        ).grid(row=1, column=0, sticky='w')

        self.show_color = tk.BooleanVar(value=True)
        tk.Checkbutton(self.filters_frame, text="Kleur", variable=self.show_color
        ).grid(row=1, column=1, sticky='w')

        self.show_vehicle_type = tk.BooleanVar(value=True)
        tk.Checkbutton(self.filters_frame, text="Voertuigsoort", variable=self.show_vehicle_type
        ).grid(row=2, column=0, sticky='w')

        self.show_mass = tk.BooleanVar(value=False)
        tk.Checkbutton(self.filters_frame, text="Massa's", variable=self.show_mass
        ).grid(row=2, column=1, sticky='w')

        self.show_specifications = tk.BooleanVar(value=False)
        tk.Checkbutton(self.filters_frame, text="Specificaties", variable=self.show_specifications
        ).grid(row=3, column=0, sticky='w')

        self.show_dates = tk.BooleanVar(value=False)
        tk.Checkbutton(self.filters_frame, text="Datums", variable=self.show_dates
        ).grid(row=3, column=1, sticky='w')

        self.show_inspections = tk.BooleanVar(value=False)
        tk.Checkbutton(self.filters_frame, text="Keuringen", variable=self.show_inspections
        ).grid(row=4, column=0, sticky='w')

        self.show_financial = tk.BooleanVar(value=False)
        tk.Checkbutton(self.filters_frame, text="Financieel", variable=self.show_financial
        ).grid(row=4, column=1, sticky='w')
        # -------------------------

        self.view_button = tk.Button(self.root, text="Informatie bekijken",
                                     command=self.license_plate_search)
        self.view_button.pack(pady=10)

        self.output_area = scrolledtext.ScrolledText(self.root, width=70, height=40, wrap=tk.WORD)
        self.output_area.pack(pady=10)


    # --- THIS WAS MISSING: properly defined class method ---
    def should_display(self, key):
        """Return True if the field should be shown based on user selection."""

        if key in ["merk", "handelsbenaming"] and not self.show_brand.get():
            return False
        
        if key in ["eerste_kleur", "tweede_kleur"] and not self.show_color.get():
            return False
        
        if key in ["voertuigsoort"] and not self.show_vehicle_type.get():
            return False
        
        if key in [
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
        ] and not self.show_mass.get():
            return False
        
        if key in [
            "inrichting",
            "aantal_zitplaatsen",
            "aantal_cilinders",
            "aantal_deuren",
            "aantal_wielen",
            "aantal_rolstoelplaatsen",
            "export_indicator",
            "taxi_indicator",
            "plaats_chassisnummer",
            "openstaande_terugroepactie_indicator",
            "wielbasis",
            "cilinderinhoud",
            "europese_voertuigcategorie",
            "type"

        ] and not self.show_specifications.get():
            return False
        
        if key in [
            "vervaldatum_apk",
            "vervaldatum_apk_dt",

            "datum_eerste_toelating",
            "datum_eerste_toelating_dt",

            "datum_tenaamstelling",           
            "datum_tenaamstelling_dt",
            
            "datum_eerste_tenaamstelling_in_nederland",
            "datum_eerste_tenaamstelling_in_nederland_dt",

            "jaar_laatste_registratie_tellerstand"
        ] and not self.show_dates.get():
            return False
        
        if key in [
            "typegoedkeuringsnummer",
            "volgnummer_wijziging_eu_typegoedkeuring",
            "wacht_op_keuren",
            "zuinigheidsclassificatie",
            "tenaamstellen_mogelijk",
            "tellerstandoordeel",
            "code_toelichting_tellerstandoordeel"
        ] and not self.show_inspections.get():
            return False
        
        if key in [
            "bruto_bpm",
            "catalogusprijs",
            "wam_verzekerd"
        ] and not self.show_financial.get():
            return False
        
        return True
    # -------------------------------------------------------


    def license_plate_search(self):
        """Called when button is pressed."""
        kenteken = self.license_plate_entry.get().upper().replace("-","")
        
        if not kenteken:
            messagebox.showerror("Fout", "Vul een kenteken in")
            return
        
        # Start a thread to prevent UI Freeze
        threading.Thread(target=self.fetch_and_display, args=(kenteken,), daemon=True).start()
        
    def fetch_and_display(self, kenteken):
        """Runs in background thread to avoid freezing"""

        params = {"kenteken": kenteken}
        headers = {"X-App-Token": self.API_KEY}
        
        # Do NOT clear output first, we wait until results are ready.
        self.output_area.insert(tk.END, f"Gegevens ophalen voor {kenteken}...\n")

        try:
            response = requests.get(self.BASE_URL, headers=headers, params=params)
        except Exception as e:
            self.output_area.insert(tk.END, f"\nFout tijdens ophalen {e}\n")
            return

        if response.status_code != 200:
            self.output_area.insert(tk.END, f"API Fout: {response.status_code}")
            return
        
        data = response.json()

        if not data:
            self.output_area.insert(tk.END, "Geen gegevens gevonden.")
            return
        
        car = data[0]

        # Now clear safely before adding new info.
        self.output_area.delete(1.0, tk.END)
        self.output_area.insert(tk.END, f"Resultaten voor {kenteken}:\n\n")

        # Add results incrementally
        for key, value in car.items():

            if key not in self.FIELDS_TO_HIDE and self.should_display(key):

                if key.endswith("_dt"):
                    value = value.split("T")[0]

                # Insert one line at a time
                self.output_area.insert(tk.END, f"{key}: {value}\n")



root = tk.Tk()
app = RDW_API(root)
root.mainloop()