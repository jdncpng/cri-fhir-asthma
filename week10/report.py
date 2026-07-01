###################################################################
# Lecture: Clinical Research Informatics - Sommer Semester 2026

# Exercise Sheet: Week 10 - Data Analysis Report

# | Student Name     | Matriculation Number |
# | ---------------- | -------------------- |
# | LENKA TUSCHEROVA | 631168               |
# | OLEKSANDR SHKIL  | 657708               |
# | JAEDEN CAPINIG   | 656852               |
# | DAMIAN RYCHLICKI | 572581               |
#
# Additional information:
#   used additional packages: numpy, seaborn, matplotlib
#   datasets used: Coding Data 02 - standard
###################################################################

# Please add this header to all your submissions and adapt it to your information and submission.
# The following structure is a recommendation, but not mandatory to use

# import dependencies
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

from datetime import date # not used yet but maybe in future

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.expand_frame_repr', False)


# --------------------------------------------------
# Functions
# --------------------------------------------------

def asthma_Find(df, pat_list):
    new_df = df[df['PATIENT'].isin(pat_list)]
    return new_df

def calculate_age_in_years(birth_dates: pd.Series, reference_dates: pd.Series) -> pd.Series:
    """Calculate age in whole years between birth dates and reference dates."""
    return ((reference_dates - birth_dates).dt.days / 365.2425)

def calc_current_age(birthday):
    today = pd.to_datetime('now')
    age = pd.to_timedelta(today - birthday)
    age = age.dt.days / 365.2425
    return np.round(age)

def add_age_at_condition_start(conditions: pd.DataFrame, patients: pd.DataFrame) -> pd.DataFrame:
    """Add patient age at condition start to the conditions DataFrame."""
    conditions = conditions.copy()
    birthdates = patients.set_index("Id")["BIRTHDATE"]
    conditions["age_at_start"] = calculate_age_in_years(
        conditions["PATIENT"].map(birthdates),
        conditions["START"],
    )
    return conditions

def filter_patients_by_age(
    patients: pd.DataFrame,
    min_age: int,
    max_age: int,
    age_column: str = "current_age",
) -> pd.DataFrame:
    """Filter patient records to those with age within the given range (inclusive)."""
    return patients[(patients[age_column] >= min_age) & (patients[age_column] <= max_age)].copy()

# method to only include patients with certain conditions
def get_encounter_numbers_per_patient(df_enc, code):
    return df_enc[df_enc["CODE"] == code]["PATIENT"].value_counts()

def transform_air_data(df_air: pd.DataFrame):
    df_air = df_air.rename(columns={"Measurement_avg pm25": "avg_pm25"})
    df_air_pivot = df_air.pivot(index="County", columns='Year')
    df_air_pivot.columns = ['_'.join(str(c) for c in col) for col in df_air_pivot.columns]
    df_air_pivot = df_air_pivot.reset_index()  # bring County back as a real column for the merge
    return df_air_pivot

# --------------------------------------------------
# Main Script
# --------------------------------------------------

# Week 5
print("WEEK 5")

# import files as Pandas DataFrames, and provide print statements, that show for each file the number of variables (columns) and entries (rows).
DATA_FILES = {
    "patients": "patients.csv",
    "conditions": "conditions_reduced.csv",
    "careplans": "careplans.csv",
    "allergies": "allergies.csv",
    "medications": "medications_reduced.csv",
    "encounters": "encounter_reduced.csv",
    "observations": "observations_reduced.csv",
}

date_columns = {
    "patients": ["BIRTHDATE", "DEATHDATE"],
    "conditions": ["START", "STOP"],
    "careplans": ["START", "STOP"],
    "allergies": ["START", "STOP"],
    "medications": ["START", "STOP"],
    "encounters": ["START", "STOP"],
    "observations": ["DATE"],
}

dataframes = {}
for name, filename in DATA_FILES.items():
    df = pd.read_csv("Coding Data 02 - standard/" + filename, parse_dates=date_columns[name])
    dataframes[name] = df
    #print("{}: {} variables (columns), {} entries (rows)".format(filename, df.shape[1], df.shape[0]))

patients = dataframes["patients"]

