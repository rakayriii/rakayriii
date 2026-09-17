import os
import re
import json
import base64
import urllib.request
from pathlib import Path
from html import escape


# ============================================================
# CONFIG
# ============================================================

USERNAME = "rakayriii"

API_BASE = "https://api.github.com"

OUTPUT_DIR = Path("generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Technology:
# "Simple Icons slug", "brand color"
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
    "Blade": ("laravel", "#FF2D20"),

    # Backend / Frameworks
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

    # Tools
    "Vite": ("vite", "#646CFF"),
    "Tailwind CSS": ("tailwindcss", "#06B6D4"),
    "ESLint": ("eslint", "#4B32C3"),
    "Axios": ("axios", "#5A29E4"),
    "Framer Motion": ("framer", "#FFFFFF"),
    "Three.js": ("threedotjs", "#FFFFFF"),
    "Electron": ("electron", "#47848F"),
    "Docker": ("docker", "#2496ED"),
    "Git": ("git", "#F05032"),
    "GitHub": ("github", "#FFFFFF"),
}


# ============================================================
# GITHUB API
# ============================================================

def github_request(url):
    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "rakayriii-tech-stack-generator",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        url,
        headers=headers
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=20
        ) as response:

            return json.loads(
                response.read().decode("utf-8")
            )

    except Exception as error:

        print(f"GitHub API error: {url}")
        print(error)

        return None


# ============================================================
# REPOSITORIES
# ============================================================

def get_repositories():

    repositories = []

    page = 1

    while True:

        url = (
            f"{API_BASE}/users/"
            f"{USERNAME}/repos"
            f"?per_page=100"
            f"&page={page}"
            f"&type=owner"
        )

        data = github_request(url)

        if not data:
            break

        if not isinstance(data, list):
            break

        for repo in data:

            # Ignore forked repositories
            if repo.get("fork"):
                continue

            # Ignore archived repositories
            if repo.get("archived"):
                continue

            # Ignore profile repository
            if repo.get("name") == USERNAME:
                continue

            repositories.append(repo)

        if len(data) < 100:
            break

        page += 1

    print(
        f"Found {len(repositories)} repositories."
    )

    return repositories


# ============================================================
# REPOSITORY CONTENT
# ============================================================

def get_root_files(repo):

    repo_name = repo["name"]

    url = (
        f"{API_BASE}/repos/"
        f"{USERNAME}/{repo_name}/contents/"
    )

    data = github_request(url)

    if not isinstance(data, list):
        return []

    return [
        item.get("name", "")
        for item in data
    ]


def get_file(repo, filename):

    repo_name = repo["name"]

    url = (
        f"{API_BASE}/repos/"
        f"{USERNAME}/{repo_name}/contents/"
        f"{filename}"
    )

    data = github_request(url)

    if not data:
        return None

    content = data.get("content")

    if not content:
        return None

    try:

        decoded = base64.b64decode(
            content.replace("\n", "")
        )

        return decoded.decode(
            "utf-8",
            errors="ignore"
        )

    except Exception:

        return None


# ============================================================
# PACKAGE.JSON DETECTION
# ============================================================

def detect_from_package_json(
    package_content,
    detected
):

    if not package_content:
        return

    try:

        package = json.loads(
            package_content
        )

    except Exception:

        return

    dependencies = {}

    dependencies.update(
        package.get("dependencies", {})
    )

    dependencies.update(
        package.get("devDependencies", {})
    )

    dependency_names = set(
        dependencies.keys()
    )

    # --------------------------------------------------------
    # Frameworks
    # --------------------------------------------------------

    if "next" in dependency_names:
        detected.add("Next.js")

    if "react" in dependency_names:
        detected.add("React")

    if "vue" in dependency_names:
        detected.add("Vue")

    if "nuxt" in dependency_names:
        detected.add("Nuxt")

    if "svelte" in dependency_names:
        detected.add("Svelte")

    if "@sveltejs/kit" in dependency_names:
        detected.add("SvelteKit")

    if "astro" in dependency_names:
        detected.add("Astro")

    if "express" in dependency_names:
        detected.add("Express")

    if "fastify" in dependency_names:
        detected.add("Fastify")

    if "@nestjs/core" in dependency_names:
        detected.add("NestJS")

    # --------------------------------------------------------
    # Tools
    # --------------------------------------------------------

    if "vite" in dependency_names:
        detected.add("Vite")

    if "tailwindcss" in dependency_names:
        detected.add("Tailwind CSS")

    if "eslint" in dependency_names:
        detected.add("ESLint")

    if "axios" in dependency_names:
        detected.add("Axios")

    if "framer-motion" in dependency_names:
        detected.add("Framer Motion")

    if "three" in dependency_names:
        detected.add("Three.js")

    if "electron" in dependency_names:
        detected.add("Electron")

    # --------------------------------------------------------
    # TypeScript
    # --------------------------------------------------------

    if (
        "typescript" in dependency_names
        or "tsx" in dependency_names
    ):
        detected.add("TypeScript")


