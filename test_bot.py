from unittest.mock import Mock
from bot import Bot

# Mock submission object
mock_submission = Mock()
mock_submission.id = "abc123"
mock_submission.title = "Interesting Book Discussion"
mock_submission.url = "https://example.com/post/abc123"

# Mock comment object
mock_comment = Mock()
mock_comment.body = """
{{Regarding the Fountain by Kate Klise}} This starts a whole hilarious series featuring a fifth grade class, told in epistolary style through letters, memos and documents {somethingthatthereisnoresultfor}."""
mock_comment.id = "xyz456"
mock_comment.permalink = "https://example.com/comment/xyz456"
mock_comment.submission = mock_submission

bot = Bot()
print(bot.build_bot_comment(mock_comment))
