import requests as re


class olt():
    def __init__(self, username:str, password:str, debug:bool=False, auto_logginn:bool=True) -> None:
        self.info = {}
        self.req = re.Session()
        self.debug = debug
        if auto_logginn:
            self.login(username, password)
    
    def login(self, username:str, password:str) -> bool:
        try:
            if self.debug:
                print(username, password)
            resultat = self.req.post("https://api.olt-dagbok.nif.no/credentials/auth", data={"username":username, "password":password})
            if self.debug:
                print(resultat.status_code)
                print(resultat.text)
            
            if resultat.status_code != 200:
                return False
            
            self.info["aToken"] = dict(resultat.json())["accessToken"]

            resultat2 = self.req.post("https://api.olt-dagbok.nif.no/credentials/token", data={"accessToken":self.info["aToken"]})
            if resultat2.status_code != 200:
                return False
            
            self.info["id"] = dict(resultat.json())["user"]["id"]
            self.info["token"] = dict(resultat2.json())["token"]
            if self.debug:
                print(self.info)
                print(resultat2.status_code)
            
            return True

        except:
            return False

    def økt(self, payload) -> bool:
        if payload is str:
            with open(payload, encoding="UTF-8") as fil:
                from json import load
                payload = load(fil)
        resultat = self.req.post(f"https://api.olt-dagbok.nif.no/api/v1/users/{self.info['id']}/workouts", headers={"Authorization": "Bearer "+self.info["token"]}, data=payload)
        if resultat.status_code != 201:
            print(resultat.text)
            return False
        return True
    
    def kommentar(self, payload:dict, år:int, uke:int) -> bool:
        resultat = self.req.post(f"https://api.olt-dagbok.nif.no/api/v1/users/{self.info['id']}/weeks/{år}-w{uke}/comments", headers={"Authorization": "Bearer "+self.info["token"]}, data=payload)
        if self.debug:
            print(resultat.status_code)
            print(resultat.text)
        if resultat != 201:
            return False
        return True

    def finn(self, fra_dato, til_dato) -> list:
        print(f"https://api.olt-dagbok.nif.no/api/v1/users/{self.info['id']}/workouts?filter%5Bfrom%5D={fra_dato}&filter%5Bto%5D={til_dato}&page%5Bsize%5D=500")
        resultat = self.req.get(f"https://api.olt-dagbok.nif.no/api/v1/users/{self.info['id']}/workouts?filter%5Bfrom%5D={fra_dato}&filter%5Bto%5D={til_dato}&page%5Bsize%5D=500", headers={"Authorization": "Bearer "+self.info["token"]})
        return [resultat.json()["data"][i]["id"] for i in range(len(resultat.json()["data"]))]
    
    def slett(self, id) -> int:
        resultat = self.req.delete(f"https://api.olt-dagbok.nif.no/api/v1/users/{self.info['id']}/workouts?{id}")
        return resultat.status_code

if __name__ == "__main__":
    with open("creds.txt", "r") as f:
        creds = f.read().split("\n")
    olt = olt(creds[0], creds[1], debug=False)