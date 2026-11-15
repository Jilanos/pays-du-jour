"""Read the fiche contract, resolving numeric records and citation round-trips."""

import csv
import json
import re
import unicodedata
from dataclasses import dataclass
from html import escape
from urllib.parse import quote

import yaml
from markdown_it import MarkdownIt
from markdown_it.token import Token
from markupsafe import Markup

from .charts import render_chart
from .components import indices, keyfacts, reference
from .config import ROOT, Settings
from .format import record
from .maps import cities, locator
from .sources import Sources
from .typo import french

PLACEHOLDER = re.compile(r'^\s*\{\{(sources|keyfacts|chart:[\w-]+|map:(?:locator|cities|relief))\}\}\s*$')
CITATION = re.compile(r'\s*\{#([\w-]+) sources="([\w, -]+)" label="([^"]+)"\}\s*$')
VALUE = re.compile(r'\{\{value:([\w-]+)\}\}')
ISO3 = re.compile(r'[A-Z]{3}\Z')


def placeholder_block(state, start_line, end_line, silent):
    if state.sCount[start_line] - state.blkIndent >= 4:
        return False
    line = state.src[state.bMarks[start_line] + state.tShift[start_line]:state.eMarks[start_line]]
    match = PLACEHOLDER.fullmatch(line)
    if not match:
        return False
    if not silent:
        token = state.push('fiche_placeholder', '', 0)
        token.content = match[1]
        token.map = [start_line, start_line + 1]
        state.line = start_line + 1
    return True


@dataclass
class Fiche:
    meta: dict
    html: Markup
    toc: list[tuple[str,str]]
    flag: bool
    locator: Markup
    hero_marker: Markup


def alphabetical(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.casefold())
                   if not unicodedata.combining(c))


def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', alphabetical(value)).strip('-') or 'section'


def country_list(settings: Settings):
    with settings.order_path.open(encoding='utf-8-sig', newline='') as stream:
        countries = list(csv.DictReader(stream))
    directory = ROOT / 'data/countries.json'
    identities = json.loads(directory.read_text()) if directory.exists() else {}
    for country in countries:
        country['available'] = (settings.content_dir / country['iso3'] / 'fiche.md').is_file()
        country.update(identities.get(country['iso3'], {}))
    return countries


