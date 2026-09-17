import json
import os
import re
import urllib.request
import urllib.parse
import base64
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
# GITHUB API
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

        return base64.b64decode(
            data["content"]
        ).decode(
            "utf-8",
            errors="ignore"
        )

    except Exception:
        return ""


# =========================================================
# TECHNOLOGY DETECTION
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

    names = set(dependencies.keys())

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
        "@nestjs/core": "NestJS",
        "astro": "Astro",
        "vite": "Vite",
        "tailwindcss": "Tailwind CSS",
        "electron": "Electron",
        "three": "Three.js",
        "framer-motion": "Framer Motion",
        "axios": "Axios",
        "eslint": "ESLint",
    }

    for dependency, technology in checks.items():
        if dependency in names:
            technologies.add(technology)

    if "typescript" in names:
        technologies.add("TypeScript")

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

    names = set(dependencies.keys())

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
        if dependency in names:
            technologies.add(technology)

    return technologies


def detect_from_files(files):
    technologies = set()

    names = set(files.keys())

    if "dockerfile" in names:
        technologies.add("Docker")

    if "docker-compose.yml" in names:
        technologies.add("Docker")

    if "compose.yml" in names:
        technologies.add("Docker")

    if "requirements.txt" in names:
        technologies.add("Python")

    if "pyproject.toml" in names:
        technologies.add("Python")

    if "manage.py" in names:
        technologies.add("Django")

    if "go.mod" in names:
        technologies.add("Go")

    if "cargo.toml" in names:
        technologies.add("Rust")

    if "gemfile" in names:
        technologies.add("Ruby")

    if "pom.xml" in names:
        technologies.add("Java")

    if "build.gradle" in names:
        technologies.add("Java")

    return technologies


# =========================================================
# TECHNOLOGY COLORS + SIMPLE ICONS
# =========================================================

TECHNOLOGY_DATA = {

    # Languages
    "PHP": ("php", "#777BB4"),
    "JavaScript": ("javascript", "#F7DF1E"),
    "TypeScript": ("typescript", "#3178C6"),
    "HTML": ("html5", "#E34F26"),
    "CSS": ("css3", "#1572B6"),
    "Python": ("python", "#3776AB"),
    "Go": ("go", "#00ADD8"),
    "Rust": ("rust", "#DEA584"),
    "Ruby": ("ruby", "#CC342D"),
    "Java": ("openjdk", "#ED8B00"),

    # Backend
    "Laravel": ("laravel", "#FF2D20"),
    "Laravel Sanctum": ("laravel", "#FF2D20"),
    "Laravel Breeze": ("laravel", "#FF2D20"),
    "Laravel Jetstream": ("laravel", "#FF2D20"),
    "Livewire": ("livewire", "#4E56A6"),
    "Inertia.js": ("inertia", "#9553E9"),
    "Symfony": ("symfony", "#FFFFFF"),
    "Filament": ("filament", "#F59E0B"),
    "Django": ("django", "#44B78B"),

    # Frontend
    "React": ("react", "#61DAFB"),
    "Next.js": ("nextdotjs", "#FFFFFF"),
    "Vue": ("vuedotjs", "#4FC08D"),
    "Nuxt": ("nuxt", "#00DC82"),
    "Svelte": ("svelte", "#FF3E00"),
    "SvelteKit": ("svelte", "#FF3E00"),
    "Astro": ("astro", "#FF5D01"),

    # Node ecosystem
    "Node.js": ("nodedotjs", "#5FA04E"),
    "Express": ("express", "#FFFFFF"),
    "Fastify": ("fastify", "#FFFFFF"),
    "NestJS": ("nestjs", "#E0234E"),

    # Frontend tools
    "Vite": ("vite", "#646CFF"),
    "Tailwind CSS": ("tailwindcss", "#06B6D4"),
    "TypeScript": ("typescript", "#3178C6"),
    "ESLint": ("eslint", "#4B32C3"),
    "Axios": ("axios", "#5A29E4"),
    "Framer Motion": ("framer", "#FFFFFF"),
    "Three.js": ("threedotjs", "#FFFFFF"),

    # Desktop / DevOps
    "Electron": ("electron", "#47848F"),
    "Docker": ("docker", "#2496ED"),
    "Git": ("git", "#F05032"),
    "GitHub": ("github", "#FFFFFF"),
}


