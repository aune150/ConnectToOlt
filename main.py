import json
from Formater_OLT_Data import formater
from GarminConnectAPI import connect
from OLT_API import olt
import datetime


class main:
    def __init__(self, creds="C:/Users/aune1/NY/python/Connecttoolt/creds.json", debug:bool=False) -> None:
        self.debug = debug
        with open(creds) as f:
            creds = json.load(f)
        self.GC = connect(creds["GarminConnect"]["username"], creds["GarminConnect"]["password"], debug=debug)
        self.O = olt(creds["OLT"]["username"], creds["OLT"]["password"], debug=debug)
        self.F = formater()

    def get_økter(self, fra_dag, til_dag):
        "Lagrer økter i self.økt"
        self.økt = self.GC.aktiv_per_dag(fra_dag, til_dag)

    def gå_igjennom_økter(self):
        "Går igjennom alle økter i self.økt og sender til OLT"
        for i in self.økt:
            self.GC.puls(i["activityId"])
            data = i
            puls = self.GC.hr_timezones

            print("Dato: ", data["startTimeLocal"].split(" ")[0], "\n",
            "Sted: ", data["activityName"], "\n",
            "Distanse: ", data["distance"], "\n", 
            "Varighet: ", datetime.timedelta(seconds=data["duration"]))

            navn = input("Navn på økten: ")

            d = {
                "navn": data["activityName"] if navn == "" else navn,
                "dato": data["startTimeLocal"].split(" ")[0],
                "kommentar":input("Kommentar på økten:\n"),
                "belastning":input("Belastning: "),
                "dagsform":input("Dagsform: "),
                "deler":{
                    "hoveddel":{
                        "kilometer":round(data["distance"]/1000, 2),
                        "type": "RunningTerrain" if input("Type løping (T-erreng eller V-ei): ") == "T" else "RunningPath",
                    },
                },
            }

            for sone in puls:
                d["deler"]["hoveddel"]["i"+str(sone["zoneNumber"])] = round(sone["secsInZone"]/60)

            if self.debug:
                print(d)

            self.O.økt(self.F.økt(d))

if __name__ == "__main__":
    M = main()
    M.get_økter(str(datetime.datetime.date(datetime.datetime.now())), str(datetime.datetime.date(datetime.datetime.now())))
    M.gå_igjennom_økter()