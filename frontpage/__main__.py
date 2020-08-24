import argparse
import json
from subprocess import run
import os
import glob
import dropbox
import datetime
import random

def print_file(filename, printer_name):
    # print this file
    run(['mutool', 'poster', '-y', '2', filename, 'out.pdf'])
    run(['cpdf', 'out.pdf', '-draft', '-boxes', '-o', 'out.pdf'])
    run([
        'lp', '-d', printer_name, 
        '-o', 'fit-to-page', 
        '-o', 'sides=two-sided-long-edge', 
        '-o', 'orientation-requested=4', 
        'out.pdf'])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", type=str, help="path to sources JSON file with links to PDFs")
    parser.add_argument("--token", type=str, help="path to API token JSON file")
    parser.add_argument("--no-print", action='store_true', default=False, help="prevents print (overrides setting from config file")
    args = parser.parse_args()

    if args.token:
        with open(args.token, "r") as token_file:
            token = json.loads(token_file.read())['dropbox']

        dbx = dropbox.Dropbox(token)

    with open(args.config_file, "r") as config_file:
        config = json.loads(config_file.read())
        print_key = config['print']
        printer_name = config['printer']
        sources = config['sources']


    existing = glob.glob("*.pdf")
    for file in existing:
        os.remove(file)

    for page_key in sources:
        url = f"https://cdn.newseum.org/dfp/pdf{str(datetime.datetime.today().day)}/{page_key}.pdf"
        run(['wget', '-q', url])

    existing = glob.glob("*.pdf")
    if print_key == "$RANDOM" and not args.no_print:
        print_file(random.choice(existing), printer_name)

    for file in existing:
        if print_key and print_key != "$RANDOM" and file.startswith(print_key) and not args.no_print:
            print_file(file, printer_name)
        if args.token:
            with open(file, "rb") as pdf_file:
                dbx.files_upload(pdf_file.read(), f'/{file}', dropbox.files.WriteMode.overwrite)

if __name__ == "__main__":
    main()
    
