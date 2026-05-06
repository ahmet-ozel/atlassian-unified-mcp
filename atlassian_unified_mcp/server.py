"""Birlesik Atlassian MCP Sunucusu — Jira + Confluence + Bitbucket Server/DC.

Tum Jira, Confluence ve Bitbucket Server/Data Center REST API tool'larini
tek bir MCP sunucusu uzerinden sunar. IDE'ye (Kiro, Cursor, VS Code vb.)
veya sunucuya kurulabilir.

Ortam degiskenleri:
  JIRA_URL, JIRA_PAT_TOKEN (veya JIRA_USERNAME + JIRA_PASSWORD)
  CONFLUENCE_URL, CONFLUENCE_PAT_TOKEN (veya CONFLUENCE_USERNAME + CONFLUENCE_PASSWORD)
  BITBUCKET_URL, BITBUCKET_PAT_TOKEN (veya BITBUCKET_USERNAME + BITBUCKET_PASSWORD)
  SSL_VERIFY (varsayilan: true)
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("atlassian-unified")

# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()

def _env_bool(name: str, default: bool = True) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() not in {"0", "false", "no", "off"}

SSL_VERIFY = _env_bool("SSL_VERIFY", True)

# ---------------------------------------------------------------------------
# HTTP client factory
# ---------------------------------------------------------------------------

def _make_client(url: str, auth: tuple[str, str] | str) -> httpx.Client:
    headers: Dict[str, str] = {"Content-Type": "application/json"}
    http_auth: httpx.BasicAuth | None = None
    if isinstance(auth, str):
        headers["Authorization"] = f"Bearer {auth}"
    else:
        http_auth = httpx.BasicAuth(auth[0], auth[1])
    return httpx.Client(
        base_url=url.rstrip("/"), headers=headers, auth=http_auth,
        verify=SSL_VERIFY, timeout=30.0,
    )

def _req(client: httpx.Client, method: str, path: str,
         params: Optional[Dict[str, Any]] = None,
         json_body: Optional[Any] = None) -> Any:
    if client is None:
        raise Exception("Bu servis yapilandirilmamis. Ortam degiskenlerini kontrol edin.")
    r = client.request(method, path, params=params, json=json_body)
    if r.status_code >= 400:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise Exception(f"HTTP {r.status_code}: {detail}")
    if r.status_code == 204:
        return None
    if r.text and r.text.strip():
        try:
            return r.json()
        except Exception:
            return {"text": r.text}
    return None

def _json(obj: Any) -> str:
    if obj is None:
        return "Islem basarili."
    return json.dumps(obj, ensure_ascii=False, default=str)

# ---------------------------------------------------------------------------
# Client initialization
# ---------------------------------------------------------------------------

_jira: httpx.Client | None = None
_confluence: httpx.Client | None = None
_bitbucket: httpx.Client | None = None

def _init_clients():
    global _jira, _confluence, _bitbucket

    jira_url = _env("JIRA_URL")
    if jira_url:
        pat = _env("JIRA_PAT_TOKEN")
        if pat:
            _jira = _make_client(jira_url, pat)
        elif _env("JIRA_USERNAME") and _env("JIRA_PASSWORD"):
            _jira = _make_client(jira_url, (_env("JIRA_USERNAME"), _env("JIRA_PASSWORD")))

    conf_url = _env("CONFLUENCE_URL")
    if conf_url:
        pat = _env("CONFLUENCE_PAT_TOKEN")
        if pat:
            _confluence = _make_client(conf_url, pat)
        elif _env("CONFLUENCE_USERNAME") and _env("CONFLUENCE_PASSWORD"):
            _confluence = _make_client(conf_url, (_env("CONFLUENCE_USERNAME"), _env("CONFLUENCE_PASSWORD")))

    bb_url = _env("BITBUCKET_URL")
    if bb_url:
        pat = _env("BITBUCKET_PAT_TOKEN")
        if pat:
            _bitbucket = _make_client(bb_url, pat)
        elif _env("BITBUCKET_USERNAME") and _env("BITBUCKET_PASSWORD"):
            _bitbucket = _make_client(bb_url, (_env("BITBUCKET_USERNAME"), _env("BITBUCKET_PASSWORD")))


# ===========================================================================
# JIRA TOOLS (25 tool)
# ===========================================================================

# -- Issue CRUD --

@mcp.tool()
def jira_get_issue(issue_key: str, fields: str = "") -> str:
    """Jira issue detayini getirir. fields: virgul ile ayrilmis alan listesi (opsiyonel)."""
    params = {}
    if fields:
        params["fields"] = fields
    return _json(_req(_jira, "GET", f"/rest/api/2/issue/{issue_key}", params=params or None))

@mcp.tool()
def jira_create_issue(project_key: str, summary: str, issue_type: str = "Task", description: str = "") -> str:
    """Yeni Jira issue olusturur."""
    fields: Dict[str, Any] = {"project": {"key": project_key}, "summary": summary, "issuetype": {"name": issue_type}}
    if description:
        fields["description"] = description
    return _json(_req(_jira, "POST", "/rest/api/2/issue", json_body={"fields": fields}))

@mcp.tool()
def jira_update_issue(issue_key: str, summary: str = "", description: str = "",
                      assignee: str = "", priority: str = "") -> str:
    """Jira issue gunceller. Sadece doldurulan alanlar degisir."""
    fields: Dict[str, Any] = {}
    if summary: fields["summary"] = summary
    if description: fields["description"] = description
    if assignee: fields["assignee"] = {"name": assignee}
    if priority: fields["priority"] = {"name": priority}
    return _json(_req(_jira, "PUT", f"/rest/api/2/issue/{issue_key}", json_body={"fields": fields}))

@mcp.tool()
def jira_delete_issue(issue_key: str) -> str:
    """Jira issue siler."""
    return _json(_req(_jira, "DELETE", f"/rest/api/2/issue/{issue_key}"))

@mcp.tool()
def jira_assign_issue(issue_key: str, assignee: str = "") -> str:
    """Issue'yu bir kullaniciya atar. Bos string = atamayi kaldir."""
    name = assignee if assignee else None
    return _json(_req(_jira, "PUT", f"/rest/api/2/issue/{issue_key}/assignee", json_body={"name": name}))

