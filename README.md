# The Testament of Sere

A pre-industrial dark fantasy world in which the dead retain enforceable claims upon water, land, and the names of the living. Its oldest institutions are bargains with ancestors; its great disasters are often failures of administration before they become supernatural catastrophes.

Begin with the [reading paths](lore/reading-paths.md), [world bible](lore/world-bible.md), [regions](lore/regions/index.md), or [entry index](lore/index.md). The [connected history](lore/world-history.md), [chronology](lore/chronology.md), and [dated histories](lore/historical-index.md) connect its periods. The [inspiration register](lore/sources/index.md) records the actual random articles used. Historical inspiration supplies mechanisms and contradictions, rather than transplanted peoples or disguised copies of real atrocities.

The library uses ordinary relative Markdown links. It can be read in a text editor, GitHub, or a local Markdown knowledge base without a build step. Entries contain settled facts, disputed testimony, and present consequences; a disagreement in testimony does not silently change the underlying chronology.

## Working files

- `lore/entries/`: individual lore articles.
- `lore/cycles/`: authored source transformations and connected narrative records.
- `lore/dossiers/`: individually authored premises and shared histories for the structured articles.
- `lore/sources/`: research draws, source links, and notes.
- `tools/build_wiki.py`: render authored records and validate links, provenance batches, and article lengths.
- `tools/build_navigation.py`: rebuild regional, historical, and type indexes and the editorial audit.
- `tools/draft_cycles.py`: render the structured dossiers into cycle records.
- `tools/fetch_sources.py`: collect fresh batches of two People and two History articles through the requested Toolforge service.

The current age is year 1248 After the First Reckoning. The detailed history spans earlier unwritten ages and twelve centuries of recorded agreements, settlements, migrations, and failures. There is no industrial production, fossil-fuel economy, modern weaponry, or technological shortcut disguised as magic.

## Draft status

The library has more than 1,000 linked articles, each containing at least 300 narrative words. It is a **structured first draft**: most articles combine an individually authored premise with recurring role analysis, shared cycle history, and regional context. The fuller early river cycle, foundational canon, and cross-regional histories are written as independent prose. The total word count includes repeated passages; it is not a count of unique original prose. See the [editorial audit](lore/editorial-audit.json) for the actual repetition and source statistics.

The next editorial work is to replace recurring structural passages with entry-specific scenes and evidence, deepen motives beyond the repeated patron–worker conflict, and test more cross-regional consequences. The [editorial notes](lore/editorial-notes.md) state the delivery counts, limitations, and revision priorities. The saved dossiers make that revision possible without inventing fresh source provenance or losing chronology.

To regenerate after editing dossiers or independently authored cycle records:

```sh
python3 tools/draft_cycles.py && python3 tools/build_navigation.py && python3 tools/build_wiki.py
```

Edit the records rather than generated entry Markdown when a change should survive regeneration. Source JSON files preserve the research cache; source Markdown contains the selected transformations. New source collection requires network access, while rendering the saved library uses Python's standard library and works offline.
