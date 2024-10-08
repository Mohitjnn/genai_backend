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
    counter = 0  # Initialize counter to limit results

    for result_item in soup.find_all('div', class_='result'):
        if counter >= 6:  # Stop after 6 results
            break

        title = result_item.find('div', class_='result_title').get_text().strip().replace('\n', '')
        link = "https://indiankanoon.org" + result_item.find('a')['href']

        # Extract and concatenate content within 'headline' class
        headline_tag = result_item.find('div', class_='headline')
        if headline_tag:
            # Concatenate all the text in the 'headline' tag into one string and remove newlines
            headline = ''.join(headline_tag.stripped_strings).replace('\n', '')
        else:
            headline = "No headline available"

        results.append({"title": title, "link": link, "headline": headline})
        counter += 1  # Increment counter for each result

    # Print the results with minimal spaces
    for result in results:
        print(f"Title: {result['title']}\nLink: {result['link']}")
        print(f"Headline: {result['headline']}\n")

if __name__ == "__main__":
    query = input("Enter your query: ")
    search_indian_kanoon(query)