# -- Search --

@mcp.tool()
def jira_search(jql: str, fields: str = "", max_results: int = 50) -> str:
    """JQL ile Jira issue arar."""
    body: Dict[str, Any] = {"jql": jql, "maxResults": max_results}
    if fields:
        body["fields"] = [f.strip() for f in fields.split(",")]
    return _json(_req(_jira, "POST", "/rest/api/2/search", json_body=body))

# -- Transitions --

@mcp.tool()
def jira_get_transitions(issue_key: str) -> str:
    """Issue icin mevcut durum gecislerini listeler."""
    return _json(_req(_jira, "GET", f"/rest/api/2/issue/{issue_key}/transitions"))

@mcp.tool()
def jira_transition_issue(issue_key: str, transition_id: str, comment: str = "") -> str:
    """Issue durumunu degistirir."""
    body: Dict[str, Any] = {"transition": {"id": transition_id}}
    if comment:
        body["update"] = {"comment": [{"add": {"body": comment}}]}
    return _json(_req(_jira, "POST", f"/rest/api/2/issue/{issue_key}/transitions", json_body=body))

# -- Comments --

@mcp.tool()
def jira_get_comments(issue_key: str) -> str:
    """Issue yorumlarini listeler."""
    return _json(_req(_jira, "GET", f"/rest/api/2/issue/{issue_key}/comment"))

@mcp.tool()
def jira_add_comment(issue_key: str, body: str) -> str:
    """Issue'ya yorum ekler."""
    return _json(_req(_jira, "POST", f"/rest/api/2/issue/{issue_key}/comment", json_body={"body": body}))

# -- Worklog --

@mcp.tool()
def jira_get_worklogs(issue_key: str) -> str:
    """Issue worklog'larini listeler."""
    return _json(_req(_jira, "GET", f"/rest/api/2/issue/{issue_key}/worklog"))

