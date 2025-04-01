import requests
from bs4 import BeautifulSoup


def search_indian_kanoon(query):
    search_url = f"https://indiankanoon.org/search/?formInput={query.replace(' ', '+')}"
    response = requests.get(search_url)

    if response.status_code != 200:
        return {"error": f"Failed to fetch results, {response}"}

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract search results
    results = []
    counter = 0  # Initialize counter to limit results

    for result_item in soup.find_all("div", class_="result"):
        if counter >= 6:  # Stop after 6 results
            break

        title = (
            result_item.find("div", class_="result_title")
            .get_text()
            .strip()
            .replace("\n", "")
        )
        link = "https://indiankanoon.org" + result_item.find("a")["href"]

        # Extract and concatenate content within 'headline' class
        headline_tag = result_item.find("div", class_="headline")
        if headline_tag:
            # Concatenate all the text in the 'headline' tag into one string and remove newlines
            description = "".join(headline_tag.stripped_strings).replace("\n", "")
        else:
            description = "No headline available"

        results.append({"title": title, "link": link, "description": description})
        counter += 1  # Increment counter for each result

    return results
