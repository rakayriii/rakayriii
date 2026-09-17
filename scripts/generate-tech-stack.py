import json
import os
import urllib.request
import urllib.parse
from collections import Counter
from pathlib import Path


USERNAME = "rakayriii"
API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "rakayriii-tech-stack-generator",
}


# =========================================================
# GitHub API
# =========================================================

def github_get(url):
    request = urllib.request.Request(url, headers=HEADERS)

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def get_repositories():
    repositories = []
    page = 1

    while True:
        url = (
            f"{API}/users/{USERNAME}/repos"
            f"?per_page=100&page={page}&sort=updated"
        )

        data = github_get(url)

        if not data:
            break

        repositories.extend(data)

        if len(data) < 100:
            break

        page += 1

    return [
        repo
        for repo in repositories
        if not repo["fork"]
        and not repo["archived"]
        and repo["name"] != USERNAME
    ]


def get_languages(repo):
    url = f"{API}/repos/{USERNAME}/{repo['name']}/languages"

    try:
        return github_get(url)
    except Exception as error:
        print(f"Language error: {repo['name']} -> {error}")
        return {}


def get_root_files(repo):
    url = f"{API}/repos/{USERNAME}/{repo['name']}/contents"

    try:
        data = github_get(url)

        if not isinstance(data, list):
            return {}

        return {
            item["name"].lower(): item
            for item in data
            if item["type"] == "file"
        }

    except Exception as error:
        print(f"File error: {repo['name']} -> {error}")
        return {}


def get_file(repo, filename):
    url = (
        f"{API}/repos/{USERNAME}/{repo['name']}"
        f"/contents/{urllib.parse.quote(filename)}"
    )

    try:
        data = github_get(url)

        if data.get("encoding") != "base64":
            return ""

        import base64

        return base64.b64decode(data["content"]).decode(
            "utf-8",
            errors="ignore"
        )

    except Exception:
        return ""


# =========================================================
# Dependency detection
# =========================================================

def detect_from_package_json(content):
    technologies = set()

    if not content:
        return technologies

    try:
        data = json.loads(content)
    except Exception:
        return technologies

    dependencies = {}

    dependencies.update(data.get("dependencies", {}))
    dependencies.update(data.get("devDependencies", {}))
    dependencies.update(data.get("peerDependencies", {}))

    dependency_names = set(dependencies.keys())

    checks = {
        "next": "Next.js",
        "react": "React",
        "react-dom": "React",
        "vue": "Vue",
        "nuxt": "Nuxt",
        "svelte": "Svelte",
        "@sveltejs/kit": "SvelteKit",
        "express": "Express",
        "fastify": "Fastify",
        "nestjs": "NestJS",
        "@nestjs/core": "NestJS",
        "astro": "Astro",
        "vite": "Vite",
        "tailwindcss": "Tailwind CSS",
        "electron": "Electron",
        "three": "Three.js",
        "framer-motion": "Framer Motion",
        "axios": "Axios",
    }

    for dependency, technology in checks.items():
        if dependency in dependency_names:
            technologies.add(technology)

    if "typescript" in dependency_names:
        technologies.add("TypeScript")

    if "eslint" in dependency_names:
        technologies.add("ESLint")

    return technologies


def detect_from_composer_json(content):
    technologies = set()

    if not content:
        return technologies

    try:
        data = json.loads(content)
    except Exception:
        return technologies

    dependencies = {}

    dependencies.update(data.get("require", {}))
    dependencies.update(data.get("require-dev", {}))

    dependency_names = set(dependencies.keys())

    checks = {
        "laravel/framework": "Laravel",
        "laravel/sanctum": "Laravel Sanctum",
        "laravel/breeze": "Laravel Breeze",
        "laravel/jetstream": "Laravel Jetstream",
        "livewire/livewire": "Livewire",
        "inertiajs/inertia-laravel": "Inertia.js",
        "symfony/framework-bundle": "Symfony",
        "symfony/console": "Symfony",
        "filament/filament": "Filament",
    }

    for dependency, technology in checks.items():
        if dependency in dependency_names:
            technologies.add(technology)

    return technologies


def detect_from_files(files):
    technologies = set()

    names = set(files.keys())

    # Docker
    if "dockerfile" in names:
        technologies.add("Docker")

    if "docker-compose.yml" in names:
        technologies.add("Docker")

    if "compose.yml" in names:
        technologies.add("Docker")

    # Python
    if "requirements.txt" in names:
        technologies.add("Python")

    if "pyproject.toml" in names:
        technologies.add("Python")

    if "manage.py" in names:
        technologies.add("Django")

    # Go
    if "go.mod" in names:
        technologies.add("Go")

    # Rust
    if "cargo.toml" in names:
        technologies.add("Rust")

    # Ruby
    if "gemfile" in names:
        technologies.add("Ruby")

    # Java
    if "pom.xml" in names:
        technologies.add("Java")

    if "build.gradle" in names:
        technologies.add("Java")

    return technologies


