#!/usr/bin/env python3
"""Prepare one approved Obsidian draft for the Graywoods Astro blog.

This tool never commits, pushes, deletes existing content, or overwrites a post.
Dry-run is the default. Pass --apply only after reviewing the plan.
"""

from __future__ import annotations

import argparse
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

AUTHORING_ROOT = Path("/opt/data/graywoods/4. Matter/posts").resolve()
REPO_ROOT = Path(__file__).resolve().parents[1]
POSTS_ROOT = REPO_ROOT / "src/content/posts"
IMAGES_ROOT = REPO_ROOT / "public/images"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fail(message: str) -> "None":
    raise SystemExit(f"ERROR: {message}")


def ensure_within(path: Path, root: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        fail(f"{label} must be inside {root}: {resolved}")
    return resolved


def split_frontmatter(text: str) -> tuple[list[str], str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        fail("source must begin with YAML frontmatter")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index], "".join(lines[index + 1 :])
    fail("source frontmatter has no closing --- marker")


def scalar(frontmatter: list[str], key: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(key)}\s*:\s*(.*?)\s*$")
    for line in frontmatter:
        match = pattern.match(line.rstrip("\r\n"))
        if match:
            value = match.group(1).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]
            return value
    return None


def raw_scalar(frontmatter: list[str], key: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(key)}\s*:\s*(.*?)\s*$")
    for line in frontmatter:
        match = pattern.match(line.rstrip("\r\n"))
        if match:
            return match.group(1).strip()
    return None


def tags_block(frontmatter: list[str]) -> list[str]:
    for index, line in enumerate(frontmatter):
        if re.match(r"^tags\s*:", line):
            block = [line.rstrip("\r\n")]
            cursor = index + 1
            while cursor < len(frontmatter) and (
                frontmatter[cursor].startswith(" ") or frontmatter[cursor].startswith("\t")
            ):
                block.append(frontmatter[cursor].rstrip("\r\n"))
                cursor += 1
            if len(block) == 1 and re.fullmatch(r"tags\s*:\s*", block[0]):
                return ["tags: []"]
            return block
    return ["tags: []"]


def normalise_slug(value: str) -> str:
    slug = re.sub(r"\s+", "-", value.strip())
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug or slug.startswith(".") or ".." in slug:
        fail("slug is empty or unsafe")
    if any(character in slug for character in ("/", "\\", "\x00")):
        fail("slug must not contain path separators or null bytes")
    if any(ord(character) < 32 for character in slug):
        fail("slug must not contain control characters")
    if len(slug) > 120:
        fail("slug must be 120 characters or fewer")
    return slug


def jpeg_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        fail(f"hero image is not a JPEG: {path}")
    offset = 2
    while offset + 9 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        offset += 2
        if marker in {0xD8, 0xD9}:
            continue
        if offset + 2 > len(data):
            break
        segment_length = struct.unpack(">H", data[offset : offset + 2])[0]
        if segment_length < 2 or offset + segment_length > len(data):
            break
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            height, width = struct.unpack(">HH", data[offset + 3 : offset + 7])
            return width, height
        offset += segment_length
    fail(f"could not read JPEG dimensions: {path}")


def validate_body(body: str) -> None:
    findings = []
    if "![[" in body:
        findings.append("Obsidian embeds (![[...]])")
    if "[[" in body:
        findings.append("Obsidian wikilinks ([[...]])")
    if "obsidian://" in body:
        findings.append("obsidian:// links")
    local_images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", body)
    unsafe_images = [url for url in local_images if not re.match(r"^(https?://|/images/)", url.strip())]
    if unsafe_images:
        findings.append("local image paths: " + ", ".join(unsafe_images))
    if findings:
        fail("convert unsupported Obsidian syntax before publishing: " + "; ".join(findings))


