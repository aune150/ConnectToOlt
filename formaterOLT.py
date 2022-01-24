import json
from datetime import datetime

def gå_igjennom_økter(data, puls, svar={}):
    '''Går igjennom økt og sender til OLT\n
    Svar: {"navn":"", "type":"", "belastning":"", "dagsform":"", "kommentar":""}'''
    if data["activityTypeDTO"]["typeKey"] not in ["running", "cycling"]:
        return None
    d = {
        "navn": svar["navn"] if "navn" in svar else data["activityName"],
        "dato": data["summaryDTO"]["startTimeLocal"].split(" ")[0],
        "deler":{
            "hoveddel":{
            },
        },
    }

    d["belastning"] = svar["belastning"] if "belastning" in svar else 5
    d["dagsform"] = svar["dagsform"] if "dagsform" in svar else 5

    match data["activityTypeDTO"]["typeKey"]:
        case "running":
            d["deler"]["hoveddel"]["kilometer"]=round(data["summaryDTO"]["distance"]/1000, 2)
            if data["summaryDTO"]["averageSpeed"] > 2.08:
                d["deler"]["hoveddel"]["type"] = "RunningPath"
            else:
                d["deler"]["hoveddel"]["type"] = "RunningTerrain"
        case "cycling":
            d["deler"]["hoveddel"]["type"] = "Cycling"
    d["kommentar"] = svar["kommentar"] if "kommentar" in svar else ""

        

    for sone in puls:
        d["deler"]["hoveddel"]["i"+str(sone["zoneNumber"])] = round(sone["secsInZone"]/60)


    return d


def kommentar(kommentar:str, debug=False) -> dict:
    if debug:
        print({"data": {"type": "comments","attributes": {"comment": kommentar,"notify": "false"}}})
    return {"data": {"type": "comments","attributes": {"comment": kommentar,"notify": "false"}}}
    
def økt(data:dict) -> dict:
    """
    {
        "navn":
        "dato":"2021-06-23"
        "kommentar":
        "belastning":
        "dagsform":
        "deler":{
            "oppvarming":
            {
                "kilometer":"2,35"
                "type": RunningTerrain | RunningPath
                "i1":
                "i2":
                "i3":
                "i4":
                "i5":
            },
            "hoveddel":
            {
                "kilometer":"2,35"
                "type": RunningTerrain | RunningPath
                "i1":
                "i2":
                "i3":
                "i4":
                "i5":
            },
            "avsluttning":
            {
                "kilometer":"2,35"
                "type": RunningTerrain | RunningPath
                "i1":
                "i2":
                "i3":
                "i4":
                "i5":
            },
        },
    }
    """
    pointer = 0
    ordbok = {
        "oppvarming":"Start",
        "hoveddel":"Main",
        "avsluttning":"End",
        "1":"Easy",
        "2":"Moderate",
        "3":"LAT",
        "4":"HAT",
        "5":"MaxO2"
    }
    d = {}
    d["meta"] = {"included":{}}

    d["meta"]["included"]["comments"] = [
            {
                "type": "comments",
                "attributes": {
                    "comment": data["kommentar"],
                    "notify": "false"
                }
            }
        ]
    
    d["meta"]["included"]["cells"] = []
    for dell in data["deler"]:
        for item in data["deler"][dell]:
            if item == "type":
                #Må gjøres på en annen måte
                """if (data["deler"][dell][item].split("+")[1][0] == "O" or data["deler"][dell][item].split("+")[1][0] == "S") and len(data["deler"][dell][item].split("+")) == 3:
                    for navn in data["deler"][dell][item].split("+")[1:2]:
                        pointer += 1
                        d["meta"]["included"]["cells"].append({
                            "type": "cells",
                            "attributes": {
                                "value": int(data["deler"][dell][item].split("?")[1]),
                                "tagLabel": f"Orienteering.{navn}",
                                "position": 0,
                                "phaseLabel": f"Orienteering.Training.TrainingPhase{ordbok[dell]}",
                                "fragmentType": {
                                    "id": "3",
                                    "name": "Strength"
                                },
                                "groupLabel": "Orienteering.Strength"
                            }
                        })"""
                if True:
                    pointer += 1
                    d["meta"]["included"]["cells"].append({
                    "type": "cells",
                    "attributes": {
                        "value": 1,
                        "tagLabel": f"Orienteering.Movement{data['deler'][dell][item]}",
                        "position": 0,
                        "phaseLabel": f"Orienteering.Training.TrainingPhase{ordbok[dell]}",
                        "fragmentType": {
                            "id": "1",
                            "name": "Movement"
                        },
                        "groupLabel": "Orienteering.Movement"
                    }
                    })
            elif item == "kilometer":
                pointer += 1
                d["meta"]["included"]["cells"].append({
                    "type": "cells",
                    "attributes": {
                        "value": data['deler'][dell][item],
                        "tagLabel": "Orienteering.Kilometers",
                        "position": 0,
                        "phaseLabel": f"Orienteering.Training.TrainingPhase{ordbok[dell]}",
                        "fragmentType": {
                            "id": "1",
                            "name": "Movement"
                        },
                        "groupLabel": "Orienteering.Kilometer"
                    }
                })
            elif item[0] == "I" or item[0] == "i":
                pointer += 1
                d["meta"]["included"]["cells"].append({
                "type": "cells",
                "attributes": {
                    "value": data['deler'][dell][item],
                    "tagLabel": f"Orienteering.EnduranceI{item[1]}{ordbok[item[1]]}",
                    "position": 0,
                    "phaseLabel": f"Orienteering.Training.TrainingPhase{ordbok[dell]}",
                    "fragmentType": {
                        "id": "1",
                        "name": "Movement"
                    },
                    "groupLabel": "Orienteering.Endurance"
                }
            })

    d["meta"]["included"]["cells"].append({"type": "cells","attributes": {"value": data["belastning"],"tagLabel": "Orienteering.PerceivedExertion","groupLabel": "Orienteering.Training.Status"}})
    d["meta"]["included"]["cells"].append({"type": "cells","attributes": {"value": data["dagsform"],"tagLabel": "Orienteering.FormN","groupLabel": "Orienteering.Training.Status"}})
    pointer += 2

    d["data"] = {"type": "workouts","attributes": {"title": data["navn"],"date": data["dato"],"trainingType": {"id": "0"}}}

    d["data"]["meta"] = {"relationships": {"comments": {"data": [{"pointer": "/meta/included/comments/0"}]},"cells": {"data": []}}}
    l = []
    for i in range(pointer):
        l.append({"pointer": f"/meta/included/cells/{i}"})
    d["data"]["meta"]["relationships"]["cells"]["data"] = l

    return json.dumps(d)



if __name__ == "__main__":
    print("Fotmater kan ikke kjøres på egenhånd")