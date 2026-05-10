# CLAUDE.md — Introduction to GitHub (Skills Course)

## Repository Purpose

This is a **GitHub Skills interactive learning course** template repository. Its goal is to teach learners the four core GitHub concepts in sequence:

1. Creating a branch
2. Committing a file
3. Opening a pull request
4. Merging a pull request

When a learner forks/uses this template, GitHub Actions automatically guides them through each step, updating the README as they complete activities. This repo is **not** an application — it is course infrastructure.

---

## Repository Structure

```
.
├── README.md                        # Dynamic course content shown to the learner (auto-updated by Actions)
├── LICENSE                          # MIT license
├── .gitignore                       # Standard OS/binary ignores; no language-specific tooling
├── images/                          # Screenshots referenced inline in README.md and step files
│   ├── my-profile-file.png
│   ├── Green-merge-pull-request.png
│   ├── code-tab.png
│   ├── Actions-to-step-4.png
│   ├── main-branch-dropdown.png
│   ├── create-new-file.png
│   ├── create-new-repository.png
│   ├── pull-request-branches.png
│   ├── delete-branch.png
│   ├── compare-and-pull-request.png
│   ├── create-branch-button.png
│   ├── profile-readme-example.png
│   ├── commit-full-screen.png
│   └── Pull-request-description.png
└── .github/
    ├── dependabot.yml               # Monthly auto-updates for github-actions ecosystem
    ├── steps/                       # Markdown snippets injected into README at each step
    │   ├── -step.txt                # Single integer tracking current step (0–4, then X)
    │   ├── 0-welcome.md
    │   ├── 1-create-a-branch.md
    │   ├── 2-commit-a-file.md
    │   ├── 3-open-a-pull-request.md
    │   ├── 4-merge-your-pull-request.md
    │   └── X-finish.md
    └── workflows/                   # GitHub Actions that drive the step progression
        ├── 0-welcome.yml
        ├── 1-create-a-branch.yml
        ├── 2-commit-a-file.yml
        ├── 3-open-a-pull-request.yml
        └── 4-merge-your-pull-request.yml
```

---

## Step Progression System

### State file: `.github/steps/-step.txt`

This file contains a single integer (e.g., `1`) representing the current step the learner is on. All workflows read this file first via a `get_current_step` job to prevent workflows from running out of sequence.

### Step flow

| Step | File value | Trigger event | Workflow file | Action taken |
|------|-----------|---------------|---------------|--------------|
| Welcome | `0` | push to `main` | `0-welcome.yml` | Updates README to step 1, sets `-step.txt` to `1` |
| Create branch | `1` | branch `create` event | `1-create-a-branch.yml` | Listens for branch named `my-first-branch`; advances to step 2 |
| Commit a file | `2` | push to `my-first-branch` | `2-commit-a-file.yml` | Any push to the learner branch advances to step 3 |
| Open a PR | `3` | `pull_request` opened/reopened | `3-open-a-pull-request.yml` | PR from `my-first-branch` → `main` advances to step 4 |
| Merge PR | `4` | push to `main` | `4-merge-your-pull-request.yml` | Detects merge; advances to step X (finish) |

### `skills/action-update-step@v2`

All workflows call this reusable action, which:
- Replaces the current step content in `README.md` with the next step's markdown
- Updates `-step.txt` to the new step number
- Commits and pushes those changes back to `main` (or `my-first-branch` where specified)

### Guard conditions in every workflow

Each workflow's main job checks **three** conditions before running:
1. The repository is **not** the template itself (`!github.event.repository.is_template`)
2. The current step in `-step.txt` matches the expected value
3. (Where applicable) The branch name or PR head matches `my-first-branch` exactly

---

## Branching Conventions

- `main` — protected; holds course state (README + step counter). Never rewrite history here.
- `my-first-branch` — the **exact** branch name learners must create; workflows key off this literal string.
- `claude/*` — convention for AI-assisted development branches in this repo.

---

## GitHub Actions Conventions

- All workflows run on `ubuntu-latest`.
- All workflows require `contents: write` permission (to update `README.md` and `-step.txt`).
- Workflows use `actions/checkout@v4` with `fetch-depth: 0` to get full branch history.
- `workflow_dispatch` is included in every workflow to allow manual triggering for testing.
- Dependabot is configured to update Actions monthly (`dependabot.yml`).

---

## Key Files to Understand Before Making Changes

| File | Why it matters |
|------|---------------|
| `.github/steps/-step.txt` | Changing this manually advances or resets the course state |
| `README.md` | Auto-managed by Actions; hand-editing may break step injection |
| `.github/steps/*.md` | Content shown to the learner at each step; edit these to change course instructions |
| `.github/workflows/*.yml` | Course logic; changing trigger events or branch name guards changes course behavior |

---

## Development Workflow for AI Assistants

### Active development branch
All changes should be developed on: `claude/add-claude-documentation-PMJU5`

### Making changes safely
1. Never push directly to `main` — it triggers course workflows.
2. Never rename or delete `my-first-branch` while a learner session is in progress.
3. Do not manually edit `-step.txt` unless intentionally resetting course state.
4. When editing step markdown files (`.github/steps/*.md`), verify the injected content will render correctly in the context of `README.md`'s `<header>` / `<footer>` wrapper tags.

### No build system
There is no package manager, build tool, compiler, or test runner in this repository. All logic is in GitHub Actions YAML. There is nothing to `npm install`, `make`, or `pip install`.

### Images
All images live in `/images/`. They are referenced in Markdown using relative paths like `![alt](/images/filename.png)`. Do not move or rename images without updating all references in step files and `README.md`.

---

## Commit Message Style

Based on existing commits in this repo, use short imperative messages:

```
Update to 1 in STEP and README.md   # example from initial setup
Add CLAUDE.md with codebase docs
```

Keep messages under 72 characters. No ticket numbers or emoji are used in this repo's history.

---

## What This Repo Does NOT Have

- No application code, programming languages, or runtime dependencies
- No test suite
- No linter or formatter configuration
- No Docker or CI/CD pipeline beyond the Skills course workflows
- No secrets beyond `GITHUB_TOKEN` (used automatically by Actions)
