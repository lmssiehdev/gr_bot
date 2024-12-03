from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from dotenv import dotenv_values
import requests
from bs4 import BeautifulSoup
from utils.book_matcher import BookMatcher
from utils.formatter import CommnentFormatter
from utils.helpers import (
    extract_book_and_author,
)
from thefuzz import process

# Load environment variables as a dictionary
env_vars = dotenv_values(".env")
api_key = env_vars.get("API_KEY")

# Set up the GraphQL client
transport = RequestsHTTPTransport(
    url="https://kxbwmqov6jgg3daaamb744ycu4.appsync-api.us-east-1.amazonaws.com/graphql",
    headers={"X-Api-Key": api_key},
)
client = Client(transport=transport, fetch_schema_from_transport=True)

# Define the GraphQL query
query = gql(
    """
   query getBookByLegacyId($legacyBookId: Int!) {
       getBookByLegacyId(legacyId: $legacyBookId) {
           links {
               __typename
               primaryAffiliateLink {
                   name
                   url
               }
               secondaryAffiliateLinks {
                   name
                   url
               }
           }
           title
           titleComplete
           id
           legacyId
           webUrl
           description
           descriptionStripped: description(stripped: true)
           primaryContributorEdge {
           node{
            name
           }
           }
           bookGenres {
            genre {
              name
              webUrl
            }
          }
          stats {
              averageRating
          }
          details {
            numPages
            publicationTime
          }
       }
      }
"""
)


def query_book(bookId: float):
    variables = {"legacyBookId": bookId}
    result = client.execute(query, variable_values=variables)
    return result["getBookByLegacyId"]


def get_book_id_from_search_query(
    search_query: str,
    debug=False,
    skip_author_check: bool = False,
):
    try:
        if skip_author_check:
            book_title, query_author_name = search_query, None
        else:
            book_title, query_author_name = extract_book_and_author(search_query)
            search_query = book_title

        url = f"https://goodreads.com/search?page=1&q={search_query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=3000)

        if response.status_code == 404:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        if soup is None:
            return None

        books = soup.find_all("tr")

        if len(books) == 0:
            return None

        if query_author_name is not None and skip_author_check is False:
            authors = []
            for book in books:
                author_name = book.find(class_="authorName").get_text().strip()
                authors.append(author_name)

            _, ratio = process.extractOne(query_author_name, authors)

            if ratio < 90:
                # we can be sure that the author_name is part of the title
                # example: "Gone by Midnight"
                # retry again skiping the author check
                book_title += " by " + query_author_name
                return get_book_id_from_search_query(
                    book_title, debug=False, skip_author_check=True
                )

        chosen_book = None

        if query_author_name is not None:
            book_matcher = BookMatcher(
                book_title,
                query_author_name,
                debug=debug,
                skip_author_check=skip_author_check,
            )
            chosen_book = book_matcher.find_best_match(books)

        if chosen_book is not None:
            goodreads_link = chosen_book.find("a", class_="bookTitle")["href"]
            book_id = CommnentFormatter.extract_id_from_url(goodreads_link)
            return book_id

        closest_match = soup.find_all("tr")[0]
        book_id = CommnentFormatter.extract_id_from_url(
            closest_match.find("a", class_="bookTitle")["href"]
        )
        return book_id

    except Exception as e:
        print(f"Failed to fetch book info for {search_query}: {e}")
        return None
