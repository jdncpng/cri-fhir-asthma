############################################################
# Lecture: Clinical Research Informatics - Sommer Semester 2026
# Exercise Sheet: Week 06 - Coding Ex. 03
# Student Name: K. Otte
# Matriculation Number: 42231337
#
# Optional information:
# used additional packages: seaborn==0.13.2; matplotlib==3.8.4
# dataset used: Coding Data 02 - minimal
############################################################

import os.path
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.expand_frame_repr', False)

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Calibri'],
    'svg.fonttype': 'none'
})


# --------------------------------------------------
# Functions
# --------------------------------------------------

def transform_air_data(df_air: pd.DataFrame):
    df_air_pivot = df_air.pivot(index="County", columns='Year')
    df_air_pivot["City"] = df_air_pivot.index
    df_air_pivot.reset_index(drop=True, inplace=True)
    df_air_pivot.columns = ['_'.join(str(c) for c in col) for col in df_air_pivot.columns]  # reset column levels
    return df_air_pivot

# --------------------------------------------------
# Main Script
# --------------------------------------------------


if __name__ == "__main__":
    # 1.1	Import the air quality dataset and add the information to the patient dataset. Print the number of counties
    # for which the data is available.
   
    df_air = pd.read_csv(os.path.join("cri_air_pollution.csv"))
    print(f"Number of counties for which the data is available: {len(df_air['County'].unique())}")

    # 1.2 Transform the longitudinal air quality dataset into a format that can be merged with cross-sectional
    # tables. Merge it with the resulting patient data from last week’s exercise.
    df_air = transform_air_data(df_air)
    df_pat = pd.read_csv(os.path.join("week_5_data.csv"))

    df_pat = pd.merge(left=df_pat, right=df_air, left_on="CITY", right_on="City_")
    df_pat.drop("City_", axis=1, inplace=True)

    # 2.1 Explore the air quality data by using descriptive statistics and data visualization.
    # What relations do you see with your asthma severity measures?
    print("Descriptive statistics of the air quality dataset:")
    print(df_air.describe())

    variable_list = ['CURRENT_AGE', 'TOTAL_CONDITIONS', 'TOTAL_ENCOUNTER',
                     'ASTHMA_REASON_ENCOUNTER', 'ASTHMA_FU_ENCOUNTER', 'SYMPTOM_ENCOUNTER',
                     'URGENT_CARE_ENCOUNTER', 'EMERGENCY_ENCOUNTER',
                     'Measurement_avg pm25_2023']

    sns.pairplot(df_pat[variable_list])
    plt.show()
    print("We see a strong outlier in the number of total encounters that should be excluded from further analyses. \n"
          "We also see potential correlations between the number of asthma related encounters and the average PM25 "
          "measure during 2023. We also see dependencies between the current age, and the number of encounters. \n "
          "Future analysis should correct for this.")

    corr_coeff = df_pat[["ASTHMA_REASON_ENCOUNTER", 'Measurement_avg pm25_2023']].corr()
    print(f"Correlation between Asthma related encounter and PM25 measurement: {corr_coeff.iloc[0, 1]}")

    # 2.2 Create categories, that allows you to explore the relationship between air pollution and asthma severity.
    df_pat.loc[:, "IS_SEVERE"] = df_pat["ASTHMA_REASON_ENCOUNTER"] > df_pat[
        "ASTHMA_REASON_ENCOUNTER"].median()
    df_pat.loc[:, "HIGH_POLLUTION"] = df_pat["Measurement_avg pm25_2023"] > df_pat[
        "Measurement_avg pm25_2023"].mean()

    print(df_pat[["IS_SEVERE", "HIGH_POLLUTION"]].describe())
    print("We have more samples for high polluted areas then for lower pollution. "
          "Future analysis should correct for that.")

    # 2.3 Create at least two data visualizations for the exploration of disease severity vs. air pollution.
    sns.boxplot(data=df_pat, x="HIGH_POLLUTION", y="ASTHMA_REASON_ENCOUNTER")
    plt.show()
    sns.boxplot(data=df_pat, x="IS_SEVERE", y="URGENT_CARE_ENCOUNTER")
    plt.show()

    # 3.1 Export your working data into a csv file.
    export_path = os.path.join("Data", "Working Data")
    os.makedirs(export_path, exist_ok=True)
    df_pat.to_csv(os.path.join(export_path, "week_6_data.csv"), index=None)
