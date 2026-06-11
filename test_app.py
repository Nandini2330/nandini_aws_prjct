import unittest
import io
import time
from app import app, get_db_connection

class VirtualClassroomTests(unittest.TestCase):
    def setUp(self):
        # Configure Flask application for testing
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Generate unique test data for each run
        self.test_username = f"student_{int(time.time())}"
        self.test_password = "password123"
        self.test_filename = f"test_material_{int(time.time())}.txt"

    def test_scenario_1_student_registration_and_login(self):
        """
        Scenario 1: Student Registration and Access
        Action: Register a new student, log in, and access course materials.
        """
        print("\nRunning Scenario 1: Student Registration and Access...")
        
        # 1. Register a new student
        response = self.client.post('/register', data={
            'username': self.test_username,
            'password': self.test_password
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Student Login", response.data)
        print("-> Student successfully registered.")

        # 2. Log in as student
        response = self.client.post('/login', data={
            'username': self.test_username,
            'password': self.test_password
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Materials", response.data)
        print("-> Student successfully logged in and accessed Dashboard.")

    def test_scenario_2_and_3_instructor_upload_and_download(self):
        """
        Scenario 2 & 3: Instructor Uploads Materials & Downloading Course Content
        Action: Log in as instructor, upload new course materials, verify availability,
        access course content, download files, and ensure they are retrieved from S3.
        """
        print("\nRunning Scenario 2: Instructor Uploads Materials...")
        
        # 1. Log in as instructor
        response = self.client.post('/instructor', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Upload Material", response.data)
        print("-> Instructor logged in successfully.")

        # 2. Upload a test file to S3
        file_data = {
            'file': (io.BytesIO(b"Hello World from S3 test file!"), self.test_filename)
        }
        response = self.client.post('/upload', data=file_data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"File Uploaded Successfully", response.data)
        print(f"-> Successfully uploaded '{self.test_filename}' to S3.")

        print("\nRunning Scenario 3: Downloading Course Content...")
        
        # 3. Verify availability on the dashboard
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.test_filename.encode(), response.data)
        print(f"-> Verified '{self.test_filename}' is available on the Dashboard.")

        # 4. Request download and verify S3 redirection
        response = self.client.get(f'/download/{self.test_filename}')
        self.assertEqual(response.status_code, 302)
        location = response.headers.get('Location')
        self.assertIsNotNone(location)
        self.assertIn("s3.amazonaws.com", location)
        self.assertIn(self.test_filename, location)
        print("-> Verified redirection to S3 presigned URL.")
        print(f"-> S3 URL: {location}")

if __name__ == '__main__':
    unittest.main()
