from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

load_dotenv()  # Load .env

# import blueprint after environment load
from auth.routes import auth_bp

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Allow frontend to connect to backend
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)


# Register auth blueprint
app.register_blueprint(auth_bp, url_prefix="/auth")

@app.route("/")
def home():
    return {"message": "Backend Running with Supabase!"}

if __name__ == "__main__":
    app.run(debug=True)
