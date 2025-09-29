# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 17:54:50 2025

@author: jmitchell
"""

import pandas as pd
import openpyxl
import matplotlib.pyplot as plt; plt.close('all')
plt.rcParams.update(plt.rcParamsDefault)
plt.rcParams.update({'font.size': plt.rcParams['font.size'] * 1.25})
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import math

def format_dataframe_month_yield(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format 'Month' and 'Yield' columns in a DataFrame.
    Converts 'Month' to the middle of the month (15th) and 'Yield' to float.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing 'Month' as strings (e.g., 'August 2025') and 
        'Yield' as percentage strings (e.g., '100.0%').

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame with 'Month' as datetime (15th of each month) and 'Yield' as float.
    """
    # Convert 'Month' to datetime and shift to 15th
    df['Month'] = pd.to_datetime(df['Month'], format='%B %Y') + pd.DateOffset(days=14)

    # Convert 'Yield' from percentage string to float
    df['Yield'] = df['Yield'].str.rstrip('%').astype(float)

    # Sort by month
    df = df.sort_values('Month').reset_index(drop=True)

    return df

def filter_test(df: pd.DataFrame, search_string: str, delete_string=None, product_id=None) -> pd.DataFrame:
    """
    Filter rows in a DataFrame where 'Process' column contains a given substring.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing a 'Process' column with string entries.
    search_string : str
        Substring to search for within the 'Process' column.
    delete_string : str
        Substring to search for within the 'Process' column and should not include.

    Returns
    -------
    pandas.DataFrame
        Filtered DataFrame containing only rows where 'Process' includes the search string.
    """
    if product_id != None:
        df = df[df['Product'].str.contains(product_id, case=False, na=False)]
    if delete_string != None:
        df = df[~df['Process'].str.contains(delete_string, case=False, na=False)]
    filtered_df = df[df['Process'].str.contains(search_string, case=False, na=False)]
    return filtered_df

