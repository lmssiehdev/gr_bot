import re
from typing import List, Tuple
from urllib.parse import urlparse, urlunparse


def extract_book_and_author(title):
    book, *author = title.lower().rsplit("by", 1)
    book = book.strip()
    author = author[0].strip() if author else None
    return (book, author)


def extract_recommendations(comment: str) -> List[Tuple[str, bool]]:
    recommendations = []
    for m in re.finditer(r"\{\{([^}]+)\}\}|\{([^}]+)\}", comment):
        group = m.group()
        # handle empty brackets, general way to handle them
        cleaned = group.replace("{", "").replace("}", "").replace("*", "").strip()
        if cleaned == "":
            continue
        is_long_version = (group.count("{") + group.count("}")) == 4
        recommendations.append((cleaned, is_long_version))
    return recommendations


def split_book_title_and_series(book_title: str) -> Tuple[str, str | None]:
    series_match = None
    for series_match in re.finditer(r"\(([^)]+)\)", book_title):
        pass
    if series_match is not None:
        group = series_match.group()
        book_index_in_series = re.search(r"#\d.", group)

        if book_index_in_series is not None:
            series_name = group
            book_title = book_title.replace(series_name, "").strip()

            return (book_title, series_name.replace("(", "").replace(")", ""))
    return (book_title, None)


def clean_amazon_url(url: str) -> str:
    """
    Cleans up an Amazon product URL by retaining only the essential part with the ASIN.
    """
    amazon_url_pattern = re.compile(
        r"^(?:https?://)?(www[^/]+).*?(/(?:gp/product|dp)/[^/]+).*"
    )
    result = amazon_url_pattern.sub(r"https://\1\2/", url)

    if not result.endswith("/"):
        result += "/"

    result += "ref=nosim?tag=goodreadsbotr-20"
    return result
