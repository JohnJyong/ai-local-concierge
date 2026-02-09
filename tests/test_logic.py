import unittest
import requests
import base64
import os
from io import BytesIO
from unittest.mock import patch, MagicMock
from PIL import Image
from app_logic import encode_image, analyze_image_api, SYSTEM_PROMPT

class TestAppLogic(unittest.TestCase):

    def test_encode_image(self):
        """Test if an image is correctly encoded to base64."""
        # Create a dummy image
        img = Image.new('RGB', (10, 10), color='red')
        
        # Call the function
        b64_str = encode_image(img)
        
        # Decode back to verify
        decoded_bytes = base64.b64decode(b64_str)
        decoded_img = Image.open(BytesIO(decoded_bytes))
        
        self.assertEqual(decoded_img.size, (10, 10))
        self.assertEqual(decoded_img.format, 'JPEG')
    
    @patch('app_logic.requests.post')
    def test_analyze_image_api_success(self, mock_post):
        """Test API call simulation (Success)."""
        # Mocking the API response
        mock_response = MagicMock()
        expected_json = {
            "choices": [
                {
                    "message": {
                        "content": "This is a test story about the Eiffel Tower."
                    }
                }
            ]
        }
        mock_response.json.return_value = expected_json
        mock_post.return_value = mock_response

        # Call the function
        result = analyze_image_api("dummy_base64_string", "fake_api_key", model="gpt-4-test")

        # Assertions
        self.assertEqual(result, expected_json)
        
        # Check if request was sent to correct URL with correct headers
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://api.openai.com/v1/chat/completions")
        self.assertIn("Authorization", kwargs['headers'])
        self.assertEqual(kwargs['headers']['Authorization'], "Bearer fake_api_key")
        self.assertEqual(kwargs['json']['model'], "gpt-4-test")
        
        # Verify the prompt is included
        messages = kwargs['json']['messages']
        self.assertEqual(messages[0]['content'], SYSTEM_PROMPT)

    @patch('app_logic.requests.post')
    def test_analyze_image_api_failure(self, mock_post):
        """Test API call simulation (Failure/Error from API)."""
        mock_response = MagicMock()
        error_json = {
            "error": {
                "message": "Invalid API Key",
                "type": "invalid_request_error",
                "param": None,
                "code": "invalid_api_key"
            }
        }
        mock_response.json.return_value = error_json
        mock_post.return_value = mock_response

        result = analyze_image_api("dummy", "bad_key")
        self.assertIn("error", result)
        self.assertEqual(result["error"]["message"], "Invalid API Key")

if __name__ == '__main__':
    unittest.main()