# =========================================================
# Technology metadata
# =========================================================

TECHNOLOGY_DATA = {
    "PHP": ("php", "#777BB4"),
    "Laravel": ("laravel", "#FF2D20"),
    "Laravel Sanctum": ("laravel", "#FF2D20"),
    "Laravel Breeze": ("laravel", "#FF2D20"),
    "Laravel Jetstream": ("laravel", "#FF2D20"),
    "Livewire": ("livewire", "#4E56A6"),
    "Inertia.js": ("inertia", "#9553E9"),
    "Symfony": ("symfony", "#000000"),
    "Filament": ("filament", "#F59E0B"),

    "JavaScript": ("javascript", "#F7DF1E"),
    "TypeScript": ("typescript", "#3178C6"),
    "React": ("react", "#61DAFB"),
    "Next.js": ("nextdotjs", "#000000"),
    "Vue": ("vuedotjs", "#4FC08D"),
    "Nuxt": ("nuxt", "#00DC82"),
    "Svelte": ("svelte", "#FF3E00"),
    "SvelteKit": ("svelte", "#FF3E00"),
    "Express": ("express", "#000000"),
    "Fastify": ("fastify", "#000000"),
    "NestJS": ("nestjs", "#E0234E"),
    "Astro": ("astro", "#FF5D01"),
    "Vite": ("vite", "#646CFF"),
    "Tailwind CSS": ("tailwindcss", "#06B6D4"),
    "Electron": ("electron", "#47848F"),
    "Three.js": ("threedotjs", "#000000"),
    "Framer Motion": ("framer", "#0055FF"),
    "Axios": ("axios", "#5A29E4"),
    "ESLint": ("eslint", "#4B32C3"),

    "HTML": ("html5", "#E34F26"),
    "CSS": ("css3", "#1572B6"),
    "Python": ("python", "#3776AB"),
    "Django": ("django", "#092E20"),
    "Go": ("go", "#00ADD8"),
    "Rust": ("rust", "#000000"),
    "Ruby": ("ruby", "#CC342D"),
    "Java": ("openjdk", "#437291"),

    "Docker": ("docker", "#2496ED"),
    "Git": ("git", "#F05032"),
    "GitHub": ("github", "#181717"),
}


# =========================================================
# SVG helpers
# =========================================================

def escape_xml(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def icon_svg(slug, color, x, y, size=28):
    """
    Fetch Simple Icons SVG and embed its path directly.
    """

    url = (
        "https://cdn.jsdelivr.net/npm/simple-icons@latest/"
        f"icons/{slug}.svg"
    )

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "rakayriii-tech-stack-generator"}
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            svg = response.read().decode("utf-8")

        start = svg.find("<path")
        end = svg.find("</svg>")

        if start == -1 or end == -1:
            return ""

        path = svg[start:end]

        path = path.replace(
            'fill="currentColor"',
            f'fill="{color}"'
        )

        path = path.replace(
            'fill="none"',
            f'fill="{color}"'
        )

        return f"""
        <g transform="translate({x},{y}) scale({size / 24})">
            {path}
        </g>
        """

    except Exception as error:
        print(f"Icon error: {slug} -> {error}")
        return ""


def create_svg(title, items, output_file):
    width = 900
    row_height = 64
    top = 85
    height = top + len(items) * row_height + 35

    svg = [
        f'<svg width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" rx="18" fill="#0d1117"/>',
        f'<text x="35" y="45" fill="#f0f6fc" '
        f'font-family="Arial, sans-serif" font-size="22" '
        f'font-weight="700">{escape_xml(title)}</text>',
    ]

    for index, item in enumerate(items):
        name = item["name"]
        percent = item["percent"]

        y = top + index * row_height

        slug, color = TECHNOLOGY_DATA.get(
            name,
            (name.lower().replace(" ", ""), "#8b949e")
        )

        svg.append(
            icon_svg(
                slug,
                color,
                35,
                y,
                27
            )
        )

        svg.append(
            f'<text x="78" y="{y + 22}" fill="#c9d1d9" '
            f'font-family="Arial, sans-serif" font-size="16" '
            f'font-weight="600">{escape_xml(name)}</text>'
        )

        bar_x = 280
        bar_width = 430
        bar_height = 12

        svg.append(
            f'<rect x="{bar_x}" y="{y + 9}" '
            f'width="{bar_width}" height="{bar_height}" '
            f'rx="6" fill="#21262d"/>'
        )

        filled_width = max(
            3,
            bar_width * (percent / 100)
        )

        svg.append(
            f'<rect x="{bar_x}" y="{y + 9}" '
            f'width="{filled_width:.1f}" '
            f'height="{bar_height}" rx="6" '
            f'fill="{color}"/>'
        )

        svg.append(
            f'<text x="735" y="{y + 22}" fill="#f0f6fc" '
            f'font-family="Arial, sans-serif" font-size="15" '
            f'font-weight="700">{percent:.1f}%</text>'
        )

    svg.append("</svg>")

    Path(output_file).write_text(
        "\n".join(svg),
        encoding="utf-8"
    )


