"""
Main test script to run all tests.
"""

import unittest
from ..src.core.config import settings
from ..src.utils.logger import *

# from .tests.test_module import TestModule


if __name__ == "__main__":
    add_file_handler(settings.LOG_PATH + "/test.log")
    unittest.main()
