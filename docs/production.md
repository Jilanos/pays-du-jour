# Producing fiches

Pilot (Taiwan, 2026-11-15): one Codex run (high power, network on) in a worktree, about 1 h.
Prompt used: `docs/prompt-fiche-twn.md`. Reuse it per country: change the country, the topics list
and the reader hooks; keep the style rules, validation steps and source rules.

Lane per batch:
1. `git worktree add -b fiche/<iso3> ../pays-du-jour.wt/fiche-<iso3>`.
2. Dispatch with `crow dispatch pays-du-jour fiche-<iso3> --cwd <worktree>` on worka or workb,
   `--power high`, max 2 runs in parallel.
3. Review: read fiche.md, check `uv run pytest`, open `/pays/<ISO3>` locally.
4. Merge `--no-ff` into main, remove the worktree and the branch.
