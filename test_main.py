import unittest
from unittest.mock import patch, MagicMock
import tweepy
import random
import time

from main import generate_and_post_image

class MockRequestsException(Exception):
    pass

class MockTweepyForbidden(tweepy.errors.Forbidden):
    def __init__(self, response):
        super().__init__(response)

class MockOpenAIAPIError(Exception):
    pass

class MockOpenAIBadRequestError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        if code:
            self.code = code

class TestGenerateAndPostImage(unittest.TestCase):

    def setUp(self):
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
        with patch('main.OpenAI') as mock_openai_class, \
             patch('main.requests.get') as mock_requests_get, \
             patch('main.setup_twitter_clients') as mock_setup_clients, \
             patch('main.os.path.exists', return_value=True), \
             patch('main.os.remove') as mock_os_remove, \
             patch('main.time.sleep'):
            mock_openai_client = mock_openai_class.return_value
            mock_openai_client.images.generate.return_value = self.mock_openai_success_response
            mock_requests_get.return_value = self.mock_requests_success_response
            mock_setup_clients.return_value = (self.mock_api_v1, self.mock_client_v2)
            
            result = generate_and_post_image("a cute cat", "test tweet")
            
            self.assertEqual(result, "98765")
            self.mock_client_v2.create_tweet.assert_called_once()
            mock_os_remove.assert_called_once()

    def test_tweet_retry_and_succeed(self):
        with patch('main.OpenAI') as mock_openai_class, \
             patch('main.requests.get') as mock_requests_get, \
             patch('main.setup_twitter_clients') as mock_setup_clients, \
             patch('main.os.path.exists', return_value=True), \
             patch('main.os.remove'), \
             patch('main.time.sleep') as mock_time_sleep, \
             patch('main.random.uniform', return_value=0.5):
            
            mock_openai_client = mock_openai_class.return_value
            mock_openai_client.images.generate.return_value = self.mock_openai_success_response
            mock_requests_get.return_value = self.mock_requests_success_response
            mock_setup_clients.return_value = (self.mock_api_v1, self.mock_client_v2)
            
            mock_forbidden_response = MagicMock()
            mock_forbidden_response.status_code = 403
            self.mock_client_v2.create_tweet.side_effect = [
                MockTweepyForbidden(mock_forbidden_response),
                self.mock_tweet
            ]
            
            result = generate_and_post_image("a cute cat", "test tweet")
            
            self.assertEqual(result, "98765")
            self.assertEqual(self.mock_client_v2.create_tweet.call_count, 2)
            mock_time_sleep.assert_called_once_with(5.5)

    def test_tweet_failure_after_max_retries(self):
        with patch('main.OpenAI') as mock_openai_class, \
             patch('main.requests.get') as mock_requests_get, \
             patch('main.setup_twitter_clients') as mock_setup_clients, \
             patch('main.os.path.exists', return_value=True), \
             patch('main.os.remove'), \
             patch('main.time.sleep'), \
             patch('main.random.uniform', return_value=0.5):

            mock_openai_client = mock_openai_class.return_value
            mock_openai_client.images.generate.return_value = self.mock_openai_success_response
            mock_requests_get.return_value = self.mock_requests_success_response
            mock_setup_clients.return_value = (self.mock_api_v1, self.mock_client_v2)

            mock_forbidden_response = MagicMock()
            mock_forbidden_response.status_code = 403
            self.mock_client_v2.create_tweet.side_effect = MockTweepyForbidden(mock_forbidden_response)
            
            with self.assertRaises(MockTweepyForbidden):
                generate_and_post_image("a cute cat", "test tweet")
            
            self.assertEqual(self.mock_client_v2.create_tweet.call_count, 3)

    def test_tweet_failure_on_other_exception(self):
        with patch('main.OpenAI') as mock_openai_class, \
             patch('main.requests.get') as mock_requests_get, \
             patch('main.setup_twitter_clients') as mock_setup_clients, \
             patch('main.os.path.exists', return_value=True), \
             patch('main.os.remove'), \
             patch('main.time.sleep'):

            mock_openai_client = mock_openai_class.return_value
            mock_openai_client.images.generate.return_value = self.mock_openai_success_response
            mock_requests_get.return_value = self.mock_requests_success_response
            mock_setup_clients.return_value = (self.mock_api_v1, self.mock_client_v2)
            
            self.mock_client_v2.create_tweet.side_effect = Exception("Some other error")
            
            with self.assertRaises(Exception):
                generate_and_post_image("a cute cat", "test tweet")
            
            self.mock_client_v2.create_tweet.assert_called_once()

    def test_image_gen_retry_on_content_policy_and_succeed(self):
        with patch('main.APIError', new=MockOpenAIAPIError), \
             patch('main.BadRequestError', new=MockOpenAIBadRequestError), \
             patch('main.OpenAI') as mock_openai_class, \
             patch('main.requests.get') as mock_requests_get, \
             patch('main.setup_twitter_clients') as mock_setup_clients, \
             patch('main.os.path.exists'), \
             patch('main.os.remove'), \
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
            self.mock_client_v2.create_tweet.assert_called_once()

    def test_image_gen_failure_after_max_retries(self):
        with patch('main.APIError', new=MockOpenAIAPIError), \
             patch('main.BadRequestError', new=MockOpenAIBadRequestError), \
             patch('main.OpenAI') as mock_openai_class, \
             patch('main.requests.get') as mock_requests_get, \
             patch('main.setup_twitter_clients') as mock_setup_clients, \
             patch('main.os.path.exists'), \
             patch('main.os.remove'), \
             patch('main.time.sleep') as mock_time_sleep:
            mock_openai_client = mock_openai_class.return_value
            mock_openai_client.images.generate.side_effect = [MockOpenAIAPIError("Server error")] * 3
            
            with self.assertRaises(MockOpenAIAPIError):
                generate_and_post_image("a server-breaking cat", "test tweet")
            
            self.assertEqual(mock_openai_client.images.generate.call_count, 3)
            mock_requests_get.assert_not_called()
            mock_setup_clients.assert_not_called()

    def test_image_gen_failure_on_non_retryable_error(self):
        with patch('main.APIError', new=MockOpenAIAPIError), \
             patch('main.BadRequestError', new=MockOpenAIBadRequestError), \
             patch('main.OpenAI') as mock_openai_class, \
             patch('main.requests.get') as mock_requests_get, \
             patch('main.setup_twitter_clients') as mock_setup_clients, \
             patch('main.os.path.exists'), \
             patch('main.os.remove'), \
             patch('main.time.sleep'):
            mock_openai_client = mock_openai_class.return_value
            mock_openai_client.images.generate.side_effect = [
                MockOpenAIBadRequestError("Invalid prompt.", code='invalid_request_error')
            ]
            
            with self.assertRaises(MockOpenAIBadRequestError):
                generate_and_post_image("a very invalid cat", "test tweet")
            
            mock_openai_client.images.generate.assert_called_once()
            mock_setup_clients.assert_not_called()

    def test_image_gen_failure_on_bad_request_without_code(self):
        with patch('main.APIError', new=MockOpenAIAPIError), \
             patch('main.BadRequestError', new=MockOpenAIBadRequestError), \
             patch('main.OpenAI') as mock_openai_class, \
             patch('main.requests.get') as mock_requests_get, \
             patch('main.setup_twitter_clients') as mock_setup_clients, \
             patch('main.os.path.exists'), \
             patch('main.os.remove'), \
             patch('main.time.sleep'):
            mock_openai_client = mock_openai_class.return_value
            mock_openai_client.images.generate.side_effect = [
                MockOpenAIBadRequestError("Generic bad request.")
            ]
            
            with self.assertRaises(MockOpenAIBadRequestError):
                generate_and_post_image("a cat without a code", "test tweet")

            mock_openai_client.images.generate.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
