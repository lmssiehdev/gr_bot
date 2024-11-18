import re
from typing import List, Tuple


def extract_book_and_author(title):
    book, *author = title.lower().rsplit("by", 1)
    book = book.strip()
    author = author[0].strip() if author else None
    return (book, author)


def extract_recommendations(comment: str) -> List[Tuple[str, bool]]:
    recommendations = []
    for m in re.finditer("\{\{([^}]+)\}\}|\{([^}]+)\}", comment):
        group = m.group()
        # handle empty brackets, general way to handle them
        cleaned = group.replace("{", "").replace("}", "").replace("*", "").strip()
        if cleaned == "":
            continue
        is_long_version = (group.count("{") + group.count("}")) == 4
        recommendations.append((cleaned, is_long_version))
    return recommendations
