import requests
import json
from config import WX_TOKEN
hdr = WX_TOKEN

def wx(AD):
    icao = AD
    ICAO = icao.upper()
    req_metar = requests.get(f"https://api.checkwx.com/metar/{ICAO}", headers=hdr)
    req_taf = requests.get(f"https://api.checkwx.com/taf/{ICAO}", headers=hdr)

    try:
        req_metar.raise_for_status()
        req_taf.raise_for_status()
        
        resp_metar = req_metar.text
        metarJSON = json.loads(resp_metar)

        resp_taf = req_taf.text
        tafJSON = json.loads(resp_taf)


        print(json.dumps(resp_metar, indent=1))
        print(json.dumps(resp_taf, indent=1))

        #Converting to string
        metar = metarJSON['data'][0]
        taf = tafJSON['data'][0]
        
        METAR = str (metar)
        TAF = str (taf)


    except requests.exceptions.HTTPError as e:
        print(e)
    
    return METAR, TAF