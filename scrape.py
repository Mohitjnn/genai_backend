import os
import json
import requests
import http.client
import urllib.parse


class IKApiClient:
    def __init__(self, token):
        self.headers = {
            'Authorization': f'Token {token}',
            'Accept': 'application/json'
        }
        self.basehost = 'api.indiankanoon.org'

    def call_api(self, url):
        """Call the Indian Kanoon API."""
        try:
            connection = http.client.HTTPSConnection(self.basehost)
            connection.request('POST', url, headers=self.headers)
            response = connection.getresponse()
            results = response.read()

            if isinstance(results, bytes):
                results = results.decode('utf8')

            return results
        except Exception as e:
            return json.dumps({"errmsg": f"API call failed: {str(e)}"})

    def search(self, query, pagenum=0, maxpages=1):
        """Search Indian Kanoon with the provided query."""
        q = urllib.parse.quote_plus(query.encode('utf8'))
        url = f'/search/?formInput={q}&pagenum={pagenum}&maxpages={maxpages}'
        return self.call_api(url)


def search_indian_kanoon(query):
    """Search Indian Kanoon and return formatted results."""
    # Initialize API client with token
    token = "0ca52cdc1fd70a83184e00a6ace08a0c2c59d235"  # Using the token from your code
    api_client = IKApiClient(token)

    # Search using the API
    results = api_client.search(query)

    try:
        # Parse JSON response
        data = json.loads(results)

        # Check for errors
        if 'errmsg' in data:
            return {"error": data['errmsg']}

        # Format results (limited to 6)
        formatted_results = []
        if 'docs' in data:
            for i, doc in enumerate(data['docs']):
                if i >= 6:  # Limit to 6 results
                    break

                formatted_results.append({
                    "title": doc['title'],
                    "link": f"https://indiankanoon.org/doc/{doc['tid']}/",
                    "description": doc.get('headline', 'No headline available')
                })

        return formatted_results
    except json.JSONDecodeError:
        return {"error": "Failed to parse API response"}
    except Exception as e:
        return {"error": f"Error processing results: {str(e)}"}


