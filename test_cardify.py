import unittest
from cardify import Cardify

class MockLLMAgent:
    def __init__(self, response):
        self.response = response
    def get_llm_response(self, document, target_slides):
        return self.response


class TestCardify(unittest.TestCase):
    def test_invalid_target_slides(self):
        document = "some doc"
        cardify = Cardify(MockLLMAgent([]))
        with self.assertRaises(ValueError):
            cardify.section_document(document, 0)
        with self.assertRaises(ValueError):
            cardify.section_document(document, 51)

    def test_empty_document(self):
        cardify = Cardify(MockLLMAgent([]))
        with self.assertRaises(ValueError):
            cardify.section_document("", 5)
        with self.assertRaises(ValueError):
            cardify.section_document(" \n   ", 5)

    def test_single_slide(self):
        document = "some doc"
        cardify = Cardify(MockLLMAgent([]))
        sections = cardify.section_document(document, 1)
        self.assertEqual(sections, [document])

    def test_exact_match(self):
        """Test exact match of sectioning"""
        document = "This is a document that should be split here and somewhere else. Maybe here."
        response = ['somewhere else.', 'Maybe here.']

        cardify = Cardify(MockLLMAgent(response))
        result = cardify.section_document(document, 2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], 'This is a document that should be split here and somewhere else.')
        self.assertEqual(result[1], ' Maybe here.')

    def test_fuzzy_match(self):
        """Test fuzzy match in sectioning"""
        document = "This is a document that should be split here and somewhere else. Maybe here."
        response = ['somewhere elsh.', 'here.']

        cardify = Cardify(MockLLMAgent(response))
        result = cardify.section_document(document, 2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], 'This is a document that should be split here and somewhere else.')
        self.assertEqual(result[1], ' Maybe here.')

    def test_repetition(self):
        """Test if llm doesn't respond with unique strings"""
        document = "This is a document that should be split here and somewhere else. Maybe here."
        response = ['here', 'here']

        cardify = Cardify(MockLLMAgent(response))
        result = cardify.section_document(document, 2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], 'This is a document that should be split here')
        self.assertEqual(result[1], ' and somewhere else. Maybe here.')

if __name__ == '__main__':
    unittest.main()
