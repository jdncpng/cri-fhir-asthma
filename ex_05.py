import os.path
import numpy as np
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.expand_frame_repr', False)


# --------------------------------------------------
# Functions
# --------------------------------------------------

def filter_by_patientlist(df, pat_ids):
    return df[df["PATIENT"].isin(pat_ids)]


def calc_current_age(birthday):
    today = pd.to_datetime('now')
    age = pd.to_timedelta(today - birthday)
    age = age.dt.days / 365.2425
    return np.round(age)


def get_age_of_condition_start(df_pat: pd.DataFrame, df_cond: pd.DataFrame):
    temp = pd.merge(df_cond, df_pat, how="left", left_on="PATIENT", right_on="Id")
    age = pd.to_timedelta(temp["START"] - temp["BIRTHDATE"])
    age = age.dt.days / 365.2425
    return np.round(age)


def filter_by_age_range(df_pat: pd.DataFrame, min_age: int, max_age: int):
    return df_pat[(df_pat['CURRENT_AGE'] >= min_age) & (df_pat['CURRENT_AGE'] <= max_age)]


def get_encounter_numbers_per_patient(df_enc, code):
    return df_enc[df_enc["CODE"] == code]["PATIENT"].value_counts()


# --------------------------------------------------
# Main Script
# --------------------------------------------------

