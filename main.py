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
        self.GC = connect(self.innstilinger["garminconnect-username"], self.innstilinger["garminconnect-password"], debug=self.debug, app=self.app)
        return self.GC.loggInn()

    def get_økter(self, fra_dag, til_dag):
        "Lagrer økter i self.økt"
        self.økt = self.GC.aktiv_per_dag(fra_dag, til_dag)

    def gå_igjennom_økter(self):
        "Går igjennom alle økter i self.økt og sender til OLT"
        for i in self.økt:
            self.GC.puls(i["activityId"])
            data = i
            if data["activityType"]["typeKey"] == "running":
                puls = self.GC.hr_timezones

                print("Dato: ", data["startTimeLocal"].split(" ")[0], "\n",
                "Sted: ", data["activityName"], "\n",
                "Distanse: ", data["distance"], "\n", 
                "Varighet: ", datetime.timedelta(seconds=data["duration"]))

                if self.enkel:
                    data["activityName"]
                else:
                    navn = input("Navn på økten: ")

                d = {
                    "navn": data["activityName"] if navn == "" else navn,
                    "dato": data["startTimeLocal"].split(" ")[0],
                    "belastning":input("Belastning: "),
                    "dagsform":input("Dagsform: "),
                    "deler":{
                        "hoveddel":{
                            "kilometer":round(data["distance"]/1000, 2),
                            "type": "RunningTerrain" if input("Type løping (T-erreng eller V-ei): ") == "T" else "RunningPath",
                        },
                    },
                }
                
                if self.enkel:
                    d["kommentar"] = ""
                else:
                    d["kommentar"] = input("Kommentar på økten:\n")
                

                for sone in puls:
                    d["deler"]["hoveddel"]["i"+str(sone["zoneNumber"])] = round(sone["secsInZone"]/60)

                if self.debug:
                    print(d)

                self.O.økt(self.F.økt(d))

if __name__ == "__main__":
    M = main(debug=True)
    M.koble_OLT()
    M.koble_GC()
    M.get_økter(str(datetime.datetime.date(datetime.datetime.now())), str(datetime.datetime.date(datetime.datetime.now())))
    M.gå_igjennom_økter()