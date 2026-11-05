from flask import Flask, request, jsonify  # Import necessary modules from Flask
from pymongo import MongoClient  # Import MongoClient to interact with MongoDB
from datetime import datetime  # Import datetime to get the current time
import os  # Import os to access environment variables

# Initialize the Flask application
app = Flask(__name__)

# Set up the MongoDB client.
#
# The connection string is built so that the app works both locally and inside
# Kubernetes. Authentication is now enabled, so a username/password are required.
#
# Two ways to provide the connection details:
#   1. A full connection URI via the MONGODB_URI environment variable, OR
#   2. Individual components (host, username, password) which are assembled below.
#
# In Kubernetes the username/password come from a Secret and the host is the
# MongoDB headless Service DNS name (e.g. "mongodb-0.mongodb"). The credentials
# are authenticated against the "admin" database (authSource=admin), which is
# where MongoDB creates the root user.

MONGODB_URI = os.environ.get("MONGODB_URI")

if not MONGODB_URI:
    mongo_host = os.environ.get("MONGODB_HOST", "localhost")
    mongo_port = os.environ.get("MONGODB_PORT", "27017")
    mongo_user = os.environ.get("MONGODB_USERNAME")
    mongo_pass = os.environ.get("MONGODB_PASSWORD")
    auth_source = os.environ.get("MONGODB_AUTH_SOURCE", "admin")

    if mongo_user and mongo_pass:
        # Build an authenticated URI.
        MONGODB_URI = (
            f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/"
            f"?authSource={auth_source}"
        )
    else:
        # Fall back to an unauthenticated local connection (useful for Part 1).
        MONGODB_URI = f"mongodb://{mongo_host}:{mongo_port}/"

client = MongoClient(MONGODB_URI)

# Connect to the database named 'flask_db'
db = client.flask_db

# Connect to the collection named 'data' within the 'flask_db' database
collection = db.data


# Define the route for the root URL
@app.route('/')
def index():
    # Return a welcome message with the current time
    return f"Welcome to the Flask app! The current time is: {datetime.now()}"


# Define the route for the '/data' endpoint
# This endpoint supports both GET and POST methods
@app.route('/data', methods=['GET', 'POST'])
def data():
    if request.method == 'POST':
        # If the request method is POST, get the JSON data from the request
        data = request.get_json()
        # Insert the data into the 'data' collection in MongoDB
        collection.insert_one(data)
        # Return a success message with status code 201 (Created)
        return jsonify({"status": "Data inserted"}), 201
    elif request.method == 'GET':
        # If the request method is GET, retrieve all documents from the 'data' collection
        # Convert the documents to a list, excluding the '_id' field
        data = list(collection.find({}, {"_id": 0}))
        # Return the data as a JSON response with status code 200 (OK)
        return jsonify(data), 200


# Lightweight health endpoint used by Kubernetes liveness/readiness probes.
@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200


# Run the Flask application
# The application will listen on all available IP addresses (0.0.0.0) and port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
