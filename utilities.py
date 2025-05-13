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

def get_date_list(start_date, end_date):
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y%m%d'))  # Convert to 'yyyymmdd' format
        current_date += timedelta(days=1)  # Increment by one day
    return date_list

def get_driver(download_folder, url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run headless if you don't need a GUI
    chrome_options.add_argument("--disable-gpu")
    
    # Set the download directory to a custom folder
    download_dir = os.path.join(os.getcwd(), download_folder) 
    chrome_options.add_experimental_option('prefs', {
        "download.default_directory": download_dir,  # Set download folder
        "download.prompt_for_download": False,  # Disable download prompt
        "download.directory_upgrade": True
    })
    service = Service(executable_path='chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    
    # Open the webpage
    driver.get(url)
    time.sleep(5)
    return driver
## For daily short sale balances with no select button
def download_data(driver, date_str, date_css, query_css, download_css):
    """
    driver: the driver that was created for the specific page (eg. driver.get(...)))
    date_str: The string that represent the date value (eg. 20250505)
    date_css: css_selector for the date field
    query_css: css selector for the search button
    download_css: css selector for the download button
    """
    
    date = driver.find_element(By.CSS_SELECTOR, date_css)
    driver.execute_script(f"arguments[0].setAttribute('value', '{date_str}')", date)
    
    
    ## Querying
    query_button = driver.find_element(By.CSS_SELECTOR, query_css)
    query_button.click()
    time.sleep(5)
    try:
        # Wait up to 10 seconds for the download button to appear
        wait = WebDriverWait(driver, 10)
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, '#reports > div.rwd-tools'))

        download_button = driver.find_element(By.CSS_SELECTOR, download_css)
        download_button.click()
            
    except:
        return

## For Daily Margin Transactions and Balance of Securities Provided as Financing collateral
## with select button
def download_data_select(driver, date_str,select_css, select_option, date_css, query_css, download_css):
    """
    driver: the driver that was created for the specific page (eg. driver.get(...)))
    date_str: The string that represent the date value (eg. 20250505)
    select_css: css selector for the select field
    select_option: the option to be selected for select field
    date_css: css_selector for the date field
    query_css: css selector for the search button
    download_css: css selector for the download button
    """
    
    ## Change date
    date = driver.find_element(By.CSS_SELECTOR, date_css)
    driver.execute_script(f"arguments[0].setAttribute('value', '{date_str}')", date)
    value = date.get_attribute('value')

    # Change select value
    select_element = Select(driver.find_element(By.CSS_SELECTOR, select_css))
    select_element.select_by_visible_text(select_option)
    
    ## Querying
    query_button = driver.find_element(By.CSS_SELECTOR, query_css)
    query_button.click()
    time.sleep(5)
    try:
        # Wait up to 10 seconds for download button to appear
        wait = WebDriverWait(driver, 10)
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, '#reports > div.rwd-tools'))

        download_button = driver.find_element(By.CSS_SELECTOR, download_css)
        download_button.click()
            
    except:
        return


def join_files(folder, file_prefix, start_date, end_date, skip_rows, skip_footer, header):
    """
    folder: (eg. where all the .csv for Daily Margin Transactions are saved)
    file_prefix: each different table (eg. Daily Margin Transactions) have a specific file prefix
    start_date: first date of the data
    end_date: last date of the data
    skip_rows: Number of first rows to skip (these are usually date and name of table that is 
                contained in the csv filed downloaded)
    skip_footer: Number of last rows to skip (Usually remarks from TWSE)
    header: columns names
    """
    # Generate the list of date strings
    date_list = []
    
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1) 

    ## First day
    file_path = f"{folder}/{file_prefix}_{date_list[0].strftime('%Y%m%d')}.csv"
    data = pd.read_csv(file_path,
                       encoding='big5',skiprows=skip_rows,header =header)
    data = data.iloc[:-skip_footer]
    formatted_date = date_list[0].strftime('%Y.%m.%d') # Use YYYY.mm.dd format
    data.insert(0, 'date', formatted_date)

    # Loop through the days, except first one
    current_year = int(formatted_date[:4])
    for date in date_list[1:]:
        date_str = date.strftime('%Y%m%d')
        if date_str[:4] == str(current_year):
            print(current_year)
            current_year += 1
        file_path =  f"{folder}/{file_prefix}_{date_str}.csv"
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path,
                             encoding='big5',skiprows=skip_rows, header =header)
            
                df = df.iloc[:-skip_footer]
                df = df.dropna(how='all')
                if not df.empty:
                    formatted_date = date.strftime('%Y.%m.%d')
                    df.insert(0, 'date', formatted_date)
                    data = pd.concat([data, df])
            except:
                continue
    # Save file
    data.to_csv(f"result/{folder}.csv")
    return data
    