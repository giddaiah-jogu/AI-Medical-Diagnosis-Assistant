import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib

# Load dataset
data = pd.read_csv("symptoms.csv")

# Features
X = data.drop("disease", axis=1)

# Target
y = data["disease"]

# Train model
model = DecisionTreeClassifier(random_state=42)
model.fit(X, y)

# Save model
joblib.dump(model, "model.pkl")

print("Model trained successfully!")