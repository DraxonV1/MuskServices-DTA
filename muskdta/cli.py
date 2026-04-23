from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

import easygradients as eg
import requests

__version__ = "1.1.0"
__product_name__ = "MuskDTA Launcher"
__description__ = "Launcher/wrapper for MuskServices DTA"
__company__ = "DraxonV1 / MuskServices"
__copyright__ = "Copyright (c) 2025 DraxonV1"
__author__ = "DraxonV1"

GITHUB_REPO = "DraxonV1/MuskServices-DTA"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
DISCORD_LINK = "https://discord.gg/dpk45Be2e3"

DATA_DIR = Path(os.path.expanduser("~")) / ".muskdta"
META_PATH = DATA_DIR / "meta.json"
CONFIG_PATH = DATA_DIR / "config.json"
AUTOUPD_PATH = DATA_DIR / "autoupdate"
LOG_PATH = DATA_DIR / "launcher.log"
EXTENSIONS_DIR = DATA_DIR / "extensions"
NOPECHA_EXT_DIR = EXTENSIONS_DIR / "nopecha_ext"
PROXY_EXT_DIR = EXTENSIONS_DIR / "proxy_extension"

def _safe_mkdir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False

_safe_mkdir(DATA_DIR)
if not _safe_mkdir(EXTENSIONS_DIR):
    EXTENSIONS_DIR = DATA_DIR
    NOPECHA_EXT_DIR = DATA_DIR / "nopecha_ext"
    PROXY_EXT_DIR = DATA_DIR / "proxy_extension"
_safe_mkdir(NOPECHA_EXT_DIR)
_safe_mkdir(PROXY_EXT_DIR)

RESET = "\033[0m"
DIM = "\033[90m"
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

COLORS = [
    "\033[38;2;61;167;108m",
    "\033[38;2;61;175;112m",
    "\033[38;2;61;183;118m",
    "\033[38;2;61;191;124m",
    "\033[38;2;61;199;130m",
    "\033[38;2;61;207;134m",
]

def _visible_len(text):
    return len(ANSI_RE.sub("", text))

def _strip_ansi(text):
    return ANSI_RE.sub("", text)

def _log_line(level: str, msg: str):
    try:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(f"{ts} [{level}] {msg}\n")
    except Exception:
        pass

def info(msg):
    print(f"{COLORS[1]}[~]{RESET} {DIM}{msg}{RESET}")
    _log_line("INFO", msg)

def success(msg):
    print(f"{COLORS[3]}[+]{RESET} {COLORS[2]}{msg}{RESET}")
    _log_line("SUCC", msg)

def warn(msg):
    print(f"\033[38;2;255;170;0m[!]{RESET} {msg}")
    _log_line("WARN", msg)

def error(msg):
    print(f"\033[38;2;255;68;68m[-]{RESET} {msg}")
    _log_line("FAIL", msg)

_OS_MAP = {
    "Windows": ("windows", ".exe"),
    "Linux":   ("linux",   "-linux"),
    "Darwin":  ("macos",   "-macos"),
}

def _detect_os():
    sys_name = platform.system()
    return _OS_MAP.get(sys_name, (sys_name.lower(), ""))

def _tool_path_for_os():
    _, suffix = _detect_os()
    return DATA_DIR / f"tool{suffix}"

def _find_asset_for_os(release):
    _, suffix = _detect_os()
    assets = release.get("assets", [])
    for asset in assets:
        name = asset.get("name", "").lower()
        if name.endswith(suffix.lower()):
            return asset
    return None

def _available_platforms(release):
    names = [a.get("name", "") for a in release.get("assets", [])]
    platforms = []
    for p, (key, suffix) in _OS_MAP.items():
        if any(n.lower().endswith(suffix.lower()) for n in names):
            platforms.append(p)
    return platforms

def _resolve_display_tool_version():
    latest = _get_cached_latest_tag()
    if latest:
        return latest
    return str(_load_meta().get("version", "unknown")).strip() or "unknown"

