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
#   used additional packages: {Package name and version}
#   dataset used: {dataset or file name}
###################################################################

# Please add this header to all your submissions and adapt it to your information and submission.
# The following structure is a recommendation, but not mandatory to use

from datetime import date
import numpy as np
import pandas as pd

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

def get_encounter_numbers_per_patient(df_enc, code):
    return df_enc[df_enc["CODE"] == code]["PATIENT"].value_counts()

# --------------------------------------------------
# Main Script
# --------------------------------------------------

# Week 5

print("WEEK 5")
# Please import these files as Pandas DataFrames, 
# and provide print statements, that show for each file the number of variables (columns) and entries (rows).
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
# Provide print statements showing the average patient age and average age at condition start.

patients["current_age"] = calc_current_age(patients["BIRTHDATE"])
dataframes["conditions"] = add_age_at_condition_start(dataframes["conditions"], patients)

print("Average patient age: {:.2f} years".format(patients["current_age"].mean()))
print("Average age at condition start: {:.2f} years".format(dataframes["conditions"]["age_at_start"].mean()))


# In our study, we want to analyse children with a current age between 6 and 12. 
# Create a method that filters the patient table to only include records with a current age within that range. 
# Print the number of records before and after filtering.

records_before = len(patients)
patients_children_6_12 = filter_patients_by_age(patients, min_age=6, max_age=12)
records_after = len(patients_children_6_12.index)

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
print(f"Only affected Children: {len(asthma_child)}")

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
print(f"Number of children with asthma with more than one condition: {len(df_more)}")

# What is the maximum number of conditions associated with a patient?

df_max = df_more["CODE"].max()
print(f"Maximum number of conditions associated with a patient: {df_max}")


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

print()

# Week 6 

# Week 7 L

# Week 8 

# Week 9 L




