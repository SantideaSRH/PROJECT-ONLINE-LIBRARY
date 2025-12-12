from flask import Flask, request, jsonify
from flask_cors import CORS
import threading

# Load the book data from Book_library.py
from Book_library import library_data

app = Flask(__name__)
CORS(app)

# In-memory data for this session
books = library_data['media']
books_lock = threading.Lock()

def save_books():
    # Optionally, implement saving to file if you want persistence
    pass

@app.route('/sort', methods=['GET'])
def sort_books():
    by = request.args.get('by') or (request.json.get('by') if request.is_json else None)
    with books_lock:
        if by == 'year':
            sorted_books = sorted(books, key=lambda b: b.get('date_published', ''))
        elif by == 'category':
            sorted_books = sorted(books, key=lambda b: b.get('category', ''))
        else:
            sorted_books = list(books)
    return jsonify(sorted_books)

@app.route('/search', methods=['GET', 'POST'])
def search_books():
    if request.method == 'POST':
        data = request.get_json() or {}
        query = data.get('query', '').strip().lower()
        year = data.get('year', '').strip()
        category = data.get('category', '').strip().lower()
    else:
        query = request.args.get('query', '').strip().lower()
        year = request.args.get('year', '').strip()
        category = request.args.get('category', '').strip().lower()
    with books_lock:
        results = books
        if query:
            results = [b for b in results if query in b['name'].lower() or query in b['author'].lower()]
        if year:
            results = [b for b in results if year in b['date_published']]
        if category:
            results = [b for b in results if category in b['category'].lower()]
    return jsonify(results)

@app.route('/media', methods=['POST'])
def add_book():
    data = request.get_json()
    required = ['name', 'author', 'date_published', 'category']
    if not all(k in data and data[k] for k in required):
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
    with books_lock:
        if any(b['name'].lower() == data['name'].lower() for b in books):
            return jsonify({'success': False, 'message': 'Book already exists.'}), 400
        new_book = {
            'name': data['name'],
            'author': data['author'],
            'date_published': data['date_published'],
            'category': data['category'],
            'available': True
        }
        books.append(new_book)
        save_books()
    return jsonify({'success': True, 'message': 'Book added successfully!'})

@app.route('/media/<book_name>', methods=['DELETE'])
def delete_book(book_name):
    with books_lock:
        for i, b in enumerate(books):
            if b['name'].lower() == book_name.lower():
                del books[i]
                save_books()
                return jsonify({'success': True, 'message': 'Book deleted successfully!'})
    return jsonify({'success': False, 'message': 'Book not found.'}), 404

@app.route('/rent', methods=['POST'])
def rent_book():
    data = request.get_json()
    book_name = data.get('book_name', '').strip()
    if not book_name:
        return jsonify({'success': False, 'message': 'Book name required.'}), 400
    with books_lock:
        for b in books:
            if b['name'].lower() == book_name.lower():
                if not b['available']:
                    return jsonify({'success': False, 'message': 'Book is already rented.'}), 400
                b['available'] = False
                save_books()
                return jsonify({'success': True, 'message': f"You have rented '{b['name']}'!"})
    return jsonify({'success': False, 'message': 'Book not found.'}), 404

@app.route('/return', methods=['POST'])
def return_book():
    data = request.get_json()
    book_name = data.get('book_name', '').strip()
    if not book_name:
        return jsonify({'success': False, 'message': 'Book name required.'}), 400
    with books_lock:
        for b in books:
            if b['name'].lower() == book_name.lower():
                if b['available']:
                    return jsonify({'success': False, 'message': 'Book is already available.'}), 400
                b['available'] = True
                save_books()
                return jsonify({'success': True, 'message': f"You have returned '{b['name']}'!"})
    return jsonify({'success': False, 'message': 'Book not found.'}), 404

@app.route('/')
def index():
    return 'Library API is running!'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5050, debug=True)
