import datetime
import csv
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import garth
import json
import time

# (Include previously defined functions like `is_sick_date`, `fetch_data`, etc.)
# Define sick date ranges
SICK_PERIODS = [
    (datetime.date(2024, 5, 25), datetime.date(2024, 6, 7)),
    (datetime.date(2024, 8, 31), datetime.date(2024, 9, 10)),
    (datetime.date(2024, 11, 18), datetime.date(2024, 11, 25)),
    (datetime.date(2025, 1, 2), datetime.date(2025, 1, 17)),
    (datetime.date(2025, 3, 7), datetime.date(2025, 3, 16))
]

# Function to check if a date is within any sick period
def is_sick_date(date):
    for start_date, end_date in SICK_PERIODS:
        if start_date <= date <= end_date:
            return True
    return False

# Function to save the session token
def save_session(email, password, token_file="session_token.json"):
    try:
        print("step1")
        client = garth.Client()
        client.login(email, password)
        print("step2")
        # Save session cookies to a file
        with open(token_file, 'w') as file:
            print("step3")
            json.dump(client.session.cookies.get_dict(), file)
            print("step3")
        print(f"Session token saved to {token_file}")
        return client
    except Exception as e:
        print(f"Error during login: {e}")
        return None

# Function to load the session token
def load_session(token_file="session_token.json"):
    try:
        client = garth.Client()
        
        # Load session cookies from file
        if os.path.exists(token_file):
            with open(token_file, 'r') as file:
                session_cookies = json.load(file)
            
            client.session.cookies.update(session_cookies)
            print("Session loaded successfully")
            return client
        else:
            raise FileNotFoundError("Token file not found.")
    except Exception as e:
        print(f"Error loading session: {e}")
        return None

# Function to fetch and process data
def fetch_data(client, start_date, end_date):
    data = []
    current_date = start_date

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"Fetching data for {date_str}...")
        
        try:
            # Add a small delay to avoid rate limiting
            time.sleep(1)
            
            # Get Heart Rate Variability (HRV)
            hrv_data = client.get(f'/hrv-service/hrv/daily/{date_str}')
            hrv_avg = None
            if hrv_data and 'hrvSummary' in hrv_data and 'weeklyAvg' in hrv_data['hrvSummary']:
                hrv_avg = hrv_data['hrvSummary']['weeklyAvg']
            
            # Get Resting Heart Rate
            heart_rates = client.get(f'/userstats-service/wellness/daily/{date_str}')
            resting_hr = None
            if heart_rates and 'restingHeartRate' in heart_rates:
                resting_hr = heart_rates['restingHeartRate']
            
            # Get Sleep Data
            sleep_data = client.get(f'/wellness-service/wellness/dailySleepData/{date_str}')
            sleep_duration = None
            if sleep_data and 'dailySleepDTO' in sleep_data and 'sleepTimeSeconds' in sleep_data['dailySleepDTO']:
                sleep_duration = sleep_data['dailySleepDTO']['sleepTimeSeconds'] / 3600  # Convert to hours
            
            # Determine status (Sick or Healthy)
            status = "Sick" if is_sick_date(current_date) else "Healthy"
            
            # Add to data list
            data.append({
                'date': current_date,
                'hrv': hrv_avg,
                'resting_hr': resting_hr,
                'sleep_duration': sleep_duration,
                'status': status
            })
            
        except Exception as e:
            print(f"Error fetching data for {date_str}: {e}")
        
        # Move to next day
        current_date += datetime.timedelta(days=1)
    
    return data

# Function to save data to CSV
def save_to_csv(data, filename="garmin_health_data.csv"):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['date', 'hrv', 'resting_hr', 'sleep_duration', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)
    
    print(f"Data saved to {filename}")
    return filename

# Function to create visualizations
def create_visualizations(filename):
    # Read the CSV
    df = pd.read_csv(filename)
    df['date'] = pd.to_datetime(df['date'])
    
    # Create figure and subplots
    fig, axs = plt.subplots(3, 1, figsize=(12, 15), sharex=True)
    
    # Set background colors for sick periods
    for ax in axs:
        for start_date, end_date in SICK_PERIODS:
            start = pd.Timestamp(start_date)
            end = pd.Timestamp(end_date)
            ax.axvspan(start, end, color='lightcoral', alpha=0.3)
    
    # Plot HRV
    axs[0].plot(df['date'], df['hrv'], marker='o', linestyle='-', color='blue')
    axs[0].set_title('Heart Rate Variability (HRV)')
    axs[0].set_ylabel('HRV')
    axs[0].grid(True)
    
    # Plot Resting Heart Rate
    axs[1].plot(df['date'], df['resting_hr'], marker='o', linestyle='-', color='green')
    axs[1].set_title('Resting Heart Rate')
    axs[1].set_ylabel('BPM')
    axs[1].grid(True)
    
    # Plot Sleep Duration
    axs[2].plot(df['date'], df['sleep_duration'], marker='o', linestyle='-', color='purple')
    axs[2].set_title('Sleep Duration')
    axs[2].set_ylabel('Hours')
    axs[2].grid(True)
    
    # Format date axis
    for ax in axs:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('garmin_health_visualization.png', dpi=300, bbox_inches='tight')
    print("Visualization saved as garmin_health_visualization.png")
    
    plt.show()
    
# Main function
def main():
    token_file = "session_token.json"
    client = load_session(token_file)
    
    # If session loading fails, prompt for credentials and save a new session
    if not client:
        print("Session token invalid or file missing. Attempting re-login...")
        email = input("Enter your Garmin Connect email: ")
        password = input("Enter your Garmin Connect password: ")
        client = save_session(email, password, token_file)
        if not client:
            print("Failed to initialize Garmin Connect client.")
            return

    # Set date range
    start_date = datetime.date(2024, 4, 1)
    end_date = datetime.date(2025, 3, 30)
    
    # Fetch data, save to CSV, and create visualizations
    data = fetch_data(client, start_date, end_date)
    csv_filename = save_to_csv(data)
    create_visualizations(csv_filename)

if __name__ == "__main__":
    main()
