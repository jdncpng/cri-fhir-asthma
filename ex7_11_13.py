###################################################################
# Lecture: Clinical Research Informatics - Sommer Semester 2026

# Exercise Sheet: {Sheet_Number}
# Student Name: {Your_Name}
# Matriculation Number: {Your_Matriculation_Number}
#
# Additional information:
#   used additional packages: {Package name and version}
#   dataset used: {dataset or file name}
###################################################################

# Please add this header to all your submissions and adapt it to your information and submission.
# The following structure is a recommendation, but not mandatory to use

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pandas.api.types import is_numeric_dtype


# --------------------------------------------------
# Functions
# --------------------------------------------------


# --------------------------------------------------
# Main Script
# --------------------------------------------------

# 1.1 Import the dataset from the previous exercise. Select one parameter to represent children’s asthma disease severity and another to represent the level of air pollution each child is exposed to. 
# Print the descriptive statistics for the demographic information as well as these parameters. Ensure you understand the type and scale of the data you are working with.
# Note: Check if you see dependencies between your selected parameters and the children’s demographics. Adjust your parameters if needed.

# Import dataset from previous exercise
df = pd.read_csv("week_6_data.csv")

# Only demographic information important
demographic_info = df.copy()
cols = []
for i in range(0, 12):
    cols.append(i) 
for i in range(16, 22):
    cols.append(i) 
for i in range(24, 26):
    cols.append(i) 
for i in range(28, 45):
    cols.append(i) 
demographic_info.drop(demographic_info.columns[cols], axis=1, inplace=True)

# Parameter to represent children’s asthma disease severity 
disease_severity = df["IS_SEVERE"].copy()

# Parameter to represent the level of air pollution each child is exposed to
pollution_level = df["HIGH_POLLUTION"].copy()

# Print the descriptive statistics for the demographic information as well as these parameters.
print(disease_severity.describe())
print()
print(pollution_level.describe())
print()
for column in demographic_info:
    print(demographic_info[column].describe())
print()

# 1.2 Examine your dataset for potential outliers. 
# Identify any extreme values using visual and statistical methods (e.g. box plots, percentile values) for your primary parameters and the demographic information. 
# Decide if you need to exclude extreme outliers based on a 5% cut-off of the highest and lowest data values and perform it if necessary.

sns.boxplot(disease_severity)
plt.title("Box Plot for Disease severity")
plt.show()
# First parameter "Disease severity" is boolean data point - there can't be extremes - NO CUTT-OFF

sns.boxplot(pollution_level)
plt.title("Box Plot for Pollution level")
plt.show()
# Second parameter "Pollution level" is boolean data point - there can't be extremes - NO CUTT-OFF

#HEREEEEE
for column in demographic_info:
    # Box plot
    sns.boxplot(demographic_info[column])
    graph_title = "Box Plot for " + column
    plt.title(graph_title)
    plt.show()
    # Percentile
    if (is_numeric_dtype(demographic_info[column].dtypes)):
        lower_percentile_rank = np.percentile(demographic_info[column], 5)
        print(f"5%: {column}: {lower_percentile_rank}")
        upper_percentile_rank = np.percentile(demographic_info[column], 95)
        print(f"95%: {column}: {upper_percentile_rank}")

        print()

        # This is nor a terribly large dataset and so cutt-off sounds risky but we will perform a:
        # Interquartile Range (IQR) Method - searching for extremes
        Q1 = demographic_info[column].quantile(0.25)
        Q3 = demographic_info[column].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = demographic_info[(demographic_info[column] < lower_bound) | (demographic_info[column] > upper_bound)].copy()
        if (outliers.empty):
            print("No cutt-offs")
            print()
        else:
            df_filtered = demographic_info[(demographic_info[column] < upper_percentile_rank) & (demographic_info[column] > lower_percentile_rank)]

        


# 1.3 Check for and handle any other quality issues in your dataset like duplicate records. Print the count of unique records before and after duplicate removal.

relevant_df = pd.concat([disease_severity, pollution_level], axis=1)
relevant_df = pd.concat([demographic_info, relevant_df], axis=1)


for col in demographic_info:
    print(f"Count of unique records before: {relevant_df[col].nunique()}")

print()
relevant_df = relevant_df.drop_duplicates()

for col in demographic_info:
    print(f"Count of unique records after: {relevant_df[col].nunique()}")