def print_banner():
    term_width = shutil.get_terminal_size((80, 20)).columns
    ascii_logo_raw = [
        "                    \u2593\u2593         \u2593\u2593                   ",
        "                  \u2593\u2593\u2593\u2593\u2593       \u2593\u2593\u2593\u2593                  ",
        "                 \u2593\u2593\u2593\u2593\u2593\u2593\u2593    \u2593\u2593\u2593\u2593\u2593\u2593\u2593                 ",
        "                \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593  \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593               ",
        "               \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593              ",
        "              \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593             ",
        "            \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593            ",
        "           \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593 \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593  \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593           ",
        "          \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593  \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593   \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593          ",
        "         \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593  \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593   \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593        ",
        "        \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2591  \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593  \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593       ",
        "       \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593   \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593  \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593      ",
        "      \u2591\u2593\u2593\u2593\u2593\u2593\u2593\u2593   \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593  \u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593\u2593  \u2592\u2593\u2593\u2593\u2593\u2593\u2593\u2593      ",
    ]
    max_ascii_width = max(len(line) for line in ascii_logo_raw)
    available_width = term_width - 6
    if available_width < max_ascii_width:
        scale = available_width / max_ascii_width
        scaled = []
        for line in ascii_logo_raw:
            new_len = int(len(line) * scale)
            left_trim = (len(line) - new_len) // 2
            right_trim = len(line) - new_len - left_trim
            scaled.append(line[left_trim:len(line)-right_trim] if right_trim > 0 else line[left_trim:])
        ascii_logo_raw = scaled
        max_ascii_width = max(len(line) for line in ascii_logo_raw)
    inner_width = min(max_ascii_width + 4, term_width - 4)
    def box_line(text=""):
        clean_len = _visible_len(text)
        if clean_len > inner_width:
            text = _strip_ansi(text)[:inner_width]
            clean_len = len(text)
        pad_left = (inner_width - clean_len) // 2
        pad_right = inner_width - clean_len - pad_left
        return f"{DIM}\u2502{RESET} {' ' * pad_left}{text}{' ' * pad_right} {DIM}\u2502{RESET}"
    top    = f"{DIM}\u256d{'─' * (inner_width + 2)}\u256e{RESET}"
    bottom = f"{DIM}\u2570{'─' * (inner_width + 2)}\u256f{RESET}"
    ascii_logo = [f"{COLORS[i % len(COLORS)]}{line}{RESET}" for i, line in enumerate(ascii_logo_raw)]
    prefix = f"{DIM}[~]{RESET}"
    display_ver = _resolve_display_tool_version()
    s1 = f"{prefix} {COLORS[1]}MuskServices.one DTA {display_ver} {DIM}[Launcher v{__version__}]{RESET}"
    s2 = f"{prefix} {COLORS[1]}Worker, Private & AFK Mode{RESET}"
    s3 = f"{prefix} {DIM}discord.muskservices.one{RESET}"
    banner = "\n".join([top, box_line()] + [box_line(l) for l in ascii_logo] + [box_line(), box_line(s1), box_line(s2), box_line(s3), bottom])
    for line in banner.split("\n"):
        print(line.center(term_width))
    print()

def _fetch_latest_release(timeout=10, silent=False):
    try:
        r = requests.get(GITHUB_API, timeout=timeout, headers={"User-Agent": "muskdta-launcher"})
        r.raise_for_status()
        return r.json()
    except Exception as e:
        if not silent:
            warn(f"Could not reach GitHub: {e}")
        return None

