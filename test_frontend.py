import unittest
from PyQt6.QtWidgets import QApplication
import sys
from desktop_library_app import DesktopLibraryApp

class FrontendTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def test_window_title(self):
        window = DesktopLibraryApp()
        self.assertEqual(window.windowTitle(), "Book Library Desktop Dashboard")

if __name__ == '__main__':
    unittest.main()
