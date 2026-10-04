#!/usr/bin/env python3
"""Build compact browse indexes and an honest repetition/provenance audit."""
import collections,json,pathlib,re,statistics
from build_wiki import words
ROOT=pathlib.Path(__file__).resolve().parents[1]; L=ROOT/'lore'
cycles=[json.loads(p.read_text()) for p in sorted((L/'cycles').glob('*.json'))]
entries=[e for c in cycles for e in c['entries']]
for directory in ['regions','types']:(L/directory).mkdir(exist_ok=True)
regional=json.loads((L/'region-notes.json').read_text())
index='# Regions of Sere\n\n[World bible](../world-bible.md) · [Reading paths](../reading-paths.md)\n\n'
for region,note in regional.items():
    selected=[e for e in entries if region in [s.strip() for s in e['region'].replace(' and ', ',').split(',')]]
    slug=region.lower(); index+=f"- [{region}]({slug}.md) — {len(selected)} articles\n"
    content=f'# {region}\n\n'+note+'\n\n## Histories and inhabitants\n\n'
    content+='\n'.join(f"- [{e['title']}](../entries/{e['id']}.md) — {e['kind']}; {e['date']} AFR" for e in selected)
    content+='\n\n[All regions](index.md) · [All entries](../index.md)\n'
    (L/'regions'/f'{slug}.md').write_text(content)
(L/'regions'/'index.md').write_text(index)
types=collections.defaultdict(list)
for e in entries:types[e['kind']].append(e)
idx='# Browse by kind of entry\n\n'
for kind,items in sorted(types.items()):
    slug=re.sub('[^a-z0-9]+','-',kind.lower()).strip('-')
    idx+=f'- [{kind}]({slug}.md) — {len(items)} articles\n'
    (L/'types'/f'{slug}.md').write_text(f'# {kind}\n\n'+ '\n'.join(f"- [{e['title']}](../entries/{e['id']}.md) — {e['region']}; {e['date']} AFR" for e in items)+'\n\n[All kinds](index.md)\n')
(L/'types'/'index.md').write_text(idx)
def year(c):
    nums=[int(m.group()) for e in c['entries'] if (m:=re.search(r'\d+',e['date'])) and not e['date'].startswith('Before')]
    return min(nums,default=-1)
history='# Dated local histories\n\nThe date marks a cycle’s earliest recorded coverage, not every participant’s birth. The [chronology](chronology.md) distinguishes basin-wide periods.\n\n'
for c in sorted(cycles,key=year):
    first=c['entries'][0]
    history+=f"## {year(c)} AFR — {c['title']}\n\n{c['summary']}\n\nBegin with [{first['title']}](entries/{first['id']}.md).\n\n"
(L/'historical-index.md').write_text(history)
paragraphs=collections.Counter(); para_words={}
for e in entries:
    for p in (e['body']+'\n\n'+e.get('background','')).split('\n\n'):
        p=p.strip()
        if p:paragraphs[p]+=1; para_words[p]=words(p)
repeated=sum((n-1)*para_words[p] for p,n in paragraphs.items() if n>1)
total=sum(words(e['body']+' '+e.get('background','')) for e in entries)
sources=[a for p in sorted((L/'sources').glob('batch-*.json')) for a in json.loads(p.read_text())]
titles=collections.Counter(a['title'] for a in sources)
graph={e['id']:set(e.get('links',[])) for e in entries}
for node,links in list(graph.items()):
    for target in links:graph.setdefault(target,set()).add(node)
seen=set(); components=[]
for node in graph:
    if node in seen:continue
    stack=[node]; size=0
    while stack:
        cur=stack.pop()
        if cur in seen:continue
        seen.add(cur);size+=1;stack.extend(graph[cur]-seen)
    components.append(size)
report={'entries':len(entries),'source_draws':len(sources),'distinct_source_articles':len(titles),
        'repeated_draws':{t:n for t,n in titles.items() if n>1},
        'narrative_words_including_shared_context':total,
        'exact_repeated_paragraph_words_beyond_first_occurrence':repeated,
        'exact_repetition_fraction':round(repeated/total,4),
        'connected_components_undirected':components,
        'original_full_prose_entries':sum(len(c['entries']) for c in cycles if c.get('draft_method') is None),
        'structured_draft_entries':sum(len(c['entries']) for c in cycles if c.get('draft_method') is not None)}
(L/'editorial-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps(report,indent=2,ensure_ascii=False))
