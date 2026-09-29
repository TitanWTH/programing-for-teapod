from pathlib import Path
import math
import pandas as pd

BASE = Path.cwd()
DATA = BASE / "data"
OUTPUTS = BASE / "outputs"
OUTPUTS.mkdir(exist_ok=True)


n = 4
lab_value = "А"
min_ram = 8
max_power = 90
scenario_hours = 6


df = pd.read_csv(
    DATA / "devices_02.csv",
    dtype={
        "device_id": "string",
        "lab": "string",
        "device_type": "string",
        "status": "string"
    }
)

source = df.copy()

print("Shape:", df.shape)
print("Columns:", list(df.columns))
print("\nFirst 3 rows:")
print(df.head(3))
print("\nNumber of missing values:")
print(df.isna().sum())
print("\nTypes of power_w and hours_h:")
print(df[["power_w", "hours_h"]].dtypes)


print("\nFirst three rows via iloc:")
print(df.iloc[0:3][["device_id", "lab"]])

by_id = df.set_index("device_id")

print("\nCodes 001, 002, 003 via loc:")
print(by_id.loc[["001", "002", "003"], ["lab", "ram_gb"]])

print("\nSlice iloc[0:3]:")
print(by_id.iloc[0:3])

print("\nSlice loc['001':'003']:")
print(by_id.loc["001":"003"])

enriched = df.copy()

enriched["energy_kwh"] = (
    enriched["power_w"] * enriched["hours_h"] / 1000
)

enriched["below_target"] = False
enriched.loc[enriched["ram_gb"] < 32, "below_target"] = True

enriched.to_csv(
    OUTPUTS / "enriched_02.csv",
    index=False,
    encoding="utf-8"
)

print("\nEnergy of device 002:")
energy_002 = enriched.loc[
    enriched["device_id"] == "002", "energy_kwh"
].iloc[0]

print(energy_002)
print("Check:", math.isclose(
    energy_002,
    0.48,
    rel_tol=0,
    abs_tol=1e-12
))

mask = (
    (enriched["status"] == "operational")
    & (enriched["ram_gb"] >= 16)
    & (enriched["power_w"] <= 80)
)

selected = enriched.loc[
    mask,
    [
        "device_id",
        "lab",
        "ram_gb",
        "power_w",
        "hours_h",
        "energy_kwh",
        "below_target"
    ]
].sort_values(
    ["ram_gb", "device_id"],
    ascending=[False, True]
).reset_index(drop=True)

selected.to_csv(
    OUTPUTS / "selected_02.csv",
    index=False,
    encoding="utf-8"
)

print("\nCommon selection:")
print(selected)

print("\nCodes:", selected["device_id"].tolist())
print("Total energy:", selected["energy_kwh"].sum())

variant_mask = (
    (enriched["status"] == "operational")
    & (enriched["lab"] == lab_value)
    & (enriched["ram_gb"] >= min_ram)
    & (enriched["power_w"] <= max_power)
)

result = enriched.loc[
    variant_mask,
    [
        "device_id",
        "lab",
        "ram_gb",
        "power_w",
        "hours_h",
        "energy_kwh",
        "below_target"
    ]
].copy()

result["hours_h"] = scenario_hours
result["energy_kwh"] = (
    result["power_w"] * result["hours_h"] / 1000
)

result = result.sort_values(
    ["ram_gb", "power_w", "device_id"],
    ascending=[False, True, True]
).reset_index(drop=True)

result.to_csv(
    OUTPUTS / "variant_04_02.csv",
    index=False,
    encoding="utf-8"
)

print("\nVariant 4:")
print(result)

cases = pd.read_csv(
    DATA / "cases_02.csv",
    dtype={
        "device_id": "string",
        "lab": "string",
        "device_type": "string",
        "status": "string",
        "ram_gb": "Int64"
    }
)

cases_mask = (
    (cases["status"] == "operational")
    & (cases["ram_gb"] >= 16)
    & (cases["power_w"] <= 80)
).fillna(False)

cases_selected = cases.loc[cases_mask]

print("\nBoundary records:")
print(cases_selected["device_id"].tolist())

print("Number of unknown RAM values:", cases["ram_gb"].isna().sum())


empty_mask = (
    (enriched["status"] == "operational")
    & (enriched["lab"] == lab_value)
    & (enriched["ram_gb"] >= 1024)
    & (enriched["power_w"] <= max_power)
)

empty_result = enriched.loc[empty_mask]

print("\nEmpty sample:")
if empty_result.empty:
    print("No matches found.")
else:
    print(empty_result)


print("\nSource unchanged:", df.equals(source))

expected_codes = ["003", "009", "015", "002", "008", "014"]

assert selected["device_id"].tolist() == expected_codes
assert math.isclose(
    selected["energy_kwh"].sum(),
    2.385,
    rel_tol=0,
    abs_tol=1e-12
)

assert cases_selected["device_id"].tolist() == ["B01", "B05"]
assert empty_result.empty
assert df.equals(source)

print("\nAll checks passed.")