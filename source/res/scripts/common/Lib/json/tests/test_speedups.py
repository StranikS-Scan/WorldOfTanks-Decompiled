# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/json/tests/test_speedups.py
from json.tests import CTest

class BadBool:

    def __nonzero__(self):
        1 / 0.0


class TestSpeedups(CTest):

    def test_scanstring(self):
        self.assertEqual(self.json.decoder.scanstring.__module__, '_json')
        self.assertIs(self.json.decoder.scanstring, self.json.decoder.c_scanstring)

    def test_encode_basestring_ascii(self):
        self.assertEqual(self.json.encoder.encode_basestring_ascii.__module__, '_json')
        self.assertIs(self.json.encoder.encode_basestring_ascii, self.json.encoder.c_encode_basestring_ascii)


class TestDecode(CTest):

    def test_make_scanner(self):
        self.assertRaises(AttributeError, self.json.scanner.c_make_scanner, 1)

    def test_bad_bool_args(self):

        def test(value):
            self.json.decoder.JSONDecoder(strict=BadBool()).decode(value)

        self.assertRaises(ZeroDivisionError, test, '""')
        self.assertRaises(ZeroDivisionError, test, '{}')
        self.assertRaises(ZeroDivisionError, test, u'""')
        self.assertRaises(ZeroDivisionError, test, u'{}')


class TestEncode(CTest):

    def test_make_encoder(self):
        self.assertRaises(TypeError, self.json.encoder.c_make_encoder, None, "\xcd}=N\x12L\xf9y\xd7R\xba\x82\xf2'J}\xa0\xcau", None)
        return

    def test_bad_bool_args(self):

        def test(name):
            self.json.encoder.JSONEncoder(**{name: BadBool()}).encode({'a': 1})

        self.assertRaises(ZeroDivisionError, test, 'skipkeys')
        self.assertRaises(ZeroDivisionError, test, 'ensure_ascii')
        self.assertRaises(ZeroDivisionError, test, 'check_circular')
        self.assertRaises(ZeroDivisionError, test, 'allow_nan')
        self.assertRaises(ZeroDivisionError, test, 'sort_keys')

    def test_bad_encoding(self):
        with self.assertRaises(UnicodeEncodeError):
            self.json.encoder.JSONEncoder(encoding=u'\udcff').encode({'key': 123})
