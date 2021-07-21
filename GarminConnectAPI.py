from garminconnect import *
from datetime import date
import logging


#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

class connect:
    def __init__(self, username:str, password:str) -> None:        
        self.today = date.today()
        self.client = Garmin(username, password)
        self.loggInn()#username, password)kghjlk
    
    def loggInn(self):#, username:str, password:str):
        #self.client = Garmin(username, password)
        try:
            self.client.login()
        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
        ) as err:
            print("Error occurred during Garmin Connect Client login: %s" % err)
            quit()
    
    def test(self):
        print(self.client.get_full_name())
    
    def aktiv(self, start=0, limit=1):
        self.aktiviteter = self.client.get_activities(start, limit)
        print(self.aktiviteter)
    

    def puls(self, id:int):
        self.hr_timezones = self.client.get_activity_hr_in_timezones(id)
        print(self.hr_timezones)

if __name__=="__main__":
    G = connect("aune150@gmail.com", "Nelnua34")
    G.aktiv()
    G.puls(G.aktiviteter[0]["activityId"])
