import requests
import json
from config import NOTAM_TOKEN

def notam(FIR):
    region = FIR.upper()
    url = f'https://external-api.faa.gov/notamapi/v1/notams?responseFormat=geoJson&icaoLocation={region}'
    headers = {'client_id': '56cd677b07b74045b0e0906a99bc7105','client_secret': NOTAM_TOKEN}

    req_notam = requests.get(url, headers=headers)

    try:
        req_notam.raise_for_status()
        
        resp_notam = req_notam.text
        respJSON = json.loads(resp_notam)

        formatted_notam_json = json.dumps(respJSON, indent=4, separators=(',', ': '))

        # Add newline after each curly brace
        NOTAM = formatted_notam_json.replace('}', '}\n')

        with open("notam.json", "w") as f:
            f.write(NOTAM)

        items = respJSON.get("items", [])
        notam_strings = []
        for item in items:
            properties = item.get("properties", {})
            core_notam_data = properties.get("coreNOTAMData", {})
            notam_translation = core_notam_data.get("notamTranslation", [])
            for translation in notam_translation:
                formatted_text = translation.get("formattedText", "")
                notam_strings.append(formatted_text)
        
        NOTAM = '\n'.join(notam_strings)

    except requests.exceptions.HTTPError as e:
        print(e)
    
    return NOTAM

