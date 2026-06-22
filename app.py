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


# SEO Pages
@app.route("/moving-company-elyria-oh")
def moving_company_elyria():
    return render_template("moving-company-elyria-oh.html")


@app.route("/local-movers-elyria")
def local_movers_elyria():
    return render_template("local-movers-elyria.html")


@app.route("/residential-moving")
def residential_moving():
    return render_template("residential-moving.html")


@app.route("/commercial-moving")
def commercial_moving():
    return render_template("commercial-moving.html")


@app.route("/packing-services")
def packing_services():
    return render_template("packing-services.html")


@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory("static", "sitemap.xml")


@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")


@app.route("/submit-quote", methods=["POST"])
def submit_quote():
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    move_date = request.form.get("move_date", "").strip()
    pickup_location = request.form.get("pickup_location", "").strip()
    destination = request.form.get("destination", "").strip()
    service_needed = request.form.get("service_needed", "").strip()
    message = request.form.get("message", "").strip()

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
            ReplyToAddresses=[
                email
            ],
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

        print("Email sent successfully")

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