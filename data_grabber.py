import requests
import pandas as pd
import pickle
from functions import generate_month_intervals

# Define the host and endpoint
host = "https://api.binance.com"
endpoint = "/api/v3/klines"

# Define the parameters
params = {
    'symbol': 'ETHUSDT',
    'interval': '1h',  # Interval is required for klines endpoint
    "limit": 1000
}
# Define the start and end times
start = "2024-01-01"
end = "2024-05-31"

month_intervals = generate_month_intervals(start, end)
price_df = pd.DataFrame()

for interval in month_intervals:

    start_time = interval[0]
    end_time = interval[1]
    # Convert start and end times to timestamps in milliseconds
    start_timestamp = int(pd.to_datetime(start_time).timestamp() * 1000)
    end_timestamp = int(pd.to_datetime(end_time).timestamp() * 1000)

    # Add start and end times to parameters
    params['startTime'] = start_timestamp
    params['endTime'] = end_timestamp

    # Make the GET request
    response = requests.get(url=host + endpoint, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Convert byte response to string
        response_text = response.content.decode('utf-8')

        # Parse the response as JSON
        import json

        data = json.loads(response_text)

        # Create lists to hold the data
        open_times = []
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []

        for kline in data:
            open_time = pd.to_datetime(kline[0], unit='ms')
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])

            # Append data to lists
            open_times.append(open_time)
            opens.append(open_price)
            highs.append(high_price)
            lows.append(low_price)
            closes.append(close_price)
            volumes.append(volume)

        if price_df is None:
            # Create a DataFrame
            price_df = pd.DataFrame({
                'Time': open_times,
                'Open': opens,
                'High': highs,
                'Low': lows,
                'Close': closes,
                'Volume': volumes
            })

            # Set the Date column as the index
            price_df.set_index('Time', inplace=True)

        else:
            additional_df = pd.DataFrame({
                'Time': open_times,
                'Open': opens,
                'High': highs,
                'Low': lows,
                'Close': closes,
                'Volume': volumes
            })
            price_df = pd.concat([price_df, additional_df], ignore_index=True)

    else:
        # Print the error if the request was not successful
        print(f"Error: {response.status_code}, {response.text}")

if not price_df.empty:
    print(price_df)
    with open('ETHUSDT_testing.pkl', 'wb') as file:
        pickle.dump(price_df, file)
