import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Loading the csv file

df = pd.read_csv('data/covid19_mortalityrate_weekly_oecd.csv')

# Checking the first few rows to ensure our data loaded correctly
print(df.head())

# filtering the data, pt_dt (percentage of death total)

filtered_pt_data = df[df['UNIT_MEASURE'] == 'PT_DT']

# extracting data from filtered data
obs_value = filtered_pt_data['OBS_VALUE']

# mean, median, std of our data

mean_value = obs_value.mean()
median_value = obs_value.median()
std_value = obs_value.std()

# Plotting the mortality rate to a graph weekly
# Created a line plot to visualize mortality rate (pt_dt)
plt.figure(figsize=(8,6))
plt.plot(filtered_pt_data['OBS_VALUE'], marker='o', linestyle='-', color='b')
plt.xlabel("Week")
plt.ylabel("Mortality Rate")
plt.title("Weekly Covid-19 Mortality Rate")
plt.grid()
plt.show()

# Print the results
print(f"Mean: {mean_value:.2f}")
print(f"Median: {median_value:.2f}")
print(f"Standard Deviation: {std_value:.2f}")