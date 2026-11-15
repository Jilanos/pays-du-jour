Worktree: /home/paul/dev/pays-du-jour.wt/fiche-twn (branch fiche/twn of the personal repo pays-du-jour,
commit allowed, do not push, do not merge). You have network access: use it for research and downloads.
Read docs/brief.md, docs/format.md and templates/fiche.md first and follow docs/format.md exactly.

Task: write the pilot fiche for Taiwan (ISO3 TWN) in fiches/TWN/: fiche.md, data.json, assets/flag.svg,
and assets/relief.* (Taiwan's relief matters: central mountain range).

Reader: French engineer, 30, automotive industry, codes, does a lot of sport, likes techno music.
Language: French. Style: short declarative sentences, no "X, donc Y" justification, no "pas X mais Y",
no em-dashes. Factual, figures with year and source, indices (IDH, Gini, Democracy Index EIU or V-Dem,
RSF press freedom, Transparency International CPI). About 2 000 to 2 500 words (~10 minutes).

Content to cover (adapt to Taiwan):
- carte (locator, cities, relief placeholders), keyfacts box, climate and seasons (typhoons, monsoon,
  north/south contrast) with a monthly climate chart for Taipei and one for Kaohsiung;
- population: age pyramid (latest year), languages / ethnic groups share, religions share
  (folk religion, Buddhism, Taoism, Christianity...), ageing and very low fertility;
- way of life (night markets, scooters, work hours, housing cost, sport, nightlife and electronic music);
- wealth and disparities: median and mean wages, Gini, housing, urban/rural; charts;
- economy and resources: GDP by sector chart, exports structure, energy dependence (imports, nuclear
  phase-out debate), water for fabs; semiconductors as the country's phenomenon (TSMC, share of advanced
  nodes, "silicon shield") with a dedicated chart;
- main cities (6 cities in data.json with lat/lon/population and a one-line note each);
- history recap (Austronesians, Dutch/Qing, Japanese era 1895-1945, KMT 1949, martial law to 1987,
  democratisation), then the last 20 years in detail;
- political regime, recent leaders (presidents since 2000 and current premier), current dynamics:
  KMT/DPP/TPP balance, 2024 election and legislature, cross-strait pressure, US relations, recall votes,
  any 2025-2026 developments up to today (check the news, date them);
- culture and cuisine, religions, relations with France (frigates and Mirage sales, trade, office of
  representation), and a "le saviez-vous" if natural.
- Sources section: every source with URL and access date (World Bank does not cover Taiwan: use DGBAS,
  Taiwan Ministry of the Interior, Central Weather Administration, IMF WEO, CIA World Factbook, etc.).

Verify every figure against at least one primary or reputable source. Do not invent numbers; if a
figure is not found, drop it and say so in the final report.
Validate: data.json parses, every `{{chart:id}}` in fiche.md has a matching chart, arrays have the
right lengths, word count of fiche.md body.
Commits: subject `type[SCOPE]: message` (e.g. `new[MD/JSON/SVG]: Taiwan pilot fiche`), no AI attribution.
End with a short report: word count, charts list, figures dropped, doubts.