def summarize_and_replace(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    Summarize the first `n` rows of a DataFrame and replace them with a single summary row.
    The summary row inherits all column values from the `n`th entry, except for:
    - 'Month': kept from the `n`th entry
    - 'Units': summed over first `n` rows
    - 'Passed': summed over first `n` rows
    - 'Failed': summed over first `n` rows
    - 'Yield': calculated as Passed / Units

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing at least the following columns:
        'Month' (datetime-like), 'Units' (int or float), 
        'Passed' (int), 'Failed' (int), 'Yield' (float).
    n : int
        Number of initial rows to summarize.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame with the first `n` rows replaced by a single summary row.
    """
    if (n > len(df)) or (len(df) < 1):
        print("Requested summary length exceeds DataFrame size.")
        return df.copy()
    
    else:

        # Copy the nth row to preserve other column values
        base_row = df.iloc[n - 1].copy()
    
        # Update summary fields
        base_row['Month'] = df.iloc[n - 1]['Month']
        base_row['Units'] = df.iloc[:n]['Units'].sum()
        base_row['Passed'] = df.iloc[:n]['Passed'].sum()
        base_row['Failed'] = df.iloc[:n]['Failed'].sum()
        base_row['Yield'] = 100.0 * base_row['Passed'] / base_row['Units']
    
        # Create new DataFrame with summary row and remaining rows
        summary_df = pd.DataFrame([base_row])
        summarized_df = pd.concat([summary_df, df.iloc[n:]], ignore_index=True)
    
        return summarized_df

def merge_and_sum(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    For each 'Month' in df1, find matching entry in df2 and sum 'Units', 'Passed', and 'Failed'.

    Parameters
    ----------
    df1 : pandas.DataFrame
        Primary DataFrame with 'Month', 'Units', 'Passed', and 'Failed' columns.
    df2 : pandas.DataFrame
        Secondary DataFrame with the same structure to merge and sum from.

    Returns
    -------
    pandas.DataFrame
        New DataFrame with updated 'Units', 'Passed', and 'Failed' values where matches exist.
    """
    # Make a copy to avoid modifying original df1
    result_df = df1.copy()

    # Ensure 'Month' is datetime in both
    result_df['Month'] = pd.to_datetime(result_df['Month'])
    df2['Month'] = pd.to_datetime(df2['Month'])

    # Set 'Month' as index for fast lookup
    df2_indexed = df2.set_index('Month')

    # Iterate and update
    for idx, row in result_df.iterrows():
        month = row['Month']
        if month in df2_indexed.index:
            match = df2_indexed.loc[month]
            result_df.at[idx, 'Units'] += 0
            result_df.at[idx, 'Passed'] += match['Passed']
            result_df.at[idx, 'Failed'] += match['Failed']

    return result_df

# load in data
ftp = pd.read_excel(r"C:\Users\jmitchell\OneDrive - ALL.SPACE\RF Testing\5 Laboratory\Sanmina\Yields\FPY - April thru Sept.xlsx")
stp = pd.read_excel(r"C:\Users\jmitchell\OneDrive - ALL.SPACE\RF Testing\5 Laboratory\Sanmina\Yields\SPY - April through Sept.xlsx")
# ftp = pd.read_excel(r"C:\Users\jmitchell\OneDrive - ALL.SPACE\RF Testing\5 Laboratory\Sanmina\Yields\Data by week - April through Sept 14.xlsx")
# stp = pd.read_excel(r"C:\Users\jmitchell\OneDrive - ALL.SPACE\RF Testing\5 Laboratory\Sanmina\Yields\Second pass data - April through Sept 14.xlsx")

# format the dates and yields
ftp = format_dataframe_month_yield(ftp)
stp = format_dataframe_month_yield(stp)

## prepare and collate

for product in ['tx_tlm']:#, 'rx_tlm', 'pcs_jig', 'lower_housing', 'blind_mate_fan']:

    if product == 'rx_tlm':
        search_string = 'Rx TLM CAL'
        product_id = 'LFALL'
        delete_string = 'Fail'
        n_start = 2
        n_ftp = -2
        
    if product == 'tx_tlm':
        search_string = 'Tx TLM CAL'
        product_id = 'LFALL420-0345'
        delete_string = 'Fail'
        n_start = 2
        n_ftp = -2
        
    if product == 'pcs_jig':
        search_string = 'PCS RF Test'
        product_id = 'LFALL420-0361'
        delete_string = 'Fail'
        n_start = 2
        n_ftp = -2

    if product == 'lower_housing':
        search_string = 'LowerHouseFCT'
        product_id = 'LFALL440-0388'
        delete_string = 'Fail'
        n_start = 0
        n_ftp = -10
        
    if product == 'blind_mate_fan':
        search_string = 'Fan'
        product_id = None
        delete_string = 'Fail'
        n_start = 0
        n_ftp = -10

    # filter component
    ftp_filtered = filter_test(ftp, search_string, product_id=product_id, delete_string=delete_string)
    stp_filtered = filter_test(stp, search_string, product_id=product_id, delete_string=delete_string)

    # summarise collumns at the begining
    if n_start > 0:
        ftp_filtered = summarize_and_replace(ftp_filtered, n_start)
        stp_filtered = summarize_and_replace(stp_filtered, n_start)

    
    # yield
    yld = merge_and_sum(ftp_filtered, stp_filtered)
    yld_cumulative = yld.copy()
    yld_cumulative['Units'] = yld_cumulative['Units'].cumsum()
    yld_cumulative['Passed'] = yld_cumulative['Passed'].cumsum()
    yld_cumulative['Failed'] = yld_cumulative['Failed'].cumsum()
    yld_cumulative['Yield'] = 100.0 * yld_cumulative['Passed'] / yld_cumulative['Units']
    yld['Yield'] = 100.0 * yld['Passed'] / yld['Units']
    
    # rolling ftp
    ftp_filtered_cumulative = ftp_filtered.copy()
    ftp_filtered_cumulative['Units'] = ftp_filtered_cumulative['Units'].cumsum()
    ftp_filtered_cumulative['Passed'] = ftp_filtered_cumulative['Passed'].cumsum()
    ftp_filtered_cumulative['Failed'] = ftp_filtered_cumulative['Failed'].cumsum()
    ftp_filtered_cumulative['Yield'] = 100.0 * ftp_filtered_cumulative['Passed'] / ftp_filtered_cumulative['Units']
    
    # predictions
    max_predict = {
        'Month': ['August 2025', 'September 2025', 'October 2025'],
        'Yield': [71.5, 75, 86],
        'Description': ['V1.1', '9', '9']
    }
    max_predict = pd.DataFrame(max_predict)
    max_predict['Month'] = pd.to_datetime(max_predict['Month'], format='%B %Y') + pd.DateOffset(days=30)
    
    ## plot
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Set background color
    ax.set_facecolor('navy')
    
    # Add grid
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='white')
    
    # Ticks inside
    ax.tick_params(axis='both', which='major', direction='in', length=7, color='white')
    ax.tick_params(axis='both', which='minor', direction='in', length=4, color='white')
    
    # Format x-axis for monthly ticks
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%B %Y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=15))  # Optional: mid-month minor ticks
    
    # Set y-axis ticks: major every 10, minor every 5
    ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))
    
    # Set limits
    ax.set_xlim(pd.to_datetime('May 2025'), pd.to_datetime('January 2026')-pd.DateOffset(days=1))
    ax.set_ylim(0, 100)
    
    # Optional: rotate x-axis labels for readability
    plt.xticks(rotation=45)
    
    # axis labels
    ax.set_xlabel('Date')
    ax.set_ylabel('%')
    
    # data
    ax.plot(ftp_filtered_cumulative['Month'], ftp_filtered_cumulative['Yield'], 'ms-', linewidth=5, markersize=15, markeredgecolor='black', label = 'Cumulative FPY', alpha=0.75)
    ax.plot(ftp_filtered['Month'][n_ftp:], ftp_filtered['Yield'][n_ftp:], 'mo--', linewidth=3, markersize=10, markeredgecolor='black', label = 'Monthly FPY', alpha=0.75)
    
    if product == 'tx_tlm':
        ax.plot(max_predict['Month'], max_predict['Yield'], 'gX--', linewidth=3, markersize=10, markeredgecolor='black', label = 'Yield improvement forcast', alpha=0.75)
    if product == 'rx_tlm':
        ax.plot([pd.to_datetime('2025-10-14'), pd.to_datetime('2025-11-14'), pd.to_datetime('2025-12-25')], [82, 88, 93], 'gX--', linewidth=3, markersize=10, markeredgecolor='black', label = 'Yield improvement forcast', alpha=0.75)
    if product == 'pcs_jig':
        ax.plot([pd.to_datetime('2025-09-14'), pd.to_datetime('2025-10-14'), pd.to_datetime('2025-11-14'), pd.to_datetime('2025-12-14')], [50, 65, 76, 83], 'gX--', linewidth=3, markersize=10, markeredgecolor='black', label = 'Yield improvement forcast', alpha=0.75)
    
    yld_cumulative['Yield'] = [min(num, 100) for num in yld_cumulative['Yield']]
    ax.plot(yld_cumulative['Month'], yld_cumulative['Yield'], 'y^-', linewidth=7, markersize=20, markeredgecolor='black', label = 'Cumulative Yield', alpha=0.75)
    
    if product == 'pcs_jig':
        ax.plot(yld['Month'], yld['Yield'], 'yo--', linewidth=3, markersize=10, markeredgecolor='black', label = 'Monthly Yield', alpha=0.75)
    
    # twin axis
    ax2 = ax.twinx()
    ax2.plot(yld_cumulative['Month'], yld_cumulative['Units'], 'b-', linewidth=3, label = 'Units', alpha=0.75)
    ax2.set_ylabel('Units', color='b')
    ax2.tick_params(axis='y', labelcolor='b')
    value = 2 * max(yld_cumulative['Units'])
    rounded_up = math.ceil(value / 50) * 50

    ax2.set_ylim(0, value)
    
    # legend
    # Add a legend with custom styling
    legend = ax.legend(
        loc='lower right',           # Fixed position
        frameon=True,               # Show legend box
        facecolor='white',          # Background color
        edgecolor='black',          # Border color
        fontsize = 10,
    )
    
    # Optional: make legend text color contrast with dark background
    for text in legend.get_texts():
        text.set_color('black')
        
    # title
    plt.title(f'{product}')
    
    # return the plot
    plt.tight_layout()
    plt.show()
    plt.savefig(f'{product}.png', dpi=400)
