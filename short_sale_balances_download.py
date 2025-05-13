from datetime import datetime
import time
import pandas as pd
from utilities import *
    
if __name__ == "__main__":  
    # Starting and ending dates
    start_date = datetime(2005, 7, 1)
    end_date = datetime(2025, 5, 5)

    
    # Generate the list of date strings
    date_list = get_date_list(start_date, end_date)

    url = 'https://www.twse.com.tw/en/trading/margin/twt93u.html'
    driver = get_driver('Daily Short Sale Balances',url)

    ## parameters for download data
    date_css = '#form > div > div.group.date-select.D > input[type=hidden]'
    query_css = '#form > div > button'
    download_css = '#reports > div.rwd-tools > button.csv'
    
    current_year = int(date_list[0][:4])
    ## Loop through the dates
    for date_str in date_list:
        if date_str[:4] == str(current_year):
            print(current_year)
            current_year += 1
        download_data(driver, date_str, date_css, query_css, download_css)
    time.sleep(10)
    driver.quit()

    ## Joining files
    folder = "Daily Short Sale Balances"
    file_prefix = "TWT93U"
    skip_rows = 1
    skip_footer = 8
    header = [0,1]
    data = join_files(folder, file_prefix, start_date, end_date, skip_rows, skip_footer, header)