def _load_meta():
    try:
        return json.loads(META_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_meta(data):
    META_PATH.write_text(json.dumps(data, indent=4), encoding="utf-8")

def _get_cached_latest_tag(max_age_seconds=6 * 60 * 60):
    meta = _load_meta()
    cached_tag = str(meta.get("latest_tag", "")).strip()
    checked_at = int(meta.get("latest_tag_checked_at", 0) or 0)
    if cached_tag and checked_at and (time.time() - checked_at) <= max_age_seconds:
        return cached_tag
    release = _fetch_latest_release(timeout=4, silent=True)
    if not isinstance(release, dict):
        return cached_tag
    latest = str(release.get("tag_name", "")).strip()
    if latest:
        meta["latest_tag"] = latest
        meta["latest_tag_checked_at"] = int(time.time())
        _save_meta(meta)
    return latest or cached_tag

def _download_tool(asset, tag, tool_path):
    url = asset["browser_download_url"]
    filename = asset["name"]
    info(f"Downloading {filename} ({tag})")
    try:
        with requests.get(url, stream=True, timeout=120, headers={"User-Agent": "muskdta-launcher"}) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            with open(tool_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = int(downloaded / total * 100)
                            bar = "\u2588" * (pct // 5) + "\u2591" * (20 - pct // 5)
                            sys.stdout.write(f"\r  {COLORS[2]}{bar}{RESET} {pct}%")
                            sys.stdout.flush()
        if platform.system() != "Windows":
            os.chmod(tool_path, 0o755)
        print()
        meta = _load_meta()
        meta["version"] = tag
        meta["asset"] = filename
        meta["latest_tag"] = tag
        meta["latest_tag_checked_at"] = int(time.time())
        _save_meta(meta)
        success(f"Downloaded {filename} ({tag})")
    except Exception as e:
        error(f"Download failed: {e}")
        sys.exit(1)

def check_and_update(force=False):
    release = _fetch_latest_release()
    if release is None:
        return False

    tag = release.get("tag_name", "unknown")
    asset = _find_asset_for_os(release)

    if asset is None:
        current_os = platform.system()
        available = _available_platforms(release)
        available_str = ", ".join(available) if available else "none"
        error(f"No {current_os} binary detected.")
        error(f"Currently supported: {available_str}")
        sys.exit(1)

    tool_path = _tool_path_for_os()
    meta = _load_meta()

    if not tool_path.exists():
        info("Binary not found. Downloading ...")
        _download_tool(asset, tag, tool_path)
        return True
    if force:
        info(f"Forcing update to {tag} ...")
        _download_tool(asset, tag, tool_path)
        return True
    if meta.get("version") != tag:
        print(f"\n{COLORS[3]}[~] New update available: {tag}  Updating ...{RESET}\n")
        _download_tool(asset, tag, tool_path)
        return True
    success(f"Binary is up-to-date ({tag})")
    return False

TOOL_DEPS = ["requests", "pillow", "colorama"]
DEP_IMPORT_MAP = {
    "pillow": "PIL",
}

def install_deps():
    info("Checking dependencies ...")
    missing = []
    for dep in TOOL_DEPS:
        mod = DEP_IMPORT_MAP.get(dep, dep.replace("-", "_").split("[")[0])
        try:
            __import__(mod)
        except ImportError:
            missing.append(dep)
    if not missing:
        success("All dependencies present.")
        return
    warn(f"Missing: {', '.join(missing)}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet"] + missing)
        success("Dependencies installed.")
    except subprocess.CalledProcessError as e:
        error(f"pip install failed: {e}")

def _ask(prompt, default=None, choices=None):
    if choices:
        hint = f" [{'/'.join(choices)}]"
    elif default is not None:
        hint = f" (default: {default})"
    else:
        hint = ""
    sys.stdout.write(f"  {COLORS[1]}{prompt}{DIM}{hint}{RESET}{DIM}: {RESET}")
    sys.stdout.flush()
    try:
        val = input().strip()
    except (EOFError, KeyboardInterrupt):
        val = ""
    if not val and default is not None:
        return str(default)
    if choices and val.lower() not in [c.lower() for c in choices]:
        warn(f"Invalid — using default: {default}")
        return str(default)
    return val or str(default or "")

def run_config_wizard():
    print(f"\n{COLORS[2]}[~] Config Setup{RESET}\n")
    ip_rotation = _ask("IP rotation mode", default="none", choices=["none", "adb", "vpn", "proxy"]).lower()
    mode = _ask("Account mode", default="worker", choices=["worker", "private", "afk"]).lower()
    adb_rotate_every = 2
    if ip_rotation == "adb":
        try:
            adb_rotate_every = int(_ask("Rotate ADB IP every N accounts", default="2"))
        except ValueError:
            adb_rotate_every = 2
    proxy_mode = "http"
    if ip_rotation == "proxy":
        proxy_mode = _ask("Proxy protocol", default="http", choices=["http", "https", "socks5", "socks5h"]).lower()
    try:
        delay_between_accs = int(_ask("Delay between accounts (seconds)", default="0"))
    except ValueError:
        delay_between_accs = 0
    try:
        after_create_timer = int(_ask("Wait after account created (seconds)", default="0"))
    except ValueError:
        after_create_timer = 0
    return {
        "mode": mode,
        "ip_rotation": ip_rotation,
        "http_lib": "curl",
        "adb_rotate_every": adb_rotate_every,
        "proxy_mode": proxy_mode,
        "nopecha_extension_dir": str(NOPECHA_EXT_DIR),
        "proxy_extension_dir": str(PROXY_EXT_DIR),
        "delay_between_accs": delay_between_accs,
        "after_create_timer": after_create_timer,
        "notify": False,
        "notification_icon": "",
    }

def _normalize_config(cfg):
    if not isinstance(cfg, dict):
        return None
    changed = False

    mode = str(cfg.get("mode", "worker")).lower()
    if mode not in {"worker", "private", "afk"}:
        mode = "worker"
        changed = True
    if cfg.get("mode") != mode:
        cfg["mode"] = mode
        changed = True

    ip_rotation = str(cfg.get("ip_rotation", "none")).lower()
    if ip_rotation not in {"none", "adb", "vpn", "proxy"}:
        ip_rotation = "none"
        changed = True
    if cfg.get("ip_rotation") != ip_rotation:
        cfg["ip_rotation"] = ip_rotation
        changed = True

    if str(cfg.get("http_lib", "curl")).lower() not in {"curl", "requests"}:
        cfg["http_lib"] = "curl"
        changed = True

    if "nopecha_extension_dir" not in cfg:
        cfg["nopecha_extension_dir"] = str(NOPECHA_EXT_DIR)
        changed = True
    if "proxy_extension_dir" not in cfg:
        cfg["proxy_extension_dir"] = str(PROXY_EXT_DIR)
        changed = True

    if changed:
        info("Config updated with latest mode/extension settings.")
    return cfg

def save_config(cfg):
    try:
        CONFIG_PATH.write_text(json.dumps(cfg, indent=4), encoding="utf-8")
        success(f"Config saved to {CONFIG_PATH}")
        return True
    except OSError as e:
        error(f"Failed to save config: {e}")
        return False

def load_config():
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return _normalize_config(cfg)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def open_config_in_editor():
    if not CONFIG_PATH.exists():
        error("No config.json found. Run: muskdta config")
        return
    system = platform.system()
    if system == "Windows":
        os.startfile(str(CONFIG_PATH))
    elif system == "Darwin":
        subprocess.Popen(["open", "-e", str(CONFIG_PATH)])
    else:
        for ed in ["xdg-open", "nano", "vim", "vi"]:
            if shutil.which(ed):
                subprocess.Popen([ed, str(CONFIG_PATH)])
                break
    info(f"Opened {CONFIG_PATH}")

def is_auto_update_on():
    return AUTOUPD_PATH.exists()

def set_auto_update(state):
    if state:
        AUTOUPD_PATH.touch()
        success("Auto-update enabled.")
    else:
        AUTOUPD_PATH.unlink(missing_ok=True)
        success("Auto-update disabled.")

def launch_tool():
    tool_path = _tool_path_for_os()
    if not tool_path.exists():
        error(f"Binary not found ({tool_path.name}). Run: muskdta update")
        sys.exit(1)
    cfg = load_config()
    if cfg is None:
        error("config.json missing. Run: muskdta config")
        sys.exit(1)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=4), encoding="utf-8")
    info(f"Launching {tool_path.name} ...")
    try:
        result = subprocess.run([str(tool_path)], cwd=str(DATA_DIR))
        sys.exit(result.returncode)
    except FileNotFoundError:
        error(f"Could not execute {tool_path.name}.")
        sys.exit(1)
    except PermissionError:
        error("Permission denied. Try running as Administrator / sudo.")
        sys.exit(1)

