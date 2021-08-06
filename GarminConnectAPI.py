from garminconnect import *
from datetime import date
import logging
import time

def quit():
    exit()

#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

class connect:
    def __init__(self, username:str, password:str, debug:bool=False) -> None:        
        #self.today = date.today()
        self.client = Garmin(username, password)
        self.debug = debug
        self.innlogget = False
        self.loggInn()#username, password)
    
    def loggInn(self):#, username:str, password:str):
        #self.client = Garmin(username, password)
        def prøv():
            print(1)
            try:
                self.client.login()
                self.innlogget = True
                if self.debug:
                    print("Innlogget!")
            except (
                GarminConnectConnectionError,
                GarminConnectAuthenticationError,
                GarminConnectTooManyRequestsError,
            ) as err:
                if self.debug:
                    print("Error occurred during Garmin Connect Client login: %s" % err)
                self.innlogget = False
                time.sleep(1)
        
        for i in range(10):
            if not self.innlogget:
                prøv()
        if not self.innlogget:
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


        #if type_aktivitet:
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
