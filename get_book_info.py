from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from dotenv import dotenv_values
import requests
from bs4 import BeautifulSoup
from utils.formatter import extract_id_from_url

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


def get_book_info_based_on_search_query(search_query: str):
    try:
        url = f"https://goodreads.com/search?page=1&q={search_query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=3000)
        soup = BeautifulSoup(response.text, "html.parser")

        # TODO: reuse goodreads_bot matching algorithm
        closest_match = soup.find_all("tr")[0]

        # # title = closest_match.find(class_="bookTitle").get_text().strip()
        # # author_name = closest_match.find(class_="authorName").get_text().strip()
        goodreads_link = closest_match.find("a", class_="bookTitle")["href"]
        book_id = extract_id_from_url(goodreads_link)

        return query_book(book_id)

    except Exception as e:
        print(f"Failed to fetch book info for {search_query}: {e}")
        return None
