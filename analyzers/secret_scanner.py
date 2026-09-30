import re


def scan_text(text):
    findings = []

    patterns = {
        "API Key": r'(?i)\bapi[_-]?key\s*=\s*["\']?([A-Za-z0-9_\-]{8,})',
        "Secret": r'(?i)\bsecret\s*=\s*["\']?([A-Za-z0-9_\-]{8,})',
        "Token": r'(?i)\btoken\s*=\s*["\']?([A-Za-z0-9_\-]{8,})',
        "Password": r'(?i)\b(password|passwd|pwd)\s*=\s*["\']?([^\s"\']{6,})',
    }

    for category, pattern in patterns.items():

        matches = re.findall(pattern, text)

        for match in matches:

            if isinstance(match, tuple):
                value = match[-1]
            else:
                value = match

            findings.append({
                "category": category,
                "match": value
            })

    return findings