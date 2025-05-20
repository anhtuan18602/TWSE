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
    df = join_files(folder, file_prefix, start_date, end_date, skip_rows, skip_footer, header)
    df

    df = df.dropna(axis=1,how='all')

    ## ---- Flattening headers  ----
    cols = df.columns
    
    # New list to hold updated column tuples
    new_cols = []
    
    # Track current top-level category
    current_prefix = None
    
    for level0, level1 in cols:
        if level0 == 'Margin Purchase':
            current_prefix = 'MP'
        elif level0 == 'Securities Business Money Lending by Securities Firms':
            current_prefix = 'SBMLSF'
        elif level0 == 'Securities Firms Handling Non-Restricted Purpose Loan':
            current_prefix = 'SFHNPL'
        elif level0 == 'Securities Finance Business Handling Securities Secured Loan':
            current_prefix = 'SFBHSSL'
        elif level0 == 'Securities Finance Business Handling Securities Settlement Loan':
            current_prefix = 'SFBHSSL1'
        elif level0.startswith('Unnamed') and current_prefix:
            # Carry forward prefix for following unnamed level0 entries
            pass
        else:
            current_prefix = None  # Reset when a new section starts
    
        # Apply renaming if under Margin or SBL
        if current_prefix:
            new_level1 = f'{current_prefix}_{level1}'
            new_cols.append((level0, new_level1))
        else:
            new_cols.append((level0, level1))
    
    df.columns = pd.MultiIndex.from_tuples(new_cols)
    df.columns = df.columns.get_level_values(1)
    df = df.rename(columns={"SFBHSSL1_Market ID.":"Market ID.","SFBHSSL1_Note":"Note"})
    
    df = df.dropna(subset=['Security Code'])
    df = df[df['Security Code']!="Remarks:"]
    ## ---- This is dependent on the resulting df_merged, better check first ----
    df = df.rename(columns={"Unnamed: 1_level_1":"Date"})
    df = df.rename(columns={"Unnamed: 0_level_1":"Index"})
    df['Security Code'] = df['Security Code'].apply(clean_security)
    os.makedirs("formatted_result",exist_ok=True)
    df.to_csv(f"formatted_result/Balance of Securities Provided as Financing Collateral.csv",index=False)
    df