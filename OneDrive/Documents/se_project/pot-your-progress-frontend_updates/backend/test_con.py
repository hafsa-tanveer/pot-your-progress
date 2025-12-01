import unittest
import json
import time
from app import app
from db import get_db_connection

class AuthTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Unique email so tests don't fail on "User already exists" every time
        unique_id = int(time.time())
        self.test_user = {
            "name": "Test User",
            "email": f"auto_test_{unique_id}@example.com",
            "password": "SecurePassword123!"
        }

    def test_1_database_connection(self):
        """Test if Python can reach Oracle"""
        print("\n--- 1. Testing Database Connection ---")
        conn = get_db_connection()
        self.assertIsNotNone(conn, "❌ Connection Failed")
        print(f"✅ Connected to DB Version: {conn.version}")
        conn.close()

    def test_2_signup(self):
        """Test Registering (Encrypted)"""
        print("\n--- 2. Testing Signup ---")
        response = self.app.post('/auth/signup', 
                                 data=json.dumps(self.test_user),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        print("✅ Signup Successful (201 Created)")

    def test_3_login(self):
        """Test Login with same credentials"""
        print("\n--- 3. Testing Login ---")
        # First register the user (in case test_2 didn't run first)
        self.app.post('/auth/signup', 
                      data=json.dumps(self.test_user),
                      content_type='application/json')

        # Now Login
        login_data = {
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        }
        response = self.app.post('/auth/login', 
                                 data=json.dumps(login_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.data).get("token")
        print(f"✅ Login Successful (Token: {token})")

    def test_4_logout(self):
        """Test Logout"""
        print("\n--- 4. Testing Logout ---")
        response = self.app.post('/auth/logout')
        self.assertEqual(response.status_code, 200)
        print("✅ Logout Successful")

if __name__ == '__main__':
    unittest.main()