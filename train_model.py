import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import joblib

df = pd.read_csv("gart_data.csv")

X = df.drop("label", axis=1)
y = df["label"]

cat_cols = ["country", "device_type", "action_type"]
num_cols = ["user_id", "time_of_day", "failed_logins_last_hour", "is_vpn", "typing_speed"]

preprocess = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ("num", "passthrough", num_cols)
    ]
)

model = Pipeline(steps=[
    ("preprocess", preprocess),
    ("clf", RandomForestClassifier(
        n_estimators=150,
        random_state=42,
        class_weight="balanced"
    ))
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model.fit(X_train, y_train)

score = model.score(X_test, y_test)
print("Test accuracy:", round(score * 100, 2), "%")

joblib.dump(model, "gart_model.pkl")
print("Saved model to gart_model.pkl")
