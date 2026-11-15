"""Accessible HTML charts and responsive server-rendered SVG plots."""

from html import escape
from math import ceil, floor, isfinite, log10
from xml.etree.ElementTree import Element, SubElement, tostring

from .format import number, quantity

COLORS = [f'var(--cat-{i})' for i in range(1, 7)]
MONTHS = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']


def el(parent, tag, **attrs):
    return SubElement(parent, tag, {k.removesuffix('_').replace('_', '-'): str(v)
                                  for k, v in attrs.items()})


def text(parent, x, y, value, **attrs):
    node = el(parent, 'text', x=x, y=y, **attrs)
    node.text = str(value)
    return node


def finish(root):
    return tostring(root, encoding='unicode')


def svg(chart, width=720, height=350):
    root = Element('svg', {'xmlns': 'http://www.w3.org/2000/svg',
                          'viewBox': f'0 0 {width} {height}', 'role': 'img', 'class': 'chart'})
    SubElement(root, 'title').text = chart['title']
    SubElement(root, 'desc').text = chart.get('description',
        'Valeurs et libellés complets dans « Voir les données », après le graphique.')
    return root


def numbers(values):
    result = [float(v) for v in values]
    if not result or not all(isfinite(v) for v in result):
        raise ValueError('Chart values must be finite and non-empty')
    return result


def pairs(labels, values):
    vals = numbers(values)
    if len(labels) != len(vals):
        raise ValueError('Chart labels and values must have equal lengths')
    return vals


def ticks(low, high, count=4):
    """Extend to round 1/2/5 ticks, including zero unless a baseline is explicit."""
    if high <= low:
        high = low + 1
    rough = (high - low) / count
    power = 10 ** floor(log10(rough))
    step = next(s * power for s in (1, 2, 5, 10) if s * power >= rough)
    start, end = floor(low / step), ceil(high / step)
    return [i * step for i in range(start, end + 1)]


def responsive(renderer, chart):
    return ''.join(f'<div class="plot-{size}">{renderer(chart, mobile)}</div>'
                   for size, mobile in [('wide', False), ('narrow', True)])


def climate(chart, mobile=False):
    width, left, right = (240, 31, 235) if mobile else (720, 42, 700)
    root = svg(chart, width, 360)
    tmin, tmax, rain = [pairs(MONTHS, chart[k]) for k in ('tmin', 'tmax', 'precip_mm')]
    ref = chart.get('_france', {})
    if ref.get('status') in ('non_comparable', 'unavailable'):
        ref = {}
    lo, hi = chart.get('temperature_extent', [0, 40])
    rainmax = chart.get('rain_max', 600)
    step = (right - left) / 12
    x = lambda i: left + (i + .5) * step
    y = lambda v: 153 - (v - lo) / (hi - lo) * 125
    yr = lambda v: 320 - v / rainmax * 105
    text(root, left, 16, 'Températures · °C', class_='axis-label')
    for value in ticks(lo, hi):
        el(root, 'line', x1=left, x2=right, y1=y(value), y2=y(value), class_='grid')
        text(root, left - 7, y(value) + 5, number(value, 0), text_anchor='end')
    points = [(x(i), y(v)) for i, v in enumerate(tmax)] + [
        (x(i), y(tmin[i])) for i in range(11, -1, -1)]
    el(root, 'polygon', points=' '.join(f'{a},{b}' for a,b in points),
       fill='var(--warm)', opacity='.13')
    for values, color, dash in [(tmin, 'var(--cool)', 'none'), (tmax, 'var(--warm)', 'none')]:
        el(root, 'polyline', points=' '.join(f'{x(i)},{y(v)}' for i,v in enumerate(values)),
           fill='none', stroke=color, stroke_width=2.5, stroke_dasharray=dash)
    if ref:
        for key in ('tmin', 'tmax'):
            values = pairs(MONTHS, ref[key])
            el(root, 'polyline', points=' '.join(f'{x(i)},{y(v)}' for i,v in enumerate(values)),
               fill='none', stroke='var(--france)', stroke_width=1.5, stroke_dasharray='4 3')
    text(root, left, 199, 'Précipitations · mm', class_='axis-label')
    for value in (0, rainmax / 2, rainmax):
        el(root, 'line', x1=left, x2=right, y1=yr(value), y2=yr(value), class_='grid')
        text(root, left - 7, yr(value) + 5, number(value, 0), text_anchor='end')
    for i,v in enumerate(rain):
        el(root, 'rect', x=x(i) - step*.32, y=yr(v), width=step*.64,
           height=320-yr(v), fill='var(--rain)', rx=1)
        if ref:
            el(root, 'line', x1=x(i)-step*.35, x2=x(i)+step*.35,
               y1=yr(ref['precip_mm'][i]), y2=yr(ref['precip_mm'][i]),
               stroke='var(--france)', stroke_width=2)
        text(root, x(i), 345, MONTHS[i][0].upper() if mobile else MONTHS[i], text_anchor='middle')
    return finish(root)


