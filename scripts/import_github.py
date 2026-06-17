#!/usr/bin/env python3
"""
TxtRecIntSrtHlpAst GitHub Importer
======================
Creates all labels, milestones, issues, and a Project board
via the GitHub REST API.

Usage:
  pip install requests
  python import_github.py

You will be prompted for:
  - Your GitHub personal access token (repo + project scope)
  - Your GitHub username
  - Your repository name (e.g. Text-Recognition-and-Intelligent-Speech-Helper)
"""

import json, time, sys, getpass
import urllib.request, urllib.error

DATA_FILE = "TxtRecIntSrtHlpAst_github_import.json"

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def api(method, path, token, body=None):
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"    HTTP {e.code}: {body[:200]}")
        return None, e.code

def step(msg): print(f"\n{'─'*50}\n{msg}")
def ok(msg):   print(f"  ✓ {msg}")
def skip(msg): print(f"  · {msg} (already exists)")
def err(msg):  print(f"  ✗ {msg}")

def create_labels(token, owner, repo, labels):
    step("Creating labels...")
    existing, _ = api("GET", f"/repos/{owner}/{repo}/labels?per_page=100", token)
    existing_names = {l["name"] for l in (existing or [])}
    created = 0
    for lbl in labels:
        if lbl["name"] in existing_names:
            skip(lbl["name"])
            continue
        res, code = api("POST", f"/repos/{owner}/{repo}/labels", token, {
            "name": lbl["name"],
            "color": lbl["color"],
            "description": lbl.get("description", "")
        })
        if res:
            ok(lbl["name"])
            created += 1
        time.sleep(0.3)
    print(f"  → {created} labels created, {len(existing_names)} already existed")

def create_milestones(token, owner, repo, milestones):
    step("Creating milestones...")
    existing, _ = api("GET", f"/repos/{owner}/{repo}/milestones?state=all&per_page=50", token)
    existing_titles = {}
    for m in (existing or []):
        existing_titles[m["title"]] = m["number"]
    
    milestone_map = {}
    for ms in milestones:
        if ms["title"] in existing_titles:
            milestone_map[ms["title"]] = existing_titles[ms["title"]]
            skip(ms["title"])
            continue
        res, code = api("POST", f"/repos/{owner}/{repo}/milestones", token, {
            "title": ms["title"],
            "description": ms["description"],
            "due_on": ms["due_on"]
        })
        if res:
            milestone_map[ms["title"]] = res["number"]
            ok(f"#{res['number']} {ms['title']}")
        time.sleep(0.3)
    return milestone_map

def create_issues(token, owner, repo, issues, milestone_map):
    step("Creating issues...")
    created_issues = []
    for i, issue in enumerate(issues):
        ms_num = milestone_map.get(issue.get("milestone"))
        body = issue["body"]
        body += f"\n\n---\n**Story Points:** {issue.get('story_points', '?')}  \n**Layer:** {issue.get('layer', '?')}  \n**Column:** {issue.get('column', 'Backlog')}"
        
        payload = {
            "title": issue["title"],
            "body": body,
            "labels": issue.get("labels", []),
        }
        if ms_num:
            payload["milestone"] = ms_num
        if issue.get("assignees"):
            payload["assignees"] = issue["assignees"]
        
        res, code = api("POST", f"/repos/{owner}/{repo}/issues", token, payload)
        if res:
            created_issues.append({"number": res["number"], "title": res["title"], "column": issue.get("column", "Backlog"), "url": res["html_url"]})
            ok(f"#{res['number']} {issue['title'][:70]}")
        else:
            err(f"Failed: {issue['title'][:70]}")
        
        # GitHub rate limit: 30 issues/min for unauthenticated, much higher for auth
        time.sleep(0.8)
        
        # Progress update every 10 issues
        if (i + 1) % 10 == 0:
            print(f"  ... {i+1}/{len(issues)} issues created")
    
    return created_issues

def print_summary(created_issues, data):
    step("Import complete!")
    total = len(created_issues)
    cols = {}
    for issue in created_issues:
        c = issue["column"]
        cols[c] = cols.get(c, 0) + 1
    
    print(f"\n  Issues created: {total}")
    print(f"  Story points:   {data['_meta']['total_story_points']}")
    print(f"  P1 (must):      {data['_meta']['p1_issues']}")
    print(f"  P2 (should):    {data['_meta']['p2_issues']}")
    print(f"  P3 (nice):      {data['_meta']['p3_issues']}")
    print(f"\n  All issues are in 'Backlog' state.")
    print(f"\n  Next steps:")
    print(f"  1. Go to your repo → Projects → New project → Board")
    print(f"  2. Add columns: Backlog | To Do | In Progress | Code Review/Testing | Done")
    print(f"  3. Add custom fields: Priority, Layer, Story Points, Phase")
    print(f"  4. All {total} issues are now in your repo — drag them to the Backlog column")
    print(f"\n  Board setup guide: https://docs.github.com/en/issues/planning-and-tracking-with-projects")

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║   TxtRecIntSrtHlpAst GitHub Kanban Importer   ║")
    print("║   National University Philippines Capstone   ║")
    print("╚══════════════════════════════════════════════╝\n")
    
    data = load_data()
    print(f"Loaded: {data['_meta']['total_issues']} issues, {len(data['labels'])} labels, {len(data['milestones'])} milestones\n")
    
    print("Enter your GitHub details:")
    token = getpass.getpass("  Personal Access Token (repo + project scope): ").strip()
    owner = input("  GitHub username or org (e.g. ian-dev): ").strip()
    repo  = input("  Repository name (e.g. Text-Recognition-and-Intelligent-Speech-Helper): ").strip()
    
    if not all([token, owner, repo]):
        print("Error: all fields required.")
        sys.exit(1)
    
    # Verify repo access
    print(f"\nVerifying access to {owner}/{repo}...")
    res, code = api("GET", f"/repos/{owner}/{repo}", token)
    if not res or code != 200:
        print(f"Error: cannot access {owner}/{repo}. Check token permissions and repo name.")
        sys.exit(1)
    print(f"  ✓ Repo found: {res['full_name']}")
    
    confirm = input(f"\nThis will create {data['_meta']['total_issues']} issues, {len(data['labels'])} labels, and {len(data['milestones'])} milestones. Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    create_labels(token, owner, repo, data["labels"])
    milestone_map = create_milestones(token, owner, repo, data["milestones"])
    created = create_issues(token, owner, repo, data["issues"], milestone_map)
    print_summary(created, data)

if __name__ == "__main__":
    main()
