#!/usr/bin/env python3
"""
vault-sync.py — Two-way sync between a local firmware project and its Obsidian vault mirror.

Usage:
    python vault-sync.py          # continuous mode — watches both directories
    python vault-sync.py --once   # one-shot reconciliation, then exit

Run from the project root directory (where VAULT-BLUEPRINT.md lives).

How it works:
  - Reads vault.root and vault.project_path from VAULT-BLUEPRINT.md
  - Maintains .vault-sync-state.json as the trusted checksum baseline
  - On startup: reconciles all tracked files using three-way logic
  - In continuous mode: watches local (2s debounce) and vault (5s debounce)
  - Three-way logic: local changed → copy to vault | vault changed → copy to local | both changed → conflict backup
  - Conflicts: vault version saved as {file}.obsidian-{YYYYMMDD-HHMM}.md, never silently discarded
  - Lockfile: .vault-sync.lock prevents multiple instances per project
"""

import sys
import os
import json
import hashlib
import shutil
import signal
import time
import fnmatch
import argparse
import threading
from pathlib import Path
from datetime import datetime

try:
    import yaml
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}")
    print("       Run: pip install -r requirements.txt")
    sys.exit(1)

# ── Constants ─────────────────────────────────────────────────────────────────

STATE_FILE     = Path(".vault-sync-state.json")
LOCK_FILE      = Path(".vault-sync.lock")
BLUEPRINT      = Path("VAULT-BLUEPRINT.md")
LOCAL_DEBOUNCE = 2.0   # seconds — absorbs VS Code auto-save bursts
VAULT_DEBOUNCE = 5.0   # seconds — allows Obsidian Sync to finish writing


# ── Logging ──────────────────────────────────────────────────────────────────

def log(tag: str, message: str):
    ts = datetime.now().strftime("%H:%M:%S")
    tag_fmt = tag.upper().ljust(8)
    print(f"[{ts}] [{tag_fmt}] {message}", flush=True)


def ts_suffix() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M")


# ── Blueprint parsing ─────────────────────────────────────────────────────────

def load_blueprint() -> dict:
    """Parse VAULT-BLUEPRINT.md YAML frontmatter and return a config dict."""
    if not BLUEPRINT.exists():
        print("ERROR: VAULT-BLUEPRINT.md not found in current directory.")
        print(f"       Current directory: {Path.cwd()}")
        print("       Run vault-sync.py from the project root folder.")
        print("       Example: cd C:\\Desktop\\Projects\\sensor-reading && python vault-sync.py")
        sys.exit(1)

    raw = BLUEPRINT.read_text(encoding="utf-8")
    parts = raw.split("---")
    if len(parts) < 3:
        print("ERROR: VAULT-BLUEPRINT.md has no valid YAML frontmatter (missing --- delimiters).")
        sys.exit(1)

    try:
        config = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        print(f"ERROR: Could not parse VAULT-BLUEPRINT.md YAML:\n       {e}")
        sys.exit(1)

    vault_root    = Path(config["vault"]["root"])
    project_path  = config["vault"]["project_path"]
    vault_project = vault_root / project_path

    if not vault_root.exists():
        print(f"ERROR: Vault root not found: {vault_root}")
        print("       Check vault.root in VAULT-BLUEPRINT.md")
        sys.exit(1)

    if not vault_project.exists():
        print(f"ERROR: Vault project folder not found: {vault_project}")
        print("       Run firmware-init.py first, or create the folder manually.")
        sys.exit(1)

    include = [s.rstrip("/") for s in config.get("sync", {}).get("include", [])]
    exclude = config.get("sync", {}).get("exclude", [])

    return {
        "local_root":    Path.cwd(),
        "vault_project": vault_project,
        "include":       include,
        "exclude":       [str(e).strip("/") for e in exclude],
    }


# ── File filtering ────────────────────────────────────────────────────────────

