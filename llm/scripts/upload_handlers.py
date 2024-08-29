# llm/scripts/upload_handlers.py

import csv

def handle_text_file(file):
    return file.read().decode('utf-8')

def handle_csv_file(file):
    reader = csv.reader(file.read().decode('utf-8').splitlines())
    return ' '.join([' '.join(row) for row in reader])