# ============================================================
# COMPOSER.JSON DETECTION
# ============================================================

def detect_from_composer_json(
    composer_content,
    detected
):

    if not composer_content:
        return

    try:

        composer = json.loads(
            composer_content
        )

    except Exception:

        return

    dependencies = {}

    dependencies.update(
        composer.get("require", {})
    )

    dependencies.update(
        composer.get("require-dev", {})
    )

    dependency_names = set(
        dependencies.keys()
    )

    # --------------------------------------------------------
    # Laravel
    # --------------------------------------------------------

    if "laravel/framework" in dependency_names:
        detected.add("Laravel")

    if "laravel/sanctum" in dependency_names:
        detected.add("Laravel Sanctum")

    if "laravel/breeze" in dependency_names:
        detected.add("Laravel Breeze")

    if "laravel/jetstream" in dependency_names:
        detected.add("Laravel Jetstream")

    # --------------------------------------------------------
    # Laravel ecosystem
    # --------------------------------------------------------

    if "livewire/livewire" in dependency_names:
        detected.add("Livewire")

    if "inertiajs/inertia-laravel" in dependency_names:
        detected.add("Inertia.js")

    if "symfony/framework-bundle" in dependency_names:
        detected.add("Symfony")

    if "filament/filament" in dependency_names:
        detected.add("Filament")


# ============================================================
# FILE DETECTION
# ============================================================

def detect_from_files(
    files,
    detected
):

    normalized_files = {
        file.lower()
        for file in files
    }

    # Docker
    if (
        "dockerfile" in normalized_files
        or "docker-compose.yml" in normalized_files
        or "docker-compose.yaml" in normalized_files
        or "compose.yml" in normalized_files
        or "compose.yaml" in normalized_files
    ):
        detected.add("Docker")

    # Python
    if (
        "requirements.txt" in normalized_files
        or "pyproject.toml" in normalized_files
        or "setup.py" in normalized_files
        or "manage.py" in normalized_files
    ):
        detected.add("Python")

    # Django
    if "manage.py" in normalized_files:
        detected.add("Django")

    # Go
    if "go.mod" in normalized_files:
        detected.add("Go")

    # Rust
    if "cargo.toml" in normalized_files:
        detected.add("Rust")

    # Ruby
    if (
        "gemfile" in normalized_files
        or "rakefile" in normalized_files
    ):
        detected.add("Ruby")

    # Java
    if (
        "pom.xml" in normalized_files
        or "build.gradle" in normalized_files
        or "build.gradle.kts" in normalized_files
    ):
        detected.add("Java")

    # Blade
    if any(
        file.endswith(".blade.php")
        for file in normalized_files
    ):
        detected.add("Blade")

    # HTML
    if any(
        file.endswith(".html")
        for file in normalized_files
    ):
        detected.add("HTML")

    # CSS
    if any(
        file.endswith(".css")
        for file in normalized_files
    ):
        detected.add("CSS")

    # JavaScript
    if any(
        file.endswith(".js")
        or file.endswith(".jsx")
        for file in normalized_files
    ):
        detected.add("JavaScript")

    # TypeScript
    if any(
        file.endswith(".ts")
        or file.endswith(".tsx")
        for file in normalized_files
    ):
        detected.add("TypeScript")


# ============================================================
# LANGUAGE STATISTICS
# ============================================================