def yaml_line(key: str, raw_value: str | None, fallback: str = "") -> str:
    value = raw_value if raw_value not in (None, "") else fallback
    return f"{key}: {value}".rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Obsidian draft under the verified posts folder")
    parser.add_argument("--slug", required=True, help="Stable URL slug without the date")
    parser.add_argument("--date", help="Publication date in YYYY-MM-DD; required if pubDate is blank")
    image_group = parser.add_mutually_exclusive_group(required=True)
    image_group.add_argument("--image", type=Path, help="1200x630 JPEG hero image")
    image_group.add_argument("--without-image", action="store_true", help="Explicitly publish without a hero image")
    parser.add_argument("--apply", action="store_true", help="Create the post and image after dry-run review")
    args = parser.parse_args()

    source = ensure_within(args.source, AUTHORING_ROOT, "source")
    if not source.is_file():
        fail(f"source does not exist: {source}")

    frontmatter, body = split_frontmatter(source.read_text(encoding="utf-8"))
    validate_body(body)

    title = scalar(frontmatter, "title")
    if not title:
        fail("title is required")

    draft = (scalar(frontmatter, "draft") or "").lower()
    if draft not in {"true", "false"}:
        fail("draft must be a YAML boolean, true or false")
    if draft != "true":
        fail("authoring source must remain draft: true; publication approval is represented only in the copy")

    publication_date = args.date or scalar(frontmatter, "pubDate")
    if not publication_date or not DATE_RE.fullmatch(publication_date):
        fail("provide --date YYYY-MM-DD because source pubDate is blank or invalid")

    slug = normalise_slug(args.slug)
    stem = f"{publication_date}-{slug}"
    post_destination = POSTS_ROOT / f"{stem}.md"
    image_destination = IMAGES_ROOT / f"{stem}.jpg"

    if post_destination.exists():
        fail(f"post destination already exists; overwrite is forbidden: {post_destination}")

    image_source = None
    if args.image:
        image_source = args.image.expanduser().resolve()
        if not image_source.is_file():
            fail(f"hero image does not exist: {image_source}")
        width, height = jpeg_dimensions(image_source)
        if (width, height) != (1200, 630):
            fail(f"hero image must be exactly 1200x630, received {width}x{height}")
        if image_destination.exists():
            fail(f"image destination already exists; overwrite is forbidden: {image_destination}")

    description = raw_scalar(frontmatter, "description")
    output_frontmatter = [
        "---",
        yaml_line("title", raw_scalar(frontmatter, "title")),
        f"pubDate: {publication_date}",
    ]
    if description:
        output_frontmatter.append(yaml_line("description", description))
    output_frontmatter.extend(
        [
            yaml_line("author", raw_scalar(frontmatter, "author"), "서호익"),
            "draft: false",
        ]
    )
    if image_source:
        output_frontmatter.append(f"heroImage: /images/{stem}.jpg")
    output_frontmatter.extend([*tags_block(frontmatter), "---", ""])
    output = "\n".join(output_frontmatter) + body.lstrip("\r\n")

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"{mode}: Graywoods post preparation")
    print(f"source: {source}")
    print(f"post:   {post_destination}")
    print(f"image:  {image_destination if image_source else 'none (explicit)'}")
    print("body edits: none")
    print("source draft changed: no")
    print("existing files overwritten: no")

    if not args.apply:
        print("No files written. Re-run with --apply only after reviewing this plan.")
        return 0

    created: list[Path] = []
    try:
        POSTS_ROOT.mkdir(parents=True, exist_ok=True)
        with post_destination.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(output)
        created.append(post_destination)

        if image_source:
            IMAGES_ROOT.mkdir(parents=True, exist_ok=True)
            with image_destination.open("xb") as destination_handle:
                with image_source.open("rb") as source_handle:
                    shutil.copyfileobj(source_handle, destination_handle)
            created.append(image_destination)

        verification = subprocess.run(["npm", "run", "verify"], cwd=REPO_ROOT, check=False)
        if verification.returncode != 0:
            fail(f"verification failed with exit code {verification.returncode}; created files will be rolled back")
    except BaseException:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        raise

    print("Verification passed. Files are prepared but not staged, committed, pushed, or deployed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