def read_fiche(iso3: str, settings: Settings) -> Fiche:
    if not ISO3.fullmatch(iso3):
        raise FileNotFoundError(iso3)
    folder = settings.content_dir / iso3
    raw = (folder / 'fiche.md').read_text(encoding='utf-8')
    parts = re.split(r'^---\s*$', raw, maxsplit=2, flags=re.MULTILINE)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError(f'{iso3}: expected YAML front matter')
    meta = yaml.safe_load(parts[1])
    if meta['iso3'] != iso3:
        raise ValueError(f'{iso3}: front matter ISO3 mismatch')
    data = json.loads((folder / 'data.json').read_text(encoding='utf-8'))
    references = json.loads((ROOT / 'data/reference/FRA.json').read_text())
    sources = Sources(data.get('sources', []) + references['sources'], meta['date_donnees'])
    charts = {chart['id']: chart for chart in data.get('charts', [])}
    hero_marker = sources.cite('identite','Identité et drapeau',data.get('hero_sources', []))
    map_marker = sources.cite('situation','Situation régionale',data.get('map_sources', {}).get('locator', []))
    hero_map = locator(iso3, meta['nom'], settings.geo_dir, marker=map_marker)
    md = MarkdownIt('commonmark', {'html': False}).enable('table')
    md.block.ruler.before('paragraph', 'fiche_placeholder', placeholder_block,
                          {'alt': ['paragraph','reference','blockquote','list']})
    tokens = md.parse(parts[2])
    toc, counts, citation_ids = [], {}, set()
    for index, token in enumerate(tokens):
        if token.type == 'inline':
            content = VALUE.sub(lambda m: record(data['prose_values'][m[1]]),token.content)
            citation=CITATION.search(content)
            marker=''
            if citation:
                anchor, ids, label=citation.groups()
                if anchor in citation_ids:
                    raise ValueError(f'Duplicate paragraph anchor: {anchor}')
                citation_ids.add(anchor)
                tokens[index-1].attrSet('id',anchor)
                marker=sources.cite(anchor,label,[s.strip() for s in ids.split(',')])
                content=content[:citation.start()]
            token.children=md.parseInline(content)[0].children
            for child in token.children or []:
                if child.type=='text':child.content=french(child.content)
            if marker:
                extra=Token('html_inline','',0);extra.content=marker
                token.children.append(extra)
            previous=tokens[index-1]
            if previous.type=='heading_open':
                if previous.tag=='h1':
                    raise ValueError('The fiche hero owns the only H1; use H2 in Markdown')
                title=''.join(c.content for c in token.children or [] if c.type in ('text','code_inline'))
                base=slug(title);counts[base]=counts.get(base,0)+1
                anchor=base if counts[base]==1 else f'{base}-{counts[base]}'
                previous.attrSet('id',anchor)
                if previous.tag=='h2':toc.append((anchor,title))
                if title.startswith('Le saviez'):
                    previous.attrSet('class','curiosity-heading')
            if content.startswith('**') and re.match(r'^\*\*\d{4}',content):
                previous.attrSet('class','timeline-entry')
        if token.type != 'fiche_placeholder':continue
        key=token.content
        if key=='sources':continue  # Render only after every citation is collected.
        if key=='keyfacts':
            rendered=keyfacts(data,references,sources,meta['nom'])+indices(data,references,sources,meta['nom'])
            toc.append(('indices','Lire les indices'))
        elif key.startswith('chart:'):
            chart=charts[key[6:]].copy();ref=reference(chart,references);chart['_france']=ref
            marker=sources.cite('fig-'+chart['id'],chart['title'],
                chart.get('source_ids',[])+ref.get('source_ids',[]),[chart.get('note')])
            rendered=render_chart(chart,marker)
        elif key=='map:locator':
            raise ValueError('The locator belongs to the hero; remove its body placeholder')
        elif key=='map:cities':
            mark=sources.cite('villes','Villes principales',data.get('map_sources',{}).get('cities',[]))
            rendered=cities(iso3,meta['nom'],data.get('cities',[]),settings.geo_dir,marker=mark)
        else:
            relief=next((p for ext in ('jpg','jpeg','png','webp','svg')
                         if (p:=folder/'assets'/f'relief.{ext}').is_file()),None)
            rendered=''
            if meta.get('relief_pertinent') and relief:
                mark=sources.cite('relief','Relief de l’île',data.get('map_sources',{}).get('relief',[]))
                rendered=(f'<figure id="relief" class="graphic relief"><h3>Une île de montagnes{mark}</h3>'
                          f'<img src="/pays/{iso3}/assets/{quote(relief.name)}" '
                          f'alt="Relief de {escape(meta["nom"])} : montagnes au centre et à l’est, plaines à l’ouest." '
                          'loading="lazy"></figure>')
        token.type,token.content,token.children='html_block',rendered,None
    for token in tokens:
        if token.type=='fiche_placeholder' and token.content=='sources':
            token.type,token.content,token.children='html_block',sources.render(),None
            toc.append(('sources','Sources'))
    html=md.renderer.render(tokens,md.options,{})
    # Markdown tables get a keyboard-accessible local scroll region, never page overflow.
    html=html.replace('<table>','<div class="table-wrap" role="region" aria-label="Tableau" tabindex="0"><table>')
    html=html.replace('</table>\n','</table></div>\n')
    return Fiche(meta,Markup(html),toc,(folder/'assets/flag.svg').is_file(),
                 Markup(hero_map),Markup(hero_marker))
