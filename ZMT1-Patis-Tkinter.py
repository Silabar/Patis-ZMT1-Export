#!/usr/bin/env python3

import datetime
from tkinter import filedialog
import tkinter as tk
import os
import sys

if len(sys.argv) > 1:
    patis_landingzone = sys.argv[1]
else:
    patis_landingzone = ""

def setze_status(status_text, status_farbe):
    global lb
    lb.config(text = status_text, background= status_farbe)

def hauptfenster_reset():
    ent1.delete(0, "end")
    ent2.delete(0, "end")
    ent3.delete(0, "end")
    ent4.delete(0, "end")
    ent5.delete(0, "end")
    ent1.focus()
    setze_status("Reset erfolgreich", "green")

def eingaben_check(sachnummer, serialstart, serialend, auftrag, revstand):
    if not str.isdigit(sachnummer):
        setze_status("Sachnummer muss eine Nummer sein!", "red")
        return

    if not str.isdigit(serialstart):
        setze_status("Startserial muss eine Nummer sein!", "red")
        return

    if not str.isdigit(serialend):
        setze_status("Endserial muss eine Nummer sein!", "red")
        return

    if not str.isdigit(auftrag):
        setze_status("Auftrag muss eine Nummer sein!", "red")
        return

    zmt1_file_erstellen(sachnummer, serialstart, serialend, auftrag, revstand)

def zmt1_file_erstellen(sachnummer, serialstart, serialend, auftrag, revstand):
    jetzt = datetime.datetime.now()

    jahr = jetzt.year
    monat = jetzt.month
    tag = jetzt.day
    stunde = jetzt.hour
    minute = jetzt.minute
    sekunde = jetzt.second

    if os.path.exists(patis_landingzone):
        verzeichnis = filedialog.askdirectory(initialdir=patis_landingzone)
    else:
        verzeichnis = filedialog.askdirectory()

    if verzeichnis:
        eintraege = []
        for i in range(int(serialstart), int(serialend) + 1):
            eintraege.append(
                            sachnummer.zfill(18)
                            + str(i)
                            + " " * (36-18-len(str(i)))
                            + "1030" + auftrag.zfill(12)
                            + 13*" "
                            + revstand.zfill(2)
                            + "  n.a."
                            + 26*" "
                            + str(jahr)
                            + str(monat).zfill(2)+str(tag).zfill(2)
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
            with open(os.sep.join([verzeichnis, datei]), "w") as zmt1datei:
                zmt1datei.write(str(len(eintraege)).zfill(6) + "\n")
                for x in eintraege:
                    zmt1datei.write(x + "\n")
            setze_status("Datei " + datei + " wurde erzeugt", "green")

        except(IOError):
            setze_status("Datei kann nicht geschrieben werden", "red")
    else:
        setze_status("Abbruch durch Benutzer", "red")


if __name__ == "__main__":
    hauptfenster = tk.Tk()
    hauptfenster.title("Patis-ZMT1")
    hauptfenster.geometry("230x240")

    tk.Label(hauptfenster, text="Sachnummer").grid(row=0, column = 0)
    tk.Label(hauptfenster, text="Startserialnummer").grid(row=1, column = 0)
    tk.Label(hauptfenster, text="Endserialnummer").grid(row=2, column = 0)
    tk.Label(hauptfenster, text="Auftrag").grid(row=3, column = 0)
    tk.Label(hauptfenster, text="Rev-Stand").grid(row=4, column = 0)
    ent1 = tk.Entry(hauptfenster)
    ent2 = tk.Entry(hauptfenster)
    ent3 = tk.Entry(hauptfenster)
    ent4 = tk.Entry(hauptfenster)
    ent5 = tk.Entry(hauptfenster)
    ent1.grid(row=0, column=1)
    ent2.grid(row=1, column=1)
    ent3.grid(row=2, column=1)
    ent4.grid(row=3, column=1)
    ent5.grid(row=4, column=1)

    btn_exec=tk.Button(hauptfenster, text="ZMT1-File erzeugen" , command=lambda: eingaben_check(ent1.get(), ent2.get(), ent3.get(), ent4.get(), ent5.get()))
    btn_reset=tk.Button(hauptfenster, text="Reset", command=hauptfenster_reset)
    btn_exec.grid(row=5, column=1)
    btn_reset.grid(row=5, column= 0)

    lb_bock = tk.Label(hauptfenster).grid(row = 6, column = 0)
    lf = tk.LabelFrame(hauptfenster, text="Status:")
    lf.grid(row = 7, column = 0, columnspan = 2)
    lb = tk.Label(lf, wraplength=200 )
    setze_status("Bitte Werte eintragen", "yellow")
    lb.grid(row = 0, column = 0, columnspan = 2)

    hauptfenster.mainloop()
