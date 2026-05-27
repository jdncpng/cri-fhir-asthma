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

# --------------------------------------------------
# Functions
# --------------------------------------------------

import sys
from datetime import date
from pathlib import Path

import pandas as pd

def asthma_Find(df, pat_list):
    new_df = df[df['PATIENT'].isin(pat_list)]
    return new_df

# --------------------------------------------------
# Main Script

if __name__ == "__main__":

  
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


 


# 1.1 Select and download one of the provided datasets from Moodle. These sets contain synthetic medical data as .csv files. 
# Please import these files as Pandas DataFrames, and provide print statements, that show for each file the number of variables (columns) and entries (rows).

dataframes = {}
for name, filename in DATA_FILES.items():
    df = pd.read_csv("Coding Data 02 - standard/" + filename, parse_dates=date_columns[name])
    dataframes[name] = df
    #print("{}: {} variables (columns), {} entries (rows)".format(filename, df.shape[1], df.shape[0]))

patients = dataframes["patients"]
conditions = dataframes["conditions"]


# 1.4 In our study, we want to include only children with a Childhood asthma diagnosis.  
# Create a method that allows to filter the imported DataFrames (e.g. conditions, encounter, …) to only include children with the diagnosis. 
# Print the number of records before and after filtering. 

# From conditions getting people effected
filtered_conditions = conditions.query('CODE == 233678006')
print(f"conditions.csv - Number of records before: {len(conditions)}")
print(f"conditions.csv - Number of records after: {len(filtered_conditions)}")

# List of relevant people
asthma_pat = pd.DataFrame(filtered_conditions["PATIENT"])
df = asthma_pat.drop_duplicates(subset=['PATIENT'])
asthma_list = asthma_pat['PATIENT'].tolist()

# This is just a singular processing of patients.csv. It could also be incorporated into the loop with try or renaming of columns. Same logic to ther being a global DataFrame where the new ones are stored. But I dont think that's the point of the execersize.
filtered_patients = patients[patients['Id'].isin(asthma_list)]
print(f"patients.csv - Number of records before: {len(patients)}")
print(f"patients.csv - Number of records after: {len(filtered_patients)}")

# Iterating over the different DataFrames
for name, filename in DATA_FILES.items():

    if(name == "conditions"):
        continue

    if(name == "patients"):
        continue

    records_before = dataframes[name].shape[0]

    filtered_df = asthma_Find(dataframes[name], asthma_list)

    records_after = len(filtered_df) 

    print(f"{filename} - Number of records before: {records_before}")
    print(f"{filename} - Number of records after: {records_after}")


#How many children have more than one condition? 

affected = conditions[conditions['PATIENT'].isin(asthma_list)]
df_amount = affected.groupby(["PATIENT"]).count()
df_more = df_amount.query('CODE > 1')
print(f"Number of people with Childhood asthma with more than one condition: {len(df_more)}")

# What is the maximum number of conditions associated with a patient?

df_max = df_more["CODE"].max()
print(f"Maximum number of conditions associated with a patient: {df_max}")
