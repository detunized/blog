#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "pyyaml>=6"]
# ///
"""Check the local photo folder against the blog and deploy it to Cloudflare as a static Worker."""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from PIL import Image

BLOG = Path(__file__).resolve().parent.parent
PHOTOS_JSON = BLOG / "data/photos.json"
GALLERY_PAGES = BLOG / "content/photo"
PHOTOS_DIR = Path.home() / "stuff/blog-photos"
WORKER = "detunized-photos"
COMPATIBILITY_DATE = "2026-10-01"

# Re-exports keep the file names, so browsers shouldn't hold on to a photo for long
HEADERS = """/galleries/*
  Cache-Control: public, max-age=86400
"""


def galleries():
    for page in sorted(GALLERY_PAGES.glob("*.md")):
        if page.name.startswith("_"):
            continue
        front = yaml.safe_load(re.match(r"---\n(.*?)\n---\n", page.read_text(), re.S).group(1))
        yield page, front["folder"], front["photos"] + ["title.jpg"]


def check(photos_dir):
    sizes = json.loads(PHOTOS_JSON.read_text())
    errors, expected = [], set()
    for page, folder, names in galleries():
        for name in names:
            path = photos_dir / "galleries" / folder / name
            expected.add(path)
            size = sizes.get(folder, {}).get(name)
            if not path.exists():
                errors.append(f"missing {path} ({page.name})")
            elif size is None:
                errors.append(f"no size for {folder}/{name} in {PHOTOS_JSON.name}")
            elif list(Image.open(path).size) != size:
                errors.append(f"{path} is {Image.open(path).size}, {PHOTOS_JSON.name} says {size}")
    extra = sorted(p for p in (photos_dir / "galleries").rglob("*") if p.is_file() and p not in expected)
    return errors, len(expected), extra


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--photos-dir", type=Path, default=PHOTOS_DIR, help="contains galleries/<folder>/")
    parser.add_argument("--check", action="store_true", help="only check, don't deploy")
    parser.add_argument("--dry-run", action="store_true", help="let wrangler build the upload without sending it")
    args = parser.parse_args()

    errors, count, extra = check(args.photos_dir)
    for path in extra:
        print(f"not used by the blog: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(f"{len(errors)} problems, nothing deployed")
    print(f"{count} photos and banners match the blog", flush=True)
    if args.check:
        return

    (args.photos_dir / "_headers").write_text(HEADERS)
    # An empty working directory, otherwise wrangler finds the Hugo site and tries to deploy the blog
    with tempfile.TemporaryDirectory() as cwd:
        sys.exit(subprocess.run(
            ["npx", "--yes", "wrangler@4", "deploy", "--name", WORKER, "--assets", str(args.photos_dir),
             "--compatibility-date", COMPATIBILITY_DATE, *(["--dry-run"] if args.dry_run else [])],
            cwd=cwd,
        ).returncode)


if __name__ == "__main__":
    main()