@mcp.tool()
def jira_add_worklog(issue_key: str, time_spent: str, comment: str = "") -> str:
    """Issue'ya worklog ekler. time_spent: 2h, 30m, 1d gibi."""
    wl: Dict[str, Any] = {"timeSpent": time_spent}
    if comment:
        wl["comment"] = comment
    return _json(_req(_jira, "POST", f"/rest/api/2/issue/{issue_key}/worklog", json_body=wl))

# -- Projects --

@mcp.tool()
def jira_get_projects() -> str:
    """Tum Jira projelerini listeler."""
    return _json(_req(_jira, "GET", "/rest/api/2/project"))

@mcp.tool()
def jira_get_project(project_key: str) -> str:
    """Proje detayini getirir."""
    return _json(_req(_jira, "GET", f"/rest/api/2/project/{project_key}"))

# -- Users --

@mcp.tool()
def jira_search_users(username: str) -> str:
    """Kullanici arar."""
    return _json(_req(_jira, "GET", "/rest/api/2/user/search", params={"username": username, "maxResults": 50}))

@mcp.tool()
def jira_get_myself() -> str:
    """Mevcut oturum acmis kullanicinin bilgilerini dondurur."""
    return _json(_req(_jira, "GET", "/rest/api/2/myself"))

# -- Metadata --

@mcp.tool()
def jira_get_issue_types() -> str:
    """Mevcut issue tiplerini listeler."""
    return _json(_req(_jira, "GET", "/rest/api/2/issuetype"))

@mcp.tool()
def jira_get_priorities() -> str:
    """Oncelik seviyelerini listeler."""
    return _json(_req(_jira, "GET", "/rest/api/2/priority"))

@mcp.tool()
def jira_get_statuses() -> str:
    """Durum listesini dondurur."""
    return _json(_req(_jira, "GET", "/rest/api/2/status"))

# -- Links --

@mcp.tool()
def jira_create_issue_link(link_type: str, inward_issue: str, outward_issue: str) -> str:
    """Iki issue arasinda link olusturur."""
    return _json(_req(_jira, "POST", "/rest/api/2/issueLink", json_body={
        "type": {"name": link_type},
        "inwardIssue": {"key": inward_issue},
        "outwardIssue": {"key": outward_issue},
    }))

# -- Agile --

@mcp.tool()
def jira_get_boards(name: str = "", project_key: str = "") -> str:
    """Jira board listesini dondurur."""
    params: Dict[str, Any] = {}
    if name: params["name"] = name
    if project_key: params["projectKeyOrId"] = project_key
    return _json(_req(_jira, "GET", "/rest/agile/1.0/board", params=params or None))

@mcp.tool()
def jira_get_sprints(board_id: int, state: str = "") -> str:
    """Board'a ait sprint listesini dondurur. state: active, closed, future."""
    params: Dict[str, Any] = {}
    if state: params["state"] = state
    return _json(_req(_jira, "GET", f"/rest/agile/1.0/board/{board_id}/sprint", params=params or None))

@mcp.tool()
def jira_get_sprint_issues(board_id: int, sprint_id: int) -> str:
    """Sprint issue listesini dondurur."""
    return _json(_req(_jira, "GET", f"/rest/agile/1.0/board/{board_id}/sprint/{sprint_id}/issue"))

@mcp.tool()
def jira_get_backlog(board_id: int) -> str:
    """Board backlog issue listesini dondurur."""
    return _json(_req(_jira, "GET", f"/rest/agile/1.0/board/{board_id}/backlog"))

@mcp.tool()
def jira_get_epic_issues(epic_key: str) -> str:
    """Epic altindaki issue listesini dondurur."""
    return _json(_req(_jira, "GET", f"/rest/agile/1.0/epic/{epic_key}/issue"))


# ===========================================================================
# CONFLUENCE TOOLS (14 tool)
# ===========================================================================

@mcp.tool()
def confluence_search(cql: str, limit: int = 25) -> str:
    """CQL ile Confluence icerik arar."""
    return _json(_req(_confluence, "GET", "/rest/api/content/search", params={"cql": cql, "limit": limit}))

@mcp.tool()
def confluence_get_page(page_id: str, expand: str = "body.storage,version") -> str:
    """Confluence sayfa icerigini getirir."""
    return _json(_req(_confluence, "GET", f"/rest/api/content/{page_id}", params={"expand": expand}))

