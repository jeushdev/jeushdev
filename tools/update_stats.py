"""Refresh visible GitHub statistics and calendar. Standard library only."""
import html
import json
import os
import re
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / 'assets/profile'
USER = 'jeushdev'

def fetch(url, api=False):
    headers = {'User-Agent':'jeushdev-profile-stats'}
    if api and os.getenv('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as response:
        return response.read().decode('utf-8')

profile = json.loads(fetch(f'https://api.github.com/users/{USER}',True))
repos, page = [], 1
while True:
    batch = json.loads(fetch(f'https://api.github.com/users/{USER}/repos?per_page=100&type=owner&page={page}',True))
    repos.extend(repo for repo in batch if not repo.get('private',False))
    if len(batch) < 100:
        break
    page += 1
calendar = fetch(f'https://github.com/users/{USER}/contributions')
match = re.search(r'([\d,]+)\s+contributions\s+in the last year',calendar)
if not match:
    raise ValueError('Contribution total missing; preserve previous snapshot.')
days = [{'date':d,'level':int(level)} for d,level in re.findall(r'<td\b[^>]*data-date="([\d-]+)"[^>]*data-level="([0-4])"',calendar)]
if len(days) < 300:
    raise ValueError('Incomplete contribution calendar; preserve previous snapshot.')
snapshot = {
    'updated_at':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
    'contributions_last_year':int(match.group(1).replace(',','')),
    'public_repositories':profile['public_repos'],
    'followers':profile['followers'],
    'stars_on_public_repositories':sum(repo['stargazers_count'] for repo in repos),
    'source_urls':[f'https://api.github.com/users/{USER}',f'https://api.github.com/users/{USER}/repos',f'https://github.com/users/{USER}/contributions'],
    'scope':'Visible calendar follows account public settings; repository and star counts are public only.',
    'days':sorted(days,key=lambda d:d['date'])
}

def text(value,x,y,size=16,color='#eeece6'):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="monospace" font-size="{size}">{html.escape(str(value))}</text>'

for mobile in (False,True):
    w,h = (720,400) if mobile else (1200,320)
    parts = [f'<rect width="{w}" height="{h}" fill="#080808"/>']
    metrics = [('CONTRIBUTIONS / YEAR',snapshot['contributions_last_year']),('PUBLIC REPOS',snapshot['public_repositories']),('FOLLOWERS',snapshot['followers']),('PUBLIC REPO STARS',snapshot['stars_on_public_repositories'])]
    for i,(label,value) in enumerate(metrics):
        x = 32 + (i%2)*346 if mobile else 44+i*290
        y = 66 + (i//2)*112 if mobile else 70
        parts.append(text(f'{value:,}',x,y,48))
        parts.append(text(label,x,y+29,22 if mobile else 15,'#a8b0ad'))
    start = date.fromisoformat(snapshot['days'][0]['date'])
    step,unit = (12,9) if mobile else (20,15)
    top = 260 if mobile else 133
    colors = ['#1b2421','#46564c','#7a9282','#b4c7bb','#eeece6']
    for day in snapshot['days']:
        current = date.fromisoformat(day['date'])
        col,row = (current-start).days//7,(current.weekday()+1)%7
        parts.append(f'<rect x="{32+col*step}" y="{top+row*step}" width="{unit}" height="{unit}" fill="{colors[day["level"]]}"/>')
    parts.append(text('UPDATED ' + snapshot['updated_at'][:10]+' / github.com/jeushdev',32,h-20,22 if mobile else 15,'#a8b0ad'))
    label = f'GitHub snapshot: {snapshot["contributions_last_year"]:,} contributions in the last year, {snapshot["public_repositories"]} public repositories, {snapshot["followers"]} followers, {snapshot["stars_on_public_repositories"]} stars on public repositories.'
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(label)}"><title>{html.escape(label)}</title>'+''.join(parts)+'</svg>\n'
    (OUT / ('activity-mobile.svg' if mobile else 'activity.svg')).write_text(svg,encoding='utf-8')
(OUT / 'stats.json').write_text(json.dumps(snapshot,indent=2)+'\n',encoding='utf-8')
readme = OUT.parents[1] / 'README.md'
alt = f'GitHub activity: {snapshot["contributions_last_year"]:,} contributions in the last year; {snapshot["public_repositories"]} public repositories; {snapshot["followers"]} followers; {snapshot["stars_on_public_repositories"]} public repository star. Snapshot {snapshot["updated_at"][:10]}. Contribution calendar follows.'
content = readme.read_text(encoding='utf-8')
content, count = re.subn(r'alt="GitHub activity:[^"]*"', 'alt="' + html.escape(alt) + '"', content)
if count != 1:
    raise ValueError('Expected one activity image alt in README.')
readme.write_text(content,encoding='utf-8')
print(json.dumps({k:v for k,v in snapshot.items() if k not in ('days','source_urls','scope')}))
