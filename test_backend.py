import unittest
from backend import app

# Checks if the backend API is running correctly
class BackendTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Library API is running!', response.data)

if __name__ == '__main__':
    unittest.main()