def _print_status():
    meta = _load_meta()
    tool_path = _tool_path_for_os()
    print(f"\n{COLORS[2]}[~] MuskDTA Status{RESET}\n")
    print(f"  {DIM}Platform      {RESET}{platform.system()}")
    print(f"  {DIM}Binary        {RESET}{tool_path.name}")
    print(f"  {DIM}Version       {RESET}{COLORS[1]}{meta.get('version', 'not installed')}{RESET}")
    cfg_state = f"{COLORS[3]}present{RESET}" if CONFIG_PATH.exists() else f"\033[38;2;255;68;68mmissing{RESET}"
    print(f"  {DIM}Config        {RESET}{cfg_state}")
    au_state = f"{COLORS[3]}ON{RESET}" if is_auto_update_on() else f"\033[38;2;255;170;0mOFF{RESET}"
    print(f"  {DIM}Auto-update   {RESET}{au_state}")
    print(f"  {DIM}Data dir      {RESET}{DATA_DIR}")
    print()

def _validate_config_data(cfg):
    errors = []
    if not isinstance(cfg, dict):
        return False, ["Config is not a JSON object."]
    if cfg.get("mode") not in {"worker", "private", "afk"}:
        errors.append("mode must be one of: worker, private, afk")
    if cfg.get("ip_rotation") not in {"none", "adb", "vpn", "proxy"}:
        errors.append("ip_rotation must be one of: none, adb, vpn, proxy")
    if cfg.get("proxy_mode") not in {"http", "https", "socks5", "socks5h"}:
        errors.append("proxy_mode must be one of: http, https, socks5, socks5h")
    for k in ("delay_between_accs", "adb_rotate_every", "after_create_timer"):
        try:
            v = int(cfg.get(k, 0))
            if v < 0:
                errors.append(f"{k} must be >= 0")
        except Exception:
            errors.append(f"{k} must be a number")
    for k in ("nopecha_extension_dir", "proxy_extension_dir"):
        v = cfg.get(k)
        if not isinstance(v, str) or not v.strip():
            errors.append(f"{k} must be a non-empty path string")
    return len(errors) == 0, errors