# Add the patients current age to the patient DataFrame and their age at the beginning of the conditions to the conditions DataFrame. 
patients["current_age"] = calc_current_age(patients["BIRTHDATE"])
dataframes["conditions"] = add_age_at_condition_start(dataframes["conditions"], patients)

print("\n")
print("Average patient age: {:.2f} years".format(patients["current_age"].mean()))
print("Average age at condition start: {:.2f} years".format(dataframes["conditions"]["age_at_start"].mean()))

# a method that filters the patient table to only include records with a current age within 6-12. 
records_before = len(patients)
patients_children_6_12 = filter_patients_by_age(patients, min_age=6, max_age=12)
records_after = len(patients_children_6_12.index)

print("\n")
print("All Patients: {}".format(records_before))
print("Only Children:  {}".format(records_after))

# In our study, we want to include only children with a Childhood asthma diagnosis.  
# Create a method that allows to filter the imported DataFrames (e.g. conditions, encounter, …) to only include children with the diagnosis. 
# Print the number of records before and after filtering. 

# Who are the affected
filtered_conditions = dataframes["conditions"].query('CODE == 233678006')

# List of relevant people from Conditions
asthma_pat = filtered_conditions["PATIENT"].copy()
asthma_pat.drop_duplicates()
asthma_list = asthma_pat.tolist()

asthma_child = patients_children_6_12[patients_children_6_12['Id'].isin(asthma_list)]
print(f"\nOnly affected Children: {len(asthma_child)}")

asthma_child_list = asthma_child["Id"].tolist()

patients = asthma_child

# Iterating over the different DataFrames
for name, filename in DATA_FILES.items():

    if(name == "patients"):
        continue

    dataframes[name] = asthma_Find(dataframes[name], asthma_child_list)

# How many children have more than one condition? 

df_amount = dataframes["conditions"].groupby(["PATIENT"]).count()
df_more = df_amount.query('CODE > 1')
print(f"\nNumber of children with asthma with more than one condition: {len(df_more)}")

# What is the maximum number of conditions associated with a patient?

df_max = df_more["CODE"].max()
print(f"\nMaximum number of conditions associated with a patient: {df_max}")


#Consider ways to quantify the health status of these asthmatic children. Extract relevant information from the available datasets and add them to the patient DataFrame. 
#Note: Be creative in calculating and choosing your proxy metrics. Aggregating the longitudinal information into statistics allows for easier integration into the patient DataFrame. The goal should be to have only one row/record per patient. 

encounter_counts = dataframes["encounters"]["PATIENT"].value_counts()
condition_counts = dataframes["conditions"]["PATIENT"].value_counts()

patients = patients.drop_duplicates()
patients.index = patients["Id"]
patients["TOTAL_CONDITIONS"] = condition_counts
patients["TOTAL_ENCOUNTER"] = encounter_counts
patients["ASTHMA_REASON_ENCOUNTER"] = dataframes["encounters"][dataframes["encounters"]["REASONCODE"] == 233678006]["PATIENT"].value_counts()  # encounter due to asthma
patients["SYMPTOM_ENCOUNTER"] = get_encounter_numbers_per_patient(dataframes["encounters"], 185345009)  # Encounter for symptom
patients["EMERGENCY_ENCOUNTER"] = get_encounter_numbers_per_patient(dataframes["encounters"], 50849002)  # emergency hospital admission
patients["URGENT_CARE_ENCOUNTER"] = get_encounter_numbers_per_patient(dataframes["encounters"], 702927004)  # urgent care clinic
patients["ASTHMA_FU_ENCOUNTER"] = get_encounter_numbers_per_patient(dataframes["encounters"], 394701000)  # asthma follow-up


#DATA FOR NEXT WEEK
patients.to_csv("week_5_data.csv", index=True)

# Week 6 
print("Week 6")

# Importing the air quality dataset
df_pat = pd.read_csv("week_5_data.csv")
df_pat = df_pat.rename(columns={"current_age": "CURRENT_AGE"})
df_air = pd.read_csv("cri_air_pollution.csv")

# the number of counties in data.
print(df_pat.head())
print("\n")
print(df_air.head())
print(f"\nCounties available: {df_air['County'].nunique()}")

