import re
from typing import List, Optional, Tuple
from thefuzz import fuzz


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
    return (book_title, "")


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


def extract_asin(url: str) -> Optional[str]:
    """
    Extracts the ASIN (Amazon Standard Identification Number) from an Amazon product URL.
    """
    patterns = [
        r"/dp/([A-Z0-9]{10})/",
        r"/gp/product/([A-Z0-9]{10})/",
        r"/gp/aw/d/([A-Z0-9]{10})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def get_combined_score(query_author, query_title, book_author, book_title):
    author_ratio = fuzz.ratio(query_author.lower(), book_author.lower())
    title_ratio = fuzz.ratio(query_title.lower(), book_title.lower())

    # Weight author and title matches
    author_weight = 0.4
    title_weight = 0.6

    return (author_ratio * author_weight) + (title_ratio * title_weight)
