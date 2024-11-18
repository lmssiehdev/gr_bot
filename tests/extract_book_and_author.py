import unittest
from utils.helpers import extract_book_and_author


class TestBookAuthorExtraction(unittest.TestCase):
    def test_basic_extraction(self):
        # Basic case with book and author
        self.assertEqual(
            extract_book_and_author("The Great Gatsby by F. Scott Fitzgerald"),
            ("the great gatsby", "f. scott fitzgerald"),
        )

        # Just book, no author
        self.assertEqual(
            extract_book_and_author("Pride and Prejudice"),
            ("pride and prejudice", None),
        )

    def test_spacing_cases(self):
        # Extra spaces around 'by'
        self.assertEqual(
            extract_book_and_author("1984    by    George Orwell"),
            ("1984", "george orwell"),
        )

        # Leading/trailing spaces
        self.assertEqual(
            extract_book_and_author("   Dune   by   Frank Herbert   "),
            ("dune", "frank herbert"),
        )

    def test_multiple_by_in_title(self):
        # 'by' appears in book title
        self.assertEqual(
            extract_book_and_author("Stand By Me by Stephen King"),
            ("stand by me", "stephen king"),
        )

        # Multiple 'by' occurrences
        self.assertEqual(
            extract_book_and_author("Day by Day by James Smith by John Doe"),
            ("day by day by james smith", "john doe"),
        )

    def test_special_characters(self):
        # Special characters in title and author
        self.assertEqual(
            extract_book_and_author("The 100% Solution! by Dr. J.R. Smith-Jones III"),
            ("the 100% solution!", "dr. j.r. smith-jones iii"),
        )

        # Numbers and symbols
        self.assertEqual(
            extract_book_and_author("2001: A Space Odyssey by Arthur C. Clarke"),
            ("2001: a space odyssey", "arthur c. clarke"),
        )

    def test_edge_cases(self):
        # Empty string
        self.assertEqual(extract_book_and_author(""), ("", None))

        # Title and 'by'
        self.assertEqual(
            extract_book_and_author("001: A Space Odyssey by"),
            ("001: a space odyssey", ""),
        )

        # Just 'by'
        self.assertEqual(extract_book_and_author("by"), ("", ""))

        # Multiple consecutive spaces
        self.assertEqual(
            extract_book_and_author("Book     by     Author"), ("book", "author")
        )

    def test_international_titles(self):
        # Non-English characters
        self.assertEqual(
            extract_book_and_author("L'Étranger by Albert Camus"),
            ("l'étranger", "albert camus"),
        )

        # Japanese title and author
        self.assertEqual(
            extract_book_and_author("雪国 by 川端康成"), ("雪国", "川端康成")
        )

    def test_complex_cases(self):
        # Long title with punctuation
        self.assertEqual(
            extract_book_and_author(
                "The Hitchhiker's Guide to the Galaxy, Vol. 1: The Restaurant at the End of the Universe by Douglas Adams"
            ),
            (
                "the hitchhiker's guide to the galaxy, vol. 1: the restaurant at the end of the universe",
                "douglas adams",
            ),
        )

        # Multiple titles format
        self.assertEqual(
            extract_book_and_author(
                "Lord of the Rings: The Fellowship of the Ring by J.R.R. Tolkien"
            ),
            ("lord of the rings: the fellowship of the ring", "j.r.r. tolkien"),
        )
