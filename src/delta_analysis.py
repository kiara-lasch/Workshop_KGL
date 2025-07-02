#%%
from pathlib import Path
import pandas as pd
import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

# Import combined_data for each climate scenario (ssp126, ssp245, ssp585)
Combined_data_ssp126 = pd.read_csv(Path("../data/raw/deltas_30_ssp126_decr.csv"))
Combined_data_ssp245 = pd.read_csv(Path("../data/raw/deltas_30_ssp245_decr.csv"))
Combined_data_ssp585 = pd.read_csv(Path("../data/raw/deltas_30_ssp585_decr.csv"))

# %%
# Specify constant variables
riv_levee = 5
prop_width = 6
distance = 10000

# ADVANCE ---------------------------------------------------------------------------------------------
def advance(slope, distance, coastline, SLR, VLM, riv_dis, sed_dis):
    """
    This function calculates the volume required to extend the coastline seaward, the pump capacity, 
    and the number of years required to fill the new coastline with sediment.
    
    Parameters: 
    slope (float): the offshore slope from the coastline (degrees)
    distance (float): the distance that the coastline is extended offshore (m) 
    coastline (float): the length of the coastline (m)
    SLR (float): the expected sea level rise of the delta under the given scenario (m)
    VLM (float): the vertical land motion of the delta (m)
    riv_dis (float): the mean annual river discharge of the delta (m3/s)
    sed_dis (float): the mean annual sediment discharge of the delta (kg/s)

    Returns:
    offshore_depth_incl_SLR (float): the offshore depth of the delta, consdering sea level rise (m)
    sand_req_adv (float): the volume of sand required to extend the new coastline seaward (m3)
    pump_cap_adv (float): the pump capacity required to pump river discharge from the rivers to the sea (m3/s)
    number_years_adv (float): the number of years required to fill the new coastline with river sediment (years)
    """

    # offshore depth, including sea level rise (m)
    offshore_depth_incl_SLR = (slope * distance) + SLR
    
    # sand required to extent the new coastline (m3)
    depth = slope * distance
    V = 0.5 * depth * distance * coastline
    RSLR = SLR - VLM
    sand_req_adv = V + (distance * RSLR * coastline)

    # pump capacity (m3/s)
    pump_cap_adv = riv_dis

    # number of years to fill new coastline (yrs)
    Sed_dis_m3s = sed_dis / 1600 
    time_seconds = sand_req_adv / Sed_dis_m3s
    number_years_adv = time_seconds / (365 * 24 * 60 * 60)

    return offshore_depth_incl_SLR, sand_req_adv, pump_cap_adv, number_years_adv


#%%
# PROTECT-CLOSED --------------------------------------------------------------------------------------
def protect_closed(ss, swh, SLR, prop_width, coastline, VLM, riv_dis):
    # Material requirements for levees along coast
    h = 3 * (ss + swh)                              # Dike height
    b1 = h                                          # Base1
    b2 = h * prop_width                             # 1:6 ratio
    V_trap = 0.5 * (b1 + b2) * h * coastline        # Volume (trapezium only)
    RSLR = SLR - VLM                                # Relative sea level rise equation (SLR - VLM)
    levee_req_pc = V_trap + (RSLR * b2 * coastline) # Volume (incl. subsidence)`

    # Pump capacity 
    pump_cap_pc = riv_dis                           # divide by 1600kg/m3 to convert from kg/s to m3/s

    return levee_req_pc, pump_cap_pc


