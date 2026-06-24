############################################################
# Lecture: Clinical Research Informatics - Sommer Semester 2026
# Exercise Sheet: Week 09 - Coding Project 06 (Synthetic Health Data)
# Student Name: K. Otte

# | Student Name     | Matriculation Number |
# | ---------------- | -------------------- |
# | LENKA TUSCHEROVA | 631168               |
# | OLEKSANDR SHKIL  | 657708               |
# | JAEDEN CAPINIG   | 656852               |
# | DAMIAN RYCHLICKI | 572581               |


# Optional information:
# Additional information:
# used additional packages: pandas 2.3.3, matplotlib 3.10.0, scipy 1.15.2
############################################################

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pandas.api.types import is_numeric_dtype

pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.expand_frame_repr", False)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Calibri"],
    "svg.fonttype": "none",
})

# --------------------------------------------------
# Main Script
# --------------------------------------------------

if __name__ == "__main__":
    # 1.1 Load the original and anonymized datasets into your Python environment and compare them.
    # For the anonymized dataset you can built upon last week’s exercise. Your anonymized dataset should
    # at least be 2-anonymous and feature RACE, ETHNICITY, GENDER and your primary outcomes as
    # “Quasi-identifying” attributes. Use descriptive statistics (similar to exercise 7, 1.1) and
    # visualizations (e.g., histograms, box plots) to compare the distributions of key variables.

    # Original data from exercise 6 / 7
    df = pd.read_csv("week_6_data.csv")

    # Anonymized data exported from ARX (based on hu-assignment-08-example.deid)
    df_anon = pd.read_csv("anonymized_data.csv", keep_default_na=False)

    print("1.1 Comparison of original vs. anonymized data")
    print("Original shape:", df.shape)
    print("Anonymized shape:", df_anon.shape)
    print()

    # Same demographic subset as in exercise 7
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

    # Primary parameters from exercise 7
    disease_severity = df["IS_SEVERE"].copy()
    pollution_level = df["HIGH_POLLUTION"].copy()

    print("Primary parameters (original data)")
    print(disease_severity.describe())
    print()
    print(pollution_level.describe())
    print()

    print("Demographic information (original data)")
    for column in demographic_info:
        print(demographic_info[column].describe())
        print()

    # Outcome attributes configured as quasi-identifiers in ARX
    print("ASTHMA_REASON_ENCOUNTER (original)")
    print(df["ASTHMA_REASON_ENCOUNTER"].describe())
    print()
    print("Measurement_avg pm25_2024 (original)")
    print(df["Measurement_avg pm25_2024"].describe())
    print()

    print("Anonymized quasi-identifiers / outcomes")
    print(df_anon["RACE"].value_counts())
    print()
    print(df_anon["ETHNICITY"].value_counts())
    print()
    print(df_anon["GENDER"].value_counts())
    print()
    print(df_anon["ASTHMA_REASON_ENCOUNTER"].value_counts())
    print()
    print(df_anon["Measurement_avg pm25_2024"].value_counts())
    print()

    print("Data types before and after anonymization")
    compare_columns = [
        "RACE",
        "ETHNICITY",
        "GENDER",
        "ASTHMA_REASON_ENCOUNTER",
        "Measurement_avg pm25_2024",
        "IS_SEVERE",
        "HIGH_POLLUTION",
        "CURRENT_AGE",
    ]
    for column in compare_columns:
        print(column, "- original:", df[column].dtype, "| anonymized:", df_anon[column].dtype)
    print()

    # Visual comparison - same style as exercise 7
    sns.boxplot(disease_severity)
    plt.title("Box Plot for Disease severity (original)")
    plt.show()

    sns.boxplot(df_anon["IS_SEVERE"])
    plt.title("Box Plot for Disease severity (anonymized)")
    plt.show()
    # IS_SEVERE was set to insensitive in ARX - distribution stays the same

    sns.boxplot(pollution_level)
    plt.title("Box Plot for Pollution level (original)")
    plt.show()

    sns.boxplot(df_anon["HIGH_POLLUTION"])
    plt.title("Box Plot for Pollution level (anonymized)")
    plt.show()
    # HIGH_POLLUTION also unchanged after anonymization

    for column in demographic_info:
        if is_numeric_dtype(demographic_info[column].dtypes):
            sns.boxplot(demographic_info[column])
            graph_title = "Box Plot for " + column + " (original)"
            plt.title(graph_title)
            plt.show()

            sns.boxplot(df_anon[column])
            graph_title = "Box Plot for " + column + " (anonymized)"
            plt.title(graph_title)
            plt.show()

    df["ASTHMA_REASON_ENCOUNTER"].plot(kind="hist", bins=range(0, 14))
    plt.title("Histogram for ASTHMA_REASON_ENCOUNTER (original)")
    plt.show()

    df_anon["ASTHMA_REASON_ENCOUNTER"].value_counts().sort_index().plot(kind="bar")
    plt.title("Bar plot for ASTHMA_REASON_ENCOUNTER (anonymized)")
    plt.show()

    df["Measurement_avg pm25_2024"].plot(kind="hist", bins=20)
    plt.title("Histogram for Measurement_avg pm25_2024 (original)")
    plt.show()

    df_anon["Measurement_avg pm25_2024"].value_counts().sort_index().plot(kind="bar")
    plt.title("Bar plot for Measurement_avg pm25_2024 (anonymized)")
    plt.show()

    df["RACE"].value_counts().plot(kind="bar")
    plt.title("Bar plot for RACE (original)")
    plt.show()

    df_anon["RACE"].value_counts().plot(kind="bar")
    plt.title("Bar plot for RACE (anonymized)")
    plt.show()

    # 1.2 What changes do you see after anonymization (e.g. in regard to outliers and data types)?
    print("1.2 Changes after anonymization")

    race_suppressed = (df_anon["RACE"] == "*").sum()
    race_null = (df_anon["RACE"] == "NULL").sum()

    print("We still have n =", len(df_anon), "rows after anonymization.")
    print("IS_SEVERE and HIGH_POLLUTION did not change because they were insensitive attributes in ARX.")
    print("ETHNICITY and GENDER also stayed the same in our ARX setup.")
    print("RACE was generalized most - *:", race_suppressed, "records, NULL:", race_null, "records")
    print(
        "ASTHMA_REASON_ENCOUNTER went from integer values (1-12) to interval groups like [3, 5[."
    )
    print(
        "Measurement_avg pm25_2024 went from float values to wider PM2.5 intervals, "
        "so the exact min/max outliers are no longer visible."
    )
    print("CURRENT_AGE and the other insensitive demographics kept their original values and types.")
