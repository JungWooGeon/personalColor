"""Tinty (틴티) brand character, SVG only. All geometry in a 512x512 box.
Copied from the character kit (_source/tinty.py, render helpers dropped); used by make_og.py."""
import json, math

FONT = "'Apple SD Gothic Neo','Pretendard',system-ui,sans-serif"
INK = "#2B2236"


# ---------- color utils ----------
def hx(c):
    c = c.lstrip('#'); return [int(c[i:i + 2], 16) for i in (0, 2, 4)]


def tohex(r):
    return '#' + ''.join(f'{max(0, min(255, round(v))):02X}' for v in r)


def mix(a, b, t):
    A, B = hx(a), hx(b); return tohex([A[i] + (B[i] - A[i]) * t for i in range(3)])


def lum(c):
    r, g, b = [v / 255 for v in hx(c)]
    f = lambda x: x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def lift(c, minlum):
    """Lighten toward white until luminance >= minlum (keeps deep tones readable)."""
    t = 0
    while lum(mix(c, '#FFFFFF', t)) < minlum and t < .9: t += .02
    return mix(c, '#FFFFFF', t)


# ---------- tones: (body top, body bottom, scarf x4, blush) chosen from bestColors ----------
PICK = {  # id: (c1, c2, [scarf...]) by bestColors name
    'spring_light': ('피치', '웜 핑크', ['라이트 민트', '버터 옐로', '아쿠아 블루', '라이트 코랄']),
    'spring_true': ('골든 옐로', '코랄', ['터콰이즈', '애플 그린', '웜 레드', '오렌지']),
    'spring_bright': ('레몬 옐로', '비비드 코랄', ['클리어 블루', '아쿠아 민트', '비비드 그린', '클리어 레드']),
    'summer_light': ('파우더 핑크', '라벤더', ['베이비 블루', '파스텔 아쿠아', '로즈 핑크', '페리윙클']),
    'summer_true': ('소프트 로즈', '라벤더', ['미디엄 블루', '스카이 블루', '블루 그린', '라즈베리']),
    'summer_mute': ('더스티 로즈', '그레이시 블루', ['블루 세이지', '모브', '슬레이트 블루', '소프트 플럼']),
    'autumn_mute': ('살몬 베이지', '세이지 그린', ['소프트 머스터드', '소프트 카멜', '올리브 그린', '소프트 테라코타']),
    'autumn_true': ('머스터드', '펌킨 오렌지', ['올리브 그린', '러스트', '카멜', '테라코타']),
    'autumn_deep': ('브론즈', '와인 레드', ['딥 틸', '딥 올리브', '다크 체리 레드', '토바코 브라운']),
    'winter_bright': ('핫핑크', '바이올렛', ['쿨 터콰이즈', '코발트 블루', '에메랄드 그린', '퓨어 화이트']),
    'winter_true': ('마젠타', '로열 블루', ['크림슨', '퓨어 화이트', '미드나잇 네이비', '파인 그린']),
    'winter_deep': ('로열 퍼플', '딥 사파이어', ['쿨 레드', '퓨어 화이트', '와인', '에그플랜트']),
}
ORDER = list(PICK)


def load_tones(path):
    raw = json.load(open(path, encoding="utf-8"))
    items = list(raw.values())[0]
    out = {}
    for it in items:
        cmap = {c['name']: c['hex'] for c in it['bestColors']}
        a, b, sc = PICK[it['id']]
        blush = (it.get('makeup', {}).get('blushColors') or [{'hex': '#F4A3A0'}])[0]['hex']
        out[it['id']] = dict(id=it['id'], ko=it['nameKo'], en=it['nameEn'],
                             c1=lift(cmap[a], .16), c2=lift(cmap[b], .09),
                             raw=[cmap[a], cmap[b]], scarf=[cmap[s] for s in sc], blush=blush,
                             best=[c['hex'] for c in it['bestColors']])
    return [out[k] for k in ORDER]


BRAND = dict(id='brand', ko='브랜드', en='Brand', c1='#FFD3BE', c2='#C9BCF2',
             scarf=['#FF8A6B', '#9CC9EC', '#D4A017', '#B5006E'], blush='#F7A3A0', raw=['#FFCBB0', '#CBBEF5'])

