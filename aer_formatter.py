import numpy as np
import pandas as pd


def get_input_or_return_default(ask_str, default, num_response=False):
    response = input(ask_str)
    if num_response:
        response = float(response) if response else default
    else:
        response = response if response else default
    
    return response


print("\n---HEADER---")
comment = get_input_or_return_default("File comments: ", "No comment")

print("\n---TEST CONDITIONS---")
reference_velocity = get_input_or_return_default(
    "Reference velocity (Default = 60 kmh): ",
    60,
    num_response=True
    )
reference_density = get_input_or_return_default(
    "Reference density (Default = 1): ",
    1,
    num_response=True
)
front_ride_height_min = get_input_or_return_default(
    "Minimum front ride height (Default = 0): ",
    0,
    num_response=True
)
front_ride_height_max = get_input_or_return_default(
    "Maximum front ride height (Default = 100): ",
    100,
    num_response=True
)
rear_ride_height_min = get_input_or_return_default(
    "Minimum rear ride height (Default = 0): ",
    0,
    num_response=True
)
rear_ride_height_max = get_input_or_return_default(
    "Maximum rear ride height (Default = 100): ",
    100,
    num_response=True
)
drag_arm_height_min = get_input_or_return_default(
    "Minimum drag arm height (Default = -50): ",
    -50,
    num_response=True
)
drag_arm_height_max = get_input_or_return_default(
    "Maximum drag arm height (Default = 800): ",
    800,
    num_response=True
)


# Calculates constant downforce and drag values given CL, CD, and A
# Also distributes downforce to front and rear 
print("\n---AERO PARAMS---")

frontal_area = float(input("Frontal area (m^2): "))
coeff_lift = float(input("CL: "))
coeff_drag = float(input("CD: "))
front_aero_balance = float(input("Front balance: "))
if front_aero_balance < 0 or front_aero_balance > 1:
    raise ValueError("Invalid aero balance")

downforce = -(1/2)*1.2*coeff_lift*frontal_area*0.278*reference_velocity**2
front_downforce = downforce * front_aero_balance
rear_downforce = downforce - front_downforce
drag = (1/2)*1.2*coeff_drag*frontal_area*0.278*reference_velocity**2

print(
    f"Front downforce: {front_downforce}N" \
    f"\tRear downforce: {rear_downforce}N" \
    f"\tDrag: {drag}N"
)


# Prepare lookup tables for .aer file
z_data = pd.DataFrame(
    np.linspace(rear_ride_height_min, rear_ride_height_max, 5)                  # Rear ride height vector / Z data
)

front_ride_height_vec = pd.DataFrame(
    np.linspace(front_ride_height_min, front_ride_height_max, 5)                # Front ride height vector
)
front_downforce_matrix = pd.DataFrame(
    np.full((5, 5), front_downforce)                                                 # Front downforce matrix
)
rear_downforce_matrix = pd.DataFrame(
    np.full((5, 5), rear_downforce)                                                  # Rear downforce matrix
)
drag_matrix = pd.DataFrame(
    np.full((5, 5), drag)                                                            # Drag matrix
)

front_xy_data = pd.concat(
    [front_ride_height_vec, front_downforce_matrix], axis=1                     # Front XY table
)
rear_xy_data = pd.concat(
    [front_ride_height_vec, rear_downforce_matrix], axis=1                      # Rear XY table
)
drag_xy_data = pd.concat(
    [front_ride_height_vec, drag_matrix], axis=1                                # Drag XY table
)


path = input("\nOutput path: ")
print(f"\nWriting to {path}...")

with open(path, 'w') as file:
    file.write(
        "$---------------------------------------------------------------------MDI_HEADER						" \
        "\n[MDI_HEADER]" \
        "\nFILE_TYPE\t=\t'aer'" \
        "\nFILE_VERSION\t=\t5" \
        "\nFILE_FORMAT\t=\t'ASCII'" \
        "\n(COMMENTS)" \
        "\n{comment_string}" \
        f"\n'{comment}'" \
        "\n$--------------------------------------------------------------------------UNITS						" \
        "\n[UNITS]" \
        "\n(BASE)" \
        "\n{length\tforce\tangle\tmass\ttime}" \
        "\n'mm'\t'N'\t'degree'\t'kg'\t'sec'" \
        "\n(USER)" \
        "\n{unit_type\tlength\tforce\tangle\tmass\ttime\tconversion}" \
        "\n'kmh'\t1\t0\t0\t0\t-1\t277.77778" \
        "\n'ride_height'\t1\t0\t0\t0\t0\t1" \
        "\n$----------------------------------------------------------------TEST_CONDITIONS						" \
        "\n[TEST_CONDITIONS]" \
        f"\nreference_velocity\t<kmh>\t=\t{reference_velocity}" \
        f"\nreference_density\t=\t{reference_density}" \
        f"\nfront_ride_height_min\t<ride_height>\t=\t{front_ride_height_min}" \
        f"\nfront_ride_height_max\t<ride_height>\t=\t{front_ride_height_max}"
        f"\nrear_ride_height_min\t<ride_height>\t=\t{rear_ride_height_min}"
        f"\nrear_ride_height_max\t<ride_height>\t=\t{rear_ride_height_max}"
        f"\nDRAG_ARM_HEIGHT_MIN\t=\t{drag_arm_height_min}" \
        f"\nDRAG_ARM_HEIGHT_MAX\t=\t{drag_arm_height_max}" \
        "\n$----------------------------------------------------------------FRONT_DOWNFORCE						" \
        "\n[FRONT_DOWNFORCE]" \
        "\n(Z_DATA)" \
        "\n{rear_ride_height\t<ride_height>}" \
        f"\n{z_data.to_csv(sep='\t', index=False, header=False)}" \
        "(XY_DATA)" \
        "\n{front_ride_height\t<ride_height>\tdownforce\t<force>}" \
        f"\n{front_xy_data.to_csv(sep='\t', index=False, header=False)}" \
        "$-----------------------------------------------------------------REAR_DOWNFORCE						" \
        "\n[REAR_DOWNFORCE]" \
        "\n(Z_DATA)" \
        "\n{rear_ride_height\t<ride_height>}" \
        f"\n{z_data.to_csv(sep='\t', index=False, header=False)}" \
        "(XY_DATA)" \
        "\n{front_ride_height\t<ride_height>\tdownforce\t<force>}" \
        f"\n{rear_xy_data.to_csv(sep='\t', index=False, header=False)}" \
        "$---------------------------------------------------------------------------DRAG						" \
        "\n[DRAG]" \
        "\n(z_DATA)" \
        "\n{rear_ride_height\t<ride_height>}" \
        f"\n{z_data.to_csv(sep='\t', index=False, header=False)}" \
        "(XY_DATA)" \
        "\n{front_ride_height\t<ride_height>\tdrag\t<force>}" \
        f"\n{drag_xy_data.to_csv(sep='\t', index=False, header=False)}"
    )

print("Done!")
