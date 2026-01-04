import unittest
import os
from cardify import Cardify
from llm import SectionerAgent
from dotenv import load_dotenv
load_dotenv()

def _read_file(file_path):
    try:
        with open(f"./test_files/{file_path}", 'r') as f:
            return f.read()
    except Exception as e:
        raise ValueError(e)


class IntegrationTest(unittest.TestCase):

    def _validate_sectioning(self, document, sections):
        reconstructed = ''.join(sections)
        self.assertEqual(reconstructed, document)


    def test_empty_document(self):
        cardify = Cardify()
        doc = _read_file("empty.txt")
        with self.assertRaises(ValueError):
            cardify.section_document(doc, 3)

    def test_whitespace_document(self):
        cardify = Cardify()
        doc = _read_file("whitespace.txt")
        with self.assertRaises(ValueError):
            cardify.section_document(doc, 3)

    def test_special_characters_document(self):
        cardify = Cardify()
        doc = _read_file("special_characters.txt")
        sections = cardify.section_document(doc, 3)
        self.assertEqual(len(sections), 3)
        self._validate_sectioning(doc, sections)

    def test_unicode_document(self):
        cardify = Cardify()
        doc = _read_file("unicode_characters.txt")
        sections = cardify.section_document(doc, 3)
        self.assertEqual(len(sections), 3)
        self._validate_sectioning(doc, sections)

    def test_short_document(self):
        cardify = Cardify()
        doc = _read_file("short_sample.txt")
        sections = cardify.section_document(doc, 2)
        self.assertEqual(len(sections), 2)
        self._validate_sectioning(doc, sections)

    def test_long_document(self):
        cardify = Cardify()
        doc = _read_file("long_sample.txt")
        sections = cardify.section_document(doc, 20)
        self.assertEqual(len(sections), 20)
        self._validate_sectioning(doc, sections)

    def test_repeated_document(self):
        cardify = Cardify()
        doc = _read_file("repeated.txt")
        sections = cardify.section_document(doc, 7)
        self.assertEqual(len(sections), 7)
        self._validate_sectioning(doc, sections)


if __name__ == '__main__':
    unittest.main()