# ---------- character ----------
def _star(x, y, r, c, op=1):
    k = r * .28
    return (f'<path d="M{x} {y - r} Q{x + k} {y - k} {x + r} {y} Q{x + k} {y + k} {x} {y + r} '
            f'Q{x - k} {y + k} {x - r} {y} Q{x - k} {y - k} {x} {y - r}Z" fill="{c}" opacity="{op}"/>')


BODY = ("M250 106 C266 84 286 70 308 66 C318 65 320 74 312 80 C300 90 296 100 300 114 "
        "C326 174 404 226 404 322 C404 404 338 452 256 452 C174 452 108 404 108 322 C108 226 212 162 250 106 Z")
BAND = "M106 380 Q256 440 406 380 C414 392 412 410 402 418 Q256 478 110 418 C100 410 98 392 106 380 Z"


def tinty(t, expr='default', uid='a', ground=True, extras=True, small=False):
    """Return an SVG <g> (512 box). expr: default|wink|surprised|thinking|cheer|sleep."""
    c1, c2 = t['c1'], t['c2']
    if expr == 'sleep':
        c1, c2 = mix(c1, '#B9B3D6', .3), mix(c2, '#8C86B8', .3)
    deep = mix(c2, '#1B1530', .45)
    arm = mix(c1, c2, .72)
    sc = t['scarf']
    u = uid
    d = [f'''<defs>
<linearGradient id="b{u}" x1=".15" y1=".05" x2=".8" y2="1"><stop class="s1" offset="0" stop-color="{c1}"/><stop class="s2" offset="1" stop-color="{c2}"/></linearGradient>
<radialGradient id="hl{u}" cx=".34" cy=".3" r=".55"><stop offset="0" stop-color="#fff" stop-opacity=".5"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/></radialGradient>
<radialGradient id="sh{u}" cx=".72" cy="1.05" r=".75"><stop offset="0" stop-color="{deep}" stop-opacity=".45"/><stop offset=".7" stop-color="{deep}" stop-opacity="0"/></radialGradient>
<linearGradient id="am{u}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{mix(arm, '#FFFFFF', .12)}"/><stop offset="1" stop-color="{mix(arm, deep, .3)}"/></linearGradient>
<linearGradient id="sf{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".3"/><stop offset=".4" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".2"/></linearGradient>
<linearGradient id="sd{u}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity=".22"/><stop offset=".22" stop-color="#000" stop-opacity="0"/><stop offset=".78" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".22"/></linearGradient>
<clipPath id="cb{u}"><path d="{BODY}"/></clipPath>
<clipPath id="cs{u}"><path d="{BAND}"/></clipPath>
<filter id="bl{u}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="bs{u}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5"/></filter>
<filter id="ds{u}" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="{deep}" flood-opacity=".28"/></filter>
</defs>''']
    if ground:
        d.append(f'<ellipse class="gshadow" cx="256" cy="476" rx="110" ry="12" fill="{deep}" opacity=".22" filter="url(#bl{u})"/>')
    # body
    d.append(f'''<g class="body"><path d="{BODY}" fill="url(#b{u})"/>
<g clip-path="url(#cb{u})"><rect width="512" height="512" fill="url(#hl{u})"/><rect width="512" height="512" fill="url(#sh{u})"/>
<path d="M120 352 C140 430 210 456 290 448" stroke="#fff" stroke-opacity=".4" stroke-width="9" fill="none" filter="url(#bs{u})"/>
<path d="M110 428 Q256 486 402 428" stroke="{deep}" stroke-opacity=".35" stroke-width="16" fill="none" filter="url(#bs{u})"/></g>
<ellipse cx="184" cy="222" rx="16" ry="40" transform="rotate(30 184 222)" fill="#fff" opacity=".5" filter="url(#bs{u})"/>
<circle cx="216" cy="170" r="7.5" fill="#fff" opacity=".9"/><circle cx="292" cy="92" r="3.5" fill="#fff" opacity=".7"/></g>''')
    # face
    ex, ey, gap = 256, 316, 38
    f = []
    blush = ''.join(f'<ellipse cx="{ex + s * 64}" cy="{ey + 32}" rx="21" ry="11" fill="{t["blush"]}" opacity=".62" filter="url(#bs{u})"/>' for s in (-1, 1))

    if small: gap = 44

    def eye(x, y, rx=18 if small else 14, ry=24 if small else 19, look=(0, 0)):
        return (f'<g class="eye" style="transform-origin:{x}px {y}px;transform-box:view-box"><ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{INK}"/>'
                f'<circle cx="{x + 4 + look[0]}" cy="{y - 7 + look[1]}" r="{rx * .37:.1f}" fill="#fff"/>'
                f'<circle cx="{x - 4 + look[0]}" cy="{y + 7 + look[1]}" r="2.2" fill="#fff" opacity=".65"/></g>')

    def arc(x, y, up=True):
        k = 1 if up else -1
        return f'<path d="M{x - 13} {y + 5 * k} Q{x} {y - 13 * k} {x + 13} {y + 5 * k}" stroke="{INK}" stroke-width="7" stroke-linecap="round" fill="none"/>'
    smile = f'<path d="M{ex - 10} {ey + 26} Q{ex} {ey + 35} {ex + 10} {ey + 26}" stroke="{INK}" stroke-width="{9 if small else 5.5}" stroke-linecap="round" fill="none"/>'
    openm = (f'<path d="M{ex - 15} {ey + 24} Q{ex} {ey + 22} {ex + 15} {ey + 24} Q{ex + 13} {ey + 46} {ex} {ey + 46} Q{ex - 13} {ey + 46} {ex - 15} {ey + 24}Z" fill="{INK}"/>'
             f'<ellipse cx="{ex}" cy="{ey + 40}" rx="8" ry="5" fill="#F27D8C"/>')
    if expr == 'default':
        f += [blush, eye(ex - gap, ey), eye(ex + gap, ey), smile]
    elif expr == 'wink':
        f += [blush, arc(ex - gap, ey), f'<path d="M{ex + gap - 12} {ey - 7} L{ex + gap + 10} {ey + 1} L{ex + gap - 12} {ey + 9}" stroke="{INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" fill="none"/>', openm]
    elif expr == 'surprised':
        f += [blush, eye(ex - gap - 3, ey - 4, 16, 21), eye(ex + gap + 3, ey - 4, 16, 21),
              f'<ellipse cx="{ex}" cy="{ey + 36}" rx="9" ry="11" fill="{INK}"/>']
    elif expr == 'thinking':
        f += [blush, eye(ex - gap + 4, ey - 3, look=(3, -3)), eye(ex + gap + 4, ey - 3, look=(3, -3)),
              f'<path d="M{ex - 6} {ey + 31} Q{ex + 2} {ey + 25} {ex + 10} {ey + 30} Q{ex + 16} {ey + 34} {ex + 20} {ey + 28}" stroke="{INK}" stroke-width="5.5" stroke-linecap="round" fill="none"/>']
    elif expr == 'cheer':
        f += [blush, arc(ex - gap, ey), arc(ex + gap, ey), openm]
    elif expr == 'sleep':
        f += [blush, arc(ex - gap, ey + 2, False), arc(ex + gap, ey + 2, False),
              f'<ellipse cx="{ex}" cy="{ey + 32}" rx="5" ry="4" fill="{INK}" opacity=".85"/>']
    d.append('<g class="face">' + ''.join(f) + '</g>')
    # scarf: palette drape, segments foreshortened like a cylinder
    segs = []
    for i in range(4):
        a0, a1 = -math.pi / 2 + math.pi * i / 4, -math.pi / 2 + math.pi * (i + 1) / 4
        x0, x1 = 256 + 152 * math.sin(a0), 256 + 152 * math.sin(a1)
        if i == 0: x0 = 90
        if i == 3: x1 = 422
        segs.append(f'<rect class="sc{i}" x="{x0:.1f}" y="370" width="{x1 - x0 + .6:.1f}" height="120" fill="{sc[i]}"/>')
    ribbon = lambda p, c: f'<path d="{p}" fill="{c}"/><path d="{p}" fill="url(#sf{u})" opacity=".8"/>'
    d.append(f'''<g class="scarf" filter="url(#ds{u})"><g clip-path="url(#cs{u})">{''.join(segs)}
<rect y="370" width="512" height="120" fill="url(#sf{u})"/><rect x="100" y="370" width="312" height="120" fill="url(#sd{u})"/>
{''.join(f'<rect x="{256 + 152 * math.sin(-math.pi / 2 + math.pi * i / 4) - 1:.1f}" y="370" width="2" height="120" fill="#fff" opacity=".55"/>' for i in (1, 2, 3))}<path d="M106 383 Q256 443 406 383" stroke="#fff" stroke-opacity=".5" stroke-width="2.5" fill="none"/></g>
<g class="tails" style="display:{'none' if small else 'inline'}">{ribbon("M346 424 C362 438 380 454 392 476 L378 474 L376 490 C362 466 346 450 330 436 Z", sc[3])}
{ribbon("M330 430 C330 450 326 468 316 488 L330 484 L338 496 C348 474 352 452 352 430 Z", sc[0])}</g>
<rect x="322" y="400" width="38" height="34" rx="13" fill="{sc[1]}"/><rect x="322" y="400" width="38" height="34" rx="13" fill="url(#sf{u})"/>
<path d="M332 412 Q341 418 350 412" stroke="#000" stroke-opacity=".15" stroke-width="3" stroke-linecap="round" fill="none"/></g>''')
    # hands (front, soft drop shadow)
    hands = {'cheer': [(124, 262, -40), (388, 262, 40)], 'thinking': [(114, 394, 18), (334, 356, -20)]}.get(expr, [(114, 394, 18), (398, 394, -18)])
    if small: hands = []
    d.append(f'<g class="hands" filter="url(#ds{u})">' + ''.join(
        f'<ellipse cx="{x}" cy="{y}" rx="16" ry="22" transform="rotate({r} {x} {y})" fill="url(#am{u})"/><ellipse cx="{x-3}" cy="{y-8}" rx="6" ry="8" transform="rotate({r} {x} {y})" fill="#fff" opacity=".22"/>' for x, y, r in hands) + '</g>')
    if extras and not small:
        if expr == 'wink':
            d.append(_star(410, 206, 19, sc[1]) + _star(440, 250, 9, sc[0], .85))
        if expr == 'surprised':
            d.append(f'<g stroke="{INK}" stroke-width="7" stroke-linecap="round" opacity=".75"><path d="M376 126 L392 102"/><path d="M402 152 L428 142"/><path d="M348 104 L350 80"/></g>')
        if expr == 'thinking':
            d.append(''.join(f'<g transform="rotate({r} {x} {y})" filter="url(#ds{u})"><rect x="{x - 16}" y="{y - 21}" width="32" height="42" rx="6" fill="#fff"/><rect x="{x - 12}" y="{y - 17}" width="24" height="24" rx="4" fill="{c}"/><rect x="{x - 12}" y="{y + 11}" width="14" height="3" rx="1.5" fill="#C9C2CF"/></g>'
                             for (x, y, r), c in zip([(380, 132, 10), (424, 186, 20), (440, 252, 30)], [sc[0], sc[1], sc[2]])))
        if expr == 'cheer':
            d.append(_star(90, 160, 20, sc[0]) + _star(424, 140, 24, sc[1]) + _star(452, 212, 11, sc[2]) + _star(64, 222, 10, sc[3]))
        if expr == 'sleep':
            d.append(f'<g font-family="{FONT}" font-weight="800" fill="{mix(c2, INK, .4)}" opacity=".7"><text x="344" y="146" font-size="44">Z</text><text x="388" y="106" font-size="30">z</text><text x="418" y="76" font-size="20">z</text></g>')
    return '\n'.join(d)


