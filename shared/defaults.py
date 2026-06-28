from copy import deepcopy

DEFAULTS = {
    "common": {
        "entry_grid": {
            "num_columns": 3,
            "date_format": "%d-%m-%Y",
        },
        "units": {
            "hrs": "hrs",
            "count": "count",
            "kg": "kg",
        },
    },
    "dwc": {
        "handling": {
            "title": "Dry Waste Handling",
            "fields": [
                {"key": "workman_hours", "label": "Workman Hours", "unit": "hrs", "default": None},
                {"key": "number_absent", "label": "Number absent", "unit": "count", "default": 0},
                {"key": "power_outage_hours", "label": "Duration of power outages", "unit": "hrs", "default": 0},
                {"key": "municipal_waste", "label": "Municipal waste", "unit": "kg", "default": None},
                {"key": "other_waste", "label": "Other waste delivery", "unit": "kg", "default": None},
                {"key": "total_workman_hours", "label": "Total Workman Hours", "unit": "hrs", "default": None},
                {"key": "adjusted_for_variance", "label": "Adjusted for variance", "unit": "kg", "default": 0},
                {"key": "vehicle_trips", "label": "Vehicle trips", "unit": "count", "default": 15},
                {"key": "workforce", "label": "Workforce", "unit": "count", "default": 25},
                {"key": "ld", "label": "LD", "unit": "kg", "default": None},
                {"key": "rafia", "label": "Rafia", "unit": "kg", "default": None},
                {"key": "straps", "label": "Straps", "unit": "kg", "default": None},
                {"key": "milk", "label": "Milk", "unit": "kg", "default": None},
                {"key": "oil", "label": "Oil", "unit": "kg", "default": None},
                {"key": "assorted_plastics", "label": "Assorted Plastics", "unit": "kg", "default": None},
                {"key": "other_hvp", "label": "Other HVP", "unit": "kg", "default": None},
                {"key": "low_value_plastics", "label": "Low value plastics", "unit": "kg", "default": None},
                {"key": "paper", "label": "Paper", "unit": "kg", "default": None},
                {"key": "other_paper", "label": "Other paper", "unit": "kg", "default": None},
                {"key": "cardboard", "label": "Cardboard", "unit": "kg", "default": None},
                {"key": "leather_and_rubber", "label": "Leather and rubber", "unit": "kg", "default": None},
                {"key": "recyclable_glass", "label": "Recyclable glass", "unit": "kg", "default": None},
                {"key": "reusable_glass", "label": "Reusable glass", "unit": "kg", "default": None},
                {"key": "e_waste", "label": "E waste", "unit": "kg", "default": None},
                {"key": "aluminium", "label": "Aluminium", "unit": "kg", "default": None},
                {"key": "scrap_metal", "label": "Scrap Metal", "unit": "kg", "default": None},
                {"key": "other_metals", "label": "Other metals", "unit": "kg", "default": None},
                {"key": "compostable_mixed_waste", "label": "Compostable Mixed waste", "unit": "kg", "default": None},
                {"key": "inert_waste", "label": "Inert waste", "unit": "kg", "default": None},
                {"key": "incinerable_waste_ss", "label": "Incinerable Waste SS", "unit": "kg", "default": None},
                {"key": "incinerable_waste_ds", "label": "Incinerable Waste DS", "unit": "kg", "default": None},
                {"key": "others_rdf", "label": "Others RDF", "unit": "kg", "default": None},
            ],
        },
        "dispatch": {
            "title": "Dry Waste Dispatch",
            "fields": [
                {"key": "hvp", "label": "HVP", "unit": "kg", "default": None},
                {"key": "lvp", "label": "LVP", "unit": "kg", "default": None},
                {"key": "paper", "label": "Paper", "unit": "kg", "default": None},
                {"key": "cardboard", "label": "Cardboard", "unit": "kg", "default": None},
                {"key": "leather_and_rubber", "label": "Leather and rubber", "unit": "kg", "default": None},
                {"key": "reusable_glass", "label": "Reusable glass", "unit": "kg", "default": None},
                {"key": "recyclable_glass", "label": "Recyclable glass", "unit": "kg", "default": None},
                {"key": "ewaste_and_metal", "label": "Ewaste and metal", "unit": "kg", "default": None},
                {"key": "misc", "label": "Misc", "unit": "kg", "default": None},
            ],
        },
    },
    "wwc": {},
    "rural": {},
}


def get_defaults():
    return deepcopy(DEFAULTS)
