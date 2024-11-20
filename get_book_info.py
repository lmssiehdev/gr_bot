from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from dotenv import dotenv_values
import requests
from bs4 import BeautifulSoup
from utils.formatter import extract_id_from_url
from utils.helpers import extract_book_and_author, split_book_title_and_series
import pprint
from thefuzz import process, fuzz

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


def get_book_info_based_on_search_query(
    search_query: str, skip_author_check: bool = False
):
    try:
        if not skip_author_check:
            book_title, query_author_name = extract_book_and_author(search_query)
            search_query = book_title
        else:
            book_title, query_author_name = search_query, None

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

        if len(soup.find_all("tr")) == 0:
            return None

        best_author_name_ratio = 0
        best_book_name_ratio = 0
        best_series_name_ratio = 0
        chosen_book = None

        if query_author_name is not None:
            authors = []
            for book in soup.find_all("tr"):
                author_name = book.find(class_="authorName").get_text().strip()
                authors.append(author_name)
                search_book_title = book.find(class_="bookTitle").get_text().strip()
                search_author_name = book.find(class_="authorName").get_text().strip()
                search_book_title, search_series_name = split_book_title_and_series(
                    search_book_title
                )

                # some users will summon the bot with only the part of the title
                # before the ':'. i.e. Hello by Someone when the actual title is
                # Hello: World by Someone. This can confuse the bot. This check handles
                # that case.
                if book_title.lower() + ":" in search_book_title.lower():
                    search_book_title = search_book_title.split(":")[0]

                series_name_ratio = -1
                author_name_ratio = -1
                if search_series_name is not None:
                    series_name_ratio = fuzz.ratio(
                        book_title.lower(), search_series_name.lower()
                    )
                if query_author_name is not None:
                    author_name_ratio = fuzz.ratio(
                        query_author_name.lower(), search_author_name.lower()
                    )
                book_name_ratio = fuzz.ratio(
                    book_title.lower(), search_book_title.lower()
                )

                # print(
                #     "looking at %s[%d] and %s[%d] and series %s[%d], id: [%d]"
                #     % (
                #         search_author_name,
                #         author_name_ratio,
                #         search_book_title,
                #         book_name_ratio,
                #         search_series_name,
                #         series_name_ratio,
                #         extract_id_from_url(book.find("a", class_="bookTitle")["href"]),
                #     )
                # )

                if not skip_author_check or (
                    author_name_ratio >= 90
                    and author_name_ratio >= best_author_name_ratio
                ):
                    if (
                        book_name_ratio >= best_series_name_ratio
                        and book_name_ratio > best_book_name_ratio
                    ):
                        # print("setting chosen book based on book")
                        best_author_name_ratio = author_name_ratio
                        best_book_name_ratio = book_name_ratio
                        chosen_book = book
                    if (
                        series_name_ratio >= best_book_name_ratio
                        and series_name_ratio > best_series_name_ratio
                    ):
                        # print("setting chosen book based on book series")
                        best_author_name_ratio = author_name_ratio
                        best_series_name_ratio = series_name_ratio
                        chosen_book = book

            _, ratio = process.extractOne(query_author_name, authors)

            if ratio < 90 and skip_author_check is False:
                # we can be sure that the author_name is part of the title
                # example: "Gone by Midnight"
                book_title += " by " + query_author_name
                # print("By is part of the name, skipping author check", book_title)
                return get_book_info_based_on_search_query(
                    book_title, skip_author_check=True
                )

        if chosen_book is not None:
            # print("chosen book %s" % chosen_book.find("title").text)
            goodreads_link = chosen_book.find("a", class_="bookTitle")["href"]
            book_id = extract_id_from_url(goodreads_link)
            return query_book(book_id)

        closest_match = soup.find_all("tr")[0]
        book_id = extract_id_from_url(
            closest_match.find("a", class_="bookTitle")["href"]
        )
        return query_book(book_id)

    except Exception as e:
        print(f"Failed to fetch book info for {search_query}: {e}")
        return None