def svg(inner, w=512, h=512, vb=None, bg=None):
    vb = vb or f"0 0 {w} {h}"
    b = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}">{b}{inner}</svg>'


def place(inner, x, y, size):
    s = size / 512
    return f'<g transform="translate({x} {y}) scale({s})">{inner}</g>'


def tinty_small(t, uid='sm'):
    """Simplified mark for <=64px: tight crop, bigger eyes, no tails/hands. 512 box."""
    return f'<g transform="translate(256 256) scale(1.3) translate(-256 -262)">{tinty(t, uid=uid, ground=False, small=True)}</g>'


def tinty_mono(fill='#fff', uid='mo'):
    """Single-colour silhouette for Android notification / monochrome icons."""
    return (f'<mask id="mk{uid}"><rect width="512" height="512" fill="#fff"/><path d="M106 380 Q256 440 406 380" stroke="#000" stroke-width="14" fill="none"/>'
            f'<ellipse cx="218" cy="316" rx="18" ry="24" fill="#000"/><ellipse cx="294" cy="316" rx="18" ry="24" fill="#000"/></mask>'
            f'<g transform="translate(256 256) scale(1.3) translate(-256 -262)" mask="url(#mk{uid})" fill="{fill}"><path d="{BODY}"/><path d="{BAND}"/></g>')