def _cmd_config_validate():
    cfg = load_config()
    if cfg is None:
        error("config.json missing or invalid JSON. Run: muskdta config")
        return 1
    ok, errors = _validate_config_data(cfg)
    if ok:
        success("Config validation passed.")
        return 0
    error("Config validation failed:")
    for e in errors:
        print(f"  - {e}")
    return 1

def _cmd_mode_set(mode_value: str):
    cfg = load_config()
    if cfg is None:
        cfg = run_config_wizard()
    cfg["mode"] = mode_value
    if save_config(_normalize_config(cfg)):
        success(f"Mode set to '{mode_value}'.")
        return 0
    return 1

def _cmd_extensions_sync():
    _safe_mkdir(DATA_DIR)
    _safe_mkdir(EXTENSIONS_DIR)
    _safe_mkdir(NOPECHA_EXT_DIR)
    _safe_mkdir(PROXY_EXT_DIR)
    cfg = load_config()
    if cfg is None:
        cfg = run_config_wizard()
    cfg["nopecha_extension_dir"] = str(NOPECHA_EXT_DIR)
    cfg["proxy_extension_dir"] = str(PROXY_EXT_DIR)
    if save_config(_normalize_config(cfg)):
        success("Extension directories synced.")
        print(f"  {DIM}NopeCHA{RESET}: {NOPECHA_EXT_DIR}")
        print(f"  {DIM}Proxy  {RESET}: {PROXY_EXT_DIR}")
        return 0
    return 1

def _cmd_logs(lines: int):
    if not LOG_PATH.exists():
        warn("No launcher logs found yet.")
        return 0
    try:
        content = LOG_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception as e:
        error(f"Failed to read logs: {e}")
        return 1
    tail = content[-max(1, lines):]
    print(f"\n{COLORS[2]}[~] Last {len(tail)} log lines ({LOG_PATH}){RESET}\n")
    for line in tail:
        print(line)
    print()
    return 0

