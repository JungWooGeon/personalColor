#!/usr/bin/env python3
"""Generates everything Tinty-related on the site:
- share pages r/<toneId>/index.html, OG images r/og/<toneId>.png and assets/og-home.png (1200x630, rendered from HTML)
- Tinty SVGs assets/tinty/<toneId|expression|mark>.svg and the animated hero Tinty inlined in index.html
- icons: favicon.svg/.ico (tiny mark), apple-touch-icon, assets/icon-192/512 (small mark)

Usage: python3 tools/make_og.py [path/to/tones.json]
Default tones.json: the Android repo next to this one (core/data/src/main/assets/tones.json).
Needs Pillow, Google Chrome and network (Pretendard webfont for the OG images).
"""
import html
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote

from PIL import Image

import tinty as T

ROOT = Path(__file__).resolve().parent.parent
TONES = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "PersonalColorAndroid/core/data/src/main/assets/tones.json"
SITE = "https://tintycolor.com"
PKG = "com.gun.personalcolor"
PLAY = f"https://play.google.com/store/apps/details?id={PKG}"
APP_NAME = "나의 컬러는? - 퍼스널컬러"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONT_CSS = "https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"
ICON_BG = "#EFEBF6"
EXPRESSIONS = ["default", "wink", "thinking", "cheer", "surprised", "sleep"]


def band_hexes(tone):
    """First 4 best colors, skipping pure white/black (winter tones list them early)."""
    return [c["hex"] for c in tone["bestColors"] if c["hex"].upper() not in ("#FFFFFF", "#000000")][:4]


def shoot(jobs):
    """[(html, w, h, scale)] -> RGBA images via headless Chrome (transparent background)."""
    with tempfile.TemporaryDirectory() as tmp:
        def one(job):
            i, (doc, w, h, scale) = job
            page, png = Path(tmp) / f"{i}.html", Path(tmp) / f"{i}.png"
            page.write_text(doc, encoding="utf-8")
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={tmp}/u{i}",
                            f"--window-size={w},{h}", f"--force-device-scale-factor={scale}", "--default-background-color=00000000",
                            "--virtual-time-budget=8000", f"--screenshot={png}", page.as_uri()], check=True, capture_output=True)
            return Image.open(png).convert("RGBA")
        with ThreadPoolExecutor(6) as ex:
            return list(ex.map(one, enumerate(jobs)))


def svg_job(s):
    return ("<!doctype html><meta charset='utf-8'><style>html,body{margin:0;background:transparent}"
            "svg{display:block;width:512px;height:512px}</style>" + s, 512, 512, 2)


# ---------- OG images (HTML -> PNG) ----------
OG_CSS = """<!doctype html><html lang="ko"><meta charset="utf-8"><link rel="stylesheet" href="%s"><style>
*{box-sizing:border-box;margin:0}html,body{width:1200px;height:630px;overflow:hidden}
body{position:relative;background:#FAF8F6;color:#1D1B1A;font-family:"Pretendard Variable","Apple SD Gothic Neo",sans-serif;letter-spacing:-.02em;word-break:keep-all}
.blob{position:absolute;border-radius:50%%;filter:blur(60px)}
.brand{position:absolute;left:72px;top:52px;display:flex;align-items:center;gap:12px;font-weight:800;font-size:30px}
.brand svg{width:52px;height:52px}
.char{position:absolute}.char svg,.row svg{width:100%%;height:100%%}
.pill{display:inline-block;background:#EAE4F8;color:#3A2D66;border-radius:999px;padding:8px 20px;font-size:28px;font-weight:600;margin-right:10px}
</style>""" % FONT_CSS


def mix_white(hex_, t):
    return T.mix(hex_, "#FFFFFF", t)


def og_tone(tone, look):
    band = band_hexes(tone)
    blobs = "".join(f'<div class="blob" style="left:{x}px;top:{y}px;width:{s}px;height:{s}px;background:{mix_white(c, .45)};opacity:.85"></div>'
                    for (x, y, s), c in zip([(700, 40, 360), (880, 210, 340), (760, 300, 300), (980, 20, 240)], band))
    chips = "".join(f'<i style="display:block;width:76px;height:76px;border-radius:22px;background:{c["hex"]};box-shadow:inset 0 0 0 2px rgba(0,0,0,.06)"></i>'
                    for c in tone["bestColors"][:12])
    tags = "".join(f'<span class="pill">#{html.escape(k)}</span>' for k in tone["keywords"][:3])
    return OG_CSS + f"""{blobs}
<div class="brand">{T.svg(T.tinty_small(T.BRAND, uid="m"))}나의 컬러는?</div>
<div class="char" style="left:752px;top:62px;width:400px;height:400px">{T.svg(T.tinty(look, "cheer", uid="c"))}</div>
<div style="position:absolute;left:76px;top:150px;width:680px">
  <p style="font-size:36px;font-weight:600;color:#66605B">나의 퍼스널컬러는</p>
  <h1 style="font-size:124px;font-weight:800;line-height:1.08;letter-spacing:-.04em;margin-top:6px">{html.escape(tone["nameKo"])}</h1>
  <p style="font-size:30px;font-weight:600;color:#9A918B;margin-top:6px;letter-spacing:0">{html.escape(tone["nameEn"])}</p>
  <div style="margin-top:26px">{tags}</div>
</div>
<div style="position:absolute;left:72px;right:72px;top:512px;display:flex;justify-content:space-between">{chips}</div>"""


