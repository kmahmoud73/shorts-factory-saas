#!/usr/bin/env python3
"""
update_site_stats.py — Auto-update shortsfactory.io with latest channel stats.

Queries YouTube API directly for all 6 channels, patches index.html + deck.html,
commits + pushes to GitHub Pages.

Usage:
    python3 update_site_stats.py           # Update + commit + push
    python3 update_site_stats.py --dry-run # Preview changes, don't commit
    python3 update_site_stats.py --status  # Show current stats from YouTube API
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCRIPT_DIR = Path(__file__).parent
SF_DIR = SCRIPT_DIR.parent / "shorts-factory"
INDEX_HTML = SCRIPT_DIR / "index.html"
DECK_HTML = SCRIPT_DIR / "deck.html"

# Channel config: token, channel_id, card anchor pattern, milestone_goal
CHANNELS = {
    "jv": {
        "name": "The Jersey Vault",
        "token": SF_DIR / ".youtube_token.json",
        "channel_id": "UCjispA9UIoqkXI9etQicbog",
        "milestone_subs": 10000,
        "launch": "2026-02-21",
    },
    "cit": {
        "name": "Caught It Trending",
        "token": SF_DIR / ".youtube_token_trending.json",
        "channel_id": "UCaCi2G18tgDJqx6d1hcnY-Q",
        "milestone_subs": 1000,
        "launch": "2026-03-01",
    },
    "wil": {
        "name": "What If Lab",
        "token": SF_DIR / ".youtube_token_wil.json",
        "channel_id": "UCdcRf5SvVwBCmKjoB1iJETQ",
        "milestone_subs": 1000,
        "launch": "2026-03-18",
    },
    "goha": {
        "name": "Tales of Goha",
        "token": SF_DIR / ".youtube_token_goha.json",
        "channel_id": "UCs1jQlQ1wBhRI2NT4HS3gOQ",
        "milestone_subs": 1000,
        "launch": "2026-03-19",
    },
    "iyb": {
        "name": "Body X-Ray",
        "token": SF_DIR / ".youtube_token_iyb.json",
        "channel_id": "UC_-EgHYAnmFJelHCMH9ae5w",
        "milestone_subs": 1000,
        "launch": "2026-03-23",
    },
    "crime60": {
        "name": "60 Second Crime",
        "token": SF_DIR / ".youtube_token_crime60.json",
        "channel_id": "UCCRd00l1weSGq7byGzOjvzA",
        "milestone_subs": 1000,
        "launch": "2026-04-06",
    },
}

# Regex anchors to find each channel's card in index.html
# Each channel card starts with a unique text in a channel-name div
CARD_ANCHORS = {
    "jv": r'<div class="channel-name jv">The Jersey Vault</div>',
    "cit": r'<div class="channel-name cit">Caught It Trending</div>',
    "wil": r'channel-name"[^>]*>What If Lab</div>',
    "goha": r'channel-name"[^>]*>Tales of Goha</div>',
    "iyb": r'channel-name"[^>]*>Body X-Ray</div>',
    "crime60": r'channel-name"[^>]*>60 Second Crime</div>',
}


ANALYTICS_SCOPE = "https://www.googleapis.com/auth/yt-analytics.readonly"


def get_creds(token_file):
    """Load and refresh OAuth creds from token file."""
    creds = Credentials.from_authorized_user_file(str(token_file))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_file, "w") as f:
            f.write(creds.to_json())
    return creds


def get_youtube(token_file):
    """Auth via token file. Uses token's own scopes to avoid mismatch."""
    return build("youtube", "v3", credentials=get_creds(token_file))


def fetch_channel_stats(ch_key, ch_config):
    """Fetch stats + top video for a channel from YouTube API."""
    token = ch_config["token"]
    ch_id = ch_config["channel_id"]

    if not token.exists():
        print(f"  {ch_key}: token not found, skipping")
        return None

    try:
        yt = get_youtube(token)

        # Channel stats
        resp = yt.channels().list(part="statistics,contentDetails", id=ch_id).execute()
        if not resp.get("items"):
            print(f"  {ch_key}: no channel data")
            return None

        stats = resp["items"][0]["statistics"]
        subs = int(stats.get("subscriberCount", 0))
        views = int(stats.get("viewCount", 0))
        videos = int(stats.get("videoCount", 0))

        # Get top video
        uploads_pl = resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        video_ids = []
        pl_req = yt.playlistItems().list(
            part="snippet", playlistId=uploads_pl, maxResults=50
        )
        while pl_req:
            pl_resp = pl_req.execute()
            video_ids.extend(
                item["snippet"]["resourceId"]["videoId"]
                for item in pl_resp.get("items", [])
            )
            pl_req = yt.playlistItems().list_next(pl_req, pl_resp)

        top_title = ""
        top_views = 0
        # Fetch video stats in batches of 50
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i + 50]
            vid_resp = yt.videos().list(
                part="statistics,snippet", id=",".join(batch)
            ).execute()
            for item in vid_resp.get("items", []):
                v = int(item["statistics"].get("viewCount", 0))
                if v > top_views:
                    top_views = v
                    top_title = item["snippet"]["title"]

        return {
            "subs": subs,
            "views": views,
            "videos": videos,
            "top_title": top_title,
            "top_views": top_views,
        }
    except Exception as e:
        print(f"  {ch_key}: ERROR — {e}")
        return None


