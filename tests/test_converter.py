import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fix_vcard import convert


class ConverterTests(unittest.TestCase):
    def test_qp_chinese_and_photo_removed(self):
        example = ('BEGIN:VCARD\nVERSION:2.1\n'
                   'N;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:;=E6=B5=8B=E8=AF=95;;\n'
                   'FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:=E6=B5=8B=E8=AF=95\n'
                   'TEL;CELL:00000000000\n'
                   'PHOTO;ENCODING=BASE64;JPEG:AAA\n'
                   ' AAA\nEND:VCARD\n')
        result, count = convert(example)
        self.assertEqual(count, 1)
        self.assertIn('FN:测试', result)
        self.assertIn('VERSION:3.0', result)
        self.assertIn('TEL;TYPE=CELL:00000000000', result)
        self.assertNotIn('PHOTO', result)

    def test_missing_name_uses_phone(self):
        result, count = convert('BEGIN:VCARD\nVERSION:2.1\nTEL:00000000000\nEND:VCARD')
        self.assertEqual(count, 1)
        self.assertIn('FN:00000000000', result)

    def test_empty(self):
        result, count = convert('not a vcard')
        self.assertEqual(count, 0)
        self.assertEqual(result, '')

    def test_multiple_cards(self):
        sample = 'BEGIN:VCARD\nFN:甲\nEND:VCARD\nBEGIN:VCARD\nFN:乙\nEND:VCARD'
        result, count = convert(sample)
        self.assertEqual(count, 2)
        self.assertIn('FN:甲', result)
        self.assertIn('FN:乙', result)


if __name__ == '__main__':
    unittest.main()
