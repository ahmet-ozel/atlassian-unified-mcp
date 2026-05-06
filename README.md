# Atlassian Unified MCP Server

Jira + Confluence + Bitbucket Server/Data Center icin birlesik MCP sunucusu.
**61 tool** — tek paket, tek config.

## Hizli Kurulum (2 adim)

### 1. Indir

```bash
git clone https://github.com/ahmet-ozel/atlassian-unified-mcp.git
cd atlassian-unified-mcp
```

### 2. Kur (otomatik)

```bash
python install.py
```

Bu script:
- Hangi Python calistiriyorsaniz ona bagimliliklari kurar
- Sizden Jira/Confluence/Bitbucket URL ve token'larini ister
- `.vscode/mcp.json` dosyasini otomatik olusturur (dogru Python yolu ile)

Sonra:
1. VS Code'da projeyi ac
2. `.vscode/mcp.json` dosyasini ac → ustte **"Start"** butonuna tikla
3. Copilot Chat → **Agent** modu → kullan

---

## Manuel Kurulum (install.py kullanmadan)

```bash
git clone https://github.com/ahmet-ozel/atlassian-unified-mcp.git
cd atlassian-unified-mcp
pip install -e .
```

Sonra `.vscode/mcp.json` olustur:

```json
{
  "servers": {
    "atlassian": {
      "command": "python",
      "args": ["-m", "atlassian_unified_mcp"],
      "env": {
        "JIRA_URL": "https://jira.sirketiniz.com",
        "JIRA_PAT_TOKEN": "senin-pat-tokenin",
        "CONFLUENCE_URL": "https://confluence.sirketiniz.com",
        "CONFLUENCE_PAT_TOKEN": "senin-pat-tokenin",
        "BITBUCKET_URL": "https://bitbucket.sirketiniz.com",
        "BITBUCKET_PAT_TOKEN": "senin-pat-tokenin",
        "SSL_VERIFY": "false"
      }
    }
  }
}
```

> Kullanmadigin servisleri (ornegin Confluence yoksa) `env`'den cikar.

### 3. IDE'yi yeniden baslat

- VS Code: `Ctrl+Shift+P` → "Reload Window"
- `.vscode/mcp.json` dosyasini ac → ustte "Start" butonuna tikla
- Copilot Chat'i ac → **Agent** modunu sec → kullan

---

## Alternatif: pip install olmadan (sadece Python yolu ile)

`pip install` yapmak istemiyorsan, config'de script'in tam yolunu ver:

```json
{
  "servers": {
    "atlassian": {
      "command": "python",
      "args": ["C:/tam/yol/atlassian-unified-mcp/atlassian_unified_mcp/server.py"],
      "env": {
        "JIRA_URL": "https://jira.sirketiniz.com",
        "JIRA_PAT_TOKEN": "senin-pat-tokenin"
      }
    }
  }
}
```

---

## Kiro icin

`.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "python",
      "args": ["-m", "atlassian_unified_mcp"],
      "env": {
        "JIRA_URL": "https://jira.sirketiniz.com",
        "JIRA_PAT_TOKEN": "senin-pat-tokenin",
        "CONFLUENCE_URL": "https://confluence.sirketiniz.com",
        "CONFLUENCE_PAT_TOKEN": "senin-pat-tokenin",
        "BITBUCKET_URL": "https://bitbucket.sirketiniz.com",
        "BITBUCKET_PAT_TOKEN": "senin-pat-tokenin",
        "SSL_VERIFY": "false"
      }
    }
  }
}
```

> Not: Kiro `"mcpServers"` kullanir, VS Code `"servers"` kullanir.

---

## Claude Desktop icin