@mcp.tool()
def confluence_get_page_by_title(space_key: str, title: str) -> str:
    """Space ve baslik ile Confluence sayfasi arar."""
    return _json(_req(_confluence, "GET", "/rest/api/content",
                       params={"spaceKey": space_key, "title": title, "expand": "body.storage,version"}))

@mcp.tool()
def confluence_create_page(space_key: str, title: str, body_content: str, parent_id: str = "") -> str:
    """Yeni Confluence sayfasi olusturur."""
    data: Dict[str, Any] = {
        "type": "page", "title": title, "space": {"key": space_key},
        "body": {"storage": {"value": body_content, "representation": "storage"}},
    }
    if parent_id:
        data["ancestors"] = [{"id": parent_id}]
    return _json(_req(_confluence, "POST", "/rest/api/content", json_body=data))

@mcp.tool()
def confluence_update_page(page_id: str, title: str, body_content: str, version_number: int) -> str:
    """Confluence sayfasini gunceller."""
    data = {
        "type": "page", "title": title, "version": {"number": version_number},
        "body": {"storage": {"value": body_content, "representation": "storage"}},
    }
    return _json(_req(_confluence, "PUT", f"/rest/api/content/{page_id}", json_body=data))

@mcp.tool()
def confluence_delete_page(page_id: str) -> str:
    """Confluence sayfasini siler."""
    return _json(_req(_confluence, "DELETE", f"/rest/api/content/{page_id}"))

@mcp.tool()
def confluence_get_spaces(limit: int = 25) -> str:
    """Confluence space listesini dondurur."""
    return _json(_req(_confluence, "GET", "/rest/api/space", params={"limit": limit}))

@mcp.tool()
def confluence_get_space(space_key: str) -> str:
    """Space detayini dondurur."""
    return _json(_req(_confluence, "GET", f"/rest/api/space/{space_key}", params={"expand": "description.plain"}))

@mcp.tool()
def confluence_get_page_children(page_id: str) -> str:
    """Sayfa alt sayfalarini (children) listeler."""
    return _json(_req(_confluence, "GET", f"/rest/api/content/{page_id}/child/page"))

@mcp.tool()
def confluence_get_page_comments(page_id: str) -> str:
    """Sayfa yorumlarini listeler."""
    return _json(_req(_confluence, "GET", f"/rest/api/content/{page_id}/child/comment", params={"expand": "body.storage"}))

@mcp.tool()
def confluence_add_page_comment(page_id: str, body_content: str) -> str:
    """Sayfaya yorum ekler."""
    data = {
        "type": "comment", "container": {"id": page_id, "type": "page"},
        "body": {"storage": {"value": body_content, "representation": "storage"}},
    }
    return _json(_req(_confluence, "POST", "/rest/api/content", json_body=data))

@mcp.tool()
def confluence_get_page_labels(page_id: str) -> str:
    """Sayfa etiketlerini dondurur."""
    return _json(_req(_confluence, "GET", f"/rest/api/content/{page_id}/label"))

@mcp.tool()
def confluence_add_page_label(page_id: str, label: str) -> str:
    """Sayfaya etiket ekler."""
    return _json(_req(_confluence, "POST", f"/rest/api/content/{page_id}/label", json_body=[{"name": label}]))

@mcp.tool()
def confluence_get_pages_in_space(space_key: str, limit: int = 25) -> str:
    """Space'teki sayfalari listeler."""
    return _json(_req(_confluence, "GET", "/rest/api/content",
                       params={"spaceKey": space_key, "type": "page", "limit": limit}))


# ===========================================================================
# BITBUCKET TOOLS (24 tool)
# ===========================================================================

# -- Projects & Repos --

@mcp.tool()
def bb_list_projects(limit: int = 25) -> str:
    """Bitbucket projelerini listeler."""
    return _json(_req(_bitbucket, "GET", "/rest/api/1.0/projects", params={"limit": limit}))

@mcp.tool()
def bb_list_repositories(project: str = "", limit: int = 25) -> str:
    """Repository listesini dondurur. project bos ise tum repo'lar."""
    if project:
        return _json(_req(_bitbucket, "GET", f"/rest/api/1.0/projects/{project}/repos", params={"limit": limit}))
    return _json(_req(_bitbucket, "GET", "/rest/api/1.0/repos", params={"limit": limit}))

