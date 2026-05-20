import json
import pandas as pd
from datetime import date, datetime

# Load the FHIR bundle
with open("/home/oleksandr/Documents/CRI/Dyan186_Purdy2_61b11ebf-b7c1-0bb8-2ded-c5405bd62015.json") as f:
    bundle = json.load(f)

entries = bundle.get("entry", [])

# ─────────────────────────────────────────────
# 1.1 Unique top-level resource types
# ─────────────────────────────────────────────
print("=" * 55)
print("1.1  UNIQUE TOP-LEVEL RESOURCE TYPES")
print("=" * 55)

resource_types = sorted({e["resource"]["resourceType"] for e in entries})
for rt in resource_types:
    print(f"  • {rt}")
print(f"\n  Total unique types: {len(resource_types)}")

# ─────────────────────────────────────────────
# 1.2 Patient information
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("1.2  PATIENT INFORMATION")
print("=" * 55)

patient = next(e["resource"] for e in entries
               if e["resource"]["resourceType"] == "Patient")

name_entry = patient["name"][0]
given  = " ".join(name_entry.get("given", []))
family = name_entry.get("family", "")
prefix = " ".join(name_entry.get("prefix", []))
full_name = f"{prefix} {given} {family}".strip()

dob = patient.get("birthDate", "Unknown")

print(f"  Name          : {full_name}")
print(f"  Date of Birth : {dob}")
print(f"  Gender        : {patient.get('gender', 'Unknown').capitalize()}")

# ─────────────────────────────────────────────
# 2.1 Patient conditions / diagnoses
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("2.1  PATIENT CONDITIONS / DIAGNOSES")
print("=" * 55)

conditions = [e["resource"] for e in entries
              if e["resource"]["resourceType"] == "Condition"]

print(f"  Total conditions found: {len(conditions)}\n")
print(f"  {'#':<4} {'Onset Date':<14} {'Diagnosis'}")
print(f"  {'-'*4} {'-'*14} {'-'*35}")

for i, cond in enumerate(conditions, 1):
    code_text = (cond.get("code", {})
                     .get("coding", [{}])[0]
                     .get("display", "Unknown"))
    onset = cond.get("onsetDateTime", cond.get("onsetPeriod", {}).get("start", "Unknown"))
    onset_date = onset[:10] if onset != "Unknown" else "Unknown"
    print(f"  {i:<4} {onset_date:<14} {code_text}")

# ─────────────────────────────────────────────
# 2.2 Age at first asthma diagnosis
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("2.2  AGE AT FIRST ASTHMA DIAGNOSIS")
print("=" * 55)

asthma_conditions = [
    c for c in conditions
    if "asthma" in (c.get("code", {})
                      .get("coding", [{}])[0]
                      .get("display", "")).lower()
]

if asthma_conditions:
    # Sort by onset date and pick the earliest
    def onset_date(c):
        raw = c.get("onsetDateTime", c.get("onsetPeriod", {}).get("start", ""))
        return raw[:10] if raw else ""

    asthma_conditions.sort(key=onset_date)
    first = asthma_conditions[0]
    first_onset = onset_date(first)
    diagnosis_text = (first.get("code", {})
                           .get("coding", [{}])[0]
                           .get("display", "Unknown"))

    dob_dt       = datetime.strptime(dob, "%Y-%m-%d").date()
    onset_dt     = datetime.strptime(first_onset, "%Y-%m-%d").date()
    age_at_diag  = (onset_dt - dob_dt).days // 365

    print(f"  Diagnosis     : {diagnosis_text}")
    print(f"  Date of Birth : {dob}")
    print(f"  Onset Date    : {first_onset}")
    print(f"  Age at first asthma diagnosis: {age_at_diag} years old")
else:
    print("  No asthma diagnosis found in this patient's record.")

# ─────────────────────────────────────────────
# 3.1 Transform Observations into a DataFrame
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("3.1  OBSERVATIONS → PANDAS DATAFRAME (first 5 rows)")
print("=" * 55)

observations = [e["resource"] for e in entries
                if e["resource"]["resourceType"] == "Observation"]

rows = []
for obs in observations:
    obs_id     = obs.get("id", "")
    status     = obs.get("status", "")
    date_str   = obs.get("effectiveDateTime", "")[:10] if obs.get("effectiveDateTime") else ""
    code_text  = (obs.get("code", {})
                     .get("coding", [{}])[0]
                     .get("display", ""))

    # Value can be a quantity, string, or codeable concept
    value, unit = "", ""
    if "valueQuantity" in obs:
        value = obs["valueQuantity"].get("value", "")
        unit  = obs["valueQuantity"].get("unit", "")
    elif "valueCodeableConcept" in obs:
        value = (obs["valueCodeableConcept"]
                    .get("coding", [{}])[0]
                    .get("display", ""))
    elif "valueString" in obs:
        value = obs["valueString"]

    rows.append({
        "id":         obs_id,
        "date":       date_str,
        "observation": code_text,
        "value":      value,
        "unit":       unit,
        "status":     status,
    })

df_obs = pd.DataFrame(rows)

pd.set_option("display.max_colwidth", 40)
pd.set_option("display.width", 120)
print(f"\n  Total observations: {len(df_obs)}\n")
print(df_obs.head(5).to_string(index=False))
print("\n  Columns:", list(df_obs.columns))