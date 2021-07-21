

class formater():
    def __init__(self, debug:bool=False) -> None:
        self.debug = debug

    def kommentar(self, kommentar:str) -> dict:
        if self.debug:
            print({"data": {"type": "comments","attributes": {"comment": kommentar,"notify": "false"}}})
        return {"data": {"type": "comments","attributes": {"comment": kommentar,"notify": "false"}}}
    
    def økt(self, data:dict) -> dict:
        """
        {
            "navn":
            "dato":"2021-06-23"
            "kommentar":
            "belastning":
            "dagsform":
            "oppvarming":
            {
                "kilometer":"2,35"
                "type": RunningTerrain | RunningPath
                "i1":
                "i2":
                "i3":
                "i4":
                "i5":
            }
            "hoveddel":
            {
                "kilometer":"2,35"
                "type": RunningTerrain | RunningPath
                "i1":
                "i2":
                "i3":
                "i4":
                "i5":
            }
            "avslutting":
            {
                "kilometer":"2,35"
                "type": RunningTerrain | RunningPath
                "i1":
                "i2":
                "i3":
                "i4":
                "i5":
            }
        }
        """
        pointer = 0
        ordbok = {"oppvarming":"Start", "hoveddel":"Main", "avsluttning":"End"}
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
                print(item)
                if item == "type":
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
                elif item[0] == "I":
                    pointer += 1
                    d["meta"]["included"]["cells"].append({
                    "type": "cells",
                    "attributes": {
                        "value": data['deler'][dell][item],
                        "tagLabel": f"Orienteering.EnduranceI{item[1:]}",
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

        return d


#f = formater()

data = {
            "navn":"Testløp",
            "dato":"2021-06-23",
            "kommentar":"Et bra test løp",
            "belastning":8,
            "dagsform":4,
            "deler":{
                "hoveddel":{
                    "kilometer":"2,35",
                    "type": "RunningTerrain",
                    "I1Easy":1,
                    "I2Moderate":3,
                    "I3LAT":6,
                    "I4HAT":3,
                    "I5MaxO2":1
                },
                "avsluttning":{
                    "kilometer":"4.3",
                    "I5MaxO2":20
                }
            }
        }

if __name__ == "__main__":
    f = formater()
    with open("p.json", "w", encoding="UTF-8") as fil:
        fil.write(str(f.økt(data = data)).replace("'", '"'))
