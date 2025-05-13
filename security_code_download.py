from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import Select
import pandas as pd
import os
import time

def get_securities():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run headless if you don't need a GUI
    chrome_options.add_argument("--disable-gpu")
    
    # Set the download directory to a custom folder
    download_dir = os.path.join(os.getcwd(), 'temp') 
    chrome_options.add_experimental_option('prefs', {
        "download.default_directory": download_dir,  # Set download folder
        "download.prompt_for_download": False,  # Disable download prompt
        "download.directory_upgrade": True
    })
    service = Service(executable_path='chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    #url = 'https://isin.twse.com.tw/isin/e_single_main.jsp?'
    # This htm page was downloaded, the original page was loaded from
    # https://isin.twse.com.tw/isin/e_single_main.jsp?
    file_path = "all_codes.htm"
    url = f"file:///{os.path.abspath(file_path)}"
    
    
    driver.get(url)
    
    # Find the table element
    table = driver.find_element(By.XPATH, "/html/body/table[2]")
    
    # Extract table headers 
    rows = table.find_elements(By.XPATH, "./tbody/tr")
    headers = [header.text for header in rows[0].find_elements(By.XPATH, ".//td")]
    
    # Extract table rows
    rows = rows[1:]  # Skip the header row
    
    # Extract data from each row and each cell
    data = []
    for row in rows:
        cells = row.find_elements(By.XPATH, ".//td")
        data.append([cell.text for cell in cells])
    
    df = pd.DataFrame(data, columns=headers)
    
    df.to_csv("result/Security Code.csv")

    driver.quit()
    return df

if __name__ == "__main__":
    df = get_securities()