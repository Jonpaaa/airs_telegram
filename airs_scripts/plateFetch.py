import os

def get_pdf_path(plate_code: str) -> str:
    path = os.path.join(os.path.dirname(__file__), 'ad')
    for file_name in os.listdir(path):
        if file_name.endswith('.pdf') and file_name.startswith(plate_code):
            print(os.path.join(path, file_name))
            return os.path.join(path, file_name)
            
    return None
