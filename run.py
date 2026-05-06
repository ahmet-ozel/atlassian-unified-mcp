#!/usr/bin/env python3
"""Atlassian Unified MCP - Tek dosya calistirici.

Bu script:
1. Gerekli bagimliliklari kontrol eder, yoksa otomatik kurar
2. MCP sunucusunu baslatir

Kullanim:
  python run.py
"""
import subprocess
import sys
import os

# Gerekli paketler
REQUIRED = ["mcp", "httpx"]

def _ensure_deps():
    """Eksik bagimliliklari otomatik kurar."""
    missing = []
    for pkg in REQUIRED:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"[atlassian-mcp] Eksik paketler kuruluyor: {', '.join(missing)}", file=sys.stderr)
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet"] + missing,
            stdout=subprocess.DEVNULL,
        )

if __name__ == "__main__":
    _ensure_deps()

    # server.py'nin bulundugu dizini sys.path'e ekle
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)

    from atlassian_unified_mcp.server import main
    main()