def percentages(chart):
    male = pairs(chart['age_groups'], chart['male'])
    female = pairs(chart['age_groups'], chart['female'])
    if any(v < 0 for v in male + female):
        raise ValueError('Population cannot be negative')
    if chart['unit'] == '%':
        return male, female
    total = sum(male + female) or 1
    return [v / total * 100 for v in male], [v / total * 100 for v in female]


def pyramid(chart, mobile=False):
    labels = chart['age_groups']
    male, female = percentages(chart)
    width = 240 if mobile else 720
    center = width / 2
    gap = 28 if mobile else 35
    outer = 13 if mobile else 35
    extent = center - gap - outer
    base = 45 + len(labels)*25
    root = svg(chart, width, base + 46)
    ref = chart.get('_france', {})
    rm, rf = percentages(ref) if ref.get('male') else ([], [])
    if ref.get('age_groups') and ref['age_groups'] != labels:
        raise ValueError('France age cohorts must match')
    limit = max(6, ceil(max(male + female + rm + rf) / 2)*2)
    text(root, (center-gap)/2, 20, 'Hommes', text_anchor='middle')
    text(root, width-(center-gap)/2, 20, 'Femmes', text_anchor='middle')
    for side in (-1, 1):
        for value in range(0, limit+1, 2):
            x = center + side*(gap + extent*value/limit)
            el(root, 'line', x1=x, x2=x, y1=33, y2=base, class_='grid')
            text(root, x, base+25, value, text_anchor='middle')
    for i,name in enumerate(labels):
        y = base - (i+1)*25
        text(root, center, y+16, name, text_anchor='middle', class_='age-label')
        for value, side, color in [(male[i], -1, 'var(--cool)'),
                                    (female[i], 1, 'var(--warm)')]:
            size = value/limit*extent
            x = center-gap-size if side == -1 else center+gap
            el(root, 'rect', x=x, y=y, width=size, height=20, fill=color, opacity='.8')
        if rm:
            for value,side in [(rm[i],-1),(rf[i],1)]:
                size = value/limit*extent
                x = center-gap-size if side == -1 else center+gap
                el(root, 'rect', x=x, y=y, width=size, height=20, fill='none',
                   stroke='var(--france)', stroke_width=1.5)
    return finish(root)


def bar(chart):
    vals = pairs(chart['labels'], chart['values'])
    ref = chart.get('_france', {})
    refs = pairs(chart['labels'], ref['values']) if ref.get('values') else []
    if any(v < 0 for v in vals + refs):
        raise ValueError('Row bars require non-negative values')
    limit = max(vals+refs) or 1
    out = ['<div class="bar-rows">']
    for i,(label,value) in enumerate(zip(chart['labels'], vals, strict=True)):
        cls = ' highlighted' if label == chart.get('highlight') else ''
        out.append(f'<div class="bar-row{cls}"><div class="row-heading"><span>{escape(label)}</span>'
                   f'<strong>{quantity(value, chart["unit"], chart.get("precision"))}</strong></div>'
                   f'<div class="bar-track"><span style="width:{value/limit*100:.4f}%"></span></div>')
        if refs:
            out.append(f'<div class="row-france">France <strong>{quantity(refs[i],chart["unit"])}</strong></div>'
                       f'<div class="bar-track france"><span style="width:{refs[i]/limit*100:.4f}%"></span></div>')
        out.append('</div>')
    return ''.join(out) + '</div>'


def barh(chart):
    return bar(chart)


def share(chart):
    vals = pairs(chart['labels'], chart['values'])
    if any(v < 0 for v in vals) or not 98 <= sum(vals) <= 101:
        raise ValueError('Share values must be non-negative and sum to about 100')
    # Keep a residual gap rather than renormalizing the publisher's values.
    order = sorted(range(len(vals)), key=lambda i: (
        chart['labels'][i].lower().startswith(('autres', 'ne sait', 'procédés plus')), -vals[i]))
    out = ['<div class="share-strip" aria-hidden="true">']
    for i in order:
        out.append(f'<span class="category cat-{i+1}" style="width:{vals[i]}%"></span>')
    out.append('</div><dl class="share-labels">')
    for i in order:
        out.append(f'<div><dt><i class="category cat-{i+1}" aria-hidden="true"></i>'
                   f'{escape(chart["labels"][i])}</dt><dd>{quantity(vals[i], "%")}</dd></div>')
    return ''.join(out) + '</dl>'


