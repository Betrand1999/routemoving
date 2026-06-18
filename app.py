from flask import Flask, render_template, request, send_from_directory
import boto3
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Load environment variables for local development
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Environment variables
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# Amazon SES Client
ses_client = boto3.client(
    "ses",
    region_name=AWS_REGION
)

# MongoDB Client
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]
quotes_collection = db[MONGO_COLLECTION]


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

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory("static", "sitemap.xml")


@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")


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

        ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={
                "ToAddresses": [
                    RECEIVER_EMAIL
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
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)