import os
import json
import urllib.request
import urllib.error
from collections import Counter

USERNAME = "rakayriii"
TOKEN = os.environ.get("GITHUB_TOKEN")

API = "https://api.github.com"


def github_request(url):
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "rakayriii-tech-stack"
        }
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode())


def get_repositories():
    repos = []
    page = 1

    while True:
        url = f"{API}/users/{USERNAME}/repos?per_page=100&page={page}"
        data = github_request(url)

        if not data:
            break

        repos.extend(data)

        if len(data) < 100:
            break

        page += 1

    return [
        repo for repo in repos
        if not repo["fork"]
        and repo["name"] != USERNAME
        and not repo["archived"]
    ]


def get_languages(repo):
    url = f"{API}/repos/{USERNAME}/{repo['name']}/languages"

    try:
        return github_request(url)
    except Exception:
        return {}


def get_root_files(repo):
    url = f"{API}/repos/{USERNAME}/{repo['name']}/contents"

    try:
        data = github_request(url)

        if isinstance(data, list):
            return {
                item["name"].lower()
                for item in data
                if item["type"] == "file"
            }

    except Exception:
        pass

    return set()


def detect_frameworks(files):
    detected = set()

    # PHP / Laravel
    if "composer.json" in files:
        detected.add("Laravel")

    # JavaScript / TypeScript
    if "package.json" in files:
        detected.add("Node.js")

    if "next.config.js" in files or "next.config.mjs" in files or "next.config.ts" in files:
        detected.add("Next.js")

    if "vite.config.js" in files or "vite.config.ts" in files:
        detected.add("Vite")

    if "nuxt.config.ts" in files or "nuxt.config.js" in files:
        detected.add("Nuxt")

    # Python
    if "requirements.txt" in files or "pyproject.toml" in files:
        detected.add("Python")

    if "manage.py" in files:
        detected.add("Django")

    # Go
    if "go.mod" in files:
        detected.add("Go")

    # Rust
    if "cargo.toml" in files:
        detected.add("Rust")

    # Docker
    if "dockerfile" in files or "docker-compose.yml" in files or "compose.yml" in files:
        detected.add("Docker")

    return detected


def percentage(value, total):
    if total == 0:
        return 0

    return round((value / total) * 100, 1)


def make_bar(value, width=20):
    filled = round((value / 100) * width)
    return "█" * filled + "░" * (width - filled)


def main():
    print("Scanning repositories...")

    repos = get_repositories()

    print(f"Found {len(repos)} repositories.")

    language_bytes = Counter()
    framework_repos = Counter()

    total_repos = len(repos)

    for repo in repos:
        print(f"Scanning: {repo['name']}")

        languages = get_languages(repo)

        for language, amount in languages.items():
            language_bytes[language] += amount

        files = get_root_files(repo)

        frameworks = detect_frameworks(files)

        for framework in frameworks:
            framework_repos[framework] += 1

    total_language_bytes = sum(language_bytes.values())

    os.makedirs("generated", exist_ok=True)

    # -------------------------
    # Languages
    # -------------------------

    language_lines = [
        "# Languages",
        "",
        "> Automatically generated from GitHub repository language statistics.",
        ""
    ]

    for language, amount in language_bytes.most_common():
        percent = percentage(amount, total_language_bytes)

        language_lines.append(
            f"- **{language}** `{percent}%` "
            f"`{make_bar(percent)}`"
        )

    with open("generated/languages.md", "w", encoding="utf-8") as file:
        file.write("\n".join(language_lines))

    # -------------------------
    # Frameworks
    # -------------------------

    framework_lines = [
        "# Frameworks & Technologies",
        "",
        "> Automatically detected from repository files.",
        ""
    ]

    for framework, count in framework_repos.most_common():
        percent = percentage(count, total_repos)

        framework_lines.append(
            f"- **{framework}** `{percent}%` "
            f"`{make_bar(percent)}` "
            f"({count}/{total_repos} repositories)"
        )

    with open("generated/frameworks.md", "w", encoding="utf-8") as file:
        file.write("\n".join(framework_lines))

    print("Technology statistics generated successfully.")


if __name__ == "__main__":
    main()