def get_languages(repo):

    repo_name = repo["name"]

    url = (
        f"{API_BASE}/repos/"
        f"{USERNAME}/{repo_name}/languages"
    )

    data = github_request(url)

    if not isinstance(data, dict):
        return {}

    return data


# ============================================================
# ICON GENERATOR
# ============================================================

def icon_svg(
    slug,
    color,
    x,
    y,
    size=28
):

    url = (
        "https://cdn.jsdelivr.net/npm/"
        "simple-icons@latest/"
        f"icons/{slug}.svg"
    )

    try:

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            svg = response.read().decode(
                "utf-8"
            )

        # Ambil semua <path>
        paths = re.findall(
            r"<path\b[^>]*>",
            svg,
            flags=re.IGNORECASE
        )

        if not paths:
            return ""

        colored_paths = []

        for path in paths:

            # Hapus fill lama
            path = re.sub(
                r'\sfill\s*=\s*["\'][^"\']*["\']',
                "",
                path,
                flags=re.IGNORECASE
            )

            # Hapus stroke lama
            path = re.sub(
                r'\sstroke\s*=\s*["\'][^"\']*["\']',
                "",
                path,
                flags=re.IGNORECASE
            )

            # Hapus inline style
            path = re.sub(
                r'\sstyle\s*=\s*["\'][^"\']*["\']',
                "",
                path,
                flags=re.IGNORECASE
            )

            # Paksa warna
            path = path.replace(
                "<path",
                f'<path fill="{color}"'
            )

            colored_paths.append(path)

        scale = size / 24

        return (
            f'<g transform="translate({x},{y}) '
            f'scale({scale})">'
            + "".join(colored_paths)
            + "</g>"
        )

    except Exception as error:

        print(
            f"Icon error: {slug} -> {error}"
        )

        return ""


# ============================================================
# SVG GENERATOR
# ============================================================

