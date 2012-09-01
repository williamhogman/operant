"""Tests for operant"""

import sys

# Python 3.3 and greater ship with mock built-in
try:
    import unittest.mock
except ImportError:
    import mock
else:
    sys.modules["mock"] = unittest.mock
