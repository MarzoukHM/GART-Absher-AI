GART – Absher AI Behavior Guard

GART (Governmental AI Risk Tracker) is a lightweight behavioral-risk engine that analyzes login patterns and flags suspicious digital-identity activity for government platforms such as Absher.

The system combines rule-based behavioral deviation scoring with a machine-learning model trained on simulated cyber-attack patterns.

Features

Real-time behavioral deviation scoring

Machine-learning attack prediction

SOC dashboard with analytics & charts

Login anomaly simulation

Full Absher-green cybersecurity UI

Custom animated cyber background (JavaScript canvas)

Technology Stack

Python

Streamlit

Scikit-learn

Pandas

JavaScript (background animation)

Custom CSS (UI/UX styling)

 Model & Data Files

The ML model is loaded from gart_model.pkl

Training data is generated using generate_data.py

User behavior logs are stored in gart_user_history.csv

 How to Run the App

Run the Streamlit app
streamlit run app.py

The UI will open in your browser.
