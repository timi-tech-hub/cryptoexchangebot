import unittest
from responses import get_text, RESPONSES

class TestResponses(unittest.TestCase):
    def test_get_text_welcome(self):
        """Test that WELCOME responses return a string and contain placeholders if needed (none for welcome)."""
        text = get_text("WELCOME")
        self.assertIsInstance(text, str)
        self.assertTrue(any(variant in text for variant in RESPONSES["WELCOME"]))

    def test_get_text_with_kwargs(self):
        """Test that responses with placeholders are correctly formatted."""
        text = get_text("BUY_AMOUNT_SUCCESS", amount=100)
        self.assertIn("100", text)
        self.assertIn("USDT", text)

    def test_invalid_key(self):
        """Test that an invalid key returns an error message."""
        text = get_text("NON_EXISTENT_KEY")
        self.assertIn("Error: Response key 'NON_EXISTENT_KEY' not found", text)

if __name__ == "__main__":
    unittest.main()
