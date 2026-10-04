#!/usr/bin/env python3
"""Fetch four genuine Toolforge random draws per inspiration batch."""
import concurrent.futures, datetime, html, json, pathlib, re, time, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'lore' / 'sources'
OUT.mkdir(parents=True, exist_ok=True)

def draw(batch, slot):
    category = 'People' if slot < 2 else 'History'
    query = urllib.parse.urlencode({'category': 'Wikipedia level-5 vital articles in ' + category,
        'server': 'en.wikipedia.org', 'cmnamespace': '', 'cmtype': '', 'returntype': 'subject',
        'lore_draw': f'{batch}-{slot}-{time.time_ns()}'})
    endpoint = 'https://randomincategory.toolforge.org/?' + query
    for attempt in range(5):
        try:
            request = urllib.request.Request(endpoint, headers={'User-Agent':'LoreResearch/1.0 (personal creative research)'})
            with urllib.request.urlopen(request, timeout=45) as response:
                url = response.url
                page = response.read().decode('utf-8')
            if 'en.wikipedia.org/' not in url:
                raise ValueError('Random service did not redirect to an article')
            title = html.unescape(re.search(r'<title>(.*?)</title>', page, re.S).group(1)).replace(' - Wikipedia','')
            url = 'https://en.wikipedia.org/wiki/' + urllib.parse.quote(title.replace(' ','_'))
            page = re.sub(r'<(script|style)\b.*?</\1>', '', page, flags=re.S)
            paras = re.findall(r'<p\b[^>]*>(.*?)</p>', page, re.S)
            clean = [html.unescape(re.sub('<[^>]+>', '', p)) for p in paras]
            clean = [re.sub(r'\[\d+\]', '', p).strip() for p in clean if len(p)>100]
            return {'batch':batch, 'slot':slot+1, 'category':category, 'title':title,
                    'url':url, 'random_endpoint':endpoint,
                    'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'research_excerpt':'\n\n'.join(clean)[:16000]}
        except Exception as error:
            if attempt == 4: return {'batch':batch,'slot':slot+1,'error':str(error)}
            time.sleep(1+attempt)

def main(start, count):
    jobs = [(b,s) for b in range(start,start+count) for s in range(4)
            if not (OUT / f'batch-{b:03d}.json').exists()]
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        future_jobs = {pool.submit(draw,b,s):(b,s) for b,s in jobs}
        for future in concurrent.futures.as_completed(future_jobs):
            item = future.result(); b = item['batch']
            results.setdefault(b,[]).append(item)
            if len(results[b]) == 4:
                items = sorted(results[b],key=lambda i:i['slot'])
                if any('error' in i for i in items):
                    print('FAILED',b,items,flush=True)
                else:
                    (OUT / f'batch-{b:03d}.json').write_text(json.dumps(items,indent=2,ensure_ascii=False))
                    print(b, ' | '.join(i['title'] for i in items),flush=True)

if __name__ == '__main__':
    import sys
    main(int(sys.argv[1]), int(sys.argv[2]))