`claude_desktop_config.json` (genelde `%APPDATA%\Claude\`):

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "python",
      "args": ["-m", "atlassian_unified_mcp"],
      "env": {
        "JIRA_URL": "https://jira.sirketiniz.com",
        "JIRA_PAT_TOKEN": "senin-pat-tokenin",
        "CONFLUENCE_URL": "https://confluence.sirketiniz.com",
        "CONFLUENCE_PAT_TOKEN": "senin-pat-tokenin",
        "BITBUCKET_URL": "https://bitbucket.sirketiniz.com",
        "BITBUCKET_PAT_TOKEN": "senin-pat-tokenin",
        "SSL_VERIFY": "false"
      }
    }
  }
}
```

---

## Mevcut Tool'lar (61)

### Jira (25 tool)
| Tool | Aciklama |
|---|---|
| `jira_get_issue` | Issue detayi |
| `jira_create_issue` | Issue olusturma |
| `jira_update_issue` | Issue guncelleme |
| `jira_delete_issue` | Issue silme |
| `jira_assign_issue` | Issue atama |
| `jira_search` | JQL ile arama |
| `jira_get_transitions` | Durum gecisleri |
| `jira_transition_issue` | Durum degistirme |
| `jira_get_comments` | Yorum listeleme |
| `jira_add_comment` | Yorum ekleme |
| `jira_get_worklogs` | Worklog listeleme |
| `jira_add_worklog` | Worklog ekleme |
| `jira_get_projects` | Proje listesi |
| `jira_get_project` | Proje detayi |
| `jira_search_users` | Kullanici arama |
| `jira_get_myself` | Mevcut kullanici |
| `jira_get_issue_types` | Issue tipleri |
| `jira_get_priorities` | Oncelikler |
| `jira_get_statuses` | Durumlar |
| `jira_create_issue_link` | Issue link |
| `jira_get_boards` | Board listesi |
| `jira_get_sprints` | Sprint listesi |
| `jira_get_sprint_issues` | Sprint issue'lari |
| `jira_get_backlog` | Backlog |
| `jira_get_epic_issues` | Epic issue'lari |

### Confluence (14 tool)
| Tool | Aciklama |
|---|---|
| `confluence_search` | CQL ile arama |
| `confluence_get_page` | Sayfa icerigi |
| `confluence_get_page_by_title` | Baslikla arama |
| `confluence_create_page` | Sayfa olusturma |
| `confluence_update_page` | Sayfa guncelleme |
| `confluence_delete_page` | Sayfa silme |
| `confluence_get_spaces` | Space listesi |
| `confluence_get_space` | Space detayi |
| `confluence_get_page_children` | Alt sayfalar |
| `confluence_get_page_comments` | Yorumlar |
| `confluence_add_page_comment` | Yorum ekleme |
| `confluence_get_page_labels` | Etiketler |
| `confluence_add_page_label` | Etiket ekleme |
| `confluence_get_pages_in_space` | Space sayfalari |

### Bitbucket (22 tool)
| Tool | Aciklama |
|---|---|
| `bb_list_projects` | Proje listesi |
| `bb_list_repositories` | Repo listesi |
| `bb_list_branches` | Branch listesi |
| `bb_delete_branch` | Branch silme |
| `bb_list_commits` | Commit gecmisi |
| `bb_list_pull_requests` | PR listesi |
| `bb_get_pull_request` | PR detayi |
| `bb_create_pull_request` | PR olusturma |
| `bb_update_pull_request` | PR guncelleme |
| `bb_merge_pull_request` | PR merge |
| `bb_decline_pull_request` | PR reddetme |
| `bb_approve_pull_request` | PR onaylama |
| `bb_unapprove_pull_request` | Onay geri alma |
| `bb_get_pr_activities` | PR aktiviteleri |
| `bb_get_pr_comments` | PR yorumlari |
| `bb_add_pr_comment` | PR yorum ekleme |
| `bb_get_pr_diff` | PR diff |
| `bb_get_file_content` | Dosya okuma |
| `bb_browse_repository` | Dizin gozatma |
| `bb_search` | Kod/dosya arama |
| `bb_get_dashboard_pull_requests` | Dashboard PR'lar |
| `bb_get_default_branch` | Default branch |

---

## Ortam Degiskenleri

| Degisken | Zorunlu | Aciklama |
|---|---|---|
| `JIRA_URL` | Evet* | Jira sunucu adresi |
| `JIRA_PAT_TOKEN` | Hayir | Jira PAT token |
| `JIRA_USERNAME` | Hayir | Jira kullanici adi (PAT yoksa) |
| `JIRA_PASSWORD` | Hayir | Jira sifresi |
| `CONFLUENCE_URL` | Hayir | Confluence sunucu adresi |
| `CONFLUENCE_PAT_TOKEN` | Hayir | Confluence PAT token |
| `CONFLUENCE_USERNAME` | Hayir | Confluence kullanici adi |
| `CONFLUENCE_PASSWORD` | Hayir | Confluence sifresi |
| `BITBUCKET_URL` | Hayir | Bitbucket sunucu adresi |
| `BITBUCKET_PAT_TOKEN` | Hayir | Bitbucket PAT token |
| `BITBUCKET_USERNAME` | Hayir | Bitbucket kullanici adi |
| `BITBUCKET_PASSWORD` | Hayir | Bitbucket sifresi |
| `SSL_VERIFY` | Hayir | SSL dogrulama (varsayilan: true) |

*En az bir servis yapilandirilmalidir.

---

## Sorun Giderme

**"ENOENT" hatasi**: `pip install` sonrasi script PATH'te degilse, config'de `"command": "python"` ve `"args": ["-m", "atlassian_unified_mcp"]` kullanin.

**SSL hatasi**: Self-signed sertifika kullaniyorsaniz `"SSL_VERIFY": "false"` ekleyin.

**401 Unauthorized**: PAT token'in suresi dolmus veya yanlis. Jira/Confluence/Bitbucket'tan yeni token olusturun.
