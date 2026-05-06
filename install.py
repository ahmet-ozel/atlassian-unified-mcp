#!/usr/bin/env python3
"""Atlassian Unified MCP — Otomatik Kurulum.

Bu script'i calistirdiginiz Python hangisiyse, MCP o Python ile calisir.
Hicbir PATH ayari gerekmez.

Kullanim:
    python install.py

Ne yapar:
    1. Gerekli paketleri kurar (mcp, httpx)
    2. .vscode/mcp.json dosyasini olusturur (dogru Python yolu ile)
    3. Sizden Jira/Confluence/Bitbucket bilgilerini ister
"""

import json
import os
import subprocess
import sys


def main():
    print("=" * 60)
    print("  Atlassian Unified MCP — Kurulum")
    print("  Jira + Confluence + Bitbucket (61 tool)")
    print("=" * 60)
    print()

    python_exe = sys.executable
    print(f"[*] Python: {python_exe}")
    print()

    # 1. Bagimliliklari kur
    print("[1/3] Bagimliliklar kuruluyor...")
    subprocess.check_call(
        [python_exe, "-m", "pip", "install", "--quiet", "mcp>=1.0.0", "httpx>=0.27.0"],
    )

    # Paketi kendisi de kur
    script_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.check_call(
        [python_exe, "-m", "pip", "install", "--quiet", "-e", script_dir],
    )
    print("    Tamam.")
    print()

    # 2. Kullanicidan bilgileri al
    print("[2/3] Servis bilgilerini girin (bos birakirsaniz o servis devre disi kalir):")
    print()

    jira_url = input("  Jira URL (ornek: https://jira.sirket.com): ").strip()
    jira_pat = ""
    if jira_url:
        jira_pat = input("  Jira PAT Token: ").strip()

    confluence_url = input("  Confluence URL (bos = devre disi): ").strip()
    confluence_pat = ""
    if confluence_url:
        confluence_pat = input("  Confluence PAT Token: ").strip()

    bitbucket_url = input("  Bitbucket URL (bos = devre disi): ").strip()
    bitbucket_pat = ""
    if bitbucket_url:
        bitbucket_pat = input("  Bitbucket PAT Token: ").strip()

    ssl_verify = input("  SSL Verify (true/false, varsayilan: false): ").strip() or "false"

    print()

    # 3. mcp.json olustur
    print("[3/3] .vscode/mcp.json olusturuluyor...")

    env = {"SSL_VERIFY": ssl_verify}
    if jira_url:
        env["JIRA_URL"] = jira_url
    if jira_pat:
        env["JIRA_PAT_TOKEN"] = jira_pat
    if confluence_url:
        env["CONFLUENCE_URL"] = confluence_url
    if confluence_pat:
        env["CONFLUENCE_PAT_TOKEN"] = confluence_pat
    if bitbucket_url:
        env["BITBUCKET_URL"] = bitbucket_url
    if bitbucket_pat:
        env["BITBUCKET_PAT_TOKEN"] = bitbucket_pat

    config = {
        "servers": {
            "atlassian": {
                "command": python_exe.replace("\\", "\\\\") if os.name == "nt" else python_exe,
                "args": ["-m", "atlassian_unified_mcp"],
                "env": env,
            }
        }
    }

    # Hedef dizin: script'in calistirildigi dizin
    cwd = os.getcwd()
    vscode_dir = os.path.join(cwd, ".vscode")
    os.makedirs(vscode_dir, exist_ok=True)

    mcp_json_path = os.path.join(vscode_dir, "mcp.json")

    # Mevcut dosya varsa uyar
    if os.path.exists(mcp_json_path):
        overwrite = input(f"    {mcp_json_path} zaten var. Uzerine yazilsin mi? (e/h): ").strip().lower()
        if overwrite not in ("e", "evet", "y", "yes"):
            print("    Iptal edildi.")
            return

    with open(mcp_json_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"    Olusturuldu: {mcp_json_path}")
    print()
    print("=" * 60)
    print("  KURULUM TAMAMLANDI!")
    print()
    print("  Simdi:")
    print("  1. VS Code'da bu projeyi ac")
    print("  2. .vscode/mcp.json dosyasini ac")
    print("  3. Ustteki 'Start' butonuna tikla")
    print("  4. Copilot Chat → Agent modu → kullan")
    print("=" * 60)


if __name__ == "__main__":
    main()
