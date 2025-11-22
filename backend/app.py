from flask import Flask
from flask_cors import CORS
import logging
from auth.routes import auth_bp 

# 1. SETUP LOGGING (Info level shows all requests)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = "super_secret_key_for_session" 

# 2. SETUP CORS
CORS(app, supports_credentials=True)

# 3. REGISTER ROUTES
app.register_blueprint(auth_bp, url_prefix="/auth")

@app.route("/")
def home():
    return {"message": "Habit Garden Backend is Running!"}

if __name__ == "__main__":
    app.run(debug=True)