def is_included(rel: Path, cfg: dict) -> bool:
    """Return True if rel matches the whitelist and does not match the blacklist."""
    rel_posix = rel.as_posix()

    # Blacklist check first
    for pattern in cfg["exclude"]:
        if rel_posix == pattern:
            return False
        if rel_posix.startswith(pattern + "/"):
            return False
        if fnmatch.fnmatch(rel.name, pattern):
            return False

    # Whitelist check
    for pattern in cfg["include"]:
        if rel_posix == pattern:
            return True
        if rel_posix.startswith(pattern + "/"):
            return True

    return False


def all_tracked_rel_paths(cfg: dict) -> set:
    """Return all relative POSIX path strings that are tracked on either side."""
    rel_paths = set()
    for root, files in [
        (cfg["local_root"],    cfg["local_root"].rglob("*")),
        (cfg["vault_project"], cfg["vault_project"].rglob("*")),
    ]:
        for f in files:
            if not f.is_file():
                continue
            try:
                rel = f.relative_to(root)
                if is_included(rel, cfg):
                    rel_paths.add(rel.as_posix())
            except ValueError:
                continue
    return rel_paths


# ── Checksums and state ───────────────────────────────────────────────────────

def checksum(path: Path) -> str | None:
    """SHA-256 hex digest of file contents, or None if file does not exist."""
    if not path.exists():
        return None
    try:
        h = hashlib.sha256()
        h.update(path.read_bytes())
        return h.hexdigest()
    except OSError:
        return None


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(state: dict, lock: threading.Lock):
    with lock:
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


# ── Three-way sync logic ──────────────────────────────────────────────────────

def sync_pair(local: Path, vault: Path, rel_str: str,
              state: dict, state_lock: threading.Lock):
    """Apply three-way sync logic for one file pair. Updates state in-place."""
    known     = state.get(rel_str, {}).get("checksum")
    local_cs  = checksum(local)
    vault_cs  = checksum(vault)

    if local_cs is None and vault_cs is None:
        return  # Both absent — nothing to do

    local_changed = (local_cs != known)
    vault_changed = (vault_cs != known)

    if local_changed and not vault_changed and local_cs is not None:
        # Local wins → copy to vault
        vault.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local, vault)
        with state_lock:
            state[rel_str] = {"checksum": local_cs, "last_sync": time.time()}
        log("sync", f"{rel_str}  ->  vault")

    elif vault_changed and not local_changed and vault_cs is not None:
        # Vault wins → copy to local
        local.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(vault, local)
        with state_lock:
            state[rel_str] = {"checksum": vault_cs, "last_sync": time.time()}
        log("sync", f"{rel_str}  <-  vault")

    elif local_changed and vault_changed and local_cs is not None and vault_cs is not None:
        # Both changed → conflict: save vault version alongside local, keep local
        conflict_name = f"{local.stem}.obsidian-{ts_suffix()}{local.suffix}"
        conflict_path = local.parent / conflict_name
        try:
            shutil.copy2(vault, conflict_path)
        except OSError as e:
            log("error", f"Could not save conflict file: {e}")
            return
        with state_lock:
            state[rel_str] = {"checksum": local_cs, "last_sync": time.time()}
        log("CONFLICT", f"{rel_str}")
        print(f"             Both local and vault were edited since last sync.")
        print(f"             Vault version saved as: {conflict_name}")
        print(f"             Merge manually, then run /sync-vault to resync.")

    else:
        log("skip", f"{rel_str}  (no change)")

    save_state(state, state_lock)


# ── Reconciliation ────────────────────────────────────────────────────────────

def reconcile(cfg: dict, state: dict, state_lock: threading.Lock):
    """Compare all tracked files on both sides and sync using three-way logic."""
    rel_paths = all_tracked_rel_paths(cfg)
    if not rel_paths:
        log("info", "No tracked files found.")
        return

    log("info", f"Reconciling {len(rel_paths)} tracked file(s)...")
    for rel_str in sorted(rel_paths):
        local = cfg["local_root"]    / rel_str
        vault = cfg["vault_project"] / rel_str
        sync_pair(local, vault, rel_str, state, state_lock)
    log("info", "Reconciliation complete.")


