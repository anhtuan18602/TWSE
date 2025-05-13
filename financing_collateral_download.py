from datetime import datetime
import time
import pandas as pd
from utilities import *

if __name__ == "__main__": 
    start_date = datetime(2006, 10, 2)
    end_date = datetime(2025, 5, 5)

    
    # Generate the list of date strings
    date_list = get_date_list(start_date, end_date)
    
    
    #print(date_list[0],date_list[-1])
    
    # Balance of Securities Provided as Financing collateral
    url = 'https://www.twse.com.tw/en/trading/margin/twta1u.html'
    download_folder = 'Balance of Securities Provided as Financing Collateral'

    #start driver
    driver = get_driver(download_folder, url)

    # parameters for download function
    select_css = 'select[name="selectType"]'
    select_option = "Listed Stocks (Eligible for Margin Trading)"
    date_css = '#form > div > div.groups > div.group.date-select.D > input[type=hidden]'
    query_css = '#form > div > div.groups > div.submit > button'
    download_css = '#reports > div.rwd-tools > button.csv'
    
    current_year = int(date_list[0][:4])
    for date_str in date_list:
        if date_str[:4] == str(current_year):
            print(current_year)
            current_year += 1
        download_data_select(driver, date_str, select_css, select_option, date_css, query_css,
                             download_css)
    time.sleep(10)
    driver.quit()

    ## Joining files
    folder = "Balance of Securities Provided as Financing Collateral"
    file_prefix = "TWTA1U_X"
    
    skip_rows = 1
    skip_footer = 4
    header = [0,1]
    data = join_files(folder, file_prefix, start_date, end_date, skip_rows, skip_footer, header)
    data