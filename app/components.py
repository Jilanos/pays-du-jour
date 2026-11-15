"""Numeric comparison components with one reading location for each indicator."""

from html import escape

from .charts import comparison_note
from .format import number, quantity, rounded


def reference(item, references):
    ref=item.get('france')
    if isinstance(ref,str):
        if ref not in references:
            raise ValueError(f'Unknown France reference: {ref}')
        return references[ref]
    return ref or {'status':'unavailable','reason':'Référence française non renseignée.','source_ids':[]}


def metric(item):
    value=item['value']; unit=item.get('unit','')
    if abs(value)>=1e9:
        val=rounded(value/1e9);unit='milliards '+unit
    elif abs(value)>=1e6:
        val=number(value/1e6,1,fixed=True)
        unit='millions d’habitants' if unit=='habitants' else 'millions '+unit
    else:
        val=rounded(value,item.get('precision'))
    return f'<strong>{val}</strong><span class="metric-unit">{escape(unit)}</span>'


def keyfacts(data, references, sources, country):
    out=['<div class="keyfacts">']
    for item in data.get('keyfacts',[]):
        ref=reference(item,references)
        anchor='fact-'+item['id']
        mark=sources.cite(anchor,item['label'],item.get('source_ids',[])+ref.get('source_ids',[]),
                          [item.get('note'),ref.get('note')])
        out.append(f'<section class="fact" id="{anchor}" aria-label="{escape(item["label"])}">'
                   f'<h3>{escape(item["label"])}{mark}</h3><div class="metric-pair">'
                   f'<div class="metric-country"><span class="country-label">{escape(country)}</span>'
                   f'{metric(item)}<small>{escape(item.get("coverage",str(item["year"])))}</small></div>')
        if ref.get('status')=='comparable':
            out.append(f'<div class="metric-france"><span class="country-label">France</span>'
                       f'{metric(ref)}<small>{escape(ref.get("coverage",str(ref["year"])))}</small></div>')
        else:
            out.append('<div class="metric-france"><span class="country-label">France</span>'
                       '<strong class="missing">'+('Non comparable' if ref['status']=='non_comparable' else 'Indisponible')
                       +'</strong><small>'+escape(ref['reason'])+'</small></div>')
        out.append('</div>')
        if ref.get('status')=='comparable':
            maxval=max(item['value'],ref['value']) or 1
            out.append(f'<div class="comparison-bars" aria-hidden="true"><i style="width:{item["value"]/maxval*100}%"></i>'
                       f'<i class="france" style="width:{ref["value"]/maxval*100}%"></i></div>')
        out.append('</section>')
    return ''.join(out)+'</div>'


def indices(data, references, sources, country):
    out=['<section class="indices" aria-labelledby="indices"><h2 id="indices">Lire les indices</h2>'
         '<p class="section-intro">Des repères sur le développement et les institutions. '
         'Chaque indice mesure une dimension différente.</p>']
    for item in data.get('indices',[]):
        ref=reference(item,references)
        anchor='index-'+item['id']
        mark=sources.cite(anchor,item['name'],item.get('source_ids',[])+ref.get('source_ids',[]))
        out.append(f'<div class="index-row" id="{anchor}"><div class="index-name">'
                   f'<span class="eyebrow">{escape(item.get("acronym",""))}</span>'
                   f'<h3>{escape(item["name"])}{mark}</h3>'
                   f'<small>{escape(item.get("coverage",""))}</small></div><div class="index-body">'
                   '<div class="index-values">')
        for rec,cls,label in [(item,'country',country),(ref,'france','France')]:
            out.append(f'<div class="index-{cls}"><span>{escape(label)}</span>')
            if rec is item or ref.get('status')=='comparable':
                out.append(f'<strong>{number(rec["value"],rec.get("precision",item["precision"]),fixed=True)}</strong>'
                           f'<small>{escape(str(rec["year"]))} · {escape(str(rec.get("rank","")))}</small>')
            else:
                out.append(f'<strong class="missing">Non comparable</strong><small>{escape(ref["reason"])}</small>')
            out.append('</div>')
        lo,hi=item['scale_min'],item['scale_max']
        pos=lambda value: (value-lo)/(hi-lo)*100
        out.append('</div><div class="index-scale" aria-hidden="true">'
                   f'<i class="country-dot" style="left:{pos(item["value"])}%"></i>')
        if ref.get('status')=='comparable':
            out.append(f'<i class="france-dot" style="left:{pos(ref["value"])}%"></i>')
        out.append(f'</div><div class="scale-labels"><span>{number(lo)}</span>'
                   f'<span>{"Plus égalitaire ←" if not item["higher_is_better"] else "Plus favorable →"}</span>'
                   f'<span>{number(hi)}</span></div></div>')
        if item.get('note_visible'):
            out.append(f'<p class="index-caveat">{escape(item["note_visible"])}</p>')
        out.append('</div>')
    return ''.join(out)+'</section>'