# ── Watchdog event handler ────────────────────────────────────────────────────

class SyncHandler(FileSystemEventHandler):
    """Debounced file event handler for one side (local or vault)."""

    def __init__(self, cfg: dict, state: dict, state_lock: threading.Lock,
                 debounce: float, source: str):
        self.cfg        = cfg
        self.state      = state
        self.state_lock = state_lock
        self.debounce   = debounce
        self.source     = source   # "local" or "vault"
        self._timers: dict[str, threading.Timer] = {}
        self._timer_lock = threading.Lock()

    def _schedule(self, path_str: str):
        with self._timer_lock:
            existing = self._timers.pop(path_str, None)
            if existing:
                existing.cancel()
            t = threading.Timer(self.debounce, self._process, args=[path_str])
            self._timers[path_str] = t
            t.start()

    def _process(self, path_str: str):
        with self._timer_lock:
            self._timers.pop(path_str, None)

        path = Path(path_str)
        try:
            if self.source == "local":
                rel   = path.relative_to(self.cfg["local_root"])
                local = path
                vault = self.cfg["vault_project"] / rel
            else:
                rel   = path.relative_to(self.cfg["vault_project"])
                vault = path
                local = self.cfg["local_root"] / rel
        except ValueError:
            return

        if not is_included(rel, self.cfg):
            return

        sync_pair(local, vault, rel.as_posix(), self.state, self.state_lock)

    def on_modified(self, event):
        if not event.is_directory:
            self._schedule(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self._schedule(event.src_path)

    def on_deleted(self, event):
        pass  # Deletions are never propagated — too destructive


# ── Lockfile ──────────────────────────────────────────────────────────────────

def pid_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True   # Process exists but we cannot signal it
    except OSError:
        return False


def acquire_lock():
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text().strip())
            if pid_running(pid):
                print(f"ERROR: vault-sync.py is already running (PID {pid}).")
                print("       Only one instance per project is allowed.")
                print(f"       To stop it: kill the process or delete {LOCK_FILE}")
                sys.exit(1)
            else:
                log("info", f"Removing stale lockfile (PID {pid} no longer running).")
        except (ValueError, OSError):
            pass  # Unreadable — overwrite

    LOCK_FILE.write_text(str(os.getpid()))


def release_lock():
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except OSError:
        pass


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="vault-sync.py — Two-way sync between project folder and Obsidian vault."
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Reconcile all tracked files once and exit (no continuous watch)."
    )
    args = parser.parse_args()

    cfg        = load_blueprint()
    state      = load_state()
    state_lock = threading.Lock()

    if args.once:
        reconcile(cfg, state, state_lock)
        return

    # ── Continuous mode ───────────────────────────────────────────────────────
    acquire_lock()

    # Startup reconciliation — catch changes made while watcher was not running
    reconcile(cfg, state, state_lock)

    local_handler = SyncHandler(cfg, state, state_lock, LOCAL_DEBOUNCE, "local")
    vault_handler = SyncHandler(cfg, state, state_lock, VAULT_DEBOUNCE, "vault")

    local_observer = Observer()
    vault_observer = Observer()

    local_observer.schedule(local_handler, str(cfg["local_root"]),    recursive=True)
    vault_observer.schedule(vault_handler, str(cfg["vault_project"]), recursive=True)

    local_observer.start()
    vault_observer.start()

    log("info", f"Watching (local) {cfg['local_root']}")
    log("info", f"Watching (vault) {cfg['vault_project']}")
    log("info", "Two-way sync active. Press Ctrl+C to stop.")

    def shutdown(sig=None, frame=None):
        log("info", "Stopping vault-sync.py...")
        local_observer.stop()
        vault_observer.stop()
        release_lock()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            time.sleep(1)
    finally:
        local_observer.stop()
        vault_observer.stop()
        local_observer.join()
        vault_observer.join()
        release_lock()


if __name__ == "__main__":
    main()