# transforming to wide format for merge
df_air = transform_air_data(df_air)

# Merge the air pollution data with the patient data. We will use an inner join to keep all patients, 
# and add air pollution data where available based on the CITY/COUNTY match.
df_pat = pd.merge(left=df_pat, right=df_air, left_on="CITY", right_on="County")

# Drop the duplicates
df_pat = df_pat.drop(columns=["Id.1"])

# descriptive statistics
print("\nDescriptive statistics of air quality data")
print("We see a slight decline in average concentration of airbone particles as years go by.")
print("\n")
print(df_air.describe())

severity_cols = [
    "CURRENT_AGE",
    "TOTAL_CONDITIONS",
    "TOTAL_ENCOUNTER",
    "ASTHMA_REASON_ENCOUNTER",
    "ASTHMA_FU_ENCOUNTER",
    "SYMPTOM_ENCOUNTER",
    "URGENT_CARE_ENCOUNTER",
    "EMERGENCY_ENCOUNTER",
    "avg_pm25_2024"
]

# using pairplot for a general overview of relationships between air pollution and severity measures. 
# We will do more specific analyses later, but this is a good starting point to get a sense of the data.

pairplot = sns.pairplot(df_pat[severity_cols])
pairplot.savefig("6_severity_pairplot.png", bbox_inches="tight", dpi=150)
plt.close() 

# Correlation heatmap to see the strength of relationships between air pollution and severity measures.

corr = df_pat[severity_cols].corr()

fig, ax = plt.subplots(figsize=(12,10))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="viridis", ax=ax)
ax.set_title("Correlation Matrix of PM2.5 and Severity Measures")
plt.tight_layout()
plt.savefig("6_correlation_heatmap.png", bbox_inches="tight", dpi=150)
plt.close()

# create additional categories such as whether asthma condition is severe, and if a county is highly polluted

df_pat.loc[:, "IS_SEVERE"] = df_pat["ASTHMA_REASON_ENCOUNTER"] > df_pat["ASTHMA_REASON_ENCOUNTER"].median()
df_pat.loc[:, "HIGH_POLLUTION"] = df_pat["avg_pm25_2024"] > df_pat["avg_pm25_2024"].mean()

print("\n")
print(df_pat[["IS_SEVERE", "HIGH_POLLUTION"]].describe())

# boxplot and regression plot to explore asthma severity vs air pollution
fig, ax = plt.subplots()
sns.boxplot(data=df_pat, x="HIGH_POLLUTION", y="ASTHMA_REASON_ENCOUNTER", hue="HIGH_POLLUTION", palette="viridis")
ax.set_title("Distribution of Asthma Encounters in polluted areas")
plt.tight_layout()
plt.savefig("6_boxplot_highpoll.png", bbox_inches="tight", dpi=150)
plt.close()

fig, ax = plt.subplots()
sns.boxplot(data=df_pat, x="IS_SEVERE", y="avg_pm25_2024", hue="IS_SEVERE", palette="viridis")
ax.set_title("Asthma Severity according to air pollution measurements")
plt.tight_layout()
plt.savefig("6_boxplot_severe.png", bbox_inches="tight", dpi=150)
plt.close()

fig, ax = plt.subplots()
sns.regplot(data=df_pat, x="avg_pm25_2024", y="ASTHMA_REASON_ENCOUNTER")
ax.set_title("Air pollution VS Asthma encounters")
plt.tight_layout()
plt.savefig("6_regplot.png", bbox_inches="tight", dpi=150)
plt.close()

# export patient data to csv file

df_pat.to_csv("week_6_data.csv", index=False)


# Week 7

print("WEEK 7")

# 1.1 Import the dataset from the previous exercise. Select one parameter to represent children’s asthma disease severity and another to represent the level of air pollution each child is exposed to. 
# Print the descriptive statistics for the demographic information as well as these parameters. Ensure you understand the type and scale of the data you are working with.
# Note: Check if you see dependencies between your selected parameters and the children’s demographics. Adjust your parameters if needed.

# Import dataset from previous exercise
df = pd.read_csv("week_6_data.csv")

