import praw
import time
from uuid import uuid4
from dotenv import dotenv_values
from get_book_info import get_book_info_based_on_search_query
from utils.helpers import extract_recommendations
from utils.formatter import build_book_comment, build_footer
from db import DB

env_vars = dotenv_values(".env")

reddit = praw.Reddit(
    client_id=env_vars.get("REDDIT_CLIENT_ID"),
    client_secret=env_vars.get("REDDIT_CLIENT_SECRET"),
    user_agent="User-Agent: script:goodreads_bot_reloaded:v0.0.1 (by /u/WeirdDetail9)",
)


class Bot:
    def __init__(self):
        # self.reddit = praw.Reddit()
        self.db = DB()

        self.db.create_tables()

    def listen_to_subreddit(self, name):
        subreddit = reddit.subreddit("AskReddit")
        for comment in subreddit.stream.comments():
            comment_invocations = self.db.count_comment_invocations(comment.id)
            if comment_invocations > 0:
                continue
            # comment.reply(formatted_reddit_comment)

    def build_bot_comment(self, comment):
        submission = comment.submission
        formatted_reddit_comment = ""
        for recommendation, is_long_version in extract_recommendations(comment.body):
            print({recommendation: recommendation})
            book_info = get_book_info_based_on_search_query(recommendation)

            # Save the book and summons for our stats
            book = (
                book_info["id"],
                book_info["title"],
                book_info["webUrl"],
                int(time.time()),
            )
            invocation = (
                str(uuid4()),
                book_info["id"],
                comment.id,
                submission.id,
                "",
                comment.permalink,
                int(time.time()),
            )
            self.db.save_book(book)
            self.db.save_invocation(invocation)

            book_suggestions_count = self.db.count_book_requests(book_info["id"])

            formatted_reddit_comment += build_book_comment(
                book_info=book_info,
                is_long_version=is_long_version,
                book_suggestions_count=book_suggestions_count,
            )

        if len(formatted_reddit_comment) > 0:
            # We are responding to a comment, so let's save the post
            post = (submission.id, submission.title, submission.url)
            self.db.save_post(post)

            SECTION_SEPARATOR = "\n"
            formatted_reddit_comment += "***" + SECTION_SEPARATOR

            invocations = self.db.count_invocations()
            formatted_reddit_comment += build_footer(invocations)

            return formatted_reddit_comment
        return None


from unittest.mock import Mock

# Mock submission object
mock_submission = Mock()
mock_submission.id = "abc123"
mock_submission.title = "Interesting Book Discussion"
mock_submission.url = "https://example.com/post/abc123"

# Mock comment object
mock_comment = Mock()
mock_comment.body = """
{{Regarding the Fountain by Kate Klise}} This starts a whole hilarious series featuring a fifth grade class, told in epistolary style through letters, memos and documents {{the name of the wind}}."""
mock_comment.id = "xyz456"
mock_comment.permalink = "https://example.com/comment/xyz456"
mock_comment.submission = mock_submission

bot = Bot()
print(bot.build_bot_comment(mock_comment))