def fetch_watch_hours(ch_key, ch_config):
    """Fetch lifetime watch hours via YouTube Analytics API.
    Returns hours (float) or None if scope missing / error."""
    token = ch_config["token"]
    ch_id = ch_config["channel_id"]

    if not token.exists():
        return None

    try:
        creds = get_creds(token)
        # Check if token has analytics scope
        scopes = getattr(creds, "scopes", None) or []
        if not scopes:
            # Read scopes from token file directly
            with open(token) as f:
                token_data = json.load(f)
            scopes = token_data.get("scopes", [])
        if ANALYTICS_SCOPE not in scopes:
            print(f"  {ch_key}: no yt-analytics.readonly scope, skipping watch hours")
            return None

        yt_analytics = build("youtubeAnalytics", "v2", credentials=creds)

        # Query lifetime watch time (estimatedMinutesWatched)
        # Use channel launch date as start, today as end
        launch = ch_config.get("launch", "2026-01-01")
        end_date = datetime.now().strftime("%Y-%m-%d")

        resp = yt_analytics.reports().query(
            ids=f"channel=={ch_id}",
            startDate=launch,
            endDate=end_date,
            metrics="estimatedMinutesWatched",
        ).execute()

        rows = resp.get("rows", [])
        if rows:
            minutes = float(rows[0][0])
            hours = minutes / 60.0
            return round(hours, 1)
        return 0.0
    except Exception as e:
        print(f"  {ch_key}: watch hours ERROR — {e}")
        return None


def fmt(n):
    """Format number with commas."""
    return f"{n:,}"


def patch_channel_card(content, ch_key, stats, changes):
    """Patch a single channel card's stats in the HTML. Returns updated content."""
    anchor = CARD_ANCHORS[ch_key]

    # Find the card region (from anchor to the next result-card or section end)
    m = re.search(anchor, content)
    if not m:
        print(f"  {ch_key}: card anchor not found in HTML")
        return content

    card_start = m.start()
    # Find the next </div>\s*<div class="result-card" or </section> after the anchor
    # We need the region containing this card's stats
    remaining = content[card_start:]

    # Patch the 3 rs-value divs (subs, views, videos) — they appear in order
    # Pattern: <div class="rs-value"[^>]*>NUMBER</div>
    rs_pattern = r'(<div class="rs-value"[^>]*>)[\d,]+(</div>)'
    values = [fmt(stats["subs"]), fmt(stats["views"]), fmt(stats["videos"])]

    patched = remaining
    for i, val in enumerate(values):
        # Replace the (i+1)th occurrence
        count = 0
        def replacer(m):
            nonlocal count
            count += 1
            if count == i + 1:
                return f"{m.group(1)}{val}{m.group(2)}"
            return m.group(0)
        count = 0
        patched = re.sub(rs_pattern, replacer, patched, count=0)

    # Patch top video title
    patched = re.sub(
        r'(<div class="tv-title">).*?(</div>)',
        rf'\g<1>{stats["top_title"]}\g<2>',
        patched,
        count=1,
    )

    # Patch top video views
    patched = re.sub(
        r'(<div class="tv-views">)[\d,]+ views(</div>)',
        rf'\g<1>{fmt(stats["top_views"])} views\g<2>',
        patched,
        count=1,
    )

    content = content[:card_start] + patched
    changes.append(f"{ch_key.upper()}: {fmt(stats['subs'])} subs, {fmt(stats['views'])} views, {stats['videos']} videos | Top: {stats['top_title'][:40]} ({fmt(stats['top_views'])})")

    return content