# -- Branches --

@mcp.tool()
def bb_list_branches(project: str, repository: str, filter_text: str = "", limit: int = 25) -> str:
    """Repository branch listesini dondurur."""
    params: Dict[str, Any] = {"limit": limit}
    if filter_text: params["filterText"] = filter_text
    return _json(_req(_bitbucket, "GET", f"/rest/api/1.0/projects/{project}/repos/{repository}/branches", params=params))

@mcp.tool()
def bb_delete_branch(project: str, repository: str, branch: str) -> str:
    """Branch siler."""
    return _json(_req(_bitbucket, "DELETE", f"/rest/api/1.0/projects/{project}/repos/{repository}/branches",
                       json_body={"name": branch, "dryRun": False}))

# -- Commits --

@mcp.tool()
def bb_list_commits(project: str, repository: str, branch: str = "", limit: int = 25) -> str:
    """Commit gecmisini listeler."""
    params: Dict[str, Any] = {"limit": limit}
    if branch: params["until"] = branch
    return _json(_req(_bitbucket, "GET", f"/rest/api/1.0/projects/{project}/repos/{repository}/commits", params=params))

# -- Pull Requests --

@mcp.tool()
def bb_list_pull_requests(project: str, repository: str, state: str = "OPEN",
                          direction: str = "INCOMING", limit: int = 25) -> str:
    """PR listesini dondurur. state: OPEN, MERGED, DECLINED, ALL."""
    return _json(_req(_bitbucket, "GET", f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests",
                       params={"state": state, "direction": direction, "limit": limit}))

@mcp.tool()
def bb_get_pull_request(project: str, repository: str, pr_id: int) -> str:
    """Pull request detayini getirir."""
    return _json(_req(_bitbucket, "GET", f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pr_id}"))

@mcp.tool()
def bb_create_pull_request(project: str, repository: str, title: str,
                           source_branch: str, target_branch: str,
                           description: str = "", reviewers: str = "") -> str:
    """Yeni pull request olusturur. reviewers: virgul ile ayrilmis kullanici adlari."""
    body: Dict[str, Any] = {
        "title": title,
        "fromRef": {"id": f"refs/heads/{source_branch}", "repository": {"slug": repository, "project": {"key": project}}},
        "toRef": {"id": f"refs/heads/{target_branch}", "repository": {"slug": repository, "project": {"key": project}}},
    }
    if description: body["description"] = description
    if reviewers:
        body["reviewers"] = [{"user": {"name": r.strip()}} for r in reviewers.split(",")]
    return _json(_req(_bitbucket, "POST", f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests", json_body=body))

@mcp.tool()
def bb_update_pull_request(project: str, repository: str, pr_id: int,
                           title: str = "", description: str = "", reviewers: str = "") -> str:
    """PR baslik, aciklama veya reviewer gunceller."""
    pr = _req(_bitbucket, "GET", f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pr_id}")
    if title: pr["title"] = title
    if description: pr["description"] = description
    if reviewers:
        pr["reviewers"] = [{"user": {"name": r.strip()}} for r in reviewers.split(",")]
    return _json(_req(_bitbucket, "PUT", f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pr_id}",
                       json_body=pr))

@mcp.tool()
def bb_merge_pull_request(project: str, repository: str, pr_id: int, message: str = "") -> str:
    """Pull request'i merge eder."""
    pr = _req(_bitbucket, "GET", f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pr_id}")
    version = pr.get("version", 0) if pr else 0
    params: Dict[str, Any] = {"version": version}
    body = None
    if message:
        body = {"message": message}
    return _json(_req(_bitbucket, "POST", f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pr_id}/merge",
                       params=params, json_body=body))

@mcp.tool()
def bb_decline_pull_request(project: str, repository: str, pr_id: int) -> str:
    """Pull request'i reddeder."""
    pr = _req(_bitbucket, "GET", f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pr_id}")
    version = pr.get("version", 0) if pr else 0
    return _json(_req(_bitbucket, "POST", f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pr_id}/decline",
                       params={"version": version}))

