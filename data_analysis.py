import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Loading the csv file

df = pd.read_csv('data/covid19_mortalityrate_weekly_oecd.csv')

# Checking the first few rows to ensure our data loaded correctly
print(df.head())

# filtering the data

# extracting the data from OBS_VALUE column
obs_value = df['OBS_VALUE']



# mean, median, std of our data

mean_value = obs_value.mean()
median_value = obs_value.median()
std_value = obs_value.std()

# Print the results
print(f"Mean: {mean_value:.2f}")
print(f"Median: {median_value:.2f}")
print(f"Standard Deviation: {std_value:.2f}")