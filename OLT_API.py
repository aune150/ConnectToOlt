import requests as re


class olt():
    def __init__(self, username:str, password:str, debug:bool=False) -> None:
        self.info = {}
        self.req = re.Session()
        self.debug = debug
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
        if self.debug:
            print("økt")
            print(resultat.status_code)
            print(resultat.text)
        if resultat != 201:
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


if __name__ == "__main__":
    olt = olt("aune150@gmail.com", "aB6YUdHl", debug=True)
    with open("p.json", "r") as f:
        payload = f.read()
    olt.økt(payload=payload)