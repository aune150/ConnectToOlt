import os
#os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy.lang.builder import Builder
from kivymd.app import MDApp
from kivymd.uix.picker import MDDatePicker
from main import main
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty



jdata = str([
    {
        "type": "title",
        "title": "OLT"
    },

    {
        "type": "string",
        "title": "Brukernavn",
        "section": "section1",
        "key": "OLT-username"
    },

    {
        "type": "string",
        "title": "Passord",
        "section": "section1",
        "key": "OLT-password"
    },
    
    {
        "type": "title",
        "title": "Garmin Connect"
    },

    {
        "type": "string",
        "title": "Brukernavn",
        "section": "section1",
        "key": "GarminConnect-username"
    },

    {
        "type": "string",
        "title": "Passord",
        "section": "section1",
        "key": "GarminConnect-password"
    },
    
    {
        "type": "title",
        "title": "System"
    },

    { 
        "type": "bool",
        "title": "Debug",
        "section": "section1",
        "key": "debug"
    }#,

    #{ 
    #    "type": "bool",
    #    "title": "Enkel modus",
    #    "desc": "Slår av muligheten for å velge egene navn",
    #    "section": "section1",
    #    "key": "enkel"
    #}
]).replace("'", '"')

def read_ini(path:str) -> dict:
    with open(path, "r") as f:
        fil = f.read().split("\n")
    ut = {}
    for row in fil:
        if row != "":
            if row[0] != "[":
                ut[row.split(" = ")[0]] = row.split(" = ")[1]
    return ut

def fra_HTML_to_RGBA100(kode:str, a:float=1) -> list:
    return [int(kode[0:2], 16)/256, int(kode[2:4], 16)/256, int(kode[4:6], 16)/256, 1]



class C2O(MDApp):

    green = fra_HTML_to_RGBA100("43A047")
    red = fra_HTML_to_RGBA100("E53935")
    grey = fra_HTML_to_RGBA100("BDBDBD")
    gc_innlogget = False
    olt_innlogget = False
    date_range = []
    økter = []
    popup_text = StringProperty()

    def build(self):
        self.innstilinger = read_ini("c2o.ini")
        self.debug = True if self.innstilinger["debug"] == "1" else False
        self.enkel = True# if self.innstilinger["enkel"] == "1" else False
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        Builder.load_file("C2O.kv")
        self.root.ids.olt.text = f"OLT: {self.innstilinger['olt-username']}"
        self.root.ids.garmin.text = f"Garmin: {self.innstilinger['garminconnect-username']}"
        self.main = main(innstilinger=self.innstilinger, debug=self.debug, enkel=self.enkel, app=self)

    def build_U(self):
        self.innstilinger = read_ini("c2o.ini")
        self.debug = True if self.innstilinger["debug"] == "1" else False
        self.enkel = True# if self.innstilinger["enkel"] == "1" else False
        self.root.ids.olt.text = f"OLT: {self.innstilinger['olt-username']}"
        self.root.ids.garmin.text = f"Garmin: {self.innstilinger['garminconnect-username']}"
        self.main = main(innstilinger=self.innstilinger, debug=self.debug, enkel=self.enkel, app=self)

    def on_config_change(self, *args):
        self.build_U()

    def koble_til_olt(self):
        if self.innstilinger["olt-username"] and self.innstilinger["olt-password"]:
            if self.main.koble_OLT():
                self.root.ids.olt_icon.icon = "check-circle"
                self.root.ids.olt_icon.text_color = self.green
                self.root.ids.olt_koble.color = self.grey
                self.root.ids.olt_koble.on_release = self.test
                self.logg("Koblet til OLT")
                self.olt_innlogget = True
        else:
            self.logg("Legg inn brukernavn og passord til OLT i innstingene før du kobler til")

    def koble_til_gc(self):
        if self.innstilinger["garminconnect-username"] and self.innstilinger["garminconnect-password"]:
            if self.main.koble_GC():
                self.root.ids.garmin_icon.icon = "check-circle"
                self.root.ids.garmin_icon.text_color = self.green
                self.root.ids.garmin_koble.color = self.grey
                self.root.ids.garmin_koble.on_release = self.test
                self.logg("Koblet til Garmin")
                self.gc_innlogget = True
        else:
            self.logg("Legg inn brukernavn og passord til Garmin i innstingene før du kobler til")

    def get_date(self, instance, date, date_range):
        if self.debug:
            print(instance, date, date_range)
        if len(date_range) == 0:
            #Bare en dato valgt
            self.date_range = [str(date), str(date)]
        else:
            self.date_range = [str(date_range[0]), str(date_range[-1])]
        self.root.ids.fra_dato.text = self.date_range[0]
        self.root.ids.til_dato.text = self.date_range[1]

    def on_cancel(self, instance, date):
        self.logg("Avbrutt")

    def show_date_picker(self):
        date_dialog = MDDatePicker(mode="range")
        date_dialog.bind(on_cancel=self.on_cancel, on_save=self.get_date)
        date_dialog.open()

    def build_config(self, config):
        config.setdefaults('section1', {
            "OLT-username":"",
            "OLT-password":"",
            "GarminConnect-username":"",
            "GarminConnect-password":"",
            "debug":False,
            "enkel":False
        })
    
    def build_settings(self, settings):
        settings.add_json_panel("Innstilinger", self.config, data=jdata)
    
    def test(self, *args):
        pass
    
    def logg(self, out:str):
        self.root.ids.logg.text = str(out).replace("\n", "")
    
    def hent_okter(self):
        if len(self.date_range) != 0:
            if self.gc_innlogget:
                self.main.get_økter(self.date_range[0], self.date_range[1])
                self.logg(f"Hentet {len(self.main.økt)} økter fra Garmin")
                self.økter = self.main.økt
            else:
                self.logg("Prøv å koble til Garmin før du henter økter")
        else:
            self.logg("Velg datoer før du henter økter")
    
    def ga_igjennom(self):
        if len(self.økter) != 0:
            if not self.olt_innlogget:
                self.logg("Prøv å koble til OLT før du går igjennom økter")
            else:
                for i in self.økter:
                    print(i)
                    #self.root.ids.rest_økter.text = f"Antall økter igjen: {len(self.økter)}"
                    self.main.gå_igjennom_økter(i)
        else:
            self.logg("Prøv å hente noen økter først")
    
    def pop_avbryt(self):
        self.popupW.dismiss()
        self.logg("Du avbrøt gjennomgangen")
    
    def pop_lagre(self):
        self.logg("Sendte 1 økt til OLT", self.root.ids.hello)
        self.popupW.dismiss()


if __name__ == "__main__":
    C2O().run()