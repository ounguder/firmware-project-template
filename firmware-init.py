#!/usr/bin/env python3
"""
firmware-init.py — Initialize a new firmware project and its Obsidian vault entry.

Run by Claude during /new-project Phase 1. Do not run directly unless you know what you're doing.

What this script does:
  1. Checks prerequisites (gh CLI auth, Obsidian CLI)
  2. Detects the Obsidian vault path automatically via `obsidian vault info=path`
  3. Collects project metadata interactively
  4. Validates project name (kebab-case enforced)
  5. Checks for collisions (folder exists, GitHub repo exists)
  6. Copies the firmware-project-template to the new project folder
  7. Creates the vault folder hierarchy under 01 - Projects/
  8. Writes VAULT-BLUEPRINT.md with all fields filled in
  9. Creates or updates 00 - overview.md at the component level
 10. Prints next steps for Claude to continue with Phase 2 (Design Review)
"""

import sys
import os
import re
import shutil
import subprocess
import json
from pathlib import Path
from datetime import date
from textwrap import dedent

# ── Prerequisite checks ───────────────────────────────────────────────────────

def check_prereqs():
    errors = []

    # gh CLI installed
    if not shutil.which("gh"):
        errors.append(
            "gh CLI not found.\n"
            "  Install from: https://cli.github.com\n"
            "  Then run: gh auth login"
        )
    else:
        # gh CLI authenticated
        result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        if result.returncode != 0:
            errors.append(
                "gh CLI is not authenticated.\n"
                "  Run: gh auth login\n"
                "  Then retry /new-project."
            )

    # obsidian CLI present
    if not shutil.which("obsidian"):
        errors.append(
            "Obsidian CLI not found.\n"
            "  Ensure Obsidian is installed and `obsidian` is on your PATH.\n"
            "  On Windows, Obsidian CLI is available in the Obsidian install directory."
        )

    if errors:
        print("\nERROR: Prerequisites not met:\n")
        for e in errors:
            print(f"  • {e}\n")
        sys.exit(1)

    print("Prerequisites OK (gh authenticated, obsidian CLI found).")


# ── Vault path detection ──────────────────────────────────────────────────────

