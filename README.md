# ConnectToOlt
Skal lage OLT økter av GarminConnect økter

Garmin API og OLT API skal være delvis fungerende

For å få Garmin API til å fungere må man logge inn på nytt og huke av for å bli husket på denne PC'en. Det er også ofte at denne API ikke fungerer.
Derfor kan det være lurt å ta så mange økter om gangen som mulig.


<h1>Instalasjon:</h1>

<h3>Last ned koden</h3>
Bruk git clone https://github.com/aune150/ConnectToOlt

<h3>Lagre passord og brukernavn</h3>
Lag en creds.json fil med innholdet:
{\n
  "GarminConnect":{
    "password":"PASSORD", 
    "username":"BRUKERNAVN"
    }, 
    "OLT":{
    "password":"PASSORD", 
    "username":"BRUKERNAVN"
    }
}