# PROECT-OPEN -----------------------------------------------------------------------------------------
def protect_open(ss, swh, SLR, prop_width, riv_levee, coastline, VLM, riv_wid, riv_len):
    # Material requirements for levees along coast and rivers
    h_c = 3 * (ss + swh)  # Levee height along coast (calc with wave height)
    b1_c = h_c  # Base1 (short base)
    b2_c = h_c * prop_width  # 1:6 ratio (long base)
    L_c = coastline - riv_wid  # Length_to_build = coastline - river width
    V_trap_c = 0.5 * (b1_c + b2_c) * h_c * L_c  # Volume (trapezium only)
    RSLR = SLR - VLM  # relative sea level rise equation (SLR - VLM)
    V_levee_c = V_trap_c + (RSLR * b2_c * L_c)  # Volume (incl. subsidence)

    h_r = riv_levee  # Levee height along river. Assume it is 5m high (was 5 before it was river_lev)
    b1_r = h_r  # Base1 (short base)
    b2_r = h_r * prop_width  # 1:6 ratio (long base)
    L_r = riv_len  # Length_to_build_along_river = river length
    V_trap_r = 0.5 * (b1_r + b2_r) * h_r * L_r  # Volume (trapezium only)
    V_levee_r = (
        V_trap_r + (RSLR * b2_r * L_r) * 2
    )  # Volume (incl subsidence) --> * 2 for both sides of the river

    levee_req_po = V_levee_c + V_levee_r

    # River width for storm surge barriers
    river_width_po = riv_wid

    return levee_req_po, river_width_po


# ACCOMMODATE ---------------------------------------------------------------------------------------------
volume_to_fill_columns = [
    "whole_urban_inundated_volume",
    "total_inundation_volume",
    "urban_inundated_volume",
]
# whole_urban_inundated_volume = if no flooding in certain urban areas, assume we raise it by mean flood depth
# total_inundation_volume = the volume to be filled if the whole flooded area is filled
# urban_inundated_volume = volume to fill if we only fill the urban_flooded volume

def accommodate(acc_raise_0p5, acc_raise_1, acc_raise_10, sed_dis, volume_to_fill):
    # Urban flooded area raising through stilts
    acc_raise_0p5 = acc_raise_0p5
    acc_raise_1 = acc_raise_1
    acc_raise_10 = acc_raise_10

    # Years to collect sediment for natural land raising
    sed_dis = sed_dis / 1600  # Convert from kg/s to m3/s
    time_seconds = volume_to_fill / sed_dis
    number_years_acc = time_seconds / (365 * 24 * 60 * 60)  # Convert seconds to years

    return number_years_acc


# RETREAT ---------------------------------------------------------------------------------------------
to_retreat_to_columns = ["urban_non_inundated_area", "non_inundated_area"]
# urban_non_inundated_area = retreat to urban areas that aren't flooded
# outside_delta = whatever makes it "yes" in threshold (took out for now -------?)
# non_inundated_area = retreat to non_flooded areas within delta


def retreat(urban_flooded_area, retreat_to):
    # Land avaliability (bigger than 1 is good)
    land_avaliability = retreat_to / urban_flooded_area

    return land_avaliability


# ------------------------------------------------------------------------------------------------------
# APPLY EQUATIONS --------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

# Define the result lists for each SSP scenario
Equation_results_ssp126 = []
Equation_results_ssp245 = []
Equation_results_ssp585 = []

# List of datasets and corresponding result containers
datasets = [
    (Combined_data_ssp126, Equation_results_ssp126),
    (Combined_data_ssp245, Equation_results_ssp245),
    (Combined_data_ssp585, Equation_results_ssp585),
]

