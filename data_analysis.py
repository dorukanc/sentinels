import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Read the xlsx file
df = pd.read_excel("./data/covidcases-byagegender.xlsx")
print(df.head())

# Draw a bar chart because this is a categorical data

# Set the figure size
plt.figure(figsize=(10, 6))

# Define the age groups and their positions on the x-axis
age_groups = df['Age Groups']
x = np.arange(len(age_groups))

# Plot the bars for Men and Women
plt.bar(x - 0.2, df['Men'], width=0.4, label='Men', color='skyblue', edgecolor='black')
plt.bar(x + 0.2, df['Women'], width=0.4, label='Women', color='salmon', edgecolor='black')

# Customize the plot
plt.xlabel('Age Group')
plt.ylabel('Population')
plt.title('Hospitalized by Age Group (Men vs. Women) Covid-19 Germany')
plt.xticks(x, age_groups, rotation=45)
plt.legend()

plt.tight_layout()
plt.show()