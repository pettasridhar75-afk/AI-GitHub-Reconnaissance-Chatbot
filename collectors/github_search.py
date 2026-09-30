import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def get_github_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "AI-GitHub-Reconnaissance-Chatbot",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    return headers


def search_repositories(company_name):
    url = f"{GITHUB_API_URL}/search/repositories"

    params = {
        "q": company_name,
        "per_page": 10,
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=get_github_headers(),
            timeout=15,
        )

        if response.status_code == 403:
            return {
                "error": (
                    "GitHub API access was rate-limited or denied. "
                    "Add a valid GITHUB_TOKEN to your .env file and try again."
                )
            }

        if response.status_code != 200:
            return {
                "error": f"GitHub API returned status {response.status_code}"
            }

        data = response.json()

        repositories = []

        for repo in data.get("items", []):
            repositories.append({
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "url": repo.get("html_url"),
                "stars": repo.get("stargazers_count"),
                "language": repo.get("language"),
                "owner": repo.get("owner", {}).get("login"),
                "forks": repo.get("forks_count"),
            })

        return repositories

    except requests.exceptions.Timeout:
        return {
            "error": "GitHub request timed out. Please try again."
        }

    except requests.exceptions.ConnectionError:
        return {
            "error": "Could not connect to GitHub. Please check your internet connection."
        }

    except requests.exceptions.RequestException as error:
        return {
            "error": f"GitHub request failed: {error}"
        } 
    