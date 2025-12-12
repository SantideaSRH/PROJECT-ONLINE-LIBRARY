import os
import sys
import requests
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QPushButton, QWidget, QHBoxLayout, QLineEdit, QLabel
from PyQt6.QtCore import Qt

API_BASE_URL = 'http://127.0.0.1:5050'

script_dir = os.path.dirname(__file__)
ui_file_path = os.path.join(script_dir, "mainwindow.ui")

try:
    MainWindowUI, _ = uic.loadUiType(ui_file_path)
except Exception as e:
    print(f"Error loading UI file: {e}")
    print(f"Please ensure '{ui_file_path}' exists in the same directory as this script.")
    sys.exit(1)

class DesktopLibraryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = MainWindowUI()
        self.ui.setupUi(self)
        self.setWindowTitle("Book Library Desktop Dashboard")
        self.all_books_cache = []
        self._setup_ui_elements()
        self._connect_signals()
        self.load_all_books()

    def _setup_ui_elements(self):
        headers = ["Name", "Author", "Date Published", "Category", "Available", "Actions"]
        self.ui.bookTable.setColumnCount(len(headers))
        self.ui.bookTable.setHorizontalHeaderLabels(headers)
        self.ui.bookTable.setColumnWidth(0, 200)
        self.ui.bookTable.setColumnWidth(1, 150)
        self.ui.bookTable.setColumnWidth(2, 100)
        self.ui.bookTable.setColumnWidth(3, 120)
        self.ui.bookTable.setColumnWidth(4, 70)
        self.ui.bookTable.setColumnWidth(5, 120)
        self.ui.bookTable.horizontalHeader().setStretchLastSection(True)
        self.ui.bookTable.verticalHeader().setVisible(False)
        self.ui.bookTable.setSelectionBehavior(self.ui.bookTable.SelectionBehavior.SelectRows)
        self.ui.bookTable.setEditTriggers(self.ui.bookTable.EditTrigger.NoEditTriggers)
        self.ui.bookTable.setSelectionMode(self.ui.bookTable.SelectionMode.SingleSelection)
        self.ui.statusLabel.setText("Welcome to the Book Library Dashboard!")
        # Remove sortSelect and add year/category search bars
        if hasattr(self.ui, 'sortSelect'):
            self.ui.sortSelect.hide()
        # Add year and category search bars if not present
        if not hasattr(self.ui, 'yearSearchInput'):
            self.ui.yearSearchInput = QLineEdit()
            self.ui.yearSearchInput.setPlaceholderText("Search by year...")
            self.ui.categorySearchInput = QLineEdit()
            self.ui.categorySearchInput.setPlaceholderText("Search by category...")
            self.ui.mainVerticalLayout.insertWidget(2, QLabel("Search by Year:"))
            self.ui.mainVerticalLayout.insertWidget(3, self.ui.yearSearchInput)
            self.ui.mainVerticalLayout.insertWidget(4, QLabel("Search by Category:"))
            self.ui.mainVerticalLayout.insertWidget(5, self.ui.categorySearchInput)

    def _connect_signals(self):
        self.ui.searchButton.clicked.connect(self.perform_search)
        self.ui.searchInput.returnPressed.connect(self.perform_search)
        self.ui.addBookButton.clicked.connect(self.add_new_book)
        self.ui.bookTable.itemSelectionChanged.connect(self.display_selected_book_metadata)
        self.ui.yearSearchInput.returnPressed.connect(self.perform_search)
        self.ui.categorySearchInput.returnPressed.connect(self.perform_search)

    def _show_message(self, message, type='info'):
        if type == 'error':
            self.ui.statusLabel.setStyleSheet("color: red;")
            QMessageBox.critical(self, "Error", message)
        elif type == 'success':
            self.ui.statusLabel.setStyleSheet("color: green;")
        else:
            self.ui.statusLabel.setStyleSheet("color: black;")
        self.ui.statusLabel.setText(message)

    def _clear_add_book_form(self):
        self.ui.addNameInput.clear()
        self.ui.addAuthorInput.clear()
        self.ui.addDatePublishedInput.clear()
        self.ui.addCategoryInput.clear()

    def _clear_rent_book_form(self):
        self.ui.rentBookNameInput.clear()

    def _make_api_request(self, endpoint, method='GET', data=None):
        url = f"{API_BASE_URL}{endpoint}"
        try:
            if method == 'GET':
                response = requests.get(url, params=data)
            elif method == 'POST':
                response = requests.post(url, json=data)
            elif method == 'DELETE':
                response = requests.delete(url)
            else:
                raise ValueError("Unsupported HTTP method")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            self._show_message("Could not connect to the Flask API. Is it running?", 'error')
            return None
        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {e}"
            if response is not None and response.content:
                try:
                    error_json = response.json()
                    if 'message' in error_json:
                        error_message = error_json['message']
                except Exception:
                    error_message = response.text
            self._show_message(error_message, 'error')
            return None

    def load_all_books(self):
        books_data = self._make_api_request('/search', data={})
        if books_data is not None:
            self.all_books_cache = books_data
            self._update_book_table(books_data)
            self._show_message(f"Loaded {len(books_data)} books.", 'info')
        else:
            self._update_book_table([])

    def perform_search(self):
        query = self.ui.searchInput.text().strip()
        year = self.ui.yearSearchInput.text().strip()
        category = self.ui.categorySearchInput.text().strip()
        if not query and not year and not category:
            self.load_all_books()
            return
        # Compose search parameters
        params = {}
        if query:
            params['query'] = query
        if year:
            params['year'] = year
        if category:
            params['category'] = category
        search_results = self._make_api_request('/search', data=params)
        if search_results is not None:
            self._update_book_table(search_results)
            self._show_message(f"Found {len(search_results)} book(s) matching your search.", 'info')
        else:
            self._update_book_table([])

    def _update_book_table(self, books):
        self.ui.bookTable.setRowCount(0)
        for row_idx, book in enumerate(books):
            self.ui.bookTable.insertRow(row_idx)
            self.ui.bookTable.setItem(row_idx, 0, QTableWidgetItem(book.get("name", "")))
            self.ui.bookTable.setItem(row_idx, 1, QTableWidgetItem(book.get("author", "")))
            self.ui.bookTable.setItem(row_idx, 2, QTableWidgetItem(book.get("date_published", "")))
            self.ui.bookTable.setItem(row_idx, 3, QTableWidgetItem(book.get("category", "")))
            available_item = QTableWidgetItem("Yes" if book.get("available", False) else "No")
            available_item.setForeground(Qt.GlobalColor.darkGreen if book.get("available", False) else Qt.GlobalColor.red)
            self.ui.bookTable.setItem(row_idx, 4, available_item)
            actions_widget = self._create_actions_widget(book['name'], book['available'])
            self.ui.bookTable.setCellWidget(row_idx, 5, actions_widget)

    def _create_actions_widget(self, book_name, is_available):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(5)
        rent_btn = QPushButton("Rent")
        rent_btn.setEnabled(is_available)
        rent_btn.clicked.connect(lambda: self.rent_book_action(book_name))
        layout.addWidget(rent_btn)
        return_btn = QPushButton("Return")
        return_btn.setEnabled(not is_available)
        return_btn.clicked.connect(lambda: self.return_book_action(book_name))
        layout.addWidget(return_btn)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.delete_book_action(book_name))
        layout.addWidget(delete_btn)
        return widget

    def return_book_action(self, book_name):
        response = self._make_api_request('/return', method='POST', data={'book_name': book_name})
        if response and response.get('success'):
            self._show_message(response.get('message', 'Book returned successfully!'), 'success')
            self.load_all_books()
        elif response:
            self._show_message(response.get('message', 'Failed to return book.'), 'error')

    def display_selected_book_metadata(self):
        pass

    def rent_book_action(self, book_name):
        response = self._make_api_request('/rent', method='POST', data={'book_name': book_name})
        if response and response.get('success'):
            self._show_message(response.get('message', 'Book rented successfully!'), 'success')
            self.load_all_books()
        elif response:
            self._show_message(response.get('message', 'Failed to rent book.'), 'error')

    def delete_book_action(self, book_name):
        reply = QMessageBox.question(self, 'Delete Book',
                                     f"Are you sure you want to delete '{book_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            response = self._make_api_request(f'/media/{book_name}', method='DELETE')
            if response and response.get('success'):
                self._show_message(response.get('message', 'Book deleted successfully!'), 'success')
                self.load_all_books()
            elif response:
                self._show_message(response.get('message', 'Failed to delete book.'), 'error')

    def add_new_book(self):
        name = self.ui.addNameInput.text().strip()
        author = self.ui.addAuthorInput.text().strip()
        date_published = self.ui.addDatePublishedInput.text().strip()
        category = self.ui.addCategoryInput.text().strip()
        if not all([name, author, date_published, category]):
            self._show_message("All fields are required to add a book.", 'error')
            return
        book_data = {
            'name': name,
            'author': author,
            'date_published': date_published,
            'category': category
        }
        response = self._make_api_request('/media', method='POST', data=book_data)
        if response and response.get('success'):
            self._show_message('Book added successfully!', 'success')
            self._clear_add_book_form()
            self.load_all_books()
        elif response:
            self._show_message(response.get('message', 'Failed to add book.'), 'error')

    def rent_selected_book(self):
        book_name = self.ui.rentBookNameInput.text().strip()
        if not book_name:
            self._show_message("Please enter the name of the book to rent.", 'error')
            return
        self.rent_book_action(book_name)
        self._clear_rent_book_form()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DesktopLibraryApp()
    window.show()
    sys.exit(app.exec())