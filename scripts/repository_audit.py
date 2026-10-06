from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PATHS = {
    "main.png",
    "LICENSE_ACE",
    "LICENSE_MCP",
    "graphrag",
    "ACE_PRIME",
    "CORE_DEMOS",
    "PUBLIC_PROJECTS",
    "images",
    "indexing",
    "lancedb",
    "gragSrc",
}

FORBIDDEN_WORDS = (
    "provenance",
    "upstream",
    "ACE_PRIME",
    "CORE_DEMOS",
    "PUBLIC_PROJECTS",
    "GraphRAG-Local-UI",
    "GragACE",
    "David Shapiro",
    "Beckett",
    "Microsoft Corporation",
)

TEXT_EXTENSIONS = {
    ".md", ".py", ".toml", ".txt", ".yml", ".yaml", ".json", ".sh", ".html"
}


def local_links(text: str) -> list[str]:
    values = re.findall(r"!?(?:\[[^\]]*\])\(([^)]+)\)", text)
    values += re.findall(r'<img[^>]+src="([^"]+)"', text)
    return [
        value.split("#", 1)[0]
        for value in values
        if value and not value.startswith(("http://", "https://", "data:", "#"))
    ]


def main() -> None:
    readmes = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and path.name.lower().startswith("readme")
    ]
    licenses = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.name.lower().startswith(("license", "copying"))
    ]

    assert readmes == ["README.md"], f"README files: {readmes}"
    assert licenses == ["LICENSE"], f"License files: {licenses}"

    for forbidden in FORBIDDEN_PATHS:
        assert not (ROOT / forbidden).exists(), f"forbidden path exists: {forbidden}"

    assert not (ROOT / "main.png").exists(), "main.png must not be present"

    tracked_like_files = [
        path for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and path.suffix.lower() in TEXT_EXTENSIONS
    ]

    for path in tracked_like_files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for word in FORBIDDEN_WORDS:
            assert word not in text, f"{word!r} found in {path}"

        if path.name == ".env":
            raise AssertionError(f"local .env file must not be present: {path}")

        if path.suffix.lower() == ".md":
            for relative in local_links(text):
                target = (path.parent / relative).resolve()
                assert target.exists(), (
                    f"broken local documentation link: {path} -> {relative}"
                )

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "Copyright (c) 2026 Pirate-Emperor" in license_text
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "Pirate-Emperor"' in pyproject
    init_text = (ROOT / "enterprise_graphrag" / "__init__.py").read_text(
        encoding="utf-8"
    )
    assert '__author__ = "Pirate-Emperor"' in init_text

    print("repository audit passed")
    print("README files:", readmes)
    print("license files:", licenses)
    print("text files checked:", len(tracked_like_files))


if __name__ == "__main__":
    main()
