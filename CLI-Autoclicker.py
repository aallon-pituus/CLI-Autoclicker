import time, threading, signal, re, os, sys, json, urllib.request
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, Key

# Function to clear the screen
def clear_screen():
    # 'nt' is Windows; 'posix' covers Linux, macOS, Unix
    os.system("cls" if os.name == "nt" else "clear")

# Color code definitions
RED = "\033[31m"
LIGHT_RED = "\033[38;5;9m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
ORANGE = "\033[38;5;208m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
BOLD = "\033[1m"
LIGHT_GREEN = "\033[92m"
LIGHT_MAGENTA = "\033[95m"
RESET = "\033[0m"

# Retrieve variable value if file exists, create new file and add default value if not
if os.path.exists("click_interval.var"):
    with open("click_interval.var", "r") as f:
        click_interval = float(f.read())
else:   
    with open("click_interval.var", "w") as f:
        f.write("0.01")
        click_interval = 0.01

# Retrieve variable value if file exists, create new file and add default value if not
if os.path.exists("key_interval.var"):
    with open("key_interval.var", "r") as f:
        key_interval = float(f.read())
else:   
    with open("key_interval.var", "w") as f:
        f.write("0.01")
        key_interval = 0.01

# Variable definitions 
KI_CONF_KEY = Key.f3
AUTOKEY_KEY = Key.f4
CI_CONF_KEY = Key.f5
AUTOCLICK_KEY = Key.f6
LICENSE_KEY = Key.f7
ESCAPE_KEY = Key.f8
DEBUG_KEY = Key.f9
CLEAR_KEY = Key.f10

# Updater configuration
CURRENT_VERSION = "1.0.2"
GITHUB_USER = "aallon-pituus"
REPO_NAME = "CLI-Autoclicker"

# GitHub API endpoints
LATEST_RELEASE_URL = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/releases/latest"
RAW_SCRIPT_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/CLI-Autoclicker.py"

def check_for_updates():
    # Checks GitHub for a newer version tag and offers to overwrite the script.
    global RESET, GREEN, RED, ORANGE
    print(f"{GREEN}[UPDATER]{RESET} Checking for updates...")
    
    req = urllib.request.Request(
        LATEST_RELEASE_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "").lstrip("v")
                
                if latest_version and latest_version != CURRENT_VERSION:
                    print(f"\n{GREEN}[UPDATER]{RESET} New version available: {GREEN}v{latest_version}{RESET} (Current: {GREEN}v{CURRENT_VERSION}{RESET})")
                    print(f"\n{GREEN}[UPDATER]{RESET} Read the full release notes at: https://github.com/{GITHUB_USER}/{REPO_NAME}/releases/latest")
                    choice = input(f"\n{GREEN}[UPDATER]{RESET} Would you like to update now? (y/n) {ORANGE}>>{RESET} ").strip().lower()
                    
                    if choice == "y":
                        perform_update()
                else:
                    print(f"\n{GREEN}[UPDATER]{RESET} You are running the latest version ({GREEN}v{CURRENT_VERSION}{RESET}).")
                    
    except Exception as e:
        # Tell the user if offline / repo has no releases yet
        print(f"\n{RED}[ERROR]{RESET} Could not check for updates ({e})")

