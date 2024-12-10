from datetime import datetime
from typing import Any, Dict, Final, TypedDict, List, Optional
from utils.helpers import extract_asin
import re


class SubredditConfig(TypedDict):
    amazon_link: bool
    report_link: bool


subreddit_info: Final[Dict[str, SubredditConfig]] = {
    "suggestmeabook": {
        "amazon_link": False,
        "report_link": False,
    },
    "booksuggestions": {
        "amazon_link": True,
        "report_link": True,
    },
}


class CommnentFormatter:
    def __init__(
        self,
        book_info,
        subreddit: str,
        is_long_version: bool,
        book_suggestions_count: float,
    ):
        self.book_info = book_info
        self.subreddit = subreddit
        self.is_long_version = is_long_version
        self.book_suggestions_count = book_suggestions_count
        self.section_separator = "\n"
        self.include_amazon_url = False

    def build_book_comment(self) -> str:
        return (
            f"{self.build_book_header()}"
            f"{self.section_separator}"
            f"{self.build_book_data()}"
            f"{self.section_separator}"
        )

    def build_book_header(self):
        title = self.book_info["title"]
        url = self.book_info["webUrl"]

        string = f"[**{title}**]({url})"

        if (
            self.subreddit not in subreddit_info
            or subreddit_info.get(self.subreddit, {}).get("amazon_link") is False
        ):
            return string + self.section_separator

        book_id = self.get_amazon_book_id(self.book_info)

        if book_id is None:
            return string

        string += f" ── [View on Amazon](https://gr-bot.vercel.app/book/{book_id})"

        return string + self.section_separator

    def build_book_data(self) -> str:
        book_info = self.book_info
        info = {
            "title": book_info["title"],
            "webUrl": book_info["webUrl"],
            "author_name": book_info["primaryContributorEdge"]["node"]["name"] or "?",
            "pages": book_info["details"]["numPages"] or "?",
            "published_date": self.format_timestamp(
                book_info["details"]["publicationTime"]
            ),
            "popular_shelves": self.get_genres(book_info["bookGenres"]),
            "rating": book_info["stats"]["averageRating"] or "?",
        }

        info_string = (
            f"^(By: {info['author_name']} | "
            f"Rating: {info['rating']} | "
            f"{info['pages']} pages | "
            f"Published: {info['published_date']} "
            f"{info['popular_shelves']})"
        )

        if len(book_info["description"]) and self.is_long_version:
            info_string += f"\n\n{self.format_description(book_info['description'])}"

        s = "s" if self.book_suggestions_count > 1 else ""
        info_string += (
            f"\n\n^(This book has been suggested {self.book_suggestions_count} time{s})"
        )

        info_string += "\n\n___\n\n"

        return info_string

    def format_book_footer(self, book_suggestions: int) -> str:
        s = "s" if book_suggestions > 1 else ""
        return f"^(This book has been suggested {book_suggestions} time{s})"

    @staticmethod
    def get_amazon_book_id(book_info) -> Optional[str]:
        if not book_info["links"]:
            return None

        primary = book_info["links"].get("primaryAffiliateLink", {})
        secondary = book_info["links"].get("secondaryAffiliateLinks", [])
        combined_links = [primary] + secondary
        filtered_links = [
            link for link in combined_links if link.get("name") == "Amazon"
        ]

        return extract_asin(filtered_links[0]["url"]) if filtered_links else None

    @staticmethod
    def extract_id_from_url(url: str) -> Optional[int]:
        """
        Extracts the numeric ID from a Goodreads book URL.
        """
        match = re.search(r"/book/show/(\d+)", url)

        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def format_description(description: str) -> str:
        description = re.sub("<.*?>", "", description.replace("<br />", "\n"))
        return "\n".join(f">{chunk}" for chunk in description.split("\n"))

    @staticmethod
    def format_timestamp(timestamp: float) -> str:
        """Convert timestamp to formatted date string."""
        return (
            datetime.fromtimestamp(timestamp / 1000).strftime("%m/%d/%Y")
            if timestamp
            else "?"
        )

    @staticmethod
    def get_genres(book_genres: List[Dict[str, Any]]) -> str:
        if not book_genres:
            return ""

        genre_names = [genre["genre"]["name"] for genre in book_genres]
        shelves_string = f"{", ".join(genre_names[:5])}"

        return f" | Popular Shelves: {shelves_string}"

    def build_comment_footer(self, suggestions, permalink):
        s = "s" if suggestions > 1 else ""
        string = (
            f"^({suggestions} book{s} suggested | ) "
            f"^({{{{ book name }}}} to summon me  | )"
        )

        if (
            self.subreddit not in subreddit_info
            or subreddit_info.get(self.subreddit, {}).get("report_link") is False
        ):
            return string

        string += (
            f"[^(Mistake?)](https://gr-bot.vercel.app/report?permalink={permalink})"
        )
        return string
