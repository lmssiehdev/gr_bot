from unittest.mock import Mock
from bot import Bot
from get_book_info import get_book_id_from_search_query

# # Mock submission object
# mock_submission = Mock()
# mock_submission.id = "abc123"
# mock_submission.title = "Interesting Book Discussion"
# mock_submission.url = "https://example.com/post/abc123"

# # Mock comment object
# mock_comment = Mock()
# mock_comment.body = """
# {City of Brass by S. A. Chakraborty}
# """
# mock_comment.id = "xyz456"
# mock_comment.permalink = "https://example.com/comment/xyz456"
# mock_comment.submission = mock_submission

# bot = Bot()
# print(bot.build_bot_comment(mock_comment))


# test the search edge cases


# this used to return "City of Brass" by a different author since the input is misplelled
# it should have been "The City of Brass by S. A. Chakraborty"
# we now account for the author name in the fuzzy search
# book_id = get_book_id_from_search_query("City of Brass by S. A. Chakraborty")
# print(book_id, book_id == 32718027)


# # this is used to test where "By" is part of the book title and not used for the author name
# book_id = get_book_info_based_on_search_query("Gone By Midnight")
# print(book_id, book_id == 45046577)

# # this is used to check where goodreads search doesn't return any values
# book_id = get_book_info_based_on_search_query("thisisverylongandshouldnotexist")
# print(book_id, book_id is None)

# # it should work with a book title, series and author
# book_id = get_book_info_based_on_search_query(
#     "The Name of the Wind The Kingkiller Chronicle #1 by Patrick Rothfuss"
# )
# print(book_id, book_id == 186074)
