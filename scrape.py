import requests
from bs4 import BeautifulSoup

def search_indian_kanoon(query):
    search_url = f"https://indiankanoon.org/search/?formInput={query.replace(' ', '+')}"
    response = requests.get(search_url)

    if response.status_code != 200:
        print("Failed to fetch results")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract search results
    results = []
    for i, result_item in enumerate(soup.find_all('div', class_='result_title')):
        if i >= 6:  # Limit to the first 6 results
            break
        title = result_item.get_text().strip()
        link = "https://indiankanoon.org" + result_item.find('a')['href']
        results.append({"title": title, "link": link})

    # Print the results
    for result in results:
        print(f"{result['title']}: {result['link']}")

if __name__ == "__main__":
    query = input("Enter your query: ")
    search_indian_kanoon(query)
    