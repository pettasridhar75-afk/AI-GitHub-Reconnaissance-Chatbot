import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


def build_repository_prompt(
    repository,
    branches,
    commits,
    files,
    findings
):
    file_summary = []

    for file in files[:50]:
        file_summary.append({
            "name": file.get("name"),
            "path": file.get("path"),
            "type": file.get("type"),
            "url": file.get("url")
        })

    branch_summary = branches[:20]
    commit_summary = commits[:10]

    finding_summary = []

    for finding in findings[:50]:
        finding_summary.append({
            "file": finding.get("file"),
            "category": finding.get("category"),
            "severity": finding.get("severity"),
            "url": finding.get("url")
        })

    prompt = f"""
You are an AI assistant for a GitHub reconnaissance dashboard.

Analyze ONLY publicly available repository information.

Do not exploit vulnerabilities.
Do not provide exploitation instructions.
Do not validate, use, or expose credentials, tokens, passwords, API keys, or secrets.
Do not claim a vulnerability unless supported by the supplied evidence.

Secret-like patterns are only potential findings requiring human review.

REPOSITORY
Name: {repository.get("name")}
Full Name: {repository.get("full_name")}
Owner: {repository.get("owner")}
Description: {repository.get("description")}
URL: {repository.get("url")}
Stars: {repository.get("stars")}
Forks: {repository.get("forks")}
Language: {repository.get("language")}
Default Branch: {repository.get("default_branch")}
Open Issues: {repository.get("open_issues")}
License: {repository.get("license")}

BRANCHES
{branch_summary}

RECENT COMMITS
{commit_summary}

FILES
{file_summary}

SECURITY FINDINGS
{finding_summary}

Provide exactly these sections:

1. Repository Overview
2. Technology and Structure
3. Development Activity
4. Security Findings
5. Risk Areas
6. Recommended Review Areas

Keep the response factual and concise.
Do not invent security issues.
Do not expose secret values.
"""

    return prompt


def _call_gemini(client, prompt):
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text


def generate_gemini_response(prompt):
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add your Gemini API key to the .env file."
        )

    client = genai.Client(api_key=GEMINI_API_KEY)

    last_error = None

    # Normal request
    for attempt in range(3):
        try:
            return _call_gemini(client, prompt)

        except Exception as error:
            last_error = error
            error_text = str(error)

            if "503" not in error_text and "UNAVAILABLE" not in error_text:
                raise

            if attempt < 2:
                time.sleep(2 ** attempt)

    # ---------------------------------------------------------
    # FALLBACK
    # If Gemini is busy with the larger request, send a tiny
    # request containing only the most important information.
    # ---------------------------------------------------------

    fallback_prompt = f"""
Analyze this GitHub reconnaissance summary.

Give a concise factual security/repository analysis.

Do not exploit anything.
Do not expose secrets.
Do not invent vulnerabilities.

SUMMARY:

{prompt[:5000]}

Return:

1. Repository Overview
2. Technology and Structure
3. Development Activity
4. Security Findings
5. Risk Areas
6. Recommended Review Areas
"""

    for attempt in range(3):
        try:
            return _call_gemini(client, fallback_prompt)

        except Exception as error:
            last_error = error
            error_text = str(error)

            if "503" not in error_text and "UNAVAILABLE" not in error_text:
                raise

            if attempt < 2:
                time.sleep(3 * (attempt + 1))

    raise RuntimeError(
        "Gemini is temporarily unavailable after normal and fallback "
        f"requests. Last error: {last_error}"
    )


def analyze_repository_with_ai(
    repository,
    branches,
    commits,
    files,
    findings,
    llm_function=None
):
    prompt = build_repository_prompt(
        repository,
        branches,
        commits,
        files,
        findings
    )

    if llm_function is None:
        llm_function = generate_gemini_response

    try:
        response = llm_function(prompt)

        return {
            "status": "success",
            "analysis": response
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        } 
    
    
    