import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext

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

        self.view_button = tk.Button(self.root, text="Informatie bekijken",
                                     command=self.license_plate_search)
        self.view_button.pack(pady=10)

        self.output_area = scrolledtext.ScrolledText(self.root, width=70, height=40, wrap=tk.WORD)
        self.output_area.pack(pady=10)

    def license_plate_search(self):
        """Called when button is pressed."""
        kenteken = self.license_plate_entry.get().upper().replace("-","")
        
        if not kenteken:
            messagebox.showerror("Fout", "Vul een kenteken in")
            return
        
        params = {"kenteken": kenteken}  # change to the license plate you want using the input frame.
        headers = {"X-App-Token": self.API_KEY}

        response = requests.get(self.BASE_URL, headers=headers, params=params)

        self.output_area.delete(1.0, tk.END) #Clear Output

        if response.status_code != 200:
            self.output_area.insert(tk.END, f"API Fout: {response.status_code}")
            return
        
        data = response.json()

        if not data:
            self.output_area.insert(tk.END, "Geen gegevens gevonden.")
            return
        
        #Show all key/value pairs of the first result.
        car = data[0]
        for key, value in car.items():
            if key not in self.FIELDS_TO_HIDE:
                if key in [
                    "vervaldatum_apk_dt",
                    "datum_tenaamstelling_dt",
                    "datum_eerste_toelating_dt",
                    "datum_eerste_tenaamstelling_in_nederland_dt"
                ]:
                    value = value.split("T")[0]
                self.output_area.insert(tk.END, f"{key}: {value}\n")

root = tk.Tk()
app = RDW_API(root)
root.mainloop()