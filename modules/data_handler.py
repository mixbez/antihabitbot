import csv
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.colors import LinearSegmentedColormap



import calendar
def get_file_path(user_id):
    """Get the file path for a given user ID."""
    return f"data/{user_id}.csv"

def check_file_exists(user_id):
    """Check if the CSV file for the user already exists."""
    filename = get_file_path(user_id)
    return os.path.isfile(filename)

def create_user_file(user_id):
    """Create a new CSV file for the user with Date and Number columns."""
    filename = get_file_path(user_id)
    if not check_file_exists(user_id):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Number'])
            today_date = datetime.now().strftime('%Y-%m-%d')
            writer.writerow([today_date, 0])


def update_or_create_entry(user_id, k = 1):
    """Update the user's file with today's date or create a new entry."""
    filename = get_file_path(user_id)
    create_user_file(user_id)  # Ensure file exists

    today = datetime.now().date()
    data = []

    with open(filename, 'r+', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip the header row
        for row in reader:
            date_str, count = row
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if date == today:
                count = str(int(count) + k)
            data.append([date_str, count])

        # Create rows for missing dates
        latest_date = datetime.strptime(data[-1][0], '%Y-%m-%d').date() if data else None
        while latest_date <= today - timedelta(days=1):
            latest_date += timedelta(days=1)
            if latest_date < today - timedelta(days=1):
                data.append([latest_date.strftime('%Y-%m-%d'), '0'])
            else:
                data.append([latest_date.strftime('%Y-%m-%d'), k])
                count = k

        file.seek(0)
        file.truncate()
        writer = csv.writer(file)
        writer.writerow(header)  # Write back the header
        writer.writerows(data)

    return int(count)

def create_heatmap_old(user_id):
    """Create and return a calendar heatmap based on the user's data."""
    filename = get_file_path(user_id)

    # Read the CSV file into a DataFrame
    df = pd.read_csv(filename)
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)

    # Create a pivot table with days as columns and weeks as rows
   # df['day'] = df['Date'].dt.day
    df['day'] = df['Date'].dt.dayofweek + 1
    df['week'] = df['Date'].dt.isocalendar().week
    df['month'] = df['Date'].dt.month
    df['year'] = df['Date'].dt.year
    pivot_table = df.pivot_table(
        index=['year', 'week'],
        columns='day',
        values='Number',
        fill_value=0
    )

    # Plot heatmap
        # Plot heatmap
    fig, ax = plt.subplots(figsize=(12, 8))

    heatmap = ax.imshow(pivot_table, cmap='RdYlGn_r', aspect='equal', interpolation='nearest')  # Red to Green colormap, reversed
    plt.colorbar(heatmap, ax=ax)

    # Set the labels
    ax.set_ylabel('Week of the Year')
    #ax.set_ylabel('Month of the Year')
    ax.set_xlabel('Day of the Month')
    ax.set_title(f'User {user_id} Activity Calendar Heatmap')

    # Adjust ticks
    ax.set_yticks(np.arange(len(pivot_table.index)))
    ax.set_yticklabels([f'{y}-{w:02d}' for y, w in pivot_table.index])
    ax.set_xticks(np.arange(1, 8))
    ax.set_xticklabels(np.arange(1, 8))

    # Return the figure
    return fig

def create_heatmap(user_id):
    """Create and return a calendar heatmap based on the user's data."""
    filename = get_file_path(user_id)

    # Read the CSV file into a DataFrame
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        return (None, 0, 0, 0, 0, 0)
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)

    # Create a pivot table with days as rows and weeks as columns
    df['day'] = df['Date'].dt.dayofweek
    df['week'] = df['Date'].dt.isocalendar().week
    df['month'] = df['Date'].dt.month
    df['year'] = df['Date'].dt.year
    pivot_table = df.pivot_table(
        index='day',
        columns=['year', 'week'],
        values='Number',
        fill_value= np.nan
    )
    num_entries = df.shape[0]
    max_val = round(pivot_table.max().max())
    min_val = round(pivot_table.min().min())
    avg_val = round(pivot_table.mean().mean())
    num_zeros = (pivot_table == 0).sum().sum()

    # Determine the first week of each month
    first_week_of_month = df.groupby(['year', 'month'])['week'].min()

    # Map the first week of each month to its month name
    week_to_month = {(row.year, row.week): calendar.month_name[row.month]
                     for row in first_week_of_month.reset_index().itertuples()}

    cmap = plt.cm.RdYlGn_r  # Red-Yellow-Green reversed colormap
    cmap.set_bad('grey')  # Color for missing values (NaN)


   #  Plot heatmap
    fig, ax = plt.subplots(figsize=(12, 8))
    heatmap = ax.imshow(pivot_table, cmap='YlOrRd', aspect='equal', interpolation='nearest')

    max_value = pivot_table.max().max()
    plt.colorbar(heatmap, ax=ax)
    if num_zeros > 0:
        pivot_table[pivot_table > 0] += max_value
        heatmap = ax.imshow(pivot_table, cmap='RdYlGn_r', aspect='equal', interpolation='nearest')
        #plt.colorbar(heatmap, ax=ax)


    # Set the labels
    ax.set_xlabel('Month')
    ax.set_ylabel('Day of the Week')
    ax.set_title(f'User {user_id} Activity Calendar Heatmap')

    # Adjust ticks
    ax.set_yticks(np.arange(7))
    ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])

    # Set custom X-axis labels
    x_labels = [week_to_month.get((year, week), '') for year, week in pivot_table.columns]
    ax.set_xticks(np.arange(len(pivot_table.columns)))
    ax.set_xticklabels(x_labels, rotation=90)  # Rotate labels for better readability

    # Return the figure
    return  fig, num_entries, max_val, min_val, avg_val, num_zeros

def remove_user_data(user_id):
    """Remove user data file if it exists."""
    file_path = f"data/{user_id}.csv"
    if os.path.exists(file_path):
        os.remove(file_path)