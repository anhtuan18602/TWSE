from datetime import datetime
import time
import pandas as pd
from utilities import *
    
if __name__ == "__main__": 
    ## Note that there might be changes in the data formatting downloaded from TWSE. 
    ## It's best to download the data, join files, then see if the resulting df 
    ## requires formatting

    ### ---- Download Code ----
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

    ## ---- Joining files ----
    folder = "Daily Short Sale Balances"
    file_prefix = "TWT93U"
    skip_rows = 1
    skip_footer = 8
    header = [0,1]
    df = join_files(folder, file_prefix, start_date, end_date, skip_rows, skip_footer, header)
        
    ### The dataframe may have extra columns as a result of TWSE weird formatting (there might be 
    ### some duplicate columns). The formatting below is to merge these columns.
    ### This formatting step will aslo handle flattening the multilevel headers, dropping NA columns


    ## ---- Merging similar columns ----
    # Find the index of the 'SBL Short Sales' column
    sbl_short_sales_idx = df.columns.get_loc(('SBL Short Sales', 'Previous Day Balance'))
    
    # Split into two DataFrames: one before 'SBL Short Sales' and one after
    df_before_sbl = df.iloc[:, :sbl_short_sales_idx + 1]
    df_after_sbl = df.iloc[:, sbl_short_sales_idx + 1:]
    
    # List to hold merged columns
    merged_columns = []
    
    # Iterate over unique level 1 labels after 'SBL Short Sales'
    for level_1_label in df_after_sbl.columns.get_level_values(1).unique():
        # Select all columns with the same level 1 label
        matching_columns = df_after_sbl.loc[:, 
            df_after_sbl.columns.get_level_values(1) == level_1_label]
        
        if len(matching_columns.columns) > 1:
            # If we have more than one column with the same level 1 label, merge them
            col1, col2 = matching_columns.columns
            
            # Merge the columns by filling NaN values with the values from the other column
            merged_column = matching_columns[col1].fillna(matching_columns[col2])
            
            # Create the merged column with the correct multi-level header
            new_column_name = (matching_columns.columns[0][0], level_1_label)
            
            # Add the merged column to the list of merged columns
            merged_columns.append((new_column_name, merged_column))
    
            # Drop the original columns from df_after_sbl (after merging)
            df_after_sbl = df_after_sbl.drop(matching_columns.columns, axis=1)
        else:
            # If the column doesn't belong to a pair, keep it as is (no merging)
            merged_columns.append((matching_columns.columns[0],
                                   df_after_sbl[matching_columns.columns[0]]))
    
    # Rebuild df_after_sbl with merged columns and non-paired columns
    for column_name, merged_column in merged_columns:
        df_after_sbl[column_name] = merged_column
            
    # Combine the before and after DataFrames
    df_merged = pd.concat([df_before_sbl, df_after_sbl], axis=1)
            
    # Drop NA columns
    df_merged = df_merged.dropna(axis=1,how='all')

    ## ---- Flattening headers  ----
    cols = df_merged.columns

    # New list to hold updated column tuples
    new_cols = []
    
    # Track current top-level category
    current_prefix = None
    
    for level0, level1 in cols:
        if level0 == 'Margin Short Sales':
            current_prefix = 'Margin'
        elif level0 == 'SBL Short Sales':
            current_prefix = 'SBL'
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
    
    
    df_merged.columns = pd.MultiIndex.from_tuples(new_cols)
    df_merged.columns = df_merged.columns.get_level_values(1)
    df_merged = df_merged.dropna(subset=['Security Code'])
    df_merged = df_merged[df_merged['Security Code']!="Remarks:"]
    ## ---- This is dependent on the resulting df_merged, better check first ----
    df_merged = df_merged.rename(columns={"Unnamed: 1_level_1":"Date"})
    df_merged = df_merged.rename(columns={"Unnamed: 0_level_1":"Index"})

    ## Clean security codes that look like ="0050". This format appears when I was
    ## downloading the data from TWSE, but now it seems to have been fixed
    df_merged['Security Code'] = df_merged['Security Code'].apply(clean_security)
    
    os.makedirs("formatted_result",exist_ok=True)
    df_merged.to_csv(f"formatted_result/{folder}.csv",index=False)