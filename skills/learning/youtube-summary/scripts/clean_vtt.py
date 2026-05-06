#!/usr/bin/env python3
"""Clean VTT subtitle file to plain text. Strips timestamps, tags, and deduplicates rolling captions."""
import re
import sys


def clean_vtt(vtt_text: str) -> str:
    lines = []
    prev = ""
    for line in vtt_text.splitlines():
        # Skip header, timestamps, blank lines, alignment metadata
        if re.match(r"^(WEBVTT|Kind:|Language:|\d{2}:\d{2}:|\s*$)", line):
            continue
        # Strip inline timing tags like <00:00:06.799><c>
        line = re.sub(r"<[^>]+>", "", line).strip()
        if not line or line == prev:
            continue
        # Skip if this line is a prefix of the previous (rolling caption duplicate)
        if prev.startswith(line):
            continue
        # If previous line is a prefix of this one, replace it
        if line.startswith(prev) and lines:
            lines[-1] = line
        else:
            lines.append(line)
        prev = line
    return "\n".join(lines)


if __name__ == "__main__":
    print(clean_vtt(sys.stdin.read()))
