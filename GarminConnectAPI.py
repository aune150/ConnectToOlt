from garminconnect import *
from datetime import date


def quit():
    import sys
    sys.exit()



class connect:
    def __init__(self, username:str, password:str, debug:bool=False, app=False, auto_logginn:bool=True) -> None:
        self.client = Garmin(username, password)
        self.debug = debug
        self.innlogget = False
        self.app = app
        if auto_logginn:
            self.loggInn()
    
    def loggInn(self) -> bool:
        def prøv():
            #print(1)
            try:
                self.client.login()
                self.innlogget = True
                if self.debug:
                    print("Innlogget!")
                return True
            except (
                GarminConnectConnectionError,
                GarminConnectAuthenticationError,
                GarminConnectTooManyRequestsError,
            ) as err:
                if self.debug:
                    print(str(err))
                    print("Error occurred during Garmin Connect Client login: %s" % err)
                self.innlogget = False
                return str(err)
        
        err = "Error connecting"
        i = 0
        while err == "Error connecting":
            i += 1
            err = prøv()
            if self.app:
                from app import C2O
                C2O.logg(self.app, f"Prøver å koble til Garmin. Forsøk nr: {i}")
            if i > 15:
                quit()

    
    def test(self):
        print(self.client.get_full_name())
    
    def aktiv(self, start=0, limit=1):
        self.aktiviteter = self.client.get_activities(start, limit)
        if self.debug:
            print(self.aktiviteter)
    
    def aktiv_per_dag(self, fra_dag, til_dag, type_aktivitet:str=None):
        """Fetch available activities between specific dates

        :param fra_dag: String in the format YYYY-MM-DD
        :param til_dag: String in the format YYYY-MM-DD
        :param type_aktivitet: (Optional) Type of activity you are searching
                             Possible values are [cycling, running, swimming,
                             multi_sport, fitness_equipment, hiking, walking, other]
        :return: list of JSON activities"""


        self.aktiviteter = self.client.get_activities_by_date(fra_dag, til_dag, type_aktivitet)
        if self.debug:
            print(self.aktiviteter)
        return self.aktiviteter

    def puls(self, id:int) -> list:
        self.hr_timezones:list
        self.hr_timezones = self.client.get_activity_hr_in_timezones(id)
        if self.debug:
            print(self.hr_timezones)
        return self.client.get_activity_hr_in_timezones(id)

if __name__=="__main__":
    G = connect("aune150@gmail.com", "Nelnua34", debug=True)
    G.aktiv()
    G.puls(G.aktiviteter[0]["activityId"])
