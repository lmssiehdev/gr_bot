from thefuzz import fuzz

from utils.helpers import split_book_title_and_series


class BookMatcher:
    def __init__(
        self,
        input_book_title: str,
        input_author_name: str,
        debug=False,
        skip_author_check=False,
    ):
        self.best_scores = {
            "combined": 0,
            "author": 0,
            "title": 0,
            "series": 0,
        }
        self.input_book_title = input_book_title
        self.input_author_name = input_author_name
        self.skip_author_check = skip_author_check
        self.debug = debug
        self.chosen_book = None

    def get_text_from_element(self, book, class_name: str) -> str:
        return book.find(class_=class_name).get_text().strip()

    def calculate_fuzzy_ratio(self, str1, str2):
        if str1 is None or str2 is None:
            return -1
        return fuzz.ratio(str1.lower(), str2.lower())

    def get_combined_score(self, book_author, book_title):
        author_ratio = self.calculate_fuzzy_ratio(self.input_author_name, book_author)
        title_ratio = self.calculate_fuzzy_ratio(self.input_book_title, book_title)

        author_weight = 0.4
        title_weight = 0.6

        return (author_ratio * author_weight) + (title_ratio * title_weight)

    def print_book_info(self, book_info, scores):
        if not self.debug:
            return
        print(
            f"looking at {book_info['author']}[{scores['author']}] and "
            f"{book_info['title']}[{scores['book']}] and "
            f"series {book_info['series']}[{scores['series']}], "
            f"combined score: {scores['combined']:.2f}, "
            f"id: [{book_info['id']}]"
        )

    def update_best_scores(self, scores, current_book):
        if not self.skip_author_check:
            if scores["combined"] > self.best_scores["combined"]:
                self.best_scores = scores
                self.chosen_book = current_book
            elif (
                scores["series"] >= self.best_scores["title"]
                and scores["series"] > self.best_scores["series"]
            ):
                self.best_scores["author"] = scores["author"]
                self.best_scores["series"] = scores["series"]
                self.chosen_book = current_book

    def find_best_match(self, books):
        for book in books:
            book_info = {
                "title": self.get_text_from_element(book, "bookTitle"),
                "author": self.get_text_from_element(book, "authorName"),
                "series": "",
            }

            book_info["title"], book_info["series"] = split_book_title_and_series(
                book_info["title"]
            )

            # some users will summon the bot with only the part of the title
            # before the ':'. i.e. Hello by Someone when the actual title is
            # Hello: World by Someone. This can confuse the bot. This check handles
            # that case.
            if self.input_book_title.lower() + ":" in book_info["title"].lower():
                book_info["title"] = book_info["title"].split(":")[0]

            scores = {
                "title": self.calculate_fuzzy_ratio(
                    self.input_book_title.lower(), book_info["title"].lower()
                ),
                "author": self.calculate_fuzzy_ratio(
                    self.input_author_name.lower(), book_info["author"].lower()
                ),
                "series": self.calculate_fuzzy_ratio(
                    self.input_book_title.lower(), book_info["series"].lower()
                ),
                "combined": self.get_combined_score(
                    book_info["author"], book_info["title"]
                ),
            }

            self.print_book_info(book_info, scores)
            self.update_best_scores(scores, book)

        return self.chosen_book
