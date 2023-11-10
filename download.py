import configparser
import time
import requests
import tkinter as tk
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


_login_url = 'https://www.empatica.com/connect/login.php'
_save_path = "G:\\e4CLI\\yr2022"
chromeDriverPath ="./chromedriver.exe"
html_file_path = "G:\\sessions.html"#"G:\e4-client-master\e4-client-master\e4.empatica.com_connect_connect.php_users_25383_sessions_from=0&to=999999999999.html"

def filter_and_slice_logs(html_file_path, device_id=None, start_time=None, end_time=None):
    # Read the HTML file
    with open(html_file_path, "r") as html_file:
        html_content = html_file.read()

    # Parse HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract JSON data
    json_str = soup.body.string
    entries = json.loads(json_str)

    # Filter by device_id
    if device_id:
        entries = [entry for entry in entries if entry.get('device_id') == device_id]

    # Convert start_time and end_time to integers
    if start_time:
        start_time = int(start_time)
    if end_time:
        end_time = int(end_time)

    # Filter by start_time and end_time
    if start_time:
        entries = [entry for entry in entries if int(entry.get('start_time', 0)) >= start_time]

    if end_time:
        entries = [entry for entry in entries if int(entry.get('start_time', float('inf'))) <= end_time]

    # Extract IDs as a list of integers
    ids = [int(entry['id']) for entry in entries]

    return ids



def read_config(filename='config.ini'):
    config = configparser.ConfigParser()
    config.read(filename)

    user = config.get('e4_client', 'user')
    pwd = config.get('e4_client', 'pwd')

    return user, pwd


def login(username,password):
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {"download.default_directory": _save_path,
                                                     "download.prompt_for_download": False,
                                                     "download.directory_upgrade": True,
                                                     "safebrowsing.enabled": True
                                                     })
    chrome_options.add_argument("--disable-popup-blocking")
    driver = webdriver.Chrome( executable_path=chromeDriverPath,chrome_options=chrome_options)
    driver.get('https://www.empatica.com/connect/login.php')

    usernameBox = driver.find_element_by_name("username")
    usernameBox.send_keys(username)
    passwordBox = driver.find_element_by_name("password")
    passwordBox.send_keys(password)
    passwordBox.send_keys(Keys.ENTER)
    time.sleep(3)
    return driver


def download_file(driver, download_url):
    # 打开URL
    driver.get(download_url)
    # wait until download is done
    time.sleep(3)


def download_files_for_sid(driver, sid):
    # Construct the download URL for the given sid
    download_url = f'https://e4.empatica.com/connect/download.php?id={sid}'

    # Download file for the given sid
    download_file(driver, download_url)
    driver.implicitly_wait(10)

def perform_actions(start_timestamp,end_timestamp):
    # main
    root = tk.Tk()
    root.title("Selenium")
    # load url,buttons
    tk.Label(root, text="downloac URL：").pack(pady=5)
    entry_download_url = tk.Entry(root)
    entry_download_url.pack(pady=5)

    # get download url
    download_url = entry_download_url.get()

    # get uname and pw
    username, password = read_config()

    # login remember pw

    driver = login(username, password)

    # List of sid values
    sid_list = filter_and_slice_logs(html_file_path, device_id=None, start_time=start_timestamp, end_time=end_timestamp)

    # Download files for each sid
    for sid in sid_list:
        download_files_for_sid(driver, sid)
    # close browser page
    #driver.quit()




if __name__=="__main__":
    #filtered_ids = filter_and_slice_logs(html_file_path, device_id="1dc911", start_time=None, end_time=None)
    #print("Filtered and sliced IDs:", filtered_ids)
    # run GUI
    st=1609459200
    ed = 1672531199
    perform_actions(st,ed)