if __name__ == "__main__":
    # 1.1	Select and download one of the provided datasets from Moodle. These sets contain synthetic patient
    # populations as .csv files. Please import these files, and provide a print statements, that show for each file
    # the number of variables (columns) and entries (rows).

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
        df = pd.read_csv(os.path.join("data/2_standard", filename), parse_dates=date_columns[name])
        dataframes[name] = df
        print("{}: {} variables (columns), {} entries (rows)".format(filename, df.shape[1], df.shape[0]))

    df_pat = dataframes["patients"]
    df_cond = dataframes["conditions"]
    df_enc = dataframes["encounters"]
    df_med = dataframes["medications"]
    df_obs = dataframes["observations"]
    df_cp = dataframes["careplans"]
    df_all = dataframes["allergies"]

    print(f"Patients table has {df_pat.columns.size} columns and {df_pat.index.size} rows.")
    print(f"Conditions table has {df_cond.columns.size} columns and {df_cond.index.size} rows.")
    print(f"Encounter table has {df_enc.columns.size} columns and {df_enc.index.size} rows.")
    print(f"Medication table has {df_med.columns.size} columns and {df_med.index.size} rows.")
    print(f"Observation table has {df_obs.columns.size} columns and {df_obs.index.size} rows.")
    print(f"Careplan table has {df_cp.columns.size} columns and {df_cp.index.size} rows.")
    print(f"Allergy table has {df_all.columns.size} columns and {df_all.index.size} rows.")
    print()

    # 1.2	Add the patients current age to the patient DataFrame and their age at the beginning of the conditions to
    # the conditions DataFrame. Provide print statements showing the average patient age and average age
    # at condition start.
    df_pat["CURRENT_AGE"] = calc_current_age(df_pat["BIRTHDATE"])
    df_cond["START_AGE"] = get_age_of_condition_start(df_pat, df_cond)
    print(f"Average age of the patients is {df_pat['CURRENT_AGE'].mean()}.")
    print(f"Average age of condition start is {df_cond['START_AGE'].mean()}.")

    # 1.3	In our study, we want to analyse children with a current age between 6 and 12. Create a method that filters
    # the patient table to only include records with their appropriate current age. Print the number of records before
    # and after your filtering.
    print(f"Patients table has {len(df_pat.index)} rows before filtering.")
    df_pat = filter_by_age_range(df_pat, 6, 12)
    print(f"Patients table has {len(df_pat.index)} rows after filtering.")

    # 1.4	Create a method that allows to filter tables with a given list of patient IDs. Use this method to filter
    # for children who are diagnosed with childhood asthma. Print the number of records before and after your filtering.
    # How many children have more than one condition? What is the maximum number of conditions?

    asthma_patients = df_cond[df_cond["CODE"].isin([233678006])]["PATIENT"]  # filter for childhood asthma
    df_pat = df_pat[df_pat["Id"].isin(asthma_patients)]

    print(f"Patients table has {len(df_pat.index)} rows after filtering for Asthma.")
    print(f"Average age of the patients is {df_pat['CURRENT_AGE'].mean():.0f}.")
    print(f"Conditions table has {len(df_cond.index)} rows before filtering.")
    print(f"Encounter table has {len(df_enc.index)} rows before filtering.")
    print(f"Allergies table has {len(df_all.index)} rows before filtering.")
    print(f"Medications table has {len(df_med.index)} rows before filtering.")
    print(f"Observations table has {len(df_obs.index)} rows before filtering.")
    print(f"Careplans table has {len(df_cp.index)} rows before filtering.")

    df_cond = filter_by_patientlist(df_cond, df_pat["Id"])
    df_enc = filter_by_patientlist(df_enc, df_pat["Id"])
    df_all = filter_by_patientlist(df_all, df_pat["Id"])
    df_med = filter_by_patientlist(df_med, df_pat["Id"])
    df_obs = filter_by_patientlist(df_obs, df_pat["Id"])
    df_cp = filter_by_patientlist(df_cp, df_pat["Id"])

    print(f"Conditions table has {len(df_cond.index)} rows after filtering.")
    print(f"Encounter table has {len(df_enc.index)} rows after filtering.")
    print(f"Allergies table has {len(df_all.index)} rows after filtering.")
    print(f"Medications table has {len(df_med.index)} rows after filtering.")
    print(f"Observations table has {len(df_obs.index)} rows after filtering.")  
    print(f"Careplans table has {len(df_cp.index)} rows after filtering.")


    condition_counts = df_cond["PATIENT"].value_counts()
    num_children_multimorbid = (condition_counts > 1).sum()
    print(f"{num_children_multimorbid} children have more than one condition.")
    print(f"The maximum number of conditions for a child is {condition_counts.max()}.")

    # 2.1	Consider ways to quantify the health status of these asthmatic children. Extract relevant information from
    # the available datasets and add them to the patient DataFrame.

    encounter_counts = df_enc["PATIENT"].value_counts()
    print(f"Average number of encounter: {encounter_counts.mean():.2f}")
    print(f"Maximum number of encounter: {encounter_counts.max()}")

    encounter_frequencies = df_enc["DESCRIPTION"].value_counts()
    condition_frequencies = df_cond["DESCRIPTION"].value_counts()

    df_pat = df_pat.drop_duplicates()
    df_pat.index = df_pat["Id"]
    df_pat["TOTAL_CONDITIONS"] = condition_counts
    df_pat["TOTAL_ENCOUNTER"] = encounter_counts
    df_pat["ASTHMA_REASON_ENCOUNTER"] = df_enc[df_enc["REASONCODE"] == 233678006]["PATIENT"].value_counts()  # encounter due to asthma
    df_pat["SYMPTOM_ENCOUNTER"] = get_encounter_numbers_per_patient(df_enc, 185345009)  # Encounter for symptom
    df_pat["EMERGENCY_ENCOUNTER"] = get_encounter_numbers_per_patient(df_enc, 50849002)  # emergency hospital admission
    df_pat["URGENT_CARE_ENCOUNTER"] = get_encounter_numbers_per_patient(df_enc, 702927004)  # urgent care clinic
    df_pat["ASTHMA_FU_ENCOUNTER"] = get_encounter_numbers_per_patient(df_enc, 394701000)  # asthma follow-up
    df_pat["ACTIVE_ALLERGY_COUNT"] = df_all[df_all["STOP"].isna()].groupby("PATIENT")["CODE"].nunique() # active allergy count (no stop date)
    df_pat["ACTIVE_MEDICATION_COUNT"] = df_med[df_med["STOP"].isna()].groupby("PATIENT")["CODE"].nunique()  # active medication count (no stop date)
    df_pat["ACTIVE_CAREPLAN_COUNT"] = df_cp[df_cp["STOP"].isna()].groupby("PATIENT")["CODE"].nunique()  # active careplan count (no stop date)

    # 3.1	Export your working data into a csv file.
    export_path = os.path.join("data", "working_data")
    os.makedirs(export_path, exist_ok=True)
    df_pat.to_csv(os.path.join(export_path, "week_5_data.csv"), index=None)
