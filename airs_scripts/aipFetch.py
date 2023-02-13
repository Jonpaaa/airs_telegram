import os
import json

def get_eaip_by_alpha_code(alpha_code):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    aip_file = os.path.join(current_directory, 'aip.json')
    with open(aip_file, 'r') as f:
        aip_data = json.load(f)
    for item in aip_data:
        if alpha_code in item:
            return item
