#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

PROMPTS_START = "<!-- prompts start -->"
PROMPTS_END = "<!-- prompts end -->"

ROOT = Path(__file__).resolve().parents[2]


def sorted_md_files(directory: Path) -> list[Path]:
    markdown_files: list[Path] = []
    for path in directory.iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() != ".md":
            continue
        if path.name.casefold() == "readme.md":
            continue
        markdown_files.append(path)
    return sorted(markdown_files, key=lambda path: path.name.casefold())


def fallback_title_from_filename(path: Path) -> str:
    stem = path.stem.replace("_", " ").replace("-", " ").strip()
    return stem or path.stem


def extract_title(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8-sig") as file:
            first_line = file.readline().strip()
    except OSError:
        return fallback_title_from_filename(path)

    if not first_line:
        return fallback_title_from_filename(path)

    if first_line.startswith("#"):
        heading = re.sub(r"^#+\s*", "", first_line).strip()
        if heading:
            return heading
        return fallback_title_from_filename(path)

    if first_line.startswith("<!--"):
        return fallback_title_from_filename(path)

    return first_line


def escape_link_title(title: str) -> str:
    return title.replace("[", "\\[").replace("]", "\\]")


def build_prompt_links(directory: Path, *, link_from_root: bool) -> list[str]:
    links: list[str] = []
    for md_file in sorted_md_files(directory):
        title = escape_link_title(extract_title(md_file))
        target = f"{directory.name}/{md_file.name}" if link_from_root else md_file.name
        links.append(f"#### [{title}]({target})")
    return links


def update_prompts_block(readme_path: Path, lines: list[str]) -> bool:
    if not readme_path.exists():
        raise FileNotFoundError(f"README not found: {readme_path}")

    content = readme_path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"{re.escape(PROMPTS_START)}.*?{re.escape(PROMPTS_END)}",
        re.DOTALL,
    )

    if not pattern.search(content):
        raise ValueError(
            f"Missing prompts marker block in {readme_path}: "
            f"expected '{PROMPTS_START}' and '{PROMPTS_END}'"
        )

    new_block_lines = [PROMPTS_START]
    new_block_lines.extend(lines)
    new_block_lines.append(PROMPTS_END)
    new_block = "\n".join(new_block_lines)

    updated = pattern.sub(new_block, content, count=1)
    if updated == content:
        return False

    readme_path.write_text(updated, encoding="utf-8")
    return True


def category_title(readme_path: Path) -> str:
    return extract_title(readme_path)


def list_category_dirs() -> list[Path]:
    dirs = []
    for path in ROOT.iterdir():
        if not path.is_dir() or path.name.startswith("."):
            continue
        if sorted_md_files(path):
            dirs.append(path)
    return sorted(dirs, key=lambda item: item.name.casefold())


def update_subdirectory_readmes() -> None:
    errors: list[str] = []
    for directory in list_category_dirs():
        readme_path = directory / "README.md"
        links = build_prompt_links(directory, link_from_root=False)
        try:
            update_prompts_block(readme_path, links)
        except (FileNotFoundError, ValueError) as error:
            errors.append(str(error))
    if errors:
        details = "\n".join(f"- {error}" for error in errors)
        raise RuntimeError(f"Failed to update some subdirectory README.md files:\n{details}")


def build_root_lines() -> list[str]:
    lines: list[str] = []

    root_links = build_prompt_links(ROOT, link_from_root=False)
    if root_links:
        lines.append("### [Root / 根目录](.)")
        lines.extend(root_links)
        lines.append("")

    for directory in list_category_dirs():
        readme_path = directory / "README.md"
        links = build_prompt_links(directory, link_from_root=True)
        if not links:
            continue
        lines.append(f"### [{escape_link_title(category_title(readme_path))}]({directory.name})")
        lines.extend(links)
        lines.append("")

    end_idx = next((i for i in range(len(lines) - 1, -1, -1) if lines[i].strip()), -1)
    return lines[: end_idx + 1] if end_idx >= 0 else []


def main() -> None:
    update_subdirectory_readmes()
    update_prompts_block(ROOT / "README.md", build_root_lines())


if __name__ == "__main__":
    main()