def create_svg(
    title,
    items,
    output_file
):

    width = 900
    row_height = 64

    # Tidak ada title di dalam SVG.
    # Judul sudah ada di README.
    top = 35

    height = (
        top
        + len(items) * row_height
        + 35
    )

    svg = [

        f'<svg '
        f'width="{width}" '
        f'height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg">',

        '<rect '
        'width="100%" '
        'height="100%" '
        'rx="18" '
        'fill="#0d1117"/>',
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

        # ----------------------------------------------------
        # ICON
        # ----------------------------------------------------

        icon = icon_svg(
            slug,
            color,
            35,
            y,
            28
        )

        svg.append(icon)

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        svg.append(
            f'<text '
            f'x="78" '
            f'y="{y + 22}" '
            f'fill="#c9d1d9" '
            f'font-family="Arial, sans-serif" '
            f'font-size="16" '
            f'font-weight="600">'
            f'{escape(name)}'
            f'</text>'
        )

        # ----------------------------------------------------
        # BACKGROUND BAR
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # PROGRESS BAR
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # PERCENTAGE
        # ----------------------------------------------------

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


# ============================================================
# README UPDATE
# ============================================================

def update_readme():

    readme_path = Path("README.md")

    if not readme_path.exists():

        print(
            "README.md not found."
        )

        return

    readme = readme_path.read_text(
        encoding="utf-8"
    )

    language_block = (
        "<!-- LANGUAGES_START -->\n"
        '<div align="center">\n\n'
        '<img src="./generated/languages.svg?v=2" '
        'alt="Languages" />\n\n'
        '</div>\n'
        "<!-- LANGUAGES_END -->"
    )

    framework_block = (
        "<!-- FRAMEWORKS_START -->\n"
        '<div align="center">\n\n'
        '<img src="./generated/frameworks.svg?v=2" '
        'alt="Frameworks & Technologies" />\n\n'
        '</div>\n'
        "<!-- FRAMEWORKS_END -->"
    )

    # --------------------------------------------------------
    # Languages
    # --------------------------------------------------------

    language_pattern = re.compile(
        r"<!-- LANGUAGES_START -->.*?"
        r"<!-- LANGUAGES_END -->",
        re.DOTALL
    )

    if language_pattern.search(readme):

        readme = language_pattern.sub(
            language_block,
            readme
        )

    else:

        readme += (
            "\n\n"
            + language_block
            + "\n"
        )

    # --------------------------------------------------------
    # Frameworks
    # --------------------------------------------------------

    framework_pattern = re.compile(
        r"<!-- FRAMEWORKS_START -->.*?"
        r"<!-- FRAMEWORKS_END -->",
        re.DOTALL
    )

    if framework_pattern.search(readme):

        readme = framework_pattern.sub(
            framework_block,
            readme
        )

    else:

        readme += (
            "\n\n"
            + framework_block
            + "\n"
        )

    readme_path.write_text(
        readme,
        encoding="utf-8"
    )

    print(
        "README.md updated."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "========================================"
    )

    print(
        " GitHub Technology Stack Generator"
    )

    print(
        "========================================"
    )

    repositories = get_repositories()

    if not repositories:

        print(
            "No repositories found."
        )

        return

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    language_bytes = {}

    framework_usage = {}

    total_repositories = len(
        repositories
    )

    # --------------------------------------------------------
    # Scan repositories
    # --------------------------------------------------------

    for index, repo in enumerate(
        repositories,
        start=1
    ):

        repo_name = repo["name"]

        print(
            f"[{index}/{total_repositories}] "
            f"Scanning {repo_name}..."
        )

        detected = set()

        # ----------------------------------------------------
        # Languages
        # ----------------------------------------------------

        languages = get_languages(repo)

        for language, bytes_count in languages.items():

            language_bytes[language] = (
                language_bytes.get(
                    language,
                    0
                )
                + bytes_count
            )

        # ----------------------------------------------------
        # Root files
        # ----------------------------------------------------

        files = get_root_files(repo)

        detect_from_files(
            files,
            detected
        )

        # ----------------------------------------------------
        # package.json
        # ----------------------------------------------------

        if "package.json" in files:

            package_content = get_file(
                repo,
                "package.json"
            )

            detect_from_package_json(
                package_content,
                detected
            )

        # ----------------------------------------------------
        # composer.json
        # ----------------------------------------------------

        if "composer.json" in files:

            composer_content = get_file(
                repo,
                "composer.json"
            )

            detect_from_composer_json(
                composer_content,
                detected
            )

        # ----------------------------------------------------
        # Count framework usage
        # ----------------------------------------------------

        for technology in detected:

            framework_usage[technology] = (
                framework_usage.get(
                    technology,
                    0
                )
                + 1
            )

    # ========================================================
    # LANGUAGE PERCENTAGES
    # ========================================================

    total_language_bytes = sum(
        language_bytes.values()
    )

    language_items = []

    if total_language_bytes > 0:

        for language, bytes_count in sorted(
            language_bytes.items(),
            key=lambda item: item[1],
            reverse=True
        ):

            percent = (
                bytes_count
                / total_language_bytes
                * 100
            )

            language_items.append(
                {
                    "name": language,
                    "percent": percent
                }
            )

    # Limit to top 10
    language_items = language_items[:10]

    # ========================================================
    # FRAMEWORK PERCENTAGES
    # ========================================================

    framework_items = []

    for technology, count in sorted(
        framework_usage.items(),
        key=lambda item: item[1],
        reverse=True
    ):

        percent = (
            count
            / total_repositories
            * 100
        )

        framework_items.append(
            {
                "name": technology,
                "percent": percent
            }
        )

    # Limit to top 10
    framework_items = framework_items[:10]

    # ========================================================
    # CREATE SVG
    # ========================================================

    create_svg(
        "Languages",
        language_items,
        OUTPUT_DIR / "languages.svg"
    )

    create_svg(
        "Frameworks & Technologies",
        framework_items,
        OUTPUT_DIR / "frameworks.svg"
    )

    # ========================================================
    # UPDATE README
    # ========================================================

    update_readme()

    # ========================================================
    # OUTPUT
    # ========================================================

    print()
    print(
        "========================================"
    )

    print(
        " Technology statistics generated!"
    )

    print(
        "========================================"
    )

    print(
        f"Languages: {len(language_items)}"
    )

    print(
        f"Frameworks: {len(framework_items)}"
    )

    print(
        f"Output: {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()
