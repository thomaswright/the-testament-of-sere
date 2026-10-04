#!/usr/bin/env python3
"""Render explicitly authored lore records and audit the Markdown graph."""
import collections, json, pathlib, re, sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
LORE=ROOT/'lore'
def words(text):
    text=re.sub(r'\[[^\]]*\]\([^)]*\)', lambda m:m.group(0).split(']')[0][1:],text)
    return len(re.findall(r"\b[\w]+(?:['’-][\w]+)*\b",text))

def build():
    cycles=[json.loads(p.read_text()) for p in sorted((LORE/'cycles').glob('*.json'))]
    records=[dict(e,cycle=c) for c in cycles for e in c['entries']]
    by_id={e['id']:e for e in records}
    if len(by_id)!=len(records): raise ValueError('Duplicate entry id')
    referrers=collections.defaultdict(list)
    for record in records:
        for target in record.get('links',[]):referrers[target].append(record)
    failures=[]
    if len(records)<1000: failures.append('Fewer than 1,000 entries')
    for e in records:
        c=e['cycle']; name=e['id']+'.md'
        prose=e['body']
        # Shared regional context remains explicit in the authored draft records.
        if e.get('background'): prose+='\n\n'+e['background']
        related=e.get('links',[])
        links=[]
        for target in related:
            if target not in by_id: failures.append(f"{e['id']}: missing target {target}")
            else: links.append(f"[{by_id[target]['title']}]({target}.md)")
        text=f"# {e['title']}\n\n*{e['kind']} · {e['region']} · Historical coverage: {e['date']} AFR*\n\n{prose}\n\n"
        if links:text+='## Connected entries\n\n'+ ' · '.join(links)+'\n\n'
        back=referrers[e['id']]
        if back:
            text+='## Referenced by\n\n'+' · '.join(f"[{r['title']}]({r['id']}.md)" for r in back)+'\n\n'
        batches=e.get('inspiration_batches',[c['batch']])
        refs=' · '.join(f"[Source batch {b:03d}](../sources/batch-{b:03d}.md)" for b in batches)
        text+=f"## Inspiration\n\n{refs}. {e['inspiration']}\n\n[All entries](../index.md) · [World bible](../world-bible.md)\n"
        (LORE/'entries'/name).write_text(text)
        count=words(prose)
        if count<300:failures.append(f"{e['id']}: {count} narrative words (minimum 300)")
    idx='# Lore entry index\n\n'+f"{len(records):,} articles. Dates use the common Reckoning; the present is 1248.\n\n[Reading paths](reading-paths.md) · [Regions](regions/index.md) · [Dated histories](historical-index.md) · [Kinds of entry](types/index.md)\n\n"
    for c in cycles:
        idx+=f"## {c['title']}\n\n{c['summary']}\n\n"
        for e in c['entries']:
            idx+=f"- [{e['title']}](entries/{e['id']}.md) — {e['kind']}, {e['region']}, {e['date']} AFR\n"
        idx+='\n'
    for batch in sorted({c['batch'] for c in cycles}):
        group=[c for c in cycles if c['batch']==batch]
        c=group[0]
        sources=json.loads((LORE/'sources'/f"batch-{batch:03d}.json").read_text())
        src=f"# Inspiration batch {c['batch']:03d}: {c['title']}\n\nThese four articles were drawn through the requested Toolforge categories. The lore transforms selected mechanisms; it does not reproduce the historical societies or claim historical equivalence.\n\n"
        for a,note in zip(sources,c['source_notes']):
            src+=f"## [{a['title']}]({a['url']})\n\nCategory: {a['category']}.\n\n{note}\n\n"
        for extra in group[1:]:
            src+=f"## Additional synthesis: {extra['title']}\n\n{extra['summary']}\n\n"
        src+='## Resulting entries\n\n'+'\n'.join(f"- [{e['title']}](../entries/{e['id']}.md)" for g in group for e in g['entries'])+'\n'
        (LORE/'sources'/f"batch-{c['batch']:03d}.md").write_text(src)
    (LORE/'index.md').write_text(idx)
    unique={}
    for c in cycles:unique.setdefault(c['batch'],c)
    (LORE/'sources'/'index.md').write_text('# Inspiration register\n\n'+ '\n'.join(f"- [Batch {b:03d}: {c['title']}](batch-{b:03d}.md)" for b,c in sorted(unique.items()))+'\n')
    incoming=collections.Counter(t for e in records for t in e.get('links',[]))
    isolated=[e['id'] for e in records if not incoming[e['id']] and not e.get('links')]
    for p in [ROOT/'README.md', *LORE.rglob('*.md')]:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in target or target.startswith('#'):continue
            if not (p.parent/target.split('#')[0]).exists(): failures.append(f'{p.name}: broken link {target}')
    counts=[words(e['body']+' '+e.get('background','')) for e in records]
    for batch in sorted(unique):
        source_records=json.loads((LORE/'sources'/f'batch-{batch:03d}.json').read_text())
        categories=collections.Counter(a['category'] for a in source_records)
        if len(source_records)!=4 or categories!={'People':2,'History':2}:
            failures.append(f'Batch {batch:03d}: expected two People and two History sources')
    report={'entries':len(records),'narrative_words':sum(counts),'minimum_words':min(counts,default=0),
            'directed_connections':sum(len(e.get('links',[])) for e in records),
            'source_batches':len(unique),'story_cycles':len(cycles),'isolated_entries':isolated,'failures':failures}
    (LORE/'validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    return not failures

if __name__=='__main__':sys.exit(0 if build() else 1)