def og_home(looks):
    row = "".join(f'<div style="width:84px;height:84px">{T.svg(T.tinty(l, uid=f"r{i}", ground=False))}</div>'
                  for i, l in enumerate(looks))
    return OG_CSS + f"""
<div class="blob" style="left:700px;top:10px;width:420px;height:420px;background:#E6DFFB"></div>
<div class="blob" style="left:820px;top:200px;width:340px;height:300px;background:#FFE3D4"></div>
<div class="brand">{T.svg(T.tinty_small(T.BRAND, uid="m"))}나의 컬러는? - 퍼스널컬러</div>
<div class="char" style="left:770px;top:40px;width:400px;height:400px">{T.svg(T.tinty(T.BRAND, "wink", uid="c"))}</div>
<div style="position:absolute;left:76px;top:150px;width:700px">
  <h1 style="font-size:84px;font-weight:800;line-height:1.18;letter-spacing:-.04em">사진 한 장으로<br>나의 컬러를 찾아요</h1>
  <p style="font-size:32px;font-weight:600;color:#66605B;margin-top:22px">12톤 진단부터 오늘의 코디까지 · 사진은 기기 안에서만</p>
</div>
<div class="row" style="position:absolute;left:66px;right:66px;top:500px;display:flex;justify-content:space-between">{row}</div>"""


# ---------- share pages ----------
LOCK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg>'

PAGE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{summary}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{app}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{summary}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{summary}">
<meta name="twitter:image" content="{image}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#FAF8F6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141312" media="(prefers-color-scheme: dark)">
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="stylesheet" href="{font}">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<a class="skip" href="#main">본문으로 건너뛰기</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/"><img src="/assets/tinty/mark.svg" alt="" width="36" height="36">나의 컬러는?</a>
    <a class="btn btn-primary btn-sm" href="{play}">다운로드</a>
  </div>
</header>
<main id="main" class="wrap share">
  <div class="share-sheet">
  <div class="share-hero" style="--a1:{a1};--a2:{a2};--a3:{a3}">
    <img class="bob" src="/assets/tinty/{tid}.svg" alt="{name} 컬러의 틴티" width="200" height="200">
  </div>
  <section class="share-card">
    <div class="head">
      <p class="eyebrow">친구의 퍼스널컬러는</p>
      <h1>{name}</h1>
      <p class="en">{en}</p>
      <ul class="tags">{tags}</ul>
    </div>
    <h2><span class="lbl best">BEST</span>잘 어울리는 컬러</h2>
    <ul class="swatches">{best}</ul>
    <h2><span class="lbl worst">WORST</span>피하면 좋은 컬러</h2>
    <ul class="swatches worst">{worst}</ul>
    <ul class="summary">{lines}</ul>
  </section>
  </div>
  <section class="share-cta">
    <h2>나는 어떤 톤일까?</h2>
    <p>사진 한 장이면 12톤 중 내 톤을 알려줘요.</p>
    <div class="stack">
      <a class="btn btn-primary btn-block" id="open" href="{play}">나도 진단해 보기</a>
      <a class="btn btn-ghost btn-block" href="{play}">Google Play</a>
    </div>
  </section>
  <div class="share-foot">
    <span>{lock}사진은 기기 안에서만 분석해요</span>
    <a href="/#tones">다른 톤 둘러보기</a>
  </div>
</main>
<footer class="site-footer">
  <div class="wrap">
    <a class="brand" href="/"><img src="/assets/tinty/mark.svg" alt="" width="28" height="28" loading="lazy">나의 컬러는?</a>
    <span>개발자 정우건</span>
    <span>문의 <a href="mailto:wjddnrjs123@gmail.com">wjddnrjs123@gmail.com</a></span>
    <a href="/privacy.html">개인정보처리방침</a>
    <a href="/terms.html">이용약관</a>
  </div>
</footer>
<script>
  // Android: open the app (fallback to Play Store when not installed).
  if (/Android/i.test(navigator.userAgent)) document.getElementById("open").href = "{intent}";