# We have stayed with our original primary parameters in order to stay true to our solution: "IS_SEVERE"
# But in order for the counts to match and outliers to show as intended we have matched up the other chosen parameters to the Exercise Feedback.

df_analysis = df[['DEATHDATE', 'RACE', 'ETHNICITY', 'GENDER', 'CURRENT_AGE', 'TOTAL_ENCOUNTER', 'ASTHMA_REASON_ENCOUNTER', 'URGENT_CARE_ENCOUNTER', 'ASTHMA_FU_ENCOUNTER', 'avg_pm25_2023', 'IS_SEVERE', 'HIGH_POLLUTION']]

# Print the descriptive statistics for the demographic information as well as these parameters.
print("Descriptive statistics in file \"decriptive_week7.csv\"")
df_analysis.describe(include="all").to_csv("decriptive_week7.csv", sep=';', index=False)

# 1.2 Examine your dataset for potential outliers. 
# Identify any extreme values using visual and statistical methods (e.g. box plots, percentile values) for your primary parameters and the demographic information. 
# Decide if you need to exclude extreme outliers based on a 5% cut-off of the highest and lowest data values and perform it if necessary.

# Boxplot for visual analysis
for column in df_analysis:
    # Box plot
    sns.boxplot(df_analysis[column])
    graph_title = "Box Plot for " + column
    plt.title(graph_title)
    plt.savefig("7_" + column + "_boxplot.png", bbox_inches="tight", dpi=150)
    plt.close()
    

# Percentile outlier removal
upper_percentile_rank = np.percentile(df_analysis['TOTAL_ENCOUNTER'], 95)
df_analysis = df_analysis[df_analysis['TOTAL_ENCOUNTER'] <= upper_percentile_rank]


# 1.3 Check for and handle any other quality issues in your dataset like duplicate records. Print the count of unique records before and after duplicate removal.

print(f"Count of unique records before: {len(df_analysis)}")
df_analysis = df_analysis.drop_duplicates()
df_analysis = df_analysis[df_analysis['DEATHDATE'].isna()]
print(f"Count of unique records after: {len(df_analysis)}")


# 2 HYPOTHESIS DEFINITION AND TESTING

# 2.1 State the research hypothesis.
print("2.1 Hypothesis")
print(
        "H0 (null hypothesis): There is no association between high air pollution exposure "
        "(HIGH_POLLUTION) and severe asthma (IS_SEVERE) in children.\n"
        "H1 (alternative hypothesis): Children exposed to high air pollution are more likely "
        "to have severe asthma than children exposed to low air pollution."
    )

# 2.2 Choose and apply an appropriate statistical test.
print("2.2 Statistical testing")

print(f"\nSample size after cleaning: n = {len(df_analysis)}")
print("\nBoth primary parameters are binary/categorical (IS_SEVERE, HIGH_POLLUTION), "
          "so a chi-square test of independence is appropriate.")

contingency_table = pd.crosstab(df_analysis["IS_SEVERE"], df_analysis["HIGH_POLLUTION"])
print("\nContingency table (IS_SEVERE vs HIGH_POLLUTION):")
print(contingency_table)

print("\nGroup balance (HIGH_POLLUTION):")
print(df_analysis["HIGH_POLLUTION"].value_counts())

chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
print("\nSelected test: Chi-square test of independence")
print("Assumptions: independent observations; expected frequencies >= 5 per cell.")
print(f"Test statistic (chi-square): {chi2:.4f}")
print(f"Degrees of freedom: {dof}")
print(f"p-value: {p_value:.4e}")
alpha = 0.05
if p_value < alpha:
    print(
            f"Interpretation: p < {alpha}, so we reject H0. There is a statistically significant "
            "association between high pollution exposure and severe asthma in this cohort."
        )
else:
    print(
            f"Interpretation: p >= {alpha}, so we fail to reject H0. No statistically significant "
            "association was detected between pollution level and asthma severity."
        )


# 3 DATA EXPORT AND REPORTING

# 3.1 Export the cleaned and analyzed dataset.
export_file = "week_7_cleaned_data.csv"
df_analysis.to_csv(export_file, index=False)

print()

# Week 9




