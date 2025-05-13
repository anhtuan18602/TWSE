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



def parse_table(rows):
    table_data = []
    row_spans = {}  # (row_idx, col_idx) -> (value, remaining_span)

    for row_idx, row in enumerate(rows):
        cols = row.find_elements(By.XPATH, "./th|./td")
        row_data = []
        col_idx = 0

        while col_idx < len(cols) or (row_idx, col_idx) in row_spans:
            # Handle ongoing rowspan from previous rows
            if (row_idx, col_idx) in row_spans:
                val, span = row_spans[(row_idx, col_idx)]
                row_data.append(val)
                if span > 1:
                    row_spans[(row_idx+1, col_idx)] = (val, span - 1)
                del row_spans[(row_idx, col_idx)]
                col_idx += 1
                continue

            # Handle current cell
            if col_idx < len(cols):
                cell = cols[col_idx]
                cell_text = cell.text.strip()
                rowspan = int(cell.get_attribute("rowspan") or 1)
                colspan = int(cell.get_attribute("colspan") or 1)

                for i in range(colspan):
                    row_data.append(cell_text)
                    if rowspan > 1:
                        row_spans[(row_idx+1, col_idx)] = (cell_text, rowspan - 1)
                    col_idx += 1
            else:
                row_data.append("")
                col_idx += 1

        table_data.append(row_data)
    return table_data


if __name__ == "__main__":
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run headless if you don't need a GUI
    chrome_options.add_argument("--disable-gpu")
    # Download chromedriver.exe from Google
    service = Service(executable_path='chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Link to Adjustment of Margin Purchase Leverage Ratio and Short Sale Margin
    driver.get("https://www.twse.com.tw/en/trading/margin/bfib9u.html")
    
    ## Modify start date and end date to 2014.04.18 - 2025.05.05
    start_date = driver.find_element(By.CSS_SELECTOR, "input[name='startDate']")
    end_date = driver.find_element(By.CSS_SELECTOR,"input[name='endDate']")
    driver.execute_script(f"arguments[0].setAttribute('value', '{20140418}')", start_date)
    driver.execute_script(f"arguments[0].setAttribute('value', '{20250505}')", end_date)
    
    #Modify the reason for Adjustment to All
    select_element = Select(driver.find_element(By.CSS_SELECTOR, 'select[name="selectType"]'))
    select_element.select_by_visible_text("All")
    
    #Find and press the query button
    query_button = driver.find_element(By.CSS_SELECTOR, "#form > div > div.groups > div.submit > button")
    query_button.click()

    #Wait for page to load
    time.sleep(10)


    #Get table
    table = driver.find_element(By.XPATH, '//*[@id="reports"]/div[1]/div[2]/table')

    #Get header
    headers = [th.text.strip() for th in table.find_elements(By.XPATH, ".//thead/tr/th")]
    
    
    data = []

    #Check for total number of pages
    last_a_text = driver.find_element(By.XPATH, 
        '//*[@id="reports"]/div[1]/div[3]/ul/li[last()-1]/a').text.strip()
    last_page = int(last_a_text)
    i = 1

    #Loop through the pages and gather data
    while i <= last_page:
        print(f"page {i}")
        table = driver.find_element(By.XPATH, '//*[@id="reports"]/div[1]/div[2]/table')
        rows = table.find_elements(By.XPATH, ".//tbody/tr")   
        data.extend(parse_table(rows))
        if i != last_page:
            next_page_a = driver.find_element(By.CSS_SELECTOR, 
                'a.page-link.next')
            next_page_a.click()
            time.sleep(5)
        i += 1
    
    
    df = pd.DataFrame(data,columns = headers)
    
    df_clean= df[~((df['Effective Date of Adjustment'] == '') 
                   & (df['Effective Date of Resumption'] == ''))]
    df_clean.to_csv("Adjustment of Margin Purchase Leverage Ratio and Short Sale Margin.csv",
                    index=False)
    
    
    driver.quit()
