#!/usr/bin/env python3
"""Generates the share pages r/<toneId>/index.html, OG images r/og/<toneId>.png and assets/og-home.png (1200x630).

Usage: python3 tools/make_og.py [path/to/tones.json]
Default tones.json: the Android repo next to this one (core/data/src/main/assets/tones.json). Needs Pillow + macOS font.
"""
import html
import json
import sys
from pathlib import Path
from urllib.parse import quote

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
TONES = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "PersonalColorAndroid/core/data/src/main/assets/tones.json"
SITE = "https://personalcolorotest.netlify.app"
PKG = "com.gun.personalcolor"
PLAY = f"https://play.google.com/store/apps/details?id={PKG}"
FONT = "/System/Library/Fonts/AppleSDGothicNeo.ttc"  # ttc index: 0 Regular, 2 Medium, 6 Bold
APP_NAME = "나의 컬러는? - 퍼스널컬러"


def font(size, index=0):
    return ImageFont.truetype(FONT, size, index=index)


def rgb(hex_):
    h = hex_.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w, h, colors):
    """Horizontal multi-stop gradient."""
    img = Image.new("RGB", (w, h))
    px = img.load()
    stops = [rgb(c) for c in colors]
    for x in range(w):
        t = x / (w - 1) * (len(stops) - 1)
        i = min(int(t), len(stops) - 2)
        f = t - i
        c = tuple(round(a + (b - a) * f) for a, b in zip(stops[i], stops[i + 1]))
        for y in range(h):
            px[x, y] = c
    return img


def make_image(tone, out):
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), "#FAF8F6")
    img.paste(gradient(W, 150, [c["hex"] for c in tone["bestColors"][:4]]), (0, 0))
    d = ImageDraw.Draw(img)
    d.text((72, 196), "나의 퍼스널컬러는", font=font(40, 2), fill="#66605B")
    d.text((68, 248), tone["nameKo"], font=font(112, 6), fill="#1D1B1A")
    d.text((72, 388), "  ".join("#" + k for k in tone["keywords"]), font=font(34, 2), fill="#5B4B8A")
    colors = tone["bestColors"][:12]
    size, gap = 76, (W - 144 - 76 * len(colors)) / max(len(colors) - 1, 1)
    for i, c in enumerate(colors):
        x = 72 + i * (size + gap)
        d.rounded_rectangle((x, 460, x + size, 460 + size), radius=20, fill=c["hex"])
    f = font(26, 6)
    d.text((W - 72 - d.textlength(APP_NAME, font=f), 572), APP_NAME, font=f, fill="#9A918B")
    img.save(out, optimize=True)


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
<link rel="icon" href="/favicon.ico" sizes="any">
<meta name="theme-color" content="#FAF8F6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141312" media="(prefers-color-scheme: dark)">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/"><img src="/assets/icon-192.png" alt="" width="32" height="32">나의 컬러는?</a>
  </div>
</header>
<main class="wrap share">
  <div class="share-band" style="background:linear-gradient(90deg,{grad})" aria-hidden="true"></div>
  <section class="share-card">
    <p class="eyebrow">친구의 퍼스널컬러는</p>
    <h1>{name}</h1>
    <ul class="tags">{tags}</ul>
    <div class="swatches" role="img" aria-label="잘 어울리는 컬러: {names}">{swatches}</div>
    <ul class="summary">{lines}</ul>
    <div class="stack">
      <a class="btn btn-primary btn-block" id="open" href="{play}">앱에서 내 퍼스널컬러 진단하기</a>
      <a class="btn btn-ghost btn-block" href="{play}">Google Play에서 앱 받기</a>
    </div>
  </section>
  <p class="section-sub" style="text-align:center;margin-top:20px">🔒 사진은 기기 안에서만 분석해요</p>
</main>
<footer class="site-footer">
  <div class="wrap">
    <span>개발자 정우건</span>
    <span>문의 <a href="mailto:wjddnrjs123@gmail.com">wjddnrjs123@gmail.com</a></span>
    <a href="/privacy.html">개인정보처리방침</a>
    <a href="/terms.html">이용약관</a>
    <span class="copy">© 2026 나의 컬러는?</span>
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
    intent = f"intent://personalcolorotest.netlify.app/r/{tid}#Intent;scheme=https;package={PKG};S.browser_fallback_url={quote(PLAY, safe='')};end"
    lines = [tone["summary"]] + [l for l in tone["characteristics"].split("\n") if l.strip()][:2]
    out.write_text(PAGE.format(
        title=e(f"나의 퍼스널컬러는 {tone['nameKo']}!"), summary=e(tone["summary"]), app=e(APP_NAME),
        image=f"{SITE}/r/og/{tid}.png", url=url, play=PLAY, intent=intent, name=e(tone["nameKo"]),
        grad=",".join(c["hex"] for c in tone["bestColors"][:4]),
        tags="".join(f"<li>#{e(k)}</li>" for k in tone["keywords"]),
        names=e(", ".join(c["name"] for c in tone["bestColors"][:12])),
        swatches="".join(f'<span style="background:{c["hex"]}" title="{e(c["name"])}"></span>' for c in tone["bestColors"][:12]),
        lines="".join(f"<li>{e(l)}</li>" for l in lines),
    ), encoding="utf-8")


def make_home_image(tones, out):
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), "#FAF8F6")
    d = ImageDraw.Draw(img)
    d.text((72, 150), "나의 컬러는?", font=font(104, 6), fill="#1D1B1A")
    d.text((76, 290), "사진 한 장으로 찾는 나의 퍼스널컬러", font=font(44, 2), fill="#5B4B8A")
    d.text((76, 356), "사진은 기기 밖으로 나가지 않아요", font=font(32, 2), fill="#6B645F")
    size, gap = 76, (W - 144 - 76 * 12) / 11
    for i, t in enumerate(tones):
        hexes = [c["hex"] for c in t["bestColors"] if c["hex"].upper() not in ("#FFFFFF", "#000000")]
        x = 72 + i * (size + gap)
        d.rounded_rectangle((x, 460, x + size, 460 + size), radius=20, fill=hexes[0])
    f = font(26, 6)
    d.text((W - 72 - d.textlength("Google Play", font=f), 572), "Google Play", font=f, fill="#9A918B")
    img.save(out, optimize=True)


def main():
    tones = json.loads(TONES.read_text(encoding="utf-8"))["tones"]
    assert len(tones) == 12, len(tones)
    (ROOT / "r/og").mkdir(parents=True, exist_ok=True)
    for t in tones:
        make_image(t, ROOT / f"r/og/{t['id']}.png")
        (ROOT / f"r/{t['id']}").mkdir(exist_ok=True)
        make_page(t, ROOT / f"r/{t['id']}/index.html")
    (ROOT / "assets").mkdir(exist_ok=True)
    make_home_image(tones, ROOT / "assets/og-home.png")
    print(f"generated {len(tones)} pages + images in {ROOT / 'r'}")


if __name__ == "__main__":
    main()