@mcp.tool()
def bb_approve_pull_request(project: str, repository: str, pr_id: int) -> str:
    """Pull request'i onaylar."""
    return _json(_req(_bitbucket, "POST",
                       f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pr_id}/approve"))

@mcp.tool()
def bb_unapprove_pull_request(project: str, repository: str, pr_id: int) -> str:
    """Pull request onayini geri alir."""
    return _json(_req(_bitbucket, "DELETE",
                       f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pr_id}/approve"))

# -- PR Comments --

@mcp.tool()
def bb_get_pr_activities(project: str, repository: str, pr_id: int) -> str:
    """PR aktivite zaman cizelgesini getirir (yorumlar, review'lar, commit'ler)."""
    return _json(_req(_bitbucket, "GET",
                       f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pr_id}/activities",
                       params={"limit": 100}))

@mcp.tool()
def bb_get_pr_comments(project: str, repository: str, pr_id: int) -> str:
    """PR yorumlarini listeler."""
    return _json(_req(_bitbucket, "GET",
                       f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pr_id}/comments",
                       params={"limit": 100}))

@mcp.tool()
def bb_add_pr_comment(project: str, repository: str, pr_id: int, text: str) -> str:
    """Pull request'e yorum ekler."""
    return _json(_req(_bitbucket, "POST",
                       f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pr_id}/comments",
                       json_body={"text": text}))

# -- PR Diff --

@mcp.tool()
def bb_get_pr_diff(project: str, repository: str, pr_id: int, context_lines: int = 10) -> str:
    """Pull request diff'ini getirir."""
    return _json(_req(_bitbucket, "GET",
                       f"/rest/api/1.0/projects/{project}/repos/{repository}/pull-requests/{pr_id}/diff",
                       params={"contextLines": context_lines}))

# -- File Operations --

@mcp.tool()
def bb_get_file_content(project: str, repository: str, file_path: str,
                        branch: str = "", limit: int = 500) -> str:
    """Repository'deki dosya icerigini okur."""
    params: Dict[str, Any] = {"limit": limit}
    if branch: params["at"] = branch
    return _json(_req(_bitbucket, "GET",
                       f"/rest/api/1.0/projects/{project}/repos/{repository}/browse/{file_path}", params=params))

@mcp.tool()
def bb_browse_repository(project: str, repository: str, path: str = "", branch: str = "") -> str:
    """Repository dizin yapisini gosterir."""
    params: Dict[str, Any] = {"limit": 100}
    if branch: params["at"] = branch
    endpoint = f"/rest/api/1.0/projects/{project}/repos/{repository}/browse"
    if path: endpoint += f"/{path}"
    return _json(_req(_bitbucket, "GET", endpoint, params=params))

# -- Search --

@mcp.tool()
def bb_search(query: str, project: str = "", repository: str = "", limit: int = 25) -> str:
    """Bitbucket'ta kod ve dosya arar. project/repository ile daraltilabilir."""
    params: Dict[str, Any] = {"query": query, "limit": limit}
    if project: params["project"] = project
    if repository: params["repository"] = repository
    return _json(_req(_bitbucket, "GET", "/rest/search/1.0/search", params=params))

# -- Dashboard --

@mcp.tool()
def bb_get_dashboard_pull_requests(state: str = "OPEN", role: str = "", limit: int = 25) -> str:
    """Tum repository'lerdeki PR'lari listeler (dashboard). role: AUTHOR, REVIEWER, PARTICIPANT."""
    params: Dict[str, Any] = {"state": state, "limit": limit}
    if role: params["role"] = role
    return _json(_req(_bitbucket, "GET", "/rest/api/1.0/dashboard/pull-requests", params=params))

@mcp.tool()
def bb_get_default_branch(project: str, repository: str) -> str:
    """Repository'nin default branch'ini dondurur."""
    return _json(_req(_bitbucket, "GET",
                       f"/rest/api/1.0/projects/{project}/repos/{repository}/default-branch"))


# ===========================================================================
# Entry point
# ===========================================================================

def main():
    _init_clients()
    mcp.run()

if __name__ == "__main__":
    main()