def patch_milestone(content, ch_key, stats, ch_config, changes):
    """Patch milestone progress bar for a channel."""
    goal = ch_config["milestone_subs"]
    pct = min(stats["subs"] / goal * 100, 100)
    pct_str = f"{pct:.1f}%"

    # JV and CiT have id-based milestone elements
    if ch_key == "jv":
        # JV 1K milestone is achieved — show percentage over 1K, capped bar at 100%
        jv_1k_pct = min(stats["subs"] / 1000 * 100, 999)
        jv_pct_display = f"&#10003; {jv_1k_pct:.0f}%" if stats["subs"] >= 1000 else f"{jv_1k_pct:.1f}%"
        jv_bar_width = "100%" if stats["subs"] >= 1000 else f"{jv_1k_pct:.1f}%"
        content = re.sub(
            r'(<span id="jv-milestone-pct"[^>]*>)[^<]*(</span>)',
            rf'\g<1>{jv_pct_display}\g<2>', content
        )
        content = re.sub(
            r'(<div id="jv-milestone-bar" style="width:)[^;]+(;)',
            rf'\g<1>{jv_bar_width}\2', content
        )
        changes.append(f"{ch_key.upper()} milestone: {jv_pct_display} (1K subs)")
    elif ch_key == "cit":
        content = re.sub(
            r'(<span id="cit-milestone-pct"[^>]*>)[^<]*(</span>)',
            rf'\g<1>{pct_str}\g<2>', content
        )
        content = re.sub(
            r'(<div id="cit-milestone-bar" style="width:)[^;]+(;)',
            rf'\g<1>{pct_str}\2', content
        )
        changes.append(f"{ch_key.upper()} milestone: {pct_str} of {fmt(goal)}")
    else:
        # Other channels: find their milestone bar by color/proximity to anchor
        # These use inline percentage text + bar width
        anchor = CARD_ANCHORS[ch_key]
        m = re.search(anchor, content)
        if m:
            # Find the milestone section after this anchor
            region_start = m.start()
            region = content[region_start:]

            # Pattern: percentage text in a span with font-weight:700
            # followed by a progress bar div with width:X%
            color_map = {
                "wil": "var(--accent-purple)",
                "goha": "#eab308",
                "iyb": "#3b82f6",
                "crime60": "#ef4444",
            }
            color = color_map.get(ch_key, "")

            # Update percentage text
            old_pct_pattern = rf'(color:{re.escape(color)};font-weight:700">)[\d.]+%(</span>)'
            region_new = re.sub(old_pct_pattern, rf'\g<1>{pct_str}\g<2>', region, count=1)

            # Update bar width
            bar_colors = {
                "wil": r"var\(--accent-purple\),#7c3aed",
                "goha": r"#eab308,#d97706",
                "iyb": r"#3b82f6,#2563eb",
                "crime60": r"#ef4444,#dc2626",
            }
            bar_gradient = bar_colors.get(ch_key, "")
            if bar_gradient:
                old_bar_pattern = rf'(width:)[\d.]+%(;height:100%;background:linear-gradient\(90deg,{bar_gradient}\))'
                region_new = re.sub(old_bar_pattern, rf'\g<1>{pct_str}\g<2>', region_new, count=1)

            content = content[:region_start] + region_new
            changes.append(f"{ch_key.upper()} milestone: {pct_str} of {fmt(goal)}")

    return content


def patch_watch_time(content, ch_key, hours, changes):
    """Patch watch time display for a channel card. Returns updated content."""
    anchor = CARD_ANCHORS[ch_key]
    m = re.search(anchor, content)
    if not m:
        return content

    card_start = m.start()
    remaining = content[card_start:]

    # Pattern: "Watch time: XX hrs / 4,000 hrs" (with optional ~)
    wt_pattern = r'(<span>Watch time: )~?[\d.,]+ hrs( / 4,000 hrs</span>)'
    wt_match = re.search(wt_pattern, remaining)
    if not wt_match:
        # No watch time element exists for this channel — skip
        return content

    hrs_display = f"{hours:,.1f}" if hours >= 10 else f"{hours:.1f}"
    remaining = re.sub(wt_pattern, rf'\g<1>{hrs_display} hrs\2', remaining, count=1)

    # Update the percentage text and bar width
    pct = hours / 4000 * 100
    pct_str = f"{pct:.1f}%" if pct >= 0.1 else "<0.1%"
    bar_width = f"{max(pct, 0.05):.2f}%"  # min visible width

    # The percentage span follows the watch time span — it's the cyan one
    # Pattern: color:#06b6d4;font-weight:700">XX%</span>
    pct_pattern = r'(color:#06b6d4;font-weight:700">)[^<]*(</span>)'
    # Replace only the FIRST occurrence (the watch time %, not some other cyan element)
    pct_match = re.search(pct_pattern, remaining)
    if pct_match:
        remaining = remaining[:pct_match.start()] + \
            re.sub(pct_pattern, rf'\g<1>{pct_str}\g<2>', remaining[pct_match.start():], count=1)

    # Update bar width — the cyan gradient bar
    bar_pattern = r'(width:)[\d.]+%(;height:100%;background:linear-gradient\(90deg,#06b6d4,#0891b2\))'
    bar_match = re.search(bar_pattern, remaining)
    if bar_match:
        remaining = remaining[:bar_match.start()] + \
            re.sub(bar_pattern, rf'\g<1>{bar_width}\g<2>', remaining[bar_match.start():], count=1)

    content = content[:card_start] + remaining
    changes.append(f"{ch_key.upper()} watch time: {hrs_display} hrs ({pct_str})")
    return content


