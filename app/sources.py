"""A discreet citation per reading block, a single bibliography with return links."""

from collections import defaultdict
from html import escape

from markdown_it import MarkdownIt

from .format import date_fr


class Sources:
    def __init__(self, records, checked):
        self.records = {r['id']: r for r in records}
        self.checked = checked
        self.uses = defaultdict(list)
        self.notes = defaultdict(list)
        self.md = MarkdownIt('commonmark', {'html': False})
        self.citations = set()

    def cite(self, anchor, label, ids, notes=()):
        ids = list(dict.fromkeys(ids))
        if not ids:
            return ''
        if anchor in self.citations:
            raise ValueError(f'Duplicate citation anchor: {anchor}')
        self.citations.add(anchor)
        for source_id in ids:
            if source_id not in self.records:
                raise ValueError(f'Unknown source {source_id} in {anchor}')
            self.uses[source_id].append((anchor, label, ids))
        for note in notes:
            if note and note not in self.notes[ids[0]]:
                self.notes[ids[0]].append(note)
        return (f'<sup class="source-marker"><a href="#ref-{escape(anchor)}" '
                f'aria-label="Sources : {escape(label, quote=True)}">·</a></sup>')

    def render(self):
        displayed = [key for key in self.records if key in self.uses]
        numbers = {key: i + 1 for i, key in enumerate(displayed)}
        out = [f'<section class="sources" aria-labelledby="sources"><h2 id="sources">Sources</h2>'
               f'<p class="source-intro">Consultées le {date_fr(self.checked)}. '
               'Les liens de retour retrouvent le passage ou la figure.</p><ol class="source-list">']
        # Unused source records are excluded, so every displayed entry has a return path.
        for source_id, source in self.records.items():
            if source_id not in self.uses:
                continue
            anchors = ''.join(f'<span class="source-target" id="ref-{escape(a)}"></span>'
                              for a, _, ids in self.uses[source_id] if ids[0] == source_id)
            out.append(f'<li id="src-{escape(source_id)}">{anchors}'
                       f'{self.md.renderInline(source["text"])}')
            for note in self.notes[source_id]:
                out.append(f'<p class="source-note">{escape(note)}</p>')
            out.append('<div class="backlinks">')
            for anchor, label, ids in self.uses[source_id]:
                out.append(f'<a href="#{escape(anchor)}">↩ {escape(label)}</a>')
                if ids[0] == source_id and len(ids) > 1:
                    out.append('<span class="related-sources">Avec ' + ', '.join(
                        f'<a href="#src-{escape(s)}">{numbers[s]}</a>'
                        for s in ids[1:]) + '</span>')
            out.append('</div></li>')
        out.append('</ol></section>')
        return ''.join(out)
