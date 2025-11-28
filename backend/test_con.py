import unittest
import json
import time
from app import app

class AuthTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        unique_id = int(time.time())
        self.test_user = {
            "name": "Test User",
            "email": f"auto_test_{unique_id}@example.com",
            "password": "SecurePassword123!"
        }

    def test_1_signup(self):
        print("\n--- 1. Testing Signup ---")
        response = self.app.post('/auth/signup', 
                                 data=json.dumps(self.test_user),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        print("✅ Signup Successful")

    def test_2_login(self):
        print("\n--- 2. Testing Login ---")
        
        # Register user again in case test_1 didn't run first
        self.app.post('/auth/signup',
                      data=json.dumps(self.test_user),
                      content_type='application/json')

        login_data = {
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        }
        response = self.app.post('/auth/login', 
                                 data=json.dumps(login_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        print("✅ Login Successful")

    def test_3_logout(self):
        print("\n--- 3. Testing Logout ---")
        response = self.app.post('/auth/logout')
        self.assertEqual(response.status_code, 200)
        print("✅ Logout Successful")

if __name__ == '__main__':
    unittest.main()
