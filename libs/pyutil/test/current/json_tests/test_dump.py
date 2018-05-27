from io import StringIO
from unittest import TestCase

from pyutil import jsonutil as json


class TestDump(TestCase):
    def test_dump(self):
        sio = StringIO()
        json.dump({}, sio)
        self.assertEqual(sio.getvalue(), '{}')

    def test_dumps(self):
        self.assertEqual(json.dumps({}), '{}')
