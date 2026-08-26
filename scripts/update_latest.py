#!/usr/bin/env python3
"""Find mkayrl's newest long-form YouTube video and write it to latest.json.

The channel's "/videos" tab lists only long-form uploads (Shorts live under
"/shorts"), newest first, so the first video in that grid is what we want.
No API key needed — we read the public page and pull the id out of the
embedded ytInitialData.
"""

import json
import re
import sys
import datetime
import urllib.request

CHANNEL_VIDEOS = "https://www.youtube.com/@mkayrl/videos"
OEMBED = "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={id}&format=json"

# A real browser UA plus the consent cookie so YouTube serves the page
# instead of the EU consent interstitial.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": "SOCS=CAI; CONSENT=YES+cb.20220301-11-p0.en+FX+700",
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def newest_longform_id(html: str) -> str:
    # First video id that appears inside a richItemRenderer = newest upload
    # on the /videos grid.
    match = re.search(
        r'richItemRenderer.*?"videoId":"([A-Za-z0-9_-]{11})"', html, re.S
    )
    if not match:
        raise RuntimeError("No video id found in the /videos page")
    return match.group(1)


def title_for(video_id: str) -> str:
    try:
        data = json.loads(fetch(OEMBED.format(id=video_id)))
        return data.get("title", "")
    except Exception:
        return ""


def main() -> int:
    html = fetch(CHANNEL_VIDEOS)
    video_id = newest_longform_id(html)

    payload = {
        "id": video_id,
        "url": "https://www.youtube.com/watch?v=%s" % video_id,
        "title": title_for(video_id),
        "updated": datetime.datetime.now(datetime.timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    with open("latest.json", "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print("latest.json -> %s  (%s)" % (video_id, payload["title"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
