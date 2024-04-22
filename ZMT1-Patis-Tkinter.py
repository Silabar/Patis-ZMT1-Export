import datetime
import tkinter as tk
from tkinter import filedialog
import os
import sys

class Hauptfenster(tk.Tk):
    def __init__(self, landingzone=""):
        super().__init__()
        self.title("Patis-ZMT1")
        self.geometry("230x240")
        self.PATIS_LANDINGZONE = landingzone
        self.create_widgets()

    def create_widgets(self):
        labels = ["Sachnummer", "Startserialnummer", "Endserialnummer", "Auftrag", "Rev-Stand"]
        self.entries = []
        for i, label_text in enumerate(labels):
            tk.Label(self, text=label_text).grid(row=i, column=0, sticky="w")
            entry = tk.Entry(self)
            entry.grid(row=i, column=1, sticky="ew")
            self.entries.append(entry)

        self.btn_exec = tk.Button(self, text="ZMT1-File erzeugen", command=self.eingaben_check)
        self.btn_exec.grid(row=len(labels), column=1, sticky="ew")
        self.btn_reset = tk.Button(self, text="Reset", command=self.hauptfenster_reset)
        self.btn_reset.grid(row=len(labels), column=0, sticky="ew")

        self.status_frame = tk.LabelFrame(self, text="Status:")
        self.status_frame.grid(row=len(labels)+1, column=0, columnspan=2, sticky="ew")
        self.lb = tk.Label(self.status_frame, wraplength=200)
        self.lb.grid(row=0, column=0, columnspan=2)

        self.entries[0].focus()
        self.setze_status("Bitte Werte eintragen", "yellow")

    def setze_status(self, status_text, status_farbe):
        self.lb.config(text=status_text, background=status_farbe)

    def hauptfenster_reset(self):
        for entry in self.entries:
            entry.delete(0, "end")
        self.entries[0].focus()
        self.setze_status("Reset erfolgreich", "green")

    def eingaben_check(self):
        eingaben = [entry.get() for entry in self.entries]
        sachnummer, serialstart, serialend, auftrag, revstand = eingaben
        try:
            sachnummer = int(sachnummer)
            auftrag = int(auftrag)
            serialstart = int(serialstart)
            serialend = int(serialend)
            revstand = int(revstand)
        except ValueError:
            self.setze_status("Ungültige Eingaben", "red")
            return

        if len(str(sachnummer)) not in [7, 8]:
            self.setze_status("Sachnummer muss eine Nummer mit 7 bis 8 Stellen sein!", "red")
        elif serialstart > serialend:
            self.setze_status("Endserial muss größer oder gleich Startserial sein!", "red")
        elif len(str(auftrag)) != 7:
            self.setze_status("Auftrag muss eine Nummer mit 7 Stellen sein!", "red")
        else:
            self.zmt1_file_erstellen(sachnummer, serialstart, serialend, auftrag, revstand)

    def zmt1_file_erstellen(self, sachnummer, serialstart, serialend, auftrag, revstand):
        jetzt = datetime.datetime.now()

        jahr = jetzt.year
        monat = jetzt.month
        tag = jetzt.day
        stunde = jetzt.hour
        minute = jetzt.minute
        sekunde = jetzt.second

        if os.path.exists(self.PATIS_LANDINGZONE):
            verzeichnis = filedialog.askdirectory(initialdir=self.PATIS_LANDINGZONE)
        else:
            verzeichnis = filedialog.askdirectory()

        if verzeichnis:
            eintraege = []
            for i in range(serialstart, serialend + 1):
                eintraege.append(
                    str(sachnummer).zfill(18)
                    + str(i)
                    + " " * (36 - 18 - len(str(i)))
                    + "1030" + str(auftrag).zfill(12)
                    + 13 * " "
                    + str(revstand).zfill(2)
                    + "  n.a."
                    + 26 * " "
                    + str(jahr)
                    + str(monat).zfill(2) + str(tag).zfill(2)
                    + "FME     ")

            datei = (
                    "FME_ZMT1_"
                    + str(minute).zfill(2)
                    + str(sekunde).zfill(2)
                    + "_"
                    + str(jahr)
                    + str(monat).zfill(2)
                    + str(tag).zfill(2)
                    + "_"
                    + str(stunde).zfill(2)
                    + ".DAT")

            try:
                os.makedirs(verzeichnis, exist_ok=True)
                with open(os.path.join(verzeichnis, datei), "w", encoding="utf-8") as zmt1datei:
                    zmt1datei.write(str(len(eintraege)).zfill(6) + "\n")
                    for x in eintraege:
                        zmt1datei.write(x + "\n")
                if os.path.isfile(os.path.join(verzeichnis, datei)):
                    self.setze_status("Datei " + datei + " wurde erzeugt", "green")
                else:
                    self.setze_status("Datei konnte nicht erstellt werden", "red")

            except IOError:
                self.setze_status("Datei kann nicht geschrieben werden", "red")
        else:
            self.setze_status("Abbruch durch Benutzer", "red")

if __name__ == "__main__":
    PATIS_LANDINGZONE = sys.argv[1] if len(sys.argv) > 1 else ""
    Hauptfenster(PATIS_LANDINGZONE).mainloop()
