import json
from Formater_OLT_Data import formater
from GarminConnectAPI import connect
from OLT_API import olt
import datetime


class main:
    def __init__(self, innstilinger=json.loads(open("C:/Users/aune1/NY/python/Connecttoolt/creds.json").read()), debug:bool=False, enkel=False) -> None:
        self.debug, self.enkel = debug, enkel
        self.GC = connect(innstilinger["garminconnect-username"], innstilinger["garminconnect-password"], debug=debug)
        self.O = olt(innstilinger["olt-username"], innstilinger["olt-password"], debug=debug)
        self.F = formater()

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
    M = main()
    M.get_økter(str(datetime.datetime.date(datetime.datetime.now())), str(datetime.datetime.date(datetime.datetime.now())))
    M.gå_igjennom_økter()