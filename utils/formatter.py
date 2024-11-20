import re
import pprint
from utils.helpers import clean_amazon_url

SECTION_SEPARATOR = "\n"


def format_book_footer(self):
    s = "s" if self.book_suggestions > 1 else ""
    return "^(This book has been suggested %s time%s)" % (self.book_suggestions, s)


def extract_id_from_url(url):
    """
    Extracts the numeric ID from a Goodreads book URL.
    """

    match = re.search(r"/book/show/(\d+)", url)
    if match:
        return int(match.group(1))
    return None


def get_genres(book_genres):
    if not book_genres:
        return []

    genre_names = [genre["genre"]["name"] for genre in book_genres]
    return genre_names[:5]


def build_book_url(book_info):
    title = book_info["title"]
    url = book_info["webUrl"]

    string = "[**%s**](%s)" % (title, url)

    if book_info["links"]:
        primary = book_info["links"].get("primaryAffiliateLink", {})
        secondary = book_info["links"].get("secondaryAffiliateLinks", [])
        combined_links = [primary] + secondary
        filtered_links = [
            link for link in combined_links if link.get("name") == "Amazon"
        ]
        # switch to string.format
        string += " ── [View on Amazon](%s)" % clean_amazon_url(
            filtered_links[0]["url"]
        )
    return string


def build_book_info(book_info, is_long_version: bool, book_suggestions_count: float):
    genre_names = get_genres(book_info["bookGenres"])

    info = {
        "title": book_info["title"],
        "webUrl": book_info["webUrl"],
        "author_name": book_info["primaryContributorEdge"]["node"]["name"] or "?",
        "pages": book_info["details"]["numPages"] or "?",
        "published_date": "2024-11-15" or "?",
        "popular_shelves": f"{", ".join(genre_names[:5])}",
        "rating": book_info["stats"]["averageRating"] or "?",
    }

    info_string = """
^(By: {author_name} | Rating: {rating} | {pages} pages | Published: {published_date} | Popular Shelves: {popular_shelves})
        """.format(
        **info
    )

    if len(book_info["description"]) and is_long_version:
        info_string += "\n\n" + format_description(book_info["description"])

    s = "s" if book_suggestions_count > 1 else ""
    info_string += "\n\n" + "^(This book has been suggested %s time%s)" % (
        book_suggestions_count,
        s,
    )

    return info_string + "\n\n"


def build_book_comment(book_info, is_long_version: bool, book_suggestions_count: float):
    # pprint.pprint(book_info)
    formatted_reddit_comment = ""

    formatted_reddit_comment += build_book_url(book_info)
    formatted_reddit_comment += SECTION_SEPARATOR
    formatted_reddit_comment += build_book_info(
        book_info, is_long_version, book_suggestions_count
    )
    formatted_reddit_comment += SECTION_SEPARATOR

    return formatted_reddit_comment


def build_footer(suggestions: float, comment_id: str):
    s = "s" if suggestions > 1 else ""
    return (
        "^(%s book%s suggested | )[^(Mistake?)](https://tally.so/r/w5lLWE?reddit_comment_id=%s) ^(| ) [^(Keep me running ♥)](https://buymeacoffee.com/lmssieh)"
        % (suggestions, s, comment_id)
    )


def format_description(description):
    description = re.sub("<.*?>", "", description.replace("<br />", "\n"))

    chunks = [">" + chunk for chunk in description.split("\n")]

    return "\n".join(chunks)
