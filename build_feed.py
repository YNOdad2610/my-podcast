"""Builds feed.xml for Sample Podcast from episodes.json. Size and duration come from each MP3."""
import json, os, subprocess, sys
from datetime import datetime
from email.utils import format_datetime
from xml.sax.saxutils import escape
BASE = "https://ynodad2610.github.io/my-podcast"
HERE = os.path.dirname(os.path.abspath(__file__))
SHOW = {"title": "Sample Podcast", "description": "Private episodes written with Claude and voiced with Artlist.", "author": "Asaf", "language": "en-us"}
def duration(p):
    s = int(round(float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],capture_output=True,text=True).stdout)))
    return f"{s//3600:02d}:{s%3600//60:02d}:{s%60:02d}"
items = []
for ep in sorted(json.load(open(os.path.join(HERE,"episodes.json"))), key=lambda e: e["date"], reverse=True):
    p = os.path.join(HERE, ep["file"])
    if not os.path.exists(p): sys.exit(f"missing audio file: {ep['file']}")
    items.append(f"""    <item>
      <title>{escape(ep['title'])}</title>
      <description>{escape(ep['description'])}</description>
      <enclosure url="{BASE}/{ep['file']}" length="{os.path.getsize(p)}" type="audio/mpeg"/>
      <guid isPermaLink="false">{escape(ep['file'])}</guid>
      <pubDate>{format_datetime(datetime.fromisoformat(ep['date']))}</pubDate>
      <itunes:duration>{duration(p)}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>""")
feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SHOW['title']}</title>
    <link>{BASE}/</link>
    <atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml"/>
    <description>{SHOW['description']}</description>
    <language>{SHOW['language']}</language>
    <itunes:author>{SHOW['author']}</itunes:author>
    <itunes:image href="{BASE}/cover.jpg"/>
    <itunes:category text="Education"/>
    <itunes:explicit>false</itunes:explicit>
    <itunes:block>Yes</itunes:block>
{chr(10).join(items)}
  </channel>
</rss>
"""
open(os.path.join(HERE,"feed.xml"),"w").write(feed)

# Shareable listen page per episode: <BASE>/e/<number>/ (e.g. episode-004.mp3 -> /e/4/).
# Open Graph tags give WhatsApp/iMessage a preview card with the cover and title.
from html import escape as h
PAGE = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{title} · {show}</title>
<meta property="og:type" content="music.song">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{ogdesc} · {show} · {mins} min">
<meta property="og:image" content="{base}/cover-share.jpg">
<meta property="og:image:width" content="600"><meta property="og:image:height" content="600">
<meta property="og:url" content="{base}/e/{n}/">
<meta property="og:audio" content="{base}/{file}"><meta property="og:audio:type" content="audio/mpeg">
<style>
 body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#111;color:#f2f2f2;display:flex;min-height:100vh;align-items:center;justify-content:center}}
 main{{max-width:420px;width:100%;padding:28px 22px;box-sizing:border-box;text-align:center}}
 img{{width:100%;max-width:300px;border-radius:14px;box-shadow:0 10px 40px rgba(0,0,0,.5)}}
 .show{{margin:22px 0 4px;font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:#9a9a9a}}
 h1{{margin:0 0 8px;font-size:22px;line-height:1.25}}
 p{{margin:0 0 22px;color:#bdbdbd;font-size:15px;line-height:1.45}}
 audio{{width:100%}}
 .meta{{margin-top:14px;font-size:13px;color:#8a8a8a}} .meta a{{color:#8a8a8a}}
</style></head><body><main>
<img src="{base}/cover-share.jpg" alt="">
<div class="show">{show}</div>
<h1>{title}</h1>
<p>{desc}</p>
<audio controls preload="metadata" src="{base}/{file}"></audio>
<div class="meta">{mins} min · <a href="{base}/{file}" download>Download MP3</a></div>
</main></body></html>
"""
for ep in json.load(open(os.path.join(HERE, "episodes.json"))):
    n = int(ep["file"].split("-")[1].split(".")[0])
    secs = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",os.path.join(HERE, ep["file"])],capture_output=True,text=True).stdout)
    d = os.path.join(HERE, "e", str(n)); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(PAGE.format(
        title=h(ep["title"]), desc=h(ep["description"]), ogdesc=h(ep["description"].rstrip(".")), show=h(SHOW["title"]),
        base=BASE, n=n, file=ep["file"], mins=round(secs / 60)))