def perform_update():
    # Downloads the latest script and overwrites the active file.
    global RESET, GREEN
    try:
        print(f"\n{GREEN}[UPDATER]{RESET} Downloading update...")
        req = urllib.request.Request(
            RAW_SCRIPT_URL,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            new_code = response.read()

        # Identify current running file path
        current_file_path = os.path.abspath(sys.argv[0])
        
        # Overwrite current file with downloaded code
        with open(current_file_path, "wb") as f:
            f.write(new_code)

        print(f"\n{GREEN}[UPDATER]{RESET} Update complete! Please restart the autoclicker.")
        sys.exit(0)

    except Exception as e:
        print(f"\n{RED}[ERROR]{RESET} Update failed ({e})")

def print_header(): 
    print(rf"""{ORANGE}
        (     (                                                                 
   (    )\ )  )\ )     (               )           (              )             
   )\  (()/( (()/(     )\       (   ( /(           )\ (        ( /(    (   (    
 (((_)  /(_)) /(_)) ((((_)(    ))\  )\()) (    (  ((_))\   (   )\())  ))\  )(   
 )\___ (_))  (_))    )\ _ )\  /((_)(_))/  )\   )\  _ ((_)  )\ ((_)\  /((_)(()\  
((/ __|| |   |_ _|   (_)_\(_)(_))( | |_  ((_) ((_)| | (_) ((_)| |(_)(_))   ((_) 
 | (__ | |__  | |     / _ \  | || ||  _|/ _ \/ _| | | | |/ _| | / / / -_) | '_| 
  \___||____||___|   /_/ \_\  \_,_| \__|\___/\__| |_| |_|\__| |_\_\ \___| |_|   {RESET}
                                                                                   
CLI Autoclicker by {LIGHT_RED}aallon-pituus{RESET} (on Github). Programmed in Python. {GREEN}{BOLD}Version {CURRENT_VERSION}.{RESET} 

Do not manually edit the variable file (click_interval.var) as the program is running.
""")

def print_instructions():
    print(f"""
Use the {BLUE}F3{RESET} key to {BLUE}configure the key interval variable{RESET}.
Use the {YELLOW}F4{RESET} key to {YELLOW}start the automatic key presser{RESET}.
Use the {LIGHT_RED}F5{RESET} key to {LIGHT_RED}configure the click interval variable{RESET}.
Use the {LIGHT_GREEN}F6{RESET} key to {LIGHT_GREEN}start the auto-clicker{RESET}.
Use the {ORANGE}F7{RESET} key to {ORANGE}read the license{RESET}.
Use the {CYAN}F8{RESET} key to {CYAN}close the program{RESET}.
Use the {RED}F9{RESET} key to {RED}show the value of the click interval variable{RESET}.
Use the {LIGHT_MAGENTA}F10{RESET} key to {LIGHT_MAGENTA}clear the REPL{RESET}.
""")

print_header()
check_for_updates()
print_instructions()

clicking = False
auto_pressing = False
keyboard = Controller()
mouse = Controller()

def clicker():
    global click_interval
    while True:
        if clicking:
            mouse.click(Button.left, 1)
        time.sleep(click_interval)

def key_presser():
    global key_interval
    while True:
        if auto_pressing:
            keyboard.press('e')
            keyboard.release('e')
        time.sleep(key_interval)
            

def toggle_event(key):
    global clicking, click_interval, auto_pressing, key_interval
    if key == AUTOKEY_KEY:
        auto_pressing = not auto_pressing
        auto_pressing_string = f"{GREEN}Yes.{RESET}" if clicking else f"{RED}No.{RESET}"
        print(f"{YELLOW}[AUTO PRESSER]{RESET} Automatic key pressing enabled? {auto_pressing_string}")
    if key == KI_CONF_KEY:
        auto_pressing = False
        while True:
            val = input(f"\n{LIGHT_RED}[CONF]{RESET} Enter new key interval (numbers and . only) {ORANGE}>>{RESET} ")
            pattern = r"^\d+(\.\d+)?$"
            if re.match(pattern, val) and float(val) > 0:
                key_interval = float(val)
                break
            print(f"\n{LIGHT_RED}[CONF]{RESET} Invalid input. Try again.")
  
        # Save to file
        with open("key_interval.var", "w") as f:
            f.write(str(key_interval))
        print(f"\n{LIGHT_RED}[CONF]{RESET} Key interval updated to {key_interval}s.\n")

    if key == CI_CONF_KEY:
        clicking = False
        while True:
            val = input(f"\n{LIGHT_RED}[CONF]{RESET} Enter new click interval (numbers and . only) {ORANGE}>>{RESET} ")
            pattern = r"^\d+(\.\d+)?$"
            if re.match(pattern, val) and float(val) > 0:
                click_interval = float(val)
                break
            print(f"\n{LIGHT_RED}[CONF]{RESET} Invalid input. Try again.")

        # Save to file
        with open("click_interval.var", "w") as f:
            f.write(str(click_interval))
        print(f"\n{LIGHT_RED}[CONF]{RESET} Click interval updated to {click_interval}s.\n")

    if key == AUTOCLICK_KEY:
        clicking = not clicking
        clicking_string = f"{GREEN}Yes.{RESET}" if clicking else f"{RED}No.{RESET}"
        print(f"{LIGHT_GREEN}[CLICKER]{RESET} Clicking enabled? {clicking_string}")
    if key == LICENSE_KEY:
            print(rf"""
            {ORANGE}MIT License{RESET}

Copyright (c) 2026 aallon-pituus

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. 
""")
    if key == DEBUG_KEY:
        print(f"\n{RED}[DEBUG]{RESET} Click interval: {click_interval}\n")
    if key == ESCAPE_KEY:
        print(f"\n{CYAN}[INTERRUPT]{RESET} Exiting autoclicker...")
        os.kill(os.getpid(), signal.SIGINT)
    if key == CLEAR_KEY:
        clear_screen()
        print_header()
        print_instructions()

# Start mouse thread
click_thread = threading.Thread(target=clicker, daemon=True)
click_thread.start()

# Start key presser thread
key_thread = threading.Thread(target=key_presser, daemon=True)
key_thread.start()

# Start keyboard listener non-blocking
listener = Listener(on_press=toggle_event)
listener.start()

# Keep main thread responsive to Ctrl+C signal
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print(f"\n{CYAN}[INTERRUPT]{RESET} Exiting autoclicker...")
