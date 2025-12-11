import pandas as pd
import numpy as np


n = 2000

np.random.seed(42)

df = pd.DataFrame({
    "user_id": np.random.randint(1, 300, n),
    "time_of_day": np.random.randint(0, 24, n),
    "country": np.random.choice(["KSA", "Unknown", "HighRiskCountry"], n, p=[0.8, 0.1, 0.1]),
    "device_type": np.random.choice(["mobile", "desktop"], n, p=[0.7, 0.3]),
    "failed_logins_last_hour": np.random.poisson(0.5, n),
    "action_type": np.random.choice(["view", "pay", "renew_passport", "update_mobile"], n),
    "is_vpn": np.random.choice([0, 1], n, p=[0.9, 0.1]),
    "typing_speed": np.clip(np.random.normal(4, 1, n), 1, 10) 
})


df["label"] = (
    ((df.country != "KSA") & (df.time_of_day >= 22)) |  
    (df.failed_logins_last_hour >= 3) |                 
    ((df.is_vpn == 1) & (df.action_type == "renew_passport")) |
    ((df.typing_speed < 2) & (df.country != "KSA"))     
).astype(int)

df.to_csv("gart_data.csv", index=False)
print("Saved gart_data.csv with", len(df), "rows")
