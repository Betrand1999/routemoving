from flask import Flask, render_template, request
import boto3
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Amazon SES Client
ses_client = boto3.client(
    "ses",
    region_name=os.getenv("AWS_REGION")
)

# MongoDB Client
mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client[os.getenv("MONGO_DB")]
quotes_collection = db[os.getenv("MONGO_COLLECTION")]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/submit-quote", methods=["POST"])
def submit_quote():
    full_name = request.form.get("full_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    move_date = request.form.get("move_date")
    pickup_location = request.form.get("pickup_location")
    destination = request.form.get("destination")
    service_needed = request.form.get("service_needed")
    message = request.form.get("message")

    quote_data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "move_date": move_date,
        "pickup_location": pickup_location,
        "destination": destination,
        "service_needed": service_needed,
        "message": message,
        "created_at": datetime.utcnow()
    }

    try:
        # Save quote request to MongoDB
        quotes_collection.insert_one(quote_data)

        email_body = f"""
New Moving Quote Request

Customer Information
---------------------
Full Name: {full_name}
Email: {email}
Phone: {phone}

Move Details
---------------------
Move Date: {move_date}
Pickup Location: {pickup_location}
Destination: {destination}
Service Needed: {service_needed}

Additional Message
---------------------
{message}
"""

        # Send email notification
        ses_client.send_email(
            Source=os.getenv("SENDER_EMAIL"),
            Destination={
                "ToAddresses": [
                    os.getenv("RECEIVER_EMAIL")
                ]
            },
            Message={
                "Subject": {
                    "Data": f"New Quote Request - {full_name}"
                },
                "Body": {
                    "Text": {
                        "Data": email_body
                    }
                }
            }
        )

        return render_template("success.html")

    except Exception as e:
        return f"""
        <h1>Submission Failed</h1>
        <p>Error: {str(e)}</p>
        <a href='/contact'>Go Back</a>
        """


if __name__ == "__main__":
    app.run(debug=True)