</script>
</body>
</html>
"""


def make_page(tone, out):
    tid = tone["id"]
    e = html.escape
    url = f"{SITE}/r/{tid}"
    intent = f"intent://tintycolor.com/r/{tid}#Intent;scheme=https;package={PKG};S.browser_fallback_url={quote(PLAY, safe='')};end"
    lines = [tone["summary"]] + [l for l in tone["characteristics"].split("\n") if l.strip()][:2]
    sw = lambda cs: "".join(f'<li><i style="background:{c["hex"]}"></i>{e(c["name"])}</li>' for c in cs)
    band = band_hexes(tone)
    out.write_text(PAGE.format(
        title=e(f"나의 퍼스널컬러는 {tone['nameKo']}!"), summary=e(tone["summary"]), app=e(APP_NAME), font=FONT_CSS,
        image=f"{SITE}/r/og/{tid}.png", url=url, tid=tid, play=PLAY, intent=intent, name=e(tone["nameKo"]), en=e(tone["nameEn"]),
        a1=mix_white(band[0], .55), a2=mix_white(band[1], .55), a3=mix_white(band[2], .65), lock=LOCK,
        tags="".join(f"<li>#{e(k)}</li>" for k in tone["keywords"]),
        best=sw(tone["bestColors"][:12]), worst=sw(tone["worstColors"][:4]),
        lines="".join(f"<li>{e(l)}</li>" for l in lines),
    ), encoding="utf-8")


def icon(mark, size):
    """Opaque square app icon: the small mark at 74% on the brand tint (safe inside a circle crop)."""
    img = Image.new("RGBA", (size, size), ICON_BG)
    m = round(size * .74)
    img.alpha_composite(mark.resize((m, m), Image.LANCZOS), ((size - m) // 2, (size - m) // 2))
    return img.convert("RGB")


def inline_hero(svg):
    """Replace the hero Tinty in index.html (between the tinty:hero markers) with a fresh animated inline SVG."""
    page = ROOT / "index.html"
    live = svg.replace('<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">',
                       '<svg class="tinty-live bob" viewBox="0 0 512 512" aria-hidden="true">').replace("\n", "")
    src = page.read_text(encoding="utf-8")
    new, n = re.subn(r"(<!-- tinty:hero -->).*?(<!-- /tinty:hero -->)", lambda m: m[1] + live + m[2], src, flags=re.S)
    assert n == 1, "tinty:hero markers missing in index.html"
    page.write_text(new, encoding="utf-8")


def main():
    tones = json.loads(TONES.read_text(encoding="utf-8"))["tones"]
    assert len(tones) == 12, len(tones)
    looks = {t["id"]: t for t in T.load_tones(TONES)}

    # Tinty SVGs
    out = ROOT / "assets/tinty"
    out.mkdir(parents=True, exist_ok=True)
    svgs = {t["id"]: T.svg(T.tinty(looks[t["id"]], uid="s")) for t in tones}
    svgs |= {x: T.svg(T.tinty(T.BRAND, x, uid="e")) for x in EXPRESSIONS}
    svgs["mark"] = T.svg(T.tinty_small(T.BRAND))
    for k, v in svgs.items():
        (out / f"{k}.svg").write_text(v, encoding="utf-8")
    tiny = T.svg(T.tinty_tiny())
    (ROOT / "favicon.svg").write_text(tiny, encoding="utf-8")
    inline_hero(T.svg(T.tinty(T.BRAND, uid="h", ground=False)))

    # Rasters: icons + OG images
    jobs = [svg_job(svgs["mark"]), svg_job(tiny), (og_home([looks[t["id"]] for t in tones]), 1200, 630, 1)]
    jobs += [(og_tone(t, looks[t["id"]]), 1200, 630, 1) for t in tones]
    mark, tiny_png, home, *ogs = shoot(jobs)

    small = lambda im, n: im.resize((n, n), Image.LANCZOS)
    tiny_png.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)],  # 16/32: tiny mark, 48: small mark
                  append_images=[small(tiny_png, 16), small(tiny_png, 32), small(mark, 48)])
    icon(mark, 180).save(ROOT / "apple-touch-icon.png", optimize=True)
    for n in (192, 512):
        icon(mark, n).save(ROOT / f"assets/icon-{n}.png", optimize=True)
    home.convert("RGB").save(ROOT / "assets/og-home.png", optimize=True)

    (ROOT / "r/og").mkdir(parents=True, exist_ok=True)
    for t, og in zip(tones, ogs):
        og.convert("RGB").save(ROOT / f"r/og/{t['id']}.png", optimize=True)
        (ROOT / f"r/{t['id']}").mkdir(exist_ok=True)
        make_page(t, ROOT / f"r/{t['id']}/index.html")
    print(f"generated {len(tones)} share pages + OG images, {len(svgs)} Tinty SVGs, icons, hero")


if __name__ == "__main__":
    main()
