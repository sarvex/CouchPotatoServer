from pyutil.jsonutil import decoder
from pyutil.jsonutil import encoder
from twisted.trial.unittest import SkipTest, TestCase


class TestSpeedups(TestCase):
    def test_scanstring(self):
        if not encoder.c_encode_basestring_ascii:
            raise SkipTest("no C extension speedups available to test")
        self.assertEqual(decoder.scanstring.__module__, "simplejson._speedups")
        self.assertTrue(decoder.scanstring is decoder.c_scanstring)

    def test_encode_basestring_ascii(self):
        if not encoder.c_encode_basestring_ascii:
            raise SkipTest("no C extension speedups available to test")
        self.assertEqual(encoder.encode_basestring_ascii.__module__, "simplejson._speedups")
        self.assertTrue(encoder.encode_basestring_ascii is
                          encoder.c_encode_basestring_ascii)
