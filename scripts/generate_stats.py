import json
import os
import urllib.request
from xml.sax.saxutils import escape

USERNAME = "Sarveshero3"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

def gh_get(url, accept="application/vnd.github+json"):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}" if TOKEN else "",
        "Accept": accept,
        "User-Agent": USERNAME,
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

try:
    user = gh_get(f"https://api.github.com/users/{USERNAME}")
    public_repos = user.get("public_repos", 0)
    followers = user.get("followers", 0)
except Exception as e:
    print("user fetch failed:", e)
    public_repos, followers = 0, 0

try:
    commits_data = gh_get(f"https://api.github.com/search/commits?q=author:{USERNAME}",
                           accept="application/vnd.github.cloak-preview+json")
    total_commits = commits_data.get("total_count", 0)
except Exception as e:
    print("commit search failed:", e)
    total_commits = 0

try:
    repos = gh_get(f"https://api.github.com/users/{USERNAME}/repos?sort=created&direction=desc&per_page=1")
    latest_repo = repos[0]["name"] if repos else "-"
except Exception as e:
    print("repos fetch failed:", e)
    latest_repo = "-"

print("RESULTS:", public_repos, total_commits, followers, latest_repo)

stats = [
    ("PUBLIC REPOS", str(public_repos), "#60a5fa"),
    ("TOTAL COMMITS", f"{total_commits:,}", "#34d399"),
    ("FOLLOWERS", str(followers), "#4ade80"),
    ("LATEST REPO", latest_repo, "#facc15"),
]

W = 1200
GAP = 14
MARGIN = 48
CARD_W = (W - MARGIN*2 - GAP*3) / 4
CARD_H = 120

cards = []
for i, (label, value, color) in enumerate(stats):
    x = MARGIN + i * (CARD_W + GAP)
    label_e = escape(label)
    value_e = escape(str(value))
    fs = 30 if len(str(value)) <= 10 else (22 if len(str(value)) <= 16 else 16)
    cards.append(f'''
  <g>
    <clipPath id="clip{i}"><rect x="{x:.1f}" y="0" width="{CARD_W:.1f}" height="{CARD_H}" rx="14"/></clipPath>
    <rect x="{x:.1f}" y="0" width="{CARD_W:.1f}" height="{CARD_H}" rx="14" fill="{color}" fill-opacity="0.08" stroke="{color}" stroke-opacity="0.4" stroke-width="1"/>
    <rect x="{x-70:.1f}" y="0" width="70" height="{CARD_H}" fill="{color}" opacity="0.16" clip-path="url(#clip{i})">
      <animate attributeName="x" from="{x-70:.1f}" to="{x+CARD_W:.1f}" dur="3.2s" begin="{i*0.45:.2f}s" repeatCount="indefinite"/>
    </rect>
    <text x="{x+CARD_W/2:.1f}" y="58" text-anchor="middle" font-family="Fira Code, monospace" font-size="{fs}" font-weight="700" fill="{color}">{value_e}</text>
    <text x="{x+CARD_W/2:.1f}" y="88" text-anchor="middle" font-family="Fira Code, monospace" font-size="11" letter-spacing="1.5" fill="{color}" opacity="0.8">{label_e}</text>
  </g>''')

svg = f'''<svg viewBox="0 0 {W} {CARD_H}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGrad3" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06120f"/>
      <stop offset="55%" stop-color="#071a16"/>
      <stop offset="100%" stop-color="#06120f"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{CARD_H}" fill="url(#bgGrad3)"/>
  {''.join(cards)}
</svg>'''

with open("stats.svg", "w") as f:
    f.write(svg)
print("stats.svg written")
