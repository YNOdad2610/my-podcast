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