def _cmd_doctor():
    failures = 0
    print(f"\n{COLORS[2]}[~] MuskDTA Doctor{RESET}\n")
    print(f"  {DIM}Python        {RESET}{platform.python_version()}")
    pip_ok = True
    try:
        subprocess.check_output([sys.executable, "-m", "pip", "--version"], stderr=subprocess.STDOUT)
    except Exception:
        pip_ok = False
    print(f"  {DIM}pip           {RESET}{'OK' if pip_ok else 'Missing'}")
    if not pip_ok:
        failures += 1
    dep_missing = []
    for dep in TOOL_DEPS:
        mod = DEP_IMPORT_MAP.get(dep, dep.replace("-", "_").split("[")[0])
        try:
            __import__(mod)
        except ImportError:
            dep_missing.append(dep)
    print(f"  {DIM}Dependencies  {RESET}{'OK' if not dep_missing else 'Missing: ' + ', '.join(dep_missing)}")
    if dep_missing:
        failures += 1
    tool_path = _tool_path_for_os()
    tool_ok = tool_path.exists()
    print(f"  {DIM}Binary        {RESET}{tool_path} {'(OK)' if tool_ok else '(Missing)'}")
    if not tool_ok:
        failures += 1
    license_path = DATA_DIR / "license.key"
    lic_ok = license_path.exists()
    print(f"  {DIM}License file  {RESET}{license_path} {'(OK)' if lic_ok else '(Missing)'}")
    if not lic_ok:
        failures += 1
    cfg = load_config()
    if cfg is None:
        print(f"  {DIM}Config        {RESET}Missing/invalid")
        failures += 1
    else:
        ok, errors = _validate_config_data(cfg)
        print(f"  {DIM}Config        {RESET}{'OK' if ok else 'Invalid'}")
        if not ok:
            failures += 1
            for e in errors:
                print(f"    - {e}")
    print(f"  {DIM}NopeCHA dir   {RESET}{NOPECHA_EXT_DIR}")
    print(f"  {DIM}Proxy dir     {RESET}{PROXY_EXT_DIR}")
    print()
    if failures:
        error(f"Doctor found {failures} issue(s).")
        return 1
    success("Doctor check passed.")
    return 0

def main():
    parser = argparse.ArgumentParser(prog="muskdta", description="MuskServices DTA launcher", add_help=True)
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("update", help="Force download latest binary")
    sub.add_parser("discord", help="Open the MuskServices Discord")
    sub.add_parser("status", help="Show install status")
    sub.add_parser("doctor", help="Run environment and config diagnostics")
    cfg_p = sub.add_parser("config", help="Edit configuration")
    cfg_p.add_argument("mode", nargs="?", choices=["manual", "validate"], help="manual = open in editor, validate = strict config check")
    mode_p = sub.add_parser("mode", help="Mode tools")
    mode_p.add_argument("action", choices=["set"], help="set mode value")
    mode_p.add_argument("value", choices=["worker", "private", "afk"], help="new mode")
    ext_p = sub.add_parser("extensions", help="Extension folder tools")
    ext_p.add_argument("action", choices=["sync"], help="sync extension dirs into config")
    logs_p = sub.add_parser("logs", help="Show launcher logs")
    logs_p.add_argument("--lines", type=int, default=50, help="number of lines to show (default: 50)")
    au_p = sub.add_parser("auto-update", help="Toggle automatic updates")
    au_p.add_argument("state", choices=["on", "off"])
    args = parser.parse_args()
    print_banner()
    if args.cmd == "discord":
        info("Opening Discord ...")
        webbrowser.open(DISCORD_LINK)
        return
    if args.cmd == "status":
        _print_status()
        return
    if args.cmd == "doctor":
        sys.exit(_cmd_doctor())
    if args.cmd == "mode":
        if args.action == "set":
            sys.exit(_cmd_mode_set(args.value))
        return
    if args.cmd == "extensions":
        if args.action == "sync":
            sys.exit(_cmd_extensions_sync())
        return
    if args.cmd == "logs":
        sys.exit(_cmd_logs(args.lines))
    if args.cmd == "auto-update":
        set_auto_update(args.state == "on")
        return
    if args.cmd == "update":
        check_and_update(force=True)
        install_deps()
        return
    if args.cmd == "config":
        if args.mode == "manual":
            open_config_in_editor()
        elif args.mode == "validate":
            sys.exit(_cmd_config_validate())
        else:
            save_config(run_config_wizard())
        return
    info("Running startup checks ...\n")
    if is_auto_update_on():
        check_and_update()
    else:
        tool_path = _tool_path_for_os()
        if not tool_path.exists():
            warn(f"Binary missing. Downloading ...")
            check_and_update()
        else:
            info(f"Auto-update is OFF. Installed: {_load_meta().get('version', 'unknown')}")
    install_deps()
    if not CONFIG_PATH.exists():
        warn("No config found.")
        save_config(run_config_wizard())
    else:
        cfg = load_config()
        if cfg is None:
            error("config.json is corrupted. Regenerating ...")
            save_config(run_config_wizard())
        else:
            success("Config OK")
    print()
    launch_tool()

if __name__ == "__main__":
    main()