# =========================================================
# README updater
# =========================================================

def update_readme(language_items, framework_items):
    readme_path = Path("README.md")

    if not readme_path.exists():
        return

    content = readme_path.read_text(encoding="utf-8")

    language_text = "\n".join(
        f"- **{item['name']}** `{item['percent']:.1f}%`"
        for item in language_items
    )

    framework_text = "\n".join(
        f"- **{item['name']}** `{item['percent']:.1f}%`"
        for item in framework_items
    )

    language_block = (
        "<!-- LANGUAGES_START -->\n"
        f"{language_text}\n"
        "<!-- LANGUAGES_END -->"
    )

    framework_block = (
        "<!-- FRAMEWORKS_START -->\n"
        f"{framework_text}\n"
        "<!-- FRAMEWORKS_END -->"
    )

    if (
        "<!-- LANGUAGES_START -->" in content
        and "<!-- LANGUAGES_END -->" in content
    ):
        start = content.index("<!-- LANGUAGES_START -->")
        end = content.index("<!-- LANGUAGES_END -->") + len(
            "<!-- LANGUAGES_END -->"
        )

        content = (
            content[:start]
            + language_block
            + content[end:]
        )

    if (
        "<!-- FRAMEWORKS_START -->" in content
        and "<!-- FRAMEWORKS_END -->" in content
    ):
        start = content.index("<!-- FRAMEWORKS_START -->")
        end = content.index("<!-- FRAMEWORKS_END -->") + len(
            "<!-- FRAMEWORKS_END -->"
        )

        content = (
            content[:start]
            + framework_block
            + content[end:]
        )

    readme_path.write_text(
        content,
        encoding="utf-8"
    )


# =========================================================
# Main
# =========================================================

def main():
    print("=" * 60)
    print("RAKAYRIII TECHNOLOGY STACK GENERATOR")
    print("=" * 60)

    repositories = get_repositories()

    print(f"\nRepositories found: {len(repositories)}")

    language_bytes = Counter()
    framework_usage = Counter()

    total_repositories = len(repositories)

    for repo in repositories:
        name = repo["name"]

        print(f"\nScanning: {name}")

        languages = get_languages(repo)

        for language, amount in languages.items():
            language_bytes[language] += amount

        files = get_root_files(repo)

        detected = detect_from_files(files)

        if "package.json" in files:
            package_json = get_file(repo, "package.json")
            detected.update(
                detect_from_package_json(package_json)
            )

        if "composer.json" in files:
            composer_json = get_file(repo, "composer.json")
            detected.update(
                detect_from_composer_json(composer_json)
            )

        print(
            "Detected:",
            ", ".join(sorted(detected))
            if detected
            else "None"
        )

        for technology in detected:
            framework_usage[technology] += 1

    # -----------------------------------------------------
    # Language percentages
    # -----------------------------------------------------

    total_bytes = sum(language_bytes.values())

    language_items = []

    for name, amount in language_bytes.most_common():
        percent = (
            (amount / total_bytes) * 100
            if total_bytes
            else 0
        )

        language_items.append({
            "name": name,
            "percent": percent,
        })

    # -----------------------------------------------------
    # Framework percentages
    # -----------------------------------------------------

    framework_items = []

    for name, count in framework_usage.most_common():
        percent = (
            (count / total_repositories) * 100
            if total_repositories
            else 0
        )

        framework_items.append({
            "name": name,
            "percent": percent,
        })

    # -----------------------------------------------------
    # Output
    # -----------------------------------------------------

    generated = Path("generated")
    generated.mkdir(exist_ok=True)

    create_svg(
        "Languages",
        language_items,
        generated / "languages.svg"
    )

    create_svg(
        "Frameworks & Technologies",
        framework_items,
        generated / "frameworks.svg"
    )

    update_readme(
        language_items,
        framework_items
    )

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)

    print("\nLanguages:")
    for item in language_items:
        print(
            f"  {item['name']}: "
            f"{item['percent']:.1f}%"
        )

    print("\nFrameworks:")
    for item in framework_items:
        print(
            f"  {item['name']}: "
            f"{item['percent']:.1f}%"
        )


if __name__ == "__main__":
    main()
