import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
from datetime import datetime


class Defects:

    API_KEY = "Q3WXIBM2PiELtoZvC7Tu8dKe6"
    BASE_URL = "https://opendata.rdw.nl/resource/hx2c-gt7k.json"

    VELDEN = {
        "Gebrek Identificatie": 'gebrek_identificatie',
        "Ingangsdatum Gebrek": 'ingangsdatum_gebrek',
        "Einddatum Gebrek": 'einddatum_gebrek',
        "Ingangsdatum Gebrek (DT)": 'ingangsdatum_gebrek_dt',
        "Einddatum Gebrek (DT)": 'einddatum_gebrek_dt',
        "Gebrek Paragraaf Nummer": 'gebrek_paragraaf_nummer',
        "Gebrek Artikel Nummer": 'gebrek_artikel_nummer',
        "Gebrek Omschrijving": 'gebrek_omschrijving' 
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Rejected Cars")
        self.root.geometry("750x900")
        self.car_cache = None
        self.create_widgets()

    def create_widgets(self):
        self.instruction_label = tk.Label(self.root, text="Maak hier uw keuze \
voor de APK-Statistieken ")
        self.instruction_label.pack(pady=10)

        self.statistics_var = tk.StringVar()
        self.statistics_dropdown = tk.OptionMenu(self.root, self.statistics_var, *self.VELDEN.keys())
        # self.statistics_var.trace("w", lambda *args: threading.Thread(target=self))
        self.statistics_dropdown.pack(pady=5)
 

root = tk.Tk()
app = Defects(root)
root.mainloop()