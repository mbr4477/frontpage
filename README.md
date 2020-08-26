# The Frontpage
The Frontpage is a Python script to download front pages of newspapers from [Newseum](http://newseum.org/). Fortunately, the pages follow an easy URL pattern: `https://cdn.newseum.org/dfp/pdf{dom}/{newspaper}.pdf` where `{dom}` is the day of the month (no leading zero), and `{newspaper}` is the key of the newspaper you want to retrieve. For example, to receive the Washington Post frontpage from the most recent 20th day of the month use https://cdn.newseum.org/dfp/pdf20/DC_WP.pdf.

## Basic Setup
This setup is designed for the Raspberry Pi. Everything should work in a similar fashion for other *nix systems. (No guarantees for Windows users. Good luck.)

1. Install CUPS to manage printers: `sudo apt-get install cups` then `sudo usermod -a -G lpadmin pi` (make sure to use the correct username if it isn't `pi`)
2. Use `lpinfo -v` to find your printer URI
3. Setup the printer with `lpadmin -p home_printer -E -v <URI> -m everywhere`. Here I'm calling the printer `home_printer`. Remember this name! 
4. Install `mutool` to split large front pages into two pages: `sudo apt-get install mupdf-tool`
5. Install `cpdf` to remove images before printing
    ```bash
    $ sudo apt-get install opam
    $ opam init
    $ eval $(opam env)
    $ opam install camlpdf
    $ opam install cpdf
    # you may also need to `add eval $(opam env)` to your ~/.bashrc file,
    # although `opam init` should be able to handle this automatically
    ```
6. Create a `frontpage.json` file with configuration details (you can actually name this file whatever you want):
    ```json
    {
        "sources": [
            "DC_WP",
            "NY_NYT",
            "KY_LHL",
            "WSJ"
        ],
        "print": "$RANDOM",
        "printer": "home_printer"
    }
    ```
    The `sources` list contains the list of newspaper keys. To find these, search for papers at https://www.newseum.org/todaysfrontpages/, and click the "PDF" link on the detail page. Check the URL for the key. Add one of the keys to the `print` property to pick which one to print out, or use `$RANDOM` to randomly select a paper to print.
7. Initialize the Python virtual environment
    ```bash
    $ python3 -m venv .venv
    $ .venv/bin/python -m pip install -r requirements.txt
    ```
8. Run the script! `$ .venv/bin/python -m frontpage frontpage.json`. Add the `--no-print` switch to prevent any printing.

## Uploading PDFs to Dropbox
1. Go to https://www.dropbox.com/developers and create a new app
2. Configure the settings so you app has access to a scoped app folder (instead of your whole Dropbox)
3. In the "Permissions" tab of the new app, check the `files.content.write` box so you will be able to upload files
4. Back in the main "Settings" tab, change the access token type to "No expiration" and click "Generate" to get an access token. **Save this token!**
5. Create a `token.json` file that includes this generated token:
    ```json
    {
        "dropbox": "API_TOKEN"
    }
    ```
6. Run using `$ .venv/bin/python -m frontpage frontpage.json --token token.json`

## Schedule Weekday Delivery
We can use `cron` to schedule the script on weekday mornings.
1. Run `$ crontab -e` to edit the table of jobs. Pick `nano` as the editor if prompted.
2. Add this line to the editor (assuming you cloned this repo into your home directory):
```cron
0 6 * * 1-5 . /home/pi/.profile && cd /home/pi/frontpage && .venv/bin/python -m frontpage frontpage.json --token token.json
```
This will schedule the job to run Mon-Fri at 6 AM. Check on the Wikipedia page on `cron` for more info about the table entries. We need to add `. /home/pi/.profile` as the first command to make sure we have access to the environment variables we need.

> Make sure your system time is correct! You can check/edit it with `timedatectl`. You may need to restart after changing the time in order to reset system logging and `cron`.