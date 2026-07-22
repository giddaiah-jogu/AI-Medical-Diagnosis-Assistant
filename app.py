import sqlite3
from flask import Flask, render_template, request
import joblib
import pandas as pd

app = Flask(__name__)

# Load trained model
model = joblib.load("model.pkl")

# Load disease information
disease_info = pd.read_csv("disease_info.csv")


# Create database table automatically
def create_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disease TEXT,
        description TEXT,
        precautions TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Disease prediction
@app.route("/predict", methods=["POST"])
def predict():

    # Get symptoms from form
    symptoms = [
        int(request.form.get("fever", 0)),
        int(request.form.get("cough", 0)),
        int(request.form.get("headache", 0)),
        int(request.form.get("fatigue", 0)),
        int(request.form.get("body_pain", 0)),
        int(request.form.get("sore_throat", 0)),
        int(request.form.get("nausea", 0))
    ]


    # Predict disease
    prediction = model.predict([symptoms])[0]


    # Get disease details
    info = disease_info[disease_info["disease"] == prediction]


    if not info.empty:
        description = info.iloc[0]["description"]
        precautions = info.iloc[0]["precautions"]

    else:
        description = "No information available."
        precautions = "Consult a doctor."


    # Save prediction history
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO history(disease, description, precautions)
        VALUES (?, ?, ?)
        """,
        (prediction, description, precautions)
    )

    conn.commit()
    conn.close()


    # Show result page
    return render_template(
        "result.html",
        disease=prediction,
        description=description,
        precautions=precautions
    )


# Prediction history page
@app.route("/history")
def history():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM history")

    records = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        records=records
    )


# Run application
if __name__ == "__main__":

    create_database()

    app.run(debug=True)