import unittest
from unittest.mock import patch, MagicMock

from main import generate_and_post_image

# --- モック用のエラークラス (変更なし) ---
class MockRequestsException(Exception):
    pass

class MockOpenAIAPIError(Exception):
    pass

class MockOpenAIBadRequestError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code

# --- テストコード本体 ---
class TestGenerateAndPostImage(unittest.TestCase):

    def setUp(self):
        # この部分は変更ありません
        self.mock_openai_success_response = MagicMock()
        self.mock_openai_success_response.data[0].url = "http://example.com/fake_image.png"
        self.mock_requests_success_response = MagicMock()
        self.mock_requests_success_response.content = b"fake_image_data"
        self.mock_requests_success_response.raise_for_status.return_value = None
        self.mock_api_v1 = MagicMock()
        self.mock_client_v2 = MagicMock()
        self.mock_media = MagicMock()
        self.mock_media.media_id = "12345"
        self.mock_tweet = MagicMock()
        self.mock_tweet.data = {'id': "98765"}
        self.mock_api_v1.media_upload.return_value = self.mock_media
        self.mock_client_v2.create_tweet.return_value = self.mock_tweet


    def test_success_on_first_try(self):
        """1回で正常に画像生成・投稿が完了するケース"""
        with patch('main.OpenAI') as mock_openai_class, \
             patch('main.requests.get') as mock_requests_get, \
             patch('main.setup_twitter_clients') as mock_setup_clients, \
             patch('main.os.path.exists', return_value=True) as mock_os_exists, \
             patch('main.os.remove') as mock_os_remove, \
             patch('main.time.sleep') as mock_time_sleep:

            mock_openai_client = mock_openai_class.return_value
            mock_openai_client.images.generate.return_value = self.mock_openai_success_response
            mock_requests_get.return_value = self.mock_requests_success_response
            mock_setup_clients.return_value = (self.mock_api_v1, self.mock_client_v2)

            result = generate_and_post_image("a cute cat", "test tweet")

            self.assertEqual(result, "98765")
            mock_openai_client.images.generate.assert_called_once()
            mock_time_sleep.assert_not_called()
            mock_os_remove.assert_called_once()


    def test_retry_on_content_policy_and_succeed(self):
        """content_policy_violationで1度失敗し、リトライで成功するケース"""
        with patch('main.APIError', new=MockOpenAIAPIError), \
             patch('main.BadRequestError', new=MockOpenAIBadRequestError), \
             patch('main.OpenAI') as mock_openai_class, \
             patch('main.requests.get') as mock_requests_get, \
             patch('main.setup_twitter_clients') as mock_setup_clients, \
             patch('main.os.path.exists') as mock_os_exists, \
             patch('main.os.remove') as mock_os_remove, \
             patch('main.time.sleep') as mock_time_sleep:

            mock_openai_client = mock_openai_class.return_value
            mock_openai_client.images.generate.side_effect = [
                MockOpenAIBadRequestError("Blocked by content filter.", code='content_policy_violation'),
                self.mock_openai_success_response
            ]
            mock_requests_get.return_value = self.mock_requests_success_response
            mock_setup_clients.return_value = (self.mock_api_v1, self.mock_client_v2)

            result = generate_and_post_image("a dangerous cat", "test tweet")

            self.assertEqual(result, "98765")
            self.assertEqual(mock_openai_client.images.generate.call_count, 2)
            mock_time_sleep.assert_called_once()
            self.mock_client_v2.create_tweet.assert_called_once()


    def test_failure_after_max_retries(self):
        """リトライ上限までエラーが続き、最終的に失敗するケース"""
        with patch('main.APIError', new=MockOpenAIAPIError), \
             patch('main.BadRequestError', new=MockOpenAIBadRequestError), \
             patch('main.OpenAI') as mock_openai_class, \
             patch('main.requests.get') as mock_requests_get, \
             patch('main.setup_twitter_clients') as mock_setup_clients, \
             patch('main.os.path.exists') as mock_os_exists, \
             patch('main.os.remove') as mock_os_remove, \
             patch('main.time.sleep') as mock_time_sleep:

            mock_openai_client = mock_openai_class.return_value
            error_to_raise = MockOpenAIAPIError("Server error")
            mock_openai_client.images.generate.side_effect = [error_to_raise] * 3

            result = generate_and_post_image("a server-breaking cat", "test tweet")

            self.assertEqual(result, error_to_raise)
            self.assertEqual(mock_openai_client.images.generate.call_count, 3)
            self.assertEqual(mock_time_sleep.call_count, 2)
            mock_requests_get.assert_not_called()
            mock_setup_clients.assert_not_called()


    def test_failure_on_non_retryable_error(self):
        """リトライ対象外のBadRequestErrorで即座に失敗するケース"""
        with patch('main.APIError', new=MockOpenAIAPIError), \
             patch('main.BadRequestError', new=MockOpenAIBadRequestError), \
             patch('main.OpenAI') as mock_openai_class, \
             patch('main.requests.get') as mock_requests_get, \
             patch('main.setup_twitter_clients') as mock_setup_clients, \
             patch('main.os.path.exists') as mock_os_exists, \
             patch('main.os.remove') as mock_os_remove, \
             patch('main.time.sleep') as mock_time_sleep:

            mock_openai_client = mock_openai_class.return_value
            error_to_raise = MockOpenAIBadRequestError("Invalid prompt.", code='invalid_request_error')
            mock_openai_client.images.generate.side_effect = [error_to_raise]

            result = generate_and_post_image("a very invalid cat", "test tweet")
            
            self.assertEqual(result, error_to_raise)
            mock_openai_client.images.generate.assert_called_once()
            mock_time_sleep.assert_not_called()
            mock_setup_clients.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
