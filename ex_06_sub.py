###################################################################
# # Lecture: Clinical Research Informatics - Sommer Semester 2026
# Exercise Sheet: 6 
   
# Additional information:   
# used additional packages: os, seaborn, matplotlib   
# dataset used: cri_air_pollution.csv
#               week_5_data.csv
###################################################################

# Please add this header to all your submissions and adapt it to your information and submission.
# The following structure is a recommendation, but not mandatory to use


import os.path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.expand_frame_repr', False)

# 1.1	Import the air quality dataset and familiarize yourself with this dataset. 
# Print the number of counties for which the data is available.

patient = pd.read_csv(os.path.join("data", "working_data", "week_5_data.csv")) 
air_pollution = pd.read_csv(os.path.join("data", "week_6", "cri_air_pollution.csv"))

print(patient.head())

print(air_pollution.head())

print(f"Counties available: {air_pollution['County'].nunique()}")

# 1.2	Transform the longitudinal air quality dataset into a format that can be merged
# with cross-sectional tables. Merge it with your data from last week’s exercise (see task 3.1).

air_pollution_wide = air_pollution.pivot(
    index="County",
    columns="Year",
    values="Measurement_avg pm25").reset_index().rename(columns={"County": "COUNTY"})

# Flatten column names: int years → labelled strings
air_pollution_wide.columns = (
    ["COUNTY"] + [f"pm25_{int(y)}" for y in air_pollution_wide.columns[1:]]
)

# Merge the air pollution data with the patient data. We will use a left join to keep all patients, 
# and add air pollution data where available based on the CITY/COUNTY match.
patient = pd.merge(patient, air_pollution_wide, how="left", left_on="CITY",              
right_on="COUNTY")

# Drop the duplicates
patient = patient.drop(columns=["COUNTY_x", "COUNTY_y"])

# 2.1	Explore the air quality data by using descriptive statistics and data visualization. 
# What relations do you see with your asthma severity measures? 
# defining severity columns and air pollution columns for later use in analyses and visualizations

pm25_cols = [c for c in patient.columns if c.startswith("pm25_")]
patient["pm25_mean"] = patient[pm25_cols].mean(axis=1)

severity_cols = [
    "pm25_mean",
    "EMERGENCY_ENCOUNTER",
    "ASTHMA_REASON_ENCOUNTER",
    "SYMPTOM_ENCOUNTER",
    #"ACTIVE_ALLERGY_COUNT",
    #"ACTIVE_CAREPLAN_COUNT",
    "URGENT_CARE_ENCOUNTER",
    "ASTHMA_FU_ENCOUNTER"
]
# descriptive statistics

print("=== PM2.5 Stats ===")                                                             
print(patient[pm25_cols].describe())
print("\n=== Severity Stats ===")
print(patient[severity_cols].describe())

# using pairplot for a general overview of relationships between air pollution and severity measures. 
# We will do more specific analyses later, 
# but this is a good starting point to get a sense of the data.

pairplot = sns.pairplot(
    patient[severity_cols].dropna(),
    diag_kind="kde",
    plot_kws={"alpha": 0.4, "s": 15}
)
pairplot.savefig(os.path.join("data", "week_6", "severity_pairplot.png"), bbox_inches="tight", dpi=150)
plt.close() 

# Correlation heatmap to see the strength of relationships between air pollution and severity measures.

corr = patient[severity_cols].corr()

fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="viridis", ax=ax)
ax.set_title("Correlation Matrix of PM2.5 and Severity Measures", fontsize=16)
plt.tight_layout()
plt.savefig(os.path.join("data", "week_6", "correlation_heatmap.png"), bbox_inches="tight", dpi=150)
plt.close()

# 2.2	Create categories, that allows you to explore the relationship between air pollution and asthma severity.
# Note: Remember one of the earlier exercises where we discussed, how binary groups like urban vs. rural areas might be 
# helpful to answer research questions.

# Binary split at the median
median_pm25 = patient["pm25_mean"].median()
patient["pm25_group"] = pd.cut(
    patient["pm25_mean"],
    bins=[-float("inf"), median_pm25, float("inf")],
    labels=["Low PM2.5", "High PM2.5"]
)

print(patient.groupby("pm25_group")[severity_cols].mean().round(2))

# 2.3	Create at least two data visualizations for the exploration of disease severity vs. air pollution.

palette = {'High PM2.5': '#3e4989', 'Low PM2.5': '#26828e'}

fig, axes = plt.subplots(2, 4, figsize=(18, 9), sharey=False)
axes = axes.flatten()

for ax, col in zip(axes, severity_cols):
    sns.boxplot(
        data=patient,
        x='pm25_group', y=col,
        order=['Low PM2.5', 'High PM2.5'],
        palette=palette,
        flierprops={"marker": ".", "markersize": 3, "alpha": 0.4},
        ax=ax
    )
    ax.set_title(col.replace("_", " ").title(), fontsize=10)
    ax.set_xlabel("")
    ax.set_ylabel("Count", fontsize=9)

# hide the unused 8th subplot
axes[-1].set_visible(False)

fig.suptitle("Asthma Severity by PM2.5 Exposure Category", fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig(os.path.join("data", "week_6", "severity_boxplots.png"), bbox_inches="tight", dpi=150)
plt.close()

# bar chart: mean severity by PM2.5 group                                        

fig, axes = plt.subplots(2, 4, figsize=(18, 9), sharey=False)
axes = axes.flatten()

for ax, col in zip(axes, severity_cols):                                          
    sns.barplot(                                                                  
        data=patient,                                                             
        x="pm25_group",                                                           
        y=col,                                                                    
        order=["Low PM2.5", "High PM2.5"],                                        
        palette=palette,
        errorbar=None,  # remove error bars for cleaner look                                                      
        ax=ax,                                                                    
    )                                                                             
    ax.set_title(col.replace("_", " ").title(), fontsize=10)                      
    ax.set_xlabel("")                                                             
    ax.set_ylabel("Mean Count", fontsize=9)                                       
                                                                            
axes[-1].set_visible(False)                                                       
                                                                            
fig.suptitle("Mean Asthma Severity by PM2.5 Exposure Category", fontsize=13, y=1.01)                                                                         
plt.tight_layout()                                                               
plt.savefig(os.path.join("data", "week_6", "severity_barplot.png"), bbox_inches="tight", dpi=150)
plt.close()

# 3.1	Please export a single DataFrame that contains all variables you want to analyse further on. 
# This should include demographic data, clinical data and the air quality measures. Export this into a csv file.

patient.to_csv(os.path.join("data", "week_6", "week_6_data.csv"), index=False)