# =========================================================
# SVG HELPERS
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
    Download Simple Icons SVG and force the icon
    to use the technology's own color.
    """

    url = (
        "https://cdn.jsdelivr.net/npm/simple-icons@latest/"
        f"icons/{slug}.svg"
    )

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "rakayriii-tech-stack-generator"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:
            svg = response.read().decode("utf-8")

        start = svg.find("<path")
        end = svg.find("</svg>")

        if start == -1 or end == -1:
            return ""

        path = svg[start:end]

        # Remove existing fill attributes
        path = re.sub(
            r'fill="[^"]*"',
            "",
            path
        )

        # Remove stroke attributes
        path = re.sub(
            r'stroke="[^"]*"',
            "",
            path
        )

        # Force technology color
        path = path.replace(
            "<path",
            f'<path fill="{color}"',
            1
        )

        scale = size / 24

        return f"""
        <g transform="translate({x},{y}) scale({scale})">
            {path}
        </g>
        """

    except Exception as error:
        print(
            f"Icon error: {slug} -> {error}"
        )
        return ""


def create_svg(title, items, output_file):

    width = 900

    row_height = 64

    top = 85

    height = (
        top
        + len(items) * row_height
        + 35
    )

    svg = [
        f'<svg width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg">',

        '<rect '
        'width="100%" '
        'height="100%" '
        'rx="18" '
        'fill="#0d1117"/>',

        f'<text '
        f'x="35" '
        f'y="45" '
        f'fill="#f0f6fc" '
        f'font-family="Arial, sans-serif" '
        f'font-size="22" '
        f'font-weight="700">'
        f'{escape_xml(title)}'
        f'</text>',
    ]

    for index, item in enumerate(items):

        name = item["name"]

        percent = item["percent"]

        y = (
            top
            + index * row_height
        )

        slug, color = TECHNOLOGY_DATA.get(
            name,
            (
                name.lower()
                .replace(" ", "")
                .replace(".", ""),
                "#58A6FF"
            )
        )

        # Icon
        svg.append(
            icon_svg(
                slug,
                color,
                35,
                y,
                28
            )
        )

        # Technology name
        svg.append(
            f'<text '
            f'x="78" '
            f'y="{y + 22}" '
            f'fill="#c9d1d9" '
            f'font-family="Arial, sans-serif" '
            f'font-size="16" '
            f'font-weight="600">'
            f'{escape_xml(name)}'
            f'</text>'
        )

        # Background bar
        bar_x = 280
        bar_width = 430
        bar_height = 12

        svg.append(
            f'<rect '
            f'x="{bar_x}" '
            f'y="{y + 9}" '
            f'width="{bar_width}" '
            f'height="{bar_height}" '
            f'rx="6" '
            f'fill="#21262d"/>'
        )

        # Progress
        filled_width = max(
            3,
            bar_width * (
                percent / 100
            )
        )

        svg.append(
            f'<rect '
            f'x="{bar_x}" '
            f'y="{y + 9}" '
            f'width="{filled_width:.1f}" '
            f'height="{bar_height}" '
            f'rx="6" '
            f'fill="{color}"/>'
        )

        # Percentage
        svg.append(
            f'<text '
            f'x="735" '
            f'y="{y + 22}" '
            f'fill="#f0f6fc" '
            f'font-family="Arial, sans-serif" '
            f'font-size="15" '
            f'font-weight="700">'
            f'{percent:.1f}%'
            f'</text>'
        )

    svg.append("</svg>")

    Path(output_file).write_text(
        "\n".join(svg),
        encoding="utf-8"
    )


# =========================================================
# README UPDATE
# =========================================================

def update_readme(
    language_items,
    framework_items
):

    readme_path = Path("README.md")

    if not readme_path.exists():
        return

    content = readme_path.read_text(
        encoding="utf-8"
    )

    language_block = (
        "<!-- LANGUAGES_START -->\n"
        '<div align="center">\n\n'
        '<img src="./generated/languages.svg" '
        'alt="Languages" />\n\n'
        '</div>\n'
        "<!-- LANGUAGES_END -->"
    )

    framework_block = (
        "<!-- FRAMEWORKS_START -->\n"
        '<div align="center">\n\n'
        '<img src="./generated/frameworks.svg" '
        'alt="Frameworks & Technologies" />\n\n'
        '</div>\n'
        "<!-- FRAMEWORKS_END -->"
    )

    if (
        "<!-- LANGUAGES_START -->" in content
        and
        "<!-- LANGUAGES_END -->" in content
    ):

        start = content.index(
            "<!-- LANGUAGES_START -->"
        )

        end = (
            content.index(
                "<!-- LANGUAGES_END -->"
            )
            + len("<!-- LANGUAGES_END -->")
        )

        content = (
            content[:start]
            + language_block
            + content[end:]
        )

    if (
        "<!-- FRAMEWORKS_START -->" in content
        and
        "<!-- FRAMEWORKS_END -->" in content
    ):

        start = content.index(
            "<!-- FRAMEWORKS_START -->"
        )

        end = (
            content.index(
                "<!-- FRAMEWORKS_END -->"
            )
            + len("<!-- FRAMEWORKS_END -->")
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
# MAIN
# =========================================================

def main():

    print("=" * 60)

    print(
        "RAKAYRIII TECHNOLOGY STACK GENERATOR"
    )

    print("=" * 60)

    repositories = get_repositories()

    print(
        f"\nRepositories found: "
        f"{len(repositories)}"
    )

    language_bytes = Counter()

    framework_usage = Counter()

    total_repositories = len(
        repositories
    )

    for repo in repositories:

        name = repo["name"]

        print(
            f"\nScanning: {name}"
        )

        # Languages
        languages = get_languages(
            repo
        )

        for language, amount in languages.items():

            language_bytes[
                language
            ] += amount

        # Files
        files = get_root_files(
            repo
        )

        detected = detect_from_files(
            files
        )

        # package.json
        if "package.json" in files:

            package_json = get_file(
                repo,
                "package.json"
            )

            detected.update(
                detect_from_package_json(
                    package_json
                )
            )

        # composer.json
        if "composer.json" in files:

            composer_json = get_file(
                repo,
                "composer.json"
            )

            detected.update(
                detect_from_composer_json(
                    composer_json
                )
            )

        print(
            "Detected:",
            ", ".join(
                sorted(detected)
            )
            if detected
            else "None"
        )

        for technology in detected:

            framework_usage[
                technology
            ] += 1

    # =====================================================
    # LANGUAGE STATISTICS
    # =====================================================

    total_bytes = sum(
        language_bytes.values()
    )

    language_items = []

    for name, amount in (
        language_bytes.most_common()
    ):

        percent = (
            amount
            / total_bytes
            * 100
            if total_bytes
            else 0
        )

        language_items.append({
            "name": name,
            "percent": percent,
        })

    # =====================================================
    # FRAMEWORK STATISTICS
    # =====================================================

    framework_items = []

    for name, count in (
        framework_usage.most_common()
    ):

        percent = (
            count
            / total_repositories
            * 100
            if total_repositories
            else 0
        )

        framework_items.append({
            "name": name,
            "percent": percent,
        })

    # =====================================================
    # GENERATE FILES
    # =====================================================

    generated = Path(
        "generated"
    )

    generated.mkdir(
        exist_ok=True
    )

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

    # =====================================================
    # RESULT
    # =====================================================

    print("\n")
    print("=" * 60)
    print("TECHNOLOGY STATISTICS")
    print("=" * 60)

    print("\nLANGUAGES:")

    for item in language_items:

        print(
            f"  {item['name']}: "
            f"{item['percent']:.1f}%"
        )

    print("\nFRAMEWORKS & TECHNOLOGIES:")

    for item in framework_items:

        print(
            f"  {item['name']}: "
            f"{item['percent']:.1f}%"
        )

    print("\n")
    print("=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
