import unittest
import requests

# This test checks the integration between adding a book and renting it via the backend API.
class IntegrationTestCase(unittest.TestCase):
    def test_add_and_rent_book(self):
        # Add a new book
        book = {
            'name': 'Test Book',
            'author': 'Test Author',
            'date_published': '2025',
            'category': 'Test Category'
        }
        add_resp = requests.post('http://127.0.0.1:5050/media', json=book)
        self.assertTrue(add_resp.json().get('success'))
        # Rent the book
        rent_resp = requests.post('http://127.0.0.1:5050/rent', json={'book_name': 'Test Book'})
        self.assertTrue(rent_resp.json().get('success'))

if __name__ == '__main__':
    unittest.main()
