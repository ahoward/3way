---
name: 3-way
description: Three seats, one job. Coder stays the night (continue). Critic is a stranger (fresh). Driver watches. Tmux or screen. Any three CLIs. Use when the user types `/3-way`, "drive the coder", or "tmux implement". Do NOT invoke implicitly.
---

# 3-way

A ménage à CLI.

The **coder** leaves their clothes on the floor. Session stays warm.
The **critic** does not leave a number. New process, no `--continue`.
The **driver** does not get in the bed. Script or human. Never the coder.

Independence is **memory policy**, not vendor. Same model twice is still two seats if one continues and one does not.

Do not use this in place of a scripted gauntlet (`joust`, ralph, debate loops). Those are fresh-vs-fresh, driver-is-a-script. This is how you ship **one unit of work** with a live TUI that already has OAuth.

## Seats (override at the top of a play)

Defaults. Change names, CLIs, mux. Do not change the memory policy.

```yaml
mux: tmux          # or screen
seats:
  driver:
    via: here
    context: continue
  coder:
    via: mux       # tmux or screen pane/window
    context: continue
    model: fable   # else opus. Never silent sonnet.
  critic:
    via: exec
    context: fresh
    model: opus
    argv: ["claude", "--model", "opus", "--no-session-persistence",
           "--dangerously-skip-permissions", "-p"]
```

Pick CLIs you already logged into. `claude`, `grok`, `codex`, `agy` — the seat does not care. **Coder = continue. Critic = fresh.** If Fable is not on the plan, coder falls back to opus and you **say so**. Same family as the critic is fine.

## Loop

1. Spec is files. Tests, CSVs, the ticket. Coder does not edit those.
2. Driver writes a prompt = HEADER + TASK + FOOTER.
3. Send it to the coder seat. Confirm the input line is yours (TUIs keep `merge it`). Then Enter / `stuff`.
4. Wait until idle. Re-run the done-when **yourself**.
5. Critic on a **new** process. Timeout ≠ pass.
6. Verdict only:

```
AGREE
DISAGREE EVIDENCE: <file:line>
DISAGREE CONCERN: <why>
```

Bounce the coder on evidence. Do not merge unless the human says merge.

## Mux

tmux:

```bash
PANE=${THREEWAY_PANE:-0:0.0}
tmux send-keys -t "$PANE" Escape
tmux send-keys -t "$PANE" C-a C-k
tmux send-keys -t "$PANE" -l "Read $PROMPT and do that. Do not merge."
tmux capture-pane -t "$PANE" -p -S -4
tmux send-keys -t "$PANE" Enter
```

screen:

```bash
SOCK=${THREEWAY_SCREEN:-3way}
screen -S "$SOCK" -X stuff "Read $PROMPT and do that. Do not merge."$'\n'
screen -S "$SOCK" -X hardcopy -h /tmp/3way.screen
```

## HEADER (every coder send)

Keep it short. Yours will differ. The shape does not:

```
HEADER
- One issue. Spec files are spec. Do not edit them.
- Open only what the issue names.
- Do not merge unless this prompt says merge.
```

## FOOTER (every coder send)

```
FOOTER
- If a test and this prompt disagree: stop. Do not pick a winner.
- Run the done-when. Paste output. If silent, stop.
- Name every file you touched. If one is not on the issue, revert it.
- Do not start the next design. Critic is a file:line tie, not new scope.
```

## Critic prompt

```
You are the CRITIC. Fresh session. Do not edit files.
Review <artifact>. Spec: <one paragraph>. Read: <paths>.
Verdict exactly one of:
AGREE
DISAGREE EVIDENCE: file:line
DISAGREE CONCERN: why
Then 3-8 ranked lines. file:line + why. No extra features.
```

Never the mux coder. Never `--continue`. Never grade a review you wrote.

## Install

Release tarball, so GitHub can count it:

```sh
curl -fsSL https://github.com/ahoward/3way/releases/latest/download/install.sh | sh
```

Copies `SKILL.md` to `.grok/skills/3-way/` and `.claude/skills/3-way/` if those trees exist, else `~/.grok/skills/3-way/`.
