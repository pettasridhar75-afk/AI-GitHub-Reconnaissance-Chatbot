from analyzers.secret_scanner import scan_text


def analyze_files(files):

    findings = []


    for file in files:

        content = file.get("content")

        if not content:
            continue


        results = scan_text(content)


        for result in results:

            findings.append({

                "file": file.get("path"),

                "category": result.get(
                    "category",
                    "Unknown"
                ),

                "severity": result.get(
                    "severity",
                    "Medium"
                ),

                "match": result.get(
                    "match"
                ),

                "url": file.get("url")

            })


    return findings