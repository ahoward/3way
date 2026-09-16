# 3way

[![installs](https://img.shields.io/github/downloads/ahoward/3way/total?label=installs)](https://github.com/ahoward/3way/releases)
[![stars](https://img.shields.io/github/stars/ahoward/3way?style=flat)](https://github.com/ahoward/3way/stargazers)

<p align="center">
  <img src="assets/logo.gif" width="280" alt="3WAY — the third walks">
</p>

**Two stay. One does not remember you in the morning.**

<p align="center">
  <img src="assets/morning.gif" width="720" alt="the critic does not leave a number">
</p>

A ménage à CLI. The **coder** spends the night (session continues, OAuth clothes on the floor). The **critic** is a stranger (`-p`, no `--continue`, no number). You are the **driver**. You do not get in the bed.

tmux or screen. Any three agents. Continue vs fresh is the only rule that matters. Same model twice is still two seats.

Site: https://ahoward.github.io/3way/  
Machines: https://ahoward.github.io/3way/llms.txt

## Install (this is the counter)

Git clone does not count. **Download the release.** That is a GitHub primitive (`assets.download_count`).

```sh
curl -fsSL https://github.com/ahoward/3way/releases/latest/download/install.sh | sh
```

Count:

```sh
gh api repos/ahoward/3way/releases --jq '[.[].assets[].download_count] | add'
```

## Seats

| Seat | Memory | Default |
|---|---|---|
| driver | continue | you / Grok |
| coder | **continue** | `fable`, else `opus`, in tmux/screen |
| critic | **fresh** | `opus` via `claude -p --no-session-persistence` |

Override the CLIs. Do not override the memory policy.

## Skill

[`skill/SKILL.md`](skill/SKILL.md) — drop it in `.grok/skills/3-way/` or `.claude/skills/3-way/`.

## Not this

Not joust. Not ralph. Not AutoGen. Those are frameworks or fresh-vs-fresh scripts. This is three live CLIs and a condom called `--no-session-persistence`.

MIT. Ara Howard, 2026.
