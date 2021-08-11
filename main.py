import json
from Formater_OLT_Data import formater
from GarminConnectAPI import connect
from OLT_API import olt
import datetime


class main:
    def __init__(self, innstilinger=json.loads(open("C:/Users/aune1/NY/python/Connecttoolt/creds.json").read()), debug:bool=False, enkel=False, app=False) -> None:
        self.debug, self.enkel, self.innstilinger, self.app= debug, enkel, innstilinger, app
        self.F = formater()

    def koble_OLT(self) -> bool:
        self.O = olt(self.innstilinger["olt-username"], self.innstilinger["olt-password"], debug=self.debug, auto_logginn=False)
        return self.O.login(self.innstilinger["olt-username"], self.innstilinger["olt-password"])
    
    def koble_GC(self) -> bool:
        if self.app:
            self.GC = connect(self.innstilinger["garminconnect-username"], self.innstilinger["garminconnect-password"], debug=self.debug, app=self.app, auto_logginn=False)
        else:
            self.GC = connect(self.innstilinger["garminconnect-username"], self.innstilinger["garminconnect-password"], debug=self.debug, app=self.app, auto_logginn=True)
        self.GC.loggInn()
        return self.GC.innlogget

    def get_økter(self, fra_dag, til_dag):
        "Lagrer økter i self.økt"
        self.økt = self.GC.aktiv_per_dag(fra_dag, til_dag)

    def gå_igjennom_økter(self, data, svar={}):
        '''Går igjennom økt og sender til OLT\n
        Svar: {"navn":"", "type":"", "belastning":"", "dagsform":"", "kommentar":""}'''
        

        if data["activityType"]["typeKey"] == "running":
            self.GC.puls(data["activityId"])
            puls = self.GC.hr_timezones


            d = {
                "navn": data["activityName"],
                "dato": data["startTimeLocal"].split(" ")[0],
                "deler":{
                    "hoveddel":{
                        "kilometer":round(data["distance"]/1000, 2)
                    },
                },
            }

            if self.enkel:
                # Hvis enkel mudus er skrudd på
                d["belastning"] = 5
                d["dagsform"] = 5
                if data["averageSpeed"] > 6/3.6:
                    d["deler"]["hoveddel"]["type"] = "RunningPath"
                else:
                    d["deler"]["hoveddel"]["type"] = "RunningTerrain"
                if data["description"] == "None" or data["description"] == None:
                    d["kommentar"] = ""
                else:
                    d["kommentar"] = data["description"]
                    if "&" in data["description"]:
                        d["deler"]["hoveddel"]["type"] = "RunningTerrain" if data["description"].split("&")[1] == "T" else "RunningPath"
                
            else:
                if self.app:
                    # Hvis det kommer fra appen med ordboka svar
                    d["deler"]["hoveddel"]["type"] = svar["type"]
                    d["belastning"]=svar["belastning"]
                    d["dagsform"]=svar["dagsform"]
                    d["kommentar"] = svar["kommentar"]
                    d["navn"] = svar["navn"]
                else:
                    # Hvis den kjøres i terminalen og bruker input()
                    print("Dato: ", data["startTimeLocal"].split(" ")[0], "\n",
                    "Sted: ", data["activityName"], "\n",
                    "Distanse: ", data["distance"], "\n", 
                    "Varighet: ", datetime.timedelta(seconds=data["duration"]))

                    navn = input("Navn på økten: ")
                    if navn != "":
                        d["navn"] = navn
                    d["deler"]["hoveddel"]["type"] = "RunningTerrain" if input("Type løping (T-erreng eller V-ei): ") == "T" else "RunningPath"
                    d["belastning"]=input("Belastning: ")
                    d["dagsform"]=input("Dagsform: ")
                    d["kommentar"] = input("Kommentar på økten:\n")

            for sone in puls:
                d["deler"]["hoveddel"]["i"+str(sone["zoneNumber"])] = round(sone["secsInZone"]/60)

            if self.debug:
                print(d)

            self.O.økt(self.F.økt(d))

if __name__ == "__main__":
    M = main(debug=True, enkel=True)
    M.koble_GC()
    M.koble_OLT()
    M.get_økter(str(datetime.datetime.date(datetime.datetime.now())), str(datetime.datetime.date(datetime.datetime.now())))
    for økt in M.økt:
        M.gå_igjennom_økter(økt)