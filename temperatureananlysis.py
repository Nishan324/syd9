import os
import pandas as pd
import numpy as np

folder = "./temperatures"

SEASONS={
    "summer":["December","January","February"],
    "autumn":["March","April","May"],
    "winter":["June","July","August"],
    "spring":["September","October","November"]
}

all_data = []

for file in os.listdir(folder):
    if file.endswith(".csv"):
        path = os.path.join(folder,file)
        df = pd.read_csv(path)
        all_data.append(df)

data = pd.concat(all_data, ignore_index=True)

seasonal_averages = {}

for season, months in SEASONS.items():
    values = data[months].values.flatten()
    seasonal_averages[season] = np.nanmean(values)

with open("average_temp.txt","w") as f:
    for season, avg in seasonal_averages.items():
        f.write(f"{season}: {avg:.1f}°C\n")

station_ranges={
}

for _, row in data.iterrows():
    station= row["STATION_NAME"]
    temps = row[list(SEASONS["summer"]+ SEASONS["autumn"]+ SEASONS["winter"]+ SEASONS["spring"])]

    max_temp= np.nanmax(temps)
    min_temp=np.nanmin(temps)

    if station not in station_ranges:
        station_ranges[station]=[max_temp,min_temp]
    else:
        station_ranges[station][0]= max(station_ranges[station][0], max_temp)
        station_ranges[station][1]= min(station_ranges[station][1],min_temp)

ranges={
    station:(vals[0]- vals[1], vals[0], vals[1])
    for station, vals in station_ranges.items()
}

max_range= max(r[0] for r in ranges.values())

with open("largest_temp_range_station.txt", "w") as f:
    for station, (rng, mx, mn) in ranges.items():
        if rng==max_range:
            f.write(
                f"{station}: Range {rng:.1f}°C"
                f"(Max:{mx:.1f}°C)\n"
            )

station_std={}

for station, group in data.groupby("STATION_NAME"):
    temps=group[
        list(SEASONS["summer"]+ SEASONS["autumn"]+SEASONS["winter"]+SEASONS["spring"])
    ].values.flatten()
    station_std[station]=np.nanstd(temps)
min_std = min(station_std.values())
max_std=max(station_std.values())

with open("temperature_stability_stations.txt","w") as f:
 for station, std in station_std.items():
     if std == min_std:
        f.write(f" Most Variable: {station}:StdDev {std:.1f}°C\n")

    
 for station, std in station_std.items(): 
     if std == max_std:
         f.write(f" Most Variable: {station}:StdDev {std:.1f}°C\n")
     
