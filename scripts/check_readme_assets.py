from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def main() -> None:
    text = README.read_text(encoding="utf-8")
    images = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text)
    html_images = re.findall(r'<img[^>]+src="([^"]+)"', text)
    paths = sorted(
        {
            value.split("#", 1)[0]
            for value in images + html_images
            if not value.startswith(("http://", "https://", "data:"))
        }
    )

    assert paths, "README does not contain any local image assets"

    for relative in paths:
        path = ROOT / relative
        assert path.is_file(), f"README image is missing: {relative}"
        if path.suffix.lower() == ".svg":
            ElementTree.parse(path)
        elif path.suffix.lower() == ".png":
            assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), (
                f"README PNG asset is invalid: {relative}"
            )

    assert not (ROOT / "main.png").exists(), "main.png should not be present"
    print(f"validated {len(paths)} local README image assets")


if __name__ == "__main__":
    main()