def line(chart, mobile=False):
    labels, series = chart['x'], list(chart['series'])
    if len(series) > 4:
        raise ValueError('Line charts support at most four series')
    ref = chart.get('_france', {})
    if ref.get('values'):
        series.append({'name':'France', 'values':ref['values'], 'france':True})
    for s in series:
        if len(s['values']) != len(labels):
            raise ValueError('Chart labels and values must have equal lengths')
        numbers([v for v in s['values'] if v is not None])
    values = [v for s in series for v in s['values'] if v is not None]
    ys = ticks(min(0, min(values)), max(0, max(values)))
    width = 240 if mobile else 720
    root = svg(chart, width, 350)
    left, right = 32, width - (80 if mobile else 125)
    times = [float(v) for v in labels]  # Real time spacing, not categorical positions.
    if any(b <= a for a,b in zip(times,times[1:])):
        raise ValueError('Line periods must be increasing')
    x = lambda i: left+(times[i]-times[0])/(times[-1]-times[0] or 1)*(right-left)
    y = lambda v: 300 - (v-ys[0])/(ys[-1]-ys[0])*265
    for v in ys:
        el(root,'line', x1=left,x2=right,y1=y(v),y2=y(v),class_='grid')
        text(root,left-7,y(v)+5,number(v),text_anchor='end')
    ends = []
    for j,s in enumerate(series):
        color = 'var(--france)' if s.get('france') else COLORS[j]
        groups, current = [], []
        for i,v in enumerate(s['values']):
            if v is None:
                if current: groups.append(current)
                current=[]
            else: current.append((i,v))
        if current: groups.append(current)
        for group in groups:
            el(root,'polyline',points=' '.join(f'{x(i)},{y(v)}' for i,v in group),
               fill='none',stroke=color,stroke_width=2.5,
               stroke_dasharray='4 3' if s.get('france') else 'none')
        i,v=groups[-1][-1]
        el(root,'circle',cx=x(i),cy=y(v),r=3,fill=color)
        ends.append((y(v),s['name'],v,color,x(i)))
    previous = -30
    for ypos,name,v,color,xpos in sorted(ends):
        label_y=max(ypos,previous+34)
        label_y=min(label_y,320)
        el(root,'line',x1=xpos+5,x2=right+7,y1=ypos,y2=label_y,stroke=color)
        text(root,right+10,label_y,name)
        text(root,right+10,label_y+16,number(v),class_='value-label')
        previous=label_y
    chosen = [0,len(labels)-1] if mobile else sorted(set([0,len(labels)//2,len(labels)-1]))
    for i in chosen: text(root,x(i),340,labels[i],text_anchor='middle')
    return finish(root)


def stacked(chart, mobile=False):
    labels, series = list(chart['labels']), chart['series']
    if len(series) > 5:
        raise ValueError('Stacked charts support at most five series')
    vals=[pairs(labels,s['values']) for s in series]
    if any(v<0 for row in vals for v in row):
        raise ValueError('Stacked charts require non-negative values')
    ref=chart.get('_france', {})
    if ref.get('values'):
        if len(ref['values']) != len(series):
            raise ValueError('France sectors must match')
        labels.append('France')
        for row,v in zip(vals,ref['values'],strict=True): row.append(v)
    totals=[sum(row[i] for row in vals) for i in range(len(labels))]
    ys=ticks(0,max(totals) or 1)
    width=240 if mobile else 720
    root=svg(chart,width,350)
    left,right=34,width-8
    y=lambda v:295-v/ys[-1]*250
    for v in ys:
        el(root,'line',x1=left,x2=right,y1=y(v),y2=y(v),class_='grid')
        text(root,left-7,y(v)+5,number(v),text_anchor='end')
    step=(right-left)/len(labels)
    for i,name in enumerate(labels):
        base=0
        for j,row in enumerate(vals):
            el(root,'rect',x=left+step*(i+.2),y=y(base+row[i]),width=step*.6,
               height=y(base)-y(base+row[i]),fill=COLORS[j],
               stroke='var(--france)' if name=='France' else 'none',
               stroke_dasharray='4 3' if name=='France' else 'none')
            base+=row[i]
        text(root,left+step*(i+.5),y(base)-9,number(base),text_anchor='middle')
        text(root,left+step*(i+.5),324,name,text_anchor='middle')
    return finish(root)


RENDERERS={'climate':climate,'pyramid':pyramid,'bar':bar,'barh':barh,'share':share,
           'stacked':stacked,'line':line}


def table(headers, rows, caption):
    head=''.join(f'<th scope="col">{escape(str(h))}</th>' for h in headers)
    body=''.join('<tr>'+''.join(f'<{"th scope=\"row\"" if i==0 else "td"}>'
         +escape(number(v,6) if isinstance(v,(int,float)) else str(v))
         + ('</th>' if i==0 else '</td>') for i,v in enumerate(row))+'</tr>' for row in rows)
    return (f'<div class="table-wrap" tabindex="0" role="region" aria-label="{escape(caption)}">'
            f'<table><caption>{escape(caption)}</caption><thead><tr>{head}</tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


def data_table(chart):
    kind=chart['type']
    if kind=='climate':
        headers=['Mois','Minimum (°C)','Maximum (°C)','Pluie (mm)']
        rows=zip(MONTHS,chart['tmin'],chart['tmax'],chart['precip_mm'],strict=True)
    elif kind=='pyramid':
        headers=['Âge',f'Hommes ({chart["unit"]})',f'Femmes ({chart["unit"]})']
        rows=zip(chart['age_groups'],chart['male'],chart['female'],strict=True)
    elif kind in ('line','stacked'):
        headers=['Période']+[f'{s["name"]} ({chart["unit"]})' for s in chart['series']]
        rows=zip(chart['x' if kind=='line' else 'labels'],*(s['values'] for s in chart['series']),strict=True)
    else:
        headers=['Catégorie',chart['unit']]
        rows=zip(chart['labels'],chart['values'],strict=True)
    out=table(headers,rows,chart.get('place',chart.get('country','Taïwan')))
    ref=chart.get('_france',{})
    if ref.get('values') or ref.get('male') or ref.get('tmin'):
        refchart={**chart,**ref,'_france':{},'country':'France','place':ref.get('place','France')}
        if kind in ('line','stacked') and 'values' in ref:
            out+=table(['Catégorie',chart['unit']],zip(
                [s['name'] for s in chart['series']] if kind=='stacked' else chart['x'],
                ref['values'],strict=True),'France')
        else:
            out+=data_table(refchart)
    return out


def comparison_note(ref):
    if not ref or ref.get('status') not in ('non_comparable','unavailable'):
        return ''
    status='non comparable' if ref['status']=='non_comparable' else 'indisponible'
    return f'<p class="comparison-note"><span>France · {status}</span> {escape(ref["reason"])}</p>'


def render_chart(chart, marker=''):
    kind=chart['type']
    subtitle=chart.get('subtitle',str(chart['year'])+' · '+chart.get('unit','°C et mm'))
    out=[f'<figure class="graphic" id="fig-{escape(chart["id"])}">'
         f'<header class="figure-header"><h3>{escape(chart["title"])}{marker}</h3>'
         f'<p>{escape(subtitle)}</p></header>']
    if kind=='climate':
        out.append('<div class="chart-legend"><span class="legend-min">Minimum</span>'
                   '<span class="legend-max">Maximum</span>'
                   '<span class="legend-france">Paris · France</span></div>')
        places=chart.get('places',[chart])
        for place in places:
            out.append(f'<div class="climate-place"><h4>{escape(place["place"])}</h4>')
            out.append(responsive(climate,{**chart,**place})+'</div>')
    elif kind=='pyramid':
        if chart.get('_france',{}).get('male'):
            out.append('<p class="chart-legend"><span class="legend-country">Taïwan</span>'
                       '<span class="legend-france">France · contours</span></p>')
        out.append(responsive(pyramid,chart))
    elif kind in ('line','stacked'):
        if kind=='stacked':
            out.append('<div class="chart-legend">'+''.join(
                f'<span><i class="category cat-{i+1}"></i>{escape(s["name"])}</span>'
                for i,s in enumerate(chart['series']))+'</div>')
        out.append(responsive(RENDERERS[kind],chart))
    else:
        out.append(RENDERERS[kind](chart))
        ref=chart.get('_france',{})
        if kind=='share' and ref.get('values'):
            out.append('<h4 class="france-label">France</h4><div class="france-share">'+
                       share({**chart,**ref})+'</div>')
    if chart.get('note_visible'):
        out.append(f'<p class="figure-note">{escape(chart["note_visible"])}</p>')
    out.append(comparison_note(chart.get('_france')))
    out.append('<details class="chart-data"><summary>Voir les données</summary>')
    if kind=='climate' and chart.get('places'):
        for place in chart['places']:
            out.append(data_table({**chart,**place,'_france':{}}))
        if chart.get('_france',{}).get('tmin'):
            out.append(data_table({**chart,**chart['_france'],'_france':{}}))
    else: out.append(data_table(chart))
    return ''.join(out)+'</details></figure>'
