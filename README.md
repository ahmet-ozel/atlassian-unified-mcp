# Atlassian Unified MCP Server

Jira + Confluence + Bitbucket Server/Data Center icin birlesik MCP sunucusu.

## Kurulum

```bash
cd mcp_server
pip install -e .
```

## Kullanim

### CLI olarak calistirma (sunucu)
```bash
export JIRA_URL=https://jira.example.com
export JIRA_PAT_TOKEN=your-jira-pat
export CONFLUENCE_URL=https://confluence.example.com
export CONFLUENCE_PAT_TOKEN=your-confluence-pat
export BITBUCKET_URL=https://bitbucket.example.com
export BITBUCKET_PAT_TOKEN=your-bitbucket-pat

atlassian-mcp
```

### IDE'ye ekleme (Kiro / VS Code / Cursor)

`.kiro/settings/mcp.json` veya IDE'nin MCP config dosyasina ekleyin:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "atlassian-mcp",
      "env": {
        "JIRA_URL": "https://jira.example.com",
        "JIRA_PAT_TOKEN": "your-jira-pat",
        "CONFLUENCE_URL": "https://confluence.example.com",
        "CONFLUENCE_PAT_TOKEN": "your-confluence-pat",
        "BITBUCKET_URL": "https://bitbucket.example.com",
        "BITBUCKET_PAT_TOKEN": "your-bitbucket-pat",
        "SSL_VERIFY": "true"
      }
    }
  }
}
```

### Basic Auth ile kullanim

PAT token yerine kullanici adi/sifre de kullanabilirsiniz:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "atlassian-mcp",
      "env": {
        "JIRA_URL": "https://jira.example.com",
        "JIRA_USERNAME": "your-username",
        "JIRA_PASSWORD": "your-password",
        "CONFLUENCE_URL": "https://confluence.example.com",
        "CONFLUENCE_USERNAME": "your-username",
        "CONFLUENCE_PASSWORD": "your-password",
        "BITBUCKET_URL": "https://bitbucket.example.com",
        "BITBUCKET_USERNAME": "your-username",
        "BITBUCKET_PASSWORD": "your-password"
      }
    }
  }
}
```

## Mevcut Tool'lar

### Jira (11 tool)
- `jira_search` — JQL ile issue arama
- `jira_get_issue` — Issue detayi
- `jira_create_issue` — Issue olusturma
- `jira_update_issue` — Issue guncelleme
- `jira_get_transitions` — Durum gecisleri
- `jira_transition_issue` — Durum degistirme
- `jira_add_comment` — Yorum ekleme
- `jira_get_projects` — Proje listesi
- `jira_get_boards` — Board listesi
- `jira_get_sprints` — Sprint listesi
- `jira_get_sprint_issues` — Sprint issue'lari

### Confluence (5 tool)
- `confluence_search` — CQL ile arama
- `confluence_get_page` — Sayfa icerigi
- `confluence_create_page` — Sayfa olusturma
- `confluence_update_page` — Sayfa guncelleme
- `confluence_get_spaces` — Space listesi

### Bitbucket (17 tool)
- `bb_list_projects` — Proje listesi
- `bb_list_repositories` — Repository listesi
- `bb_list_branches` — Branch listesi
- `bb_list_commits` — Commit gecmisi
- `bb_list_pull_requests` — PR listesi
- `bb_get_pull_request` — PR detayi
- `bb_create_pull_request` — PR olusturma
- `bb_merge_pull_request` — PR merge
- `bb_approve_pull_request` — PR onaylama
- `bb_add_pr_comment` — PR yorum ekleme
- `bb_get_pr_diff` — PR diff
- `bb_get_file_content` — Dosya okuma
- `bb_browse_repository` — Dizin gozatma
- `bb_search` — Kod/dosya arama

**Toplam: 33 tool**

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

*En az bir servis (Jira, Confluence veya Bitbucket) yapilandirilmalidir.
