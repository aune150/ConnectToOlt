import json
from Formater_OLT_Data import formater
from GarminConnectAPI import connect
from OLT_API import olt
import datetime


class main:
    def __init__(self, innstilinger={}, debug:bool=False, enkel=False, app=False) -> None:
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
        self.GC.puls(data["activityId"])
        puls = self.GC.hr_timezones
        
        if datetime.fromisoformat(data["startTimeLocal"]).isoweekday() == 4:
            if not self.d:
                d = {
                    "navn": data["activityName"],
                    "dato": data["startTimeLocal"].split(" ")[0],
                    "deler":{
                        "oppvarming":{},
                        "hoveddel":{
                            "type":""
                        },
                        "avsluttning":{}
                    },
                }
            
            if data["activityType"]["typeKey"] == "running" and datetime.fromisoformat(data["startTimeLocal"]).hour < 12:
                self.d["deler"]["oppvarming"]["type"] = "RunningPath"
                self.d["deler"]["oppvarming"]["kilometer"] = round(data["distance"]/1000, 2)
                for sone in puls:
                    self.d["deler"]["oppvarming"]["i"+str(sone["zoneNumber"])] = round(sone["secsInZone"]/60)
            elif data["activityType"]["typeKey"] == "other":
                self.d["deler"]["hoveddel"]["type"] += "+Other?"+str(round(data["duration"]/60))
            elif data["activityType"]["typeKey"] == "strength_training":
                self.d["deler"]["hoveddel"]["type"] += "+StrengthGeneral?"+str(round(data["duration"]/60))
        
        elif data["activityType"]["typeKey"] == "running" or data["activityType"]["typeKey"] == "cycling":
            


            d = {
                "navn": data["activityName"],
                "dato": data["startTimeLocal"].split(" ")[0],
                "deler":{
                    "hoveddel":{
                    },
                },
            }

            d["belastning"] = 5
            d["dagsform"] = 5
            if data["activityType"]["typeKey"] == "running":
                d["deler"]["hoveddel"]["kilometer"]=round(data["distance"]/1000, 2)
                if data["averageSpeed"] > 2.08:
                    d["deler"]["hoveddel"]["type"] = "RunningPath"
                else:
                    d["deler"]["hoveddel"]["type"] = "RunningTerrain"
            elif data["activityType"]["typeKey"] == "cycling":
                d["deler"]["hoveddel"]["type"] = "Cycling"
            if data["description"] == "None" or data["description"] == None:
                d["kommentar"] = ""
            else:
                d["kommentar"] = data["description"]
                if "&" in data["description"]:
                    d["deler"]["hoveddel"]["type"] = "RunningTerrain" if data["description"].split("&")[1] == "T" else "RunningPath"
                

            for sone in puls:
                d["deler"]["hoveddel"]["i"+str(sone["zoneNumber"])] = round(sone["secsInZone"]/60)

        if self.debug:
            print(d)

        if not self.d:
            self.O.økt(self.F.økt(d))
        else:
            if len(self.d["deler"]["hoveddel"]["type"]) == 3:
                self.O.økt(self.F.økt(self.d))

if __name__ == "__main__":
    M = main(debug=True, enkel=True)
    M.koble_GC()
    M.koble_OLT()
    M.get_økter(str(datetime.datetime.date(datetime.datetime.now())), str(datetime.datetime.date(datetime.datetime.now())))
    for økt in M.økt:
        M.gå_igjennom_økter(økt)