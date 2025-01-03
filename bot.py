import praw
import time
from uuid import uuid4
from dotenv import dotenv_values
from get_book_info import get_book_id_from_search_query, query_book
from utils.formatter import CommnentFormatter
from utils.helpers import extract_recommendations
from db import DB
from utils.analytics import posthog

env_vars = dotenv_values(".env")

reddit = praw.Reddit(
    client_id=env_vars.get("REDDIT_CLIENT_ID"),
    client_secret=env_vars.get("REDDIT_CLIENT_SECRET"),
    user_agent=env_vars.get("REDDIT_USER_AGENT"),
    username=env_vars.get("REDDIT_USERNAME"),
    password=env_vars.get("REDDIT_PASSWORD"),
)


class Bot:
    def __init__(self):
        self.db = DB()

        self.db.create_tables()

    def capute_analytics(self, book_info, comment, submission):
        """
        Save the book and capture it as an event
        """
        posthog.capture(
            "goodread_bots_reloaded",
            "fetch_book",
            {
                "book_title": book_info["title"],
                "book_url": book_info["webUrl"],
                "book_id": book_info["legacyId"],
                "subreddit": comment.subreddit.display_name,
                "comment_id": comment.id,
                "permalink": comment.permalink,
            },
        )

        # save the book to the database
        book = (
            book_info["legacyId"],
            book_info["title"],
            book_info["webUrl"],
            int(time.time()),
        )
        invocation = (
            str(uuid4()),
            book_info["legacyId"],
            comment.id,
            submission.id,
            "",
            comment.permalink,
            int(time.time()),
        )
        self.db.save_book(book)
        self.db.save_invocation(invocation)

    def listen_to_user(
        self,
    ):
        """
        used for easy testing
        """
        for comment in reddit.redditor(env_vars.get("REDDIT_USERNAME")).stream.comments(
            skip_existing=True
        ):
            comment_invocations = self.db.count_comment_invocations(comment.id)
            if comment_invocations > 0:
                continue
            formatted_reddit_comment = self.build_bot_comment(comment)
            if formatted_reddit_comment is None:
                continue
            comment.reply(formatted_reddit_comment)

    def listen_to_subreddits(self):
        subreddit = reddit.subreddit("booksuggestions")
        for comment in subreddit.stream.comments():
            comment_invocations = self.db.count_comment_invocations(comment.id)
            if comment_invocations > 0:
                continue
            formatted_reddit_comment = self.build_bot_comment(comment)
            if (formatted_reddit_comment is None) or (
                len(formatted_reddit_comment) == 0
            ):
                continue
            comment.reply(formatted_reddit_comment)

    def build_bot_comment(self, comment):
        submission = comment.submission
        formatted_reddit_comment = ""

        if comment.subreddit.display_name == "suggestmeabook":
            comment.refresh()
            for reply in comment.replies.list():
                if reply.author and reply.author.name == "goodreads-rebot":
                    return None

        for recommendation, is_long_version in extract_recommendations(comment.body)[
            :10
        ]:
            if recommendation == "book name":
                continue

            book_id = get_book_id_from_search_query(recommendation)

            if book_id is None:
                continue

            book_info = query_book(book_id)

            if book_info is None:
                continue

            self.capute_analytics(book_info, comment, submission)

            book_suggestions_count = self.db.count_book_requests(book_info["legacyId"])

            formatter = CommnentFormatter(
                book_info=book_info,
                subreddit=comment.subreddit.display_name,
                is_long_version=is_long_version,
                book_suggestions_count=book_suggestions_count,
            )
            formatted_reddit_comment += formatter.build_book_comment()

        if len(formatted_reddit_comment) > 0:
            # We are responding to a comment, so let's save the post
            post = (submission.id, submission.title, submission.url)
            self.db.save_post(post)

            invocations = self.db.count_invocations()
            comment_footer = formatter.build_comment_footer(
                suggestions=invocations,
                permalink=comment.permalink,
            )

            return (
                formatted_reddit_comment + formatter.section_separator + comment_footer
            )
        return None
