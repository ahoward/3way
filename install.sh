#!/bin/sh
# Counted install: this file is a GitHub Release asset.
# Do not curl raw.githubusercontent — that does not increment download_count.
set -e
repo="ahoward/3way"
asset_base="https://github.com/${repo}/releases/latest/download"
tmp="${TMPDIR:-/tmp}/3way.$$"
mkdir -p "$tmp"
trap 'rm -rf "$tmp"' EXIT

if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$asset_base/SKILL.md" -o "$tmp/SKILL.md"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$tmp/SKILL.md" "$asset_base/SKILL.md"
else
  echo "need curl or wget" >&2
  exit 1
fi

dest=""
if [ -d .grok ] || [ -d .git ]; then
  dest=".grok/skills/3-way"
fi
if [ -z "$dest" ]; then
  dest="${HOME}/.grok/skills/3-way"
fi
mkdir -p "$dest"
cp "$tmp/SKILL.md" "$dest/SKILL.md"
if [ -d .claude ] || [ -d .git ]; then
  mkdir -p .claude/skills/3-way
  cp "$tmp/SKILL.md" .claude/skills/3-way/SKILL.md
fi
echo "installed $dest/SKILL.md"
echo "coder continues. critic does not. /3-way"