# Loop through each dataset and its corresponding result list
for dataset, subset_results in datasets:
    for index, row in dataset.iterrows():
        BasinID2 = row["BasinID2"]
        SLR = row["SLR"]
        VLM = row["VLM_value"]
        slope = row["Bathymetric_Slope_from_RM_Sbr"]
        coastline = row["Coastline_length"]
        riv_dis = row["Discharge_dist"]  # river discharge
        sed_dis = row["QRiver_dist"]  # sediment discharge
        ss = row["Storm_surge_height"]
        swh = row["Wave_Height_Hw"]
        riv_wid = row["Total_river_width"]
        riv_len = row["Total_river_length"]
        flood_depth = row["inundation_depth"]
        urban_flooded_area = row["urban_inundated_area"]
        acc_raise_0p5 = row["acc_raise_0p5"]
        acc_raise_1 = row["acc_raise_1"]
        acc_raise_10 = row["acc_raise_10"]

        # Store the results for the delta
        delta_results = []

        # ADVANCE calculation for each distance (3 rows per delta)
        offshore_depth_incl_SLR, sand_req_adv, pump_cap_adv, number_years_adv = advance(
            slope, distance, coastline, SLR, VLM, riv_dis, sed_dis
        )
        delta_results.append(
            {
                "BasinID2": BasinID2,
                "depth_10km_offshore_inclSLR": offshore_depth_incl_SLR,
                "sand_req_adv": sand_req_adv,
                "pump_cap_adv": pump_cap_adv,
                "number_years_adv": number_years_adv,
            }
        )

        # PROTECT-CLOSED calculation (one row per delta)
        levee_req_pc, pump_cap_pc = protect_closed(
            ss, swh, SLR, prop_width, coastline, VLM, riv_dis
        )
        for result in delta_results:
            result.update({"levee_req_pc": levee_req_pc, "pump_cap_pc": pump_cap_pc})

        # PROTECT-OPEN calculation (one row per delta)
        levee_req_po, river_width_po = protect_open(
            ss, swh, SLR, prop_width, riv_levee, coastline, VLM, riv_wid, riv_len
        )
        for result in delta_results:
            result.update(
                {"levee_req_po": levee_req_po, "river_width_po": river_width_po}
            )

        # ACCOMMODATE calculation
        for volume_to_fill_col in volume_to_fill_columns:
            volume_to_fill = row[volume_to_fill_col]
            number_years_acc = accommodate(
                acc_raise_0p5, acc_raise_1, acc_raise_10, sed_dis, volume_to_fill
            )
            for result in delta_results:
                result.update(
                    {
                        "acc_raise_0p5": acc_raise_0p5,
                        "acc_raise_1": acc_raise_1,
                        "acc_raise_10": acc_raise_10,
                        f"{volume_to_fill_col}_number_years_acc": number_years_acc,
                    }
                )

        # RETREAT calculation for each retreat area (same 3 rows)
        for to_retreat_to_col in to_retreat_to_columns:
            to_retreat_to = row[to_retreat_to_col]
            if to_retreat_to == 0:
                to_retreat_to = 1e-10  # Make it a very small number
            if urban_flooded_area == 0:
                land_availability = 9999  # (easier to distinguish later. also makes it automatically 1, so possible (bigger than 0)
            else:
                land_availability = retreat(urban_flooded_area, to_retreat_to)
            for result in delta_results:
                result.update(
                    {f"{to_retreat_to_col}_land_availability": land_availability}
                )

        # Add the delta results to the final result set
        subset_results.extend(delta_results)

# Convert results to DataFrames
Equation_results_ssp126 = pd.DataFrame(Equation_results_ssp126)
Equation_results_ssp245 = pd.DataFrame(Equation_results_ssp245)
Equation_results_ssp585 = pd.DataFrame(Equation_results_ssp585)

# ------------------------------------------------------------------------------------------------------
# THRESHOLD ANALYSIS -----------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

# Apply thresholds and create new columns
for dataset in [
    Equation_results_ssp126,
    Equation_results_ssp245,
    Equation_results_ssp585,
]:
    # Advance
    dataset["adv_1200"] = dataset["pump_cap_adv"].apply(lambda x: 1 if x < 1200 else 0)
    dataset["adv_600"] = dataset["pump_cap_adv"].apply(lambda x: 1 if x < 600 else 0)
    dataset["adv_12000"] = dataset["pump_cap_adv"].apply(
        lambda x: 1 if x < 12000 else 0
    )

    dataset["adv_number_years_50"] = dataset["number_years_adv"].apply(
        lambda x: 1 if x < 50 else 0
    )
    dataset["adv_number_years_100"] = dataset["number_years_adv"].apply(
        lambda x: 1 if x < 100 else 0
    )
    dataset["adv_number_years_25"] = dataset["number_years_adv"].apply(
        lambda x: 1 if x < 25 else 0
    )

    # Advance - Combined indicator
    dataset["adv_offshore_depth_30"] = dataset["depth_10km_offshore_inclSLR"].apply(
        lambda x: 1 if x < 30 else 0
    )
    dataset["adv_offshore_depth_3"] = dataset["depth_10km_offshore_inclSLR"].apply(
        lambda x: 1 if x < 3 else 0
    )
    dataset["adv_offshore_depth_60"] = dataset["depth_10km_offshore_inclSLR"].apply(
        lambda x: 1 if x < 60 else 0
    )

    # Protect-closed
    dataset["pc_1200"] = dataset["pump_cap_adv"].apply(lambda x: 1 if x < 1200 else 0)
    dataset["pc_600"] = dataset["pump_cap_adv"].apply(lambda x: 1 if x < 600 else 0)
    dataset["pc_12000"] = dataset["pump_cap_adv"].apply(lambda x: 1 if x < 12000 else 0)

    # Protect-open
    dataset["po_9"] = dataset["river_width_po"].apply(lambda x: 1 if x < 9000 else 0)
    dataset["po_4p5"] = dataset["river_width_po"].apply(
        lambda x: 1 if x < 4500 else 0
    )  # 4500 m = 4.5km
    dataset["po_90"] = dataset["river_width_po"].apply(lambda x: 1 if x < 90000 else 0)

    # Accommodate
    dataset["acc_raise_1"] = dataset["acc_raise_1"]
    dataset["acc_raise_0p5"] = dataset["acc_raise_0p5"]
    dataset["acc_raise_10"] = dataset["acc_raise_10"]

    # Retreat
    dataset["ret_urb_ni_area"] = dataset[
        "urban_non_inundated_area_land_availability"
    ].apply(lambda x: 1 if x > 1 else 0)
    dataset["ret_ni_area"] = dataset["non_inundated_area_land_availability"].apply(
        lambda x: 1 if x > 1 else 0
    )
    dataset["ret_out_delta"] = 1