def patch_stats_bar(content, all_stats, changes):
    """Patch the top stats bar (combined views, timestamp)."""
    total_views = sum(s["views"] for s in all_stats.values() if s)
    total_videos = sum(s["videos"] for s in all_stats.values() if s)
    combined_rounded = (total_views // 100) * 100
    combined_str = f"{combined_rounded:,}+"

    content = re.sub(
        r'(<div class="stat-number">)[\d,]+\+?(</div>\s*<div class="stat-label">Total Views)',
        rf'\g<1>{combined_str}\g<2>', content
    )
    changes.append(f"Stats bar: {combined_str} combined views")

    # Timestamp
    ts = datetime.now().strftime("%b %-d")
    content = re.sub(
        r'(<span id="stats-updated-ts">)[^<]*(</span>)',
        rf'\g<1>{ts}\g<2>', content
    )
    changes.append(f"Timestamp: {ts}")

    return content


def patch_deck(content, all_stats, changes):
    """Patch deck.html stats. JV + CiT cards + summary."""
    for ch_key in ["jv", "cit"]:
        stats = all_stats.get(ch_key)
        if not stats:
            continue

        if ch_key == "jv":
            name_pattern = r'<div class="cc-name jv">The Jersey Vault</div>'
        else:
            name_pattern = r'<div class="cc-name cit">Caught It Trending</div>'

        # Patch subs/views/videos
        content, n = re.subn(
            rf'({name_pattern}.*?'
            r'<div class="cc-val">)[\d,]+(</div>.*?<div class="cc-lbl">Subscribers</div>.*?'
            r'<div class="cc-val">)[\d,]+(</div>.*?<div class="cc-lbl">Views</div>.*?'
            r'<div class="cc-val">)[\d,]+(</div>.*?<div class="cc-lbl">Videos</div>)',
            rf'\g<1>{fmt(stats["subs"])}\g<2>{fmt(stats["views"])}\g<3>{fmt(stats["videos"])}\4',
            content, flags=re.DOTALL,
        )
        if n:
            changes.append(f"Deck {ch_key.upper()}: {fmt(stats['subs'])} subs, {fmt(stats['views'])} views")

        # Patch top video views
        content, n = re.subn(
            rf'({name_pattern}.*?<div class="cc-hl-val">.*?<span>)[\d,]+ views(</span>)',
            rf'\g<1>{fmt(stats["top_views"])} views\2',
            content, flags=re.DOTALL,
        )

    # Combined summary
    total_views = sum(s["views"] for s in all_stats.values() if s)
    total_videos = sum(s["videos"] for s in all_stats.values() if s)
    combined_str = f"{(total_views // 100) * 100:,}+"

    content, _ = re.subn(
        r'(<div class="rs-big">)[\d,]+\+?(</div>\s*<div class="rs-small">Combined Views)',
        rf'\g<1>{combined_str}\2', content
    )
    content, _ = re.subn(
        r'(<div class="rs-big">)\d+(</div>\s*<div class="rs-small">Videos Live)',
        rf'\g<1>{total_videos}\2', content
    )

    days_since = (datetime.now() - datetime(2026, 2, 19)).days
    content, _ = re.subn(
        r'(<div class="rs-big">)\d+ days(</div>\s*<div class="rs-small">Since Launch)',
        rf'\g<1>{days_since} days\2', content
    )

    # Channel age badges
    for ch_key in ["jv", "cit"]:
        launch = datetime.strptime(CHANNELS[ch_key]["launch"], "%Y-%m-%d")
        age = (datetime.now() - launch).days
        age_text = f"Live for {age} days"
        cls = ch_key
        content, _ = re.subn(
            rf'((?:channel-name|cc-name) {cls}">.*?<div class="(?:channel-age|cc-age)">)Live for \d+ days(</div>)',
            rf'\g<1>{age_text}\2', content, flags=re.DOTALL,
        )

    return content


def main():
    dry_run = "--dry-run" in sys.argv
    status_only = "--status" in sys.argv

    print("=== Fetching YouTube API stats for all 6 channels ===")
    all_stats = {}
    for ch_key, ch_config in CHANNELS.items():
        stats = fetch_channel_stats(ch_key, ch_config)
        all_stats[ch_key] = stats
        if stats:
            print(f"  {ch_key:8s} | {fmt(stats['subs']):>6s} subs | {fmt(stats['views']):>8s} views | {stats['videos']:>4d} videos | Top: {stats['top_title'][:45]}")

    # Fetch watch hours (Analytics API — needs yt-analytics.readonly scope)
    print("\n=== Fetching watch hours (Analytics API) ===")
    watch_hours = {}
    for ch_key, ch_config in CHANNELS.items():
        hrs = fetch_watch_hours(ch_key, ch_config)
        watch_hours[ch_key] = hrs
        if hrs is not None:
            print(f"  {ch_key:8s} | {hrs:>8.1f} hrs")

    if status_only:
        total_views = sum(s["views"] for s in all_stats.values() if s)
        total_videos = sum(s["videos"] for s in all_stats.values() if s)
        total_watch = sum(h for h in watch_hours.values() if h is not None)
        print(f"\n  Combined: {fmt(total_views)} views | {total_videos} videos | {total_watch:.1f} watch hrs")
        return

    # Patch index.html
    all_changes = []
    files_changed = []

    with open(INDEX_HTML) as f:
        index_content = f.read()
    original_index = index_content

    for ch_key, stats in all_stats.items():
        if stats:
            index_content = patch_channel_card(index_content, ch_key, stats, all_changes)
            index_content = patch_milestone(index_content, ch_key, stats, CHANNELS[ch_key], all_changes)

    # Patch watch hours for channels that have analytics data
    for ch_key, hrs in watch_hours.items():
        if hrs is not None:
            index_content = patch_watch_time(index_content, ch_key, hrs, all_changes)

    index_content = patch_stats_bar(index_content, all_stats, all_changes)

    if index_content != original_index:
        files_changed.append("index.html")
        if not dry_run:
            with open(INDEX_HTML, "w") as f:
                f.write(index_content)
            print(f"\n[UPDATED] index.html")
        else:
            print(f"\n[DRY RUN] index.html would be updated")

    # Patch deck.html
    if DECK_HTML.exists():
        with open(DECK_HTML) as f:
            deck_content = f.read()
        original_deck = deck_content
        deck_changes = []
        deck_content = patch_deck(deck_content, all_stats, deck_changes)
        if deck_content != original_deck:
            files_changed.append("deck.html")
            all_changes.extend(deck_changes)
            if not dry_run:
                with open(DECK_HTML, "w") as f:
                    f.write(deck_content)
                print(f"[UPDATED] deck.html")

    for c in all_changes:
        print(f"  - {c}")

    if not files_changed:
        print("\nNo changes needed — site is current.")
        return

    if dry_run:
        print(f"\n[DRY RUN] Would update {len(files_changed)} file(s).")
        return

    # Git commit + push
    print("\nCommitting + pushing to GitHub Pages...")
    total_views = sum(s["views"] for s in all_stats.values() if s)
    combined_str = f"{(total_views // 100) * 100:,}+"
    total_videos = sum(s["videos"] for s in all_stats.values() if s)
    date_str = datetime.now().strftime("%b %d")
    msg = f"Auto-update stats {date_str} — {combined_str} combined views, {total_videos} videos"

    os.chdir(str(SCRIPT_DIR))
    subprocess.run(["git", "add"] + [os.path.basename(str(f)) for f in [INDEX_HTML, DECK_HTML]], check=True)

    # Check if there are changes to commit
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    if result.returncode == 0:
        print("No git changes to commit.")
        return

    subprocess.run(["git", "commit", "-m", msg], check=True)
    result = subprocess.run(["git", "push"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Pushed to GitHub Pages. Site will update in ~60s.")
    else:
        print(f"Push failed: {result.stderr}")
        sys.exit(1)

    print(f"\nDone. {len(all_changes)} stats updated across {len(files_changed)} file(s).")


if __name__ == "__main__":
    main()
