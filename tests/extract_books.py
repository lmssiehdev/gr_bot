import unittest
from utils.helpers import extract_recommendations


class TestRecommendationExtraction(unittest.TestCase):
    def test_basic_single_recommendations(self):
        # Test basic single recommendation with {Title}
        matrix_comment = "I just finished watching {The Matrix} for the first time and I'm completely blown away!"
        self.assertEqual(
            extract_recommendations(matrix_comment),
            [{"book_name": "The Matrix", "is_long_version": False}],
        )

        # Test basic single recommendation with numbers
        dystopian_comment = "If you're interested in dystopian literature, you absolutely need to read {1984}."
        self.assertEqual(
            extract_recommendations(dystopian_comment),
            [{"book_name": "1984", "is_long_version": False}],
        )

        # Test double bracket recommendation {{Title}}
        inception_comment = "{{Inception}} is honestly Nolan's masterpiece imo."
        self.assertEqual(
            extract_recommendations(inception_comment),
            [{"book_name": "Inception", "is_long_version": True}],
        )

    def test_multiple_recommendations(self):
        # Test multiple recommendations in single comment
        fantasy_comment = """For anyone looking to get into high fantasy, you absolutely must start with 
           {The Lord of the Rings} and then dive into {The Silmarillion}."""
        self.assertEqual(
            extract_recommendations(fantasy_comment),
            [
                {"book_name": "The Lord of the Rings", "is_long_version": False},
                {"book_name": "The Silmarillion", "is_long_version": False},
            ],
        )

        # Test mixed bracket types
        scifi_comment = "Been on a huge sci-fi kick lately. Just binged {{Dune}} and {Foundation} back to back."
        self.assertEqual(
            extract_recommendations(scifi_comment),
            [
                {"book_name": "Dune", "is_long_version": True},
                {"book_name": "Foundation", "is_long_version": False},
            ],
        )

    def test_spacing_edge_cases(self):
        # Test extra spaces inside brackets
        spaces_comment = "Just finished reading { Spaces } and honestly can't tell"
        self.assertEqual(
            extract_recommendations(spaces_comment),
            [{"book_name": "Spaces", "is_long_version": False}],
        )

        # Test no spaces
        no_spaces = "{{NoSpaces}}changed my life fr fr no cap"
        self.assertEqual(
            extract_recommendations(no_spaces),
            [{"book_name": "NoSpaces", "is_long_version": True}],
        )

        # Test leading space
        leading_space = "Recently picked up { Leading Space} at a used bookstore."
        self.assertEqual(
            extract_recommendations(leading_space),
            [{"book_name": "Leading Space", "is_long_version": False}],
        )

        # Test trailing space
        trailing_space = "Been meaning to tell everyone about {Trailing Space }"
        self.assertEqual(
            extract_recommendations(trailing_space),
            [{"book_name": "Trailing Space", "is_long_version": False}],
        )

    def test_empty_and_invalid_cases(self):
        # Test empty brackets
        self.assertEqual(extract_recommendations("{}"), [])
        self.assertEqual(extract_recommendations("{{}}"), [])

        # Test unclosed brackets
        self.assertEqual(extract_recommendations("{unclosed"), [])

        # Test no brackets
        self.assertEqual(extract_recommendations("no brackets here"), [])

    def test_multiple_mixed_cases(self):
        mixed_comment = """I loved {The Matrix} but {{Inception}} was even better. 
           You should also try { Spaces } and {1984} for a good dystopian double feature."""
        self.assertEqual(
            extract_recommendations(mixed_comment),
            [
                {"book_name": "The Matrix", "is_long_version": False},
                {"book_name": "Inception", "is_long_version": True},
                {"book_name": "Spaces", "is_long_version": False},
                {"book_name": "1984", "is_long_version": False},
            ],
        )


if __name__ == "__main__":
    unittest.main()
