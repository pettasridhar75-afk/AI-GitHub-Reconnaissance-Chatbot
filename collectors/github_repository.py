import os
import time

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

GITHUB_API_URL = "https://api.github.com"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def create_github_session():
    """
    Create a resilient GitHub API session.

    Only public repository API access is used.
    """

    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=10
    )

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "AI-GitHub-Reconnaissance-Chatbot",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    session.headers.update(headers)

    return session


def github_get(url, params=None):
    """
    Safely perform a GET request to GitHub.
    """

    session = create_github_session()

    try:
        response = session.get(
            url,
            params=params,
            timeout=(10, 30)
        )

        if response.status_code == 200:
            return response

        if response.status_code == 403:
            return {
                "error": (
                    "GitHub API access was rate-limited or denied. "
                    "If this continues, configure a GitHub token in .env."
                )
            }

        if response.status_code == 404:
            return {
                "error": "GitHub repository or resource was not found."
            }

        return {
            "error": (
                f"GitHub API returned status "
                f"{response.status_code}"
            )
        }

    except requests.exceptions.Timeout:
        return {
            "error": "GitHub request timed out. Please try again."
        }

    except requests.exceptions.ConnectionError:
        return {
            "error": (
                "Could not connect to GitHub. "
                "The connection was closed or interrupted. "
                "Please try again."
            )
        }

    except requests.exceptions.RequestException as error:
        return {
            "error": f"GitHub request failed: {error}"
        }

    finally:
        session.close()


def get_repository_details(owner, repo):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}"

    response = github_get(url)

    if isinstance(response, dict) and "error" in response:
        return response

    data = response.json()

    return {
        "name": data.get("name"),
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "url": data.get("html_url"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "language": data.get("language"),
        "default_branch": data.get("default_branch"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
        "open_issues": data.get("open_issues_count"),
        "license": (
            data.get("license", {}).get("name")
            if data.get("license")
            else None
        )
    }


def get_branches(owner, repo):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/branches"

    response = github_get(
        url,
        params={"per_page": 20}
    )

    if isinstance(response, dict) and "error" in response:
        return []

    return [
        branch.get("name")
        for branch in response.json()
    ]


def get_recent_commits(owner, repo):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits"

    response = github_get(
        url,
        params={"per_page": 10}
    )

    if isinstance(response, dict) and "error" in response:
        return []

    commits = []

    for commit in response.json():

        commit_data = commit.get("commit", {})
        author_data = commit_data.get("author") or {}

        commits.append({
            "sha": commit.get("sha"),
            "message": commit_data.get("message"),
            "author": author_data.get("name"),
            "date": author_data.get("date"),
            "url": commit.get("html_url")
        })

    return commits


def get_repository_files(owner, repo):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents"

    response = github_get(url)

    if isinstance(response, dict) and "error" in response:
        return []

    files = []

    for item in response.json():

        file_data = {
            "name": item.get("name"),
            "path": item.get("path"),
            "type": item.get("type"),
            "url": item.get("html_url"),
            "content": None
        }

        if item.get("type") == "file":

            download_url = item.get("download_url")

            if download_url:

                try:

                    content_response = requests.get(
                        download_url,
                        headers={
                            "User-Agent":
                                "AI-GitHub-Reconnaissance-Chatbot"
                        },
                        timeout=(10, 30)
                    )

                    if content_response.status_code == 200:

                        file_data["content"] = (
                            content_response.text[:1_000_000]
                        )

                except requests.exceptions.RequestException:
                    # Skip a file if its raw content cannot be downloaded.
                    file_data["content"] = None

        files.append(file_data)

    return files 