# Calculate thresholds for each SSP scenario separately
# Extract the relevant columns for threshold analysis
columns_to_extract = [
    "BasinID2",
    "adv_1200",
    "adv_600",
    "adv_12000",
    "adv_number_years_50",
    "adv_number_years_100",
    "adv_number_years_25",
    "adv_offshore_depth_30",
    "adv_offshore_depth_3",
    "adv_offshore_depth_60",
    "pc_1200",
    "pc_600",
    "pc_12000",
    "po_9",
    "po_4p5",
    "po_90",
    "acc_raise_1",
    "acc_raise_0p5",
    "acc_raise_10",
    "ret_ni_area",
    "ret_urb_ni_area",
    "ret_out_delta",
]

# Create the threshold analysis datasets for each SSP scenario
threshold_analysis_ssp126 = Equation_results_ssp126[columns_to_extract].drop_duplicates(
    subset=["BasinID2"]
)
threshold_analysis_ssp245 = Equation_results_ssp245[columns_to_extract].drop_duplicates(
    subset=["BasinID2"]
)
threshold_analysis_ssp585 = Equation_results_ssp585[columns_to_extract].drop_duplicates(
    subset=["BasinID2"]
)

# Create only 1 advance column by checking if the pump threshold AND the artificial depth OR the number of years for river sediment is met
# List of datasets
datasets = {
    "threshold_analysis_ssp126": threshold_analysis_ssp126,
    "threshold_analysis_ssp245": threshold_analysis_ssp245,
    "threshold_analysis_ssp585": threshold_analysis_ssp585,
}

# Loop through datasets and apply the logic
for name, df in datasets.items():
    # Calculate Adv_known_Max
    df["adv_CurrentKnown"] = (
        (df["adv_1200"] & df["adv_number_years_50"])
        | (df["adv_1200"] & df["adv_offshore_depth_30"])
    ).astype(int)

    # Calculate Adv_contracted_PSS
    df["adv_Simple"] = (
        (df["adv_600"] & df["adv_number_years_100"])
        | (df["adv_600"] & df["adv_offshore_depth_3"])
    ).astype(int)

    # Calculate Advance_expanded_PSS
    df["adv_Innovative"] = (
        (df["adv_12000"] & df["adv_number_years_25"])
        | (df["adv_12000"] & df["adv_offshore_depth_60"])
    ).astype(int)

# %%
print(threshold_analysis_ssp126.head())
print(threshold_analysis_ssp245.head())
print(threshold_analysis_ssp585.head())

# count how many deltas are in each category with print statement
print(
    "SSP126 - Advance Known Max:", threshold_analysis_ssp126["adv_CurrentKnown"].sum()
)
print("SSP126 - Advance Simple:", threshold_analysis_ssp126["adv_Simple"].sum())
print("SSP126 - Advance Innovative:", threshold_analysis_ssp126["adv_Innovative"].sum())