def detect_vault_path() -> Path:
    """
    Detect the Obsidian vault path using the Obsidian CLI.
    Falls back to manual input if detection fails.
    """
    print("\nDetecting Obsidian vault path...")

    try:
        result = subprocess.run(
            ["obsidian", "vault", "info=path"],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout.strip()

        if result.returncode == 0 and output:
            lines = [l.strip() for l in output.splitlines() if l.strip()]

            if len(lines) == 1:
                vault_path = Path(lines[0])
                if vault_path.exists():
                    print(f"  Vault detected: {vault_path}")
                    return vault_path

            elif len(lines) > 1:
                # Multiple vaults — ask user to pick
                print("  Multiple vaults found:")
                for i, line in enumerate(lines, 1):
                    print(f"    [{i}] {line}")
                while True:
                    choice = input("  Select vault number: ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(lines):
                        vault_path = Path(lines[int(choice) - 1])
                        if vault_path.exists():
                            return vault_path
                    print("  Invalid choice. Try again.")

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"  Vault auto-detection failed ({e}).")

    # Fallback — manual input
    print("  Enter the vault root path manually.")
    while True:
        raw = input("  Vault path: ").strip().strip('"').strip("'")
        p = Path(raw)
        if p.exists():
            return p
        print(f"  Path not found: {p}  Try again.")


# ── Input helpers ─────────────────────────────────────────────────────────────

def ask(prompt: str, example: str = "", required: bool = True) -> str:
    hint = f"  (e.g. {example})" if example else ""
    while True:
        value = input(f"{prompt}{hint}: ").strip()
        if value or not required:
            return value
        print("  This field is required.")


def ask_kebab(prompt: str, example: str = "sensor-reading") -> str:
    pattern = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
    while True:
        value = input(f"{prompt} (e.g. {example}): ").strip().lower()
        if pattern.match(value):
            return value
        print("  Invalid format. Use lowercase letters, digits, and hyphens only.")
        print("  Examples: sensor-reading, lora-tx, gateway-fw")


def ask_yes_no(prompt: str) -> bool:
    while True:
        answer = input(f"{prompt} [yes/no]: ").strip().lower()
        if answer in ("yes", "y"):
            return True
        if answer in ("no", "n"):
            return False
        print("  Please type yes or no.")


# ── Project name collision checks ─────────────────────────────────────────────

def check_folder_collision(projects_dir: Path, project_name: str) -> bool:
    target = projects_dir / project_name
    if target.exists():
        print(f"\nWARNING: Folder already exists: {target}")
        return ask_yes_no("Continue anyway and overwrite?")
    return True


def check_github_collision(project_name: str) -> bool:
    result = subprocess.run(
        ["gh", "repo", "view", project_name],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"\nWARNING: GitHub repo '{project_name}' already exists in your account.")
        return ask_yes_no("Continue anyway (will use existing repo)?")
    return True


# ── Template path detection ───────────────────────────────────────────────────

def find_template() -> Path:
    """
    The template is this script's parent directory.
    firmware-init.py lives inside firmware-project-template/.
    """
    return Path(__file__).resolve().parent


# ── VAULT-BLUEPRINT.md writer ─────────────────────────────────────────────────

def write_vault_blueprint(project_dir: Path, meta: dict):
    """Write a filled VAULT-BLUEPRINT.md into the new project folder."""

    predecessors_yaml = ""
    if meta["predecessors"]:
        predecessors_yaml = "\npredecessors:\n"
        for p in meta["predecessors"]:
            predecessors_yaml += (
                f"  - name: {p['name']}\n"
                f"    vault_path: \"{p['vault_path']}\"\n"
                f"    github_repo: \"{p['github_repo']}\"\n"
            )
    else:
        predecessors_yaml = (
            "\n# predecessors — uncomment and fill if this project builds on previous tasks\n"
            "# predecessors:\n"
            "#   - name: previous-project\n"
            "#     vault_path: \"01 - Projects/.../previous-project\"\n"
            "#     github_repo: https://github.com/user/previous-project\n"
        )

    vault_project_path = "/".join(filter(None, [
        "01 - Projects",
        meta["main_project"],
        meta["sub_project"],
        meta["component"],
        meta["task"],
        meta["project_name"],
    ]))

    content = dedent(f"""\
        ---
        # VAULT-BLUEPRINT.md — auto-generated by firmware-init.py on {date.today()}
        # Read by vault-sync.py on every startup. Edit carefully.

        project:
          name: {meta["project_name"]}
          main_project: "{meta["main_project"]}"
          sub_project: "{meta["sub_project"]}"
          component: "{meta["component"]}"
          task: "{meta["task"]}"
          primary_board: "{meta["primary_board"]}"
          github_repo: "https://github.com/{meta["github_user"]}/{meta["project_name"]}"

        vault:
          root: "{meta["vault_root"].as_posix()}"
          project_path: "{vault_project_path}"

        sync:
          include:
            - docs/
            - Report/
            - lessonsLearned/
            - CLAUDE.md
            - VAULT-BLUEPRINT.md
            - .claude/rules/
          exclude:
            - src/
            - include/
            - tests/
            - CLAUDE.local.md
            - .vault-sync-state.json
            - "*.obsidian-*.md"
        {predecessors_yaml}
        ---

        # Vault Blueprint — {meta["project_name"]}

        Generated: {date.today()}
        Board:     {meta["primary_board"]}
        GitHub:    https://github.com/{meta["github_user"]}/{meta["project_name"]}
        Vault:     {vault_project_path}

        Run `python vault-sync.py` from this folder to start two-way sync.
        Run `python vault-sync.py --once` for a one-shot sync.
    """)

    (project_dir / "VAULT-BLUEPRINT.md").write_text(content, encoding="utf-8")


# ── Overview note writer ──────────────────────────────────────────────────────

def update_overview_note(vault_root: Path, meta: dict):
    """
    Create or update 00 - overview.md at the component level in the vault.
    Lists all tasks under this component with their status.
    """
    parts = list(filter(None, [
        "01 - Projects",
        meta["main_project"],
        meta["sub_project"],
        meta["component"],
    ]))
    component_dir = vault_root / Path(*parts)
    overview_path = component_dir / "00 - overview.md"

    github_url = f"https://github.com/{meta['github_user']}/{meta['project_name']}"
    new_row = f"| {meta['task']} | {meta['project_name']} | planned | [repo]({github_url}) |"

    if overview_path.exists():
        # Append a new row to the existing table
        content = overview_path.read_text(encoding="utf-8")
        if meta["project_name"] in content:
            print(f"  Overview note already contains '{meta['project_name']}' — skipping update.")
            return
        content = content.rstrip() + "\n" + new_row + "\n"
        overview_path.write_text(content, encoding="utf-8")
        print(f"  Updated overview: {overview_path}")
    else:
        component_dir.mkdir(parents=True, exist_ok=True)
        content = dedent(f"""\
            ---
            type: component-overview
            component: "{meta["component"]}"
            created: {date.today()}
            updated: {date.today()}
            ---

            # {meta["component"]} — Task Overview

            | Task | Project | Status | GitHub |
            |---|---|---|---|
            {new_row}
        """)
        overview_path.write_text(content, encoding="utf-8")
        print(f"  Created overview: {overview_path}")


# ── GitHub username ───────────────────────────────────────────────────────────

def get_github_user() -> str:
    result = subprocess.run(
        ["gh", "api", "user", "--jq", ".login"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return "your-github-user"   # fallback — user can edit VAULT-BLUEPRINT.md


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "═" * 60)
    print("  firmware-init.py — New Project Initialization")
    print("═" * 60)

    # Step 1: Prerequisites
    check_prereqs()

    # Step 2: Vault path
    vault_root = detect_vault_path()

    # Step 3: Projects parent directory
    projects_dir = Path(__file__).resolve().parent.parent
    print(f"\nNew project will be created in: {projects_dir}")

    # Step 4: Collect project metadata
    print("\n" + "─" * 60)
    print("  Project Metadata")
    print("─" * 60)

    main_project  = ask("Main Project",      "Eco-Twin")
    sub_project   = ask("Sub-Project",       "DemoSetup", required=False)
    component     = ask("System Component",  "Edge-Node")
    task          = ask("Task Name",         "Sensor Reading")
    primary_board = ask("Primary MCU / Board", "Heltec LoRa32 V3 (ESP32-S3)")

    print()
    project_name = ask_kebab("Project Name (kebab-case, becomes folder + GitHub repo name)")

    # Step 5: Collision checks
    if not check_folder_collision(projects_dir, project_name):
        print("Aborted.")
        sys.exit(0)
    if not check_github_collision(project_name):
        print("Aborted.")
        sys.exit(0)

    # Step 6: Predecessors
    print()
    predecessors = []
    if ask_yes_no("Does this project build on a previous task?"):
        print("  Enter predecessor project names one by one. Leave blank to stop.")
        while True:
            name = input("  Predecessor project name (kebab-case): ").strip()
            if not name:
                break
            # Try to find vault path automatically
            guess_parts = list(filter(None, [
                "01 - Projects", main_project, sub_project, component
            ]))
            default_vault_path = "/".join(guess_parts + [name])
            vault_path_in = input(
                f"  Vault path [{default_vault_path}]: "
            ).strip() or default_vault_path

            github_user = get_github_user()
            default_repo = f"https://github.com/{github_user}/{name}"
            github_repo_in = input(
                f"  GitHub repo [{default_repo}]: "
            ).strip() or default_repo

            predecessors.append({
                "name":        name,
                "vault_path":  vault_path_in,
                "github_repo": github_repo_in,
            })

    # Step 7: Build metadata dict
    github_user = get_github_user()
    meta = {
        "project_name":  project_name,
        "main_project":  main_project,
        "sub_project":   sub_project,
        "component":     component,
        "task":          task,
        "primary_board": primary_board,
        "vault_root":    vault_root,
        "github_user":   github_user,
        "predecessors":  predecessors,
    }

    # Step 8: Copy template to new project folder
    template_dir = find_template()
    project_dir  = projects_dir / project_name

    print(f"\nCopying template to: {project_dir}")
    shutil.copytree(
        template_dir, project_dir,
        ignore=shutil.ignore_patterns(".git", "CLAUDE.local.md", "__pycache__", "*.pyc"),
    )

    # Step 9: Write filled VAULT-BLUEPRINT.md
    write_vault_blueprint(project_dir, meta)
    print("  VAULT-BLUEPRINT.md written.")

    # Step 10: Create vault folder hierarchy
    vault_parts = list(filter(None, [
        "01 - Projects", main_project, sub_project, component, task, project_name
    ]))
    vault_project_dir = vault_root / Path(*vault_parts)
    vault_project_dir.mkdir(parents=True, exist_ok=True)
    print(f"  Vault folder created: {vault_project_dir}")

    # Step 11: Update component overview note in vault
    update_overview_note(vault_root, meta)

    # Step 12: Summary
    print("\n" + "═" * 60)
    print("  Initialization complete.")
    print("═" * 60)
    print(f"  Local project : {project_dir}")
    print(f"  Vault folder  : {vault_project_dir}")
    print(f"  GitHub        : https://github.com/{github_user}/{project_name} (create next)")
    print()
    print("  Next steps (Claude handles these):")
    print("  1. git init && gh repo create (Phase 1 of /new-project)")
    print("  2. Design Review Interview    (Phase 2 of /new-project)")
    print("  3. Technical Kickoff         (Phase 3 of /new-project)")
    print()


if __name__ == "__main__":
    main()
