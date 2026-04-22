import csv
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

def plot_sensor_data(csv_file='sensor_data.csv'):
    times = []
    temps = []
    hums = []

    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Parse date and time
                    dt_str = f"{row['Date']} {row['Time']}"
                    dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                    
                    # Parse temperature and humidity, these will raise ValueError if invalid
                    temp = float(row['Temperature (F)'])
                    hum = float(row['Humidity (%)'])
                    
                    times.append(dt)
                    temps.append(temp)
                    hums.append(hum)
                except (ValueError, KeyError):
                    # Skip rows with invalid data like 'ÿÿÿÿÿÿÿ'
                    continue
    except FileNotFoundError:
        print(f"Error: The file {csv_file} was not found.")
        return

    if not times:
        print("No valid data found to plot.")
        return

    # Create the plot
    fig, ax1 = plt.subplots(figsize=(12, 6))

    color = 'tab:red'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Temperature (F)', color=color)
    ax1.plot(times, temps, color=color, label='Temperature')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  
    color = 'tab:blue'
    ax2.set_ylabel('Humidity (%)', color=color)
    ax2.plot(times, hums, color=color, label='Humidity')
    ax2.tick_params(axis='y', labelcolor=color)

    # Format the x-axis to look nice
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    fig.autofmt_xdate()

    plt.title('Temperature and Humidity vs. Time')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    fig.tight_layout()  

    plt.savefig('sensor_data_plot.png')
    print("Plot saved as 'sensor_data_plot.png'.")
    plt.show()

if __name__ == '__main__':
    plot_sensor_data()
