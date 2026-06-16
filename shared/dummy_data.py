import pandas as pd

def sample_summary_data():
    return pd.DataFrame([
        {"center": "DWC", "records": 124, "recovery_rate": 82, "workers": 14},
        {"center": "WWC", "records": 98, "recovery_rate": 76, "workers": 11},
        {"center": "Rural", "records": 76, "recovery_rate": 68, "workers": 9},
    ])
