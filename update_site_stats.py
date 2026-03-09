#!/usr/bin/env python3
"""
update_site_stats.py — Auto-update shortsfactory.io with latest channel stats.

Reads from shorts-factory analytics JSONs, patches index.html + deck.html,
commits + pushes to GitHub Pages.

Usage:
    python3 update_site_stats.py           # Update + commit + push
    python3 update_site_stats.py --dry-run # Preview changes, don't commit
    python3 update_site_stats.py --status  # Show current vs site stats
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SF_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "shorts-factory")
JV_STATS = os.path.join(SF_DIR, "analytics", "channel_stats.json")
CIT_STATS = os.path.join(SF_DIR, "analytics", "cit_channel_stats.json")
UPLOAD_QUEUE = os.path.join(SF_DIR, ".trending_upload_queue.json")
INDEX_HTML = os.path.join(SCRIPT_DIR, "index.html")
DECK_HTML = os.path.join(SCRIPT_DIR, "deck.html")
LAUNCH_DATE = datetime(2026, 2, 19)


def load_stats():
    """Load latest stats from both channel JSON files."""
    with open(JV_STATS) as f:
        jv_data = json.load(f)
    with open(CIT_STATS) as f:
        cit_data = json.load(f)

    jv_latest = jv_data["snapshots"][-1]
    cit_latest = cit_data["snapshots"][-1]

    jv_top = sorted(jv_latest["per_video"], key=lambda x: x["views"], reverse=True)[0]
    cit_top = sorted(cit_latest["per_video"], key=lambda x: x["views"], reverse=True)[0]

    queue_count = 0
    if os.path.exists(UPLOAD_QUEUE):
        with open(UPLOAD_QUEUE) as f:
            queue_count = len(json.load(f))

    days_since = (datetime.now() - LAUNCH_DATE).days

    return {
        "jv_subs": jv_data["channel"]["subscribers"],
        "jv_views": jv_latest["total_views"],
        "jv_videos": jv_latest["video_count"],
        "jv_top_title": jv_top["title"],
        "jv_top_views": jv_top["views"],
        "cit_subs": cit_data["channel"]["subscribers"],
        "cit_views": cit_latest["total_views"],
        "cit_videos": cit_latest["video_count"],
        "cit_top_title": cit_top["title"],
        "cit_top_views": cit_top["views"],
        "combined_views": jv_latest["total_views"] + cit_latest["total_views"],
        "total_videos": jv_latest["video_count"] + cit_latest["video_count"],
        "queue_count": queue_count,
        "days_since": days_since,
        "jv_date": jv_latest["date"],
        "cit_date": cit_latest["date"],
    }


def fmt(n):
    """Format number with commas."""
    return f"{n:,}"


def round_combined(n):
    """Round combined views to nearest 100 with + suffix."""
    rounded = (n // 100) * 100
    return f"{fmt(rounded)}+"


def patch_html(filepath, stats):
    """Patch an HTML file with updated stats. Returns (new_content, changes_made)."""
    with open(filepath) as f:
        content = f.read()

    original = content
    changes = []

    # --- INDEX.HTML patterns ---

    # Stats bar: combined views
    content, n = re.subn(
        r'(<div class="stat-number">)[\d,]+\+?(</div>\s*<div class="stat-label">Total Views)',
        rf'\g<1>{round_combined(stats["combined_views"])}\2',
        content,
    )
    if n:
        changes.append(f"Stats bar combined views -> {round_combined(stats['combined_views'])}")

    # JV result card block (index.html format)
    content, n = re.subn(
        r'(<div class="channel-name jv">The Jersey Vault</div>.*?'
        r'<div class="rs-value">)[\d,]+(</div>\s*<div class="rs-label">Subscribers</div>.*?'
        r'<div class="rs-value">)[\d,]+(</div>\s*<div class="rs-label">Total Views</div>.*?'
        r'<div class="rs-value">)[\d,]+(</div>\s*<div class="rs-label">Videos</div>)',
        rf'\g<1>{fmt(stats["jv_subs"])}\g<2>{fmt(stats["jv_views"])}\g<3>{fmt(stats["jv_videos"])}\4',
        content,
        flags=re.DOTALL,
    )
    if n:
        changes.append(f"JV card: {fmt(stats['jv_subs'])} subs, {fmt(stats['jv_views'])} views, {stats['jv_videos']} videos")

    # JV top video views (index.html)
    content, n = re.subn(
        r'(<div class="channel-name jv">.*?<div class="tv-views">)[\d,]+ views(</div>)',
        rf'\g<1>{fmt(stats["jv_top_views"])} views\2',
        content,
        flags=re.DOTALL,
    )
    if n:
        changes.append(f"JV top video views -> {fmt(stats['jv_top_views'])}")

    # CiT result card block (index.html format)
    content, n = re.subn(
        r'(<div class="channel-name cit">Caught It Trending</div>.*?'
        r'<div class="rs-value">)[\d,]+(</div>\s*<div class="rs-label">Subscribers</div>.*?'
        r'<div class="rs-value">)[\d,]+(</div>\s*<div class="rs-label">Total Views</div>.*?'
        r'<div class="rs-value">)[\d,]+(</div>\s*<div class="rs-label">Videos</div>)',
        rf'\g<1>{fmt(stats["cit_subs"])}\g<2>{fmt(stats["cit_views"])}\g<3>{fmt(stats["cit_videos"])}\4',
        content,
        flags=re.DOTALL,
    )
    if n:
        changes.append(f"CiT card: {fmt(stats['cit_subs'])} subs, {fmt(stats['cit_views'])} views, {stats['cit_videos']} videos")

    # CiT top video title + views (index.html)
    content, n = re.subn(
        r'(<div class="channel-name cit">.*?<div class="tv-title">).*?(</div>\s*<div class="tv-views">)[\d,]+ views(</div>)',
        rf'\g<1>{stats["cit_top_title"]}\g<2>{fmt(stats["cit_top_views"])} views\3',
        content,
        flags=re.DOTALL,
    )
    if n:
        changes.append(f"CiT top video -> {stats['cit_top_title']} ({fmt(stats['cit_top_views'])} views)")

    # --- DECK.HTML patterns ---

    # JV card (deck format)
    content, n = re.subn(
        r'(<div class="cc-name jv">The Jersey Vault</div>.*?'
        r'<div class="cc-val">)[\d,]+(</div>\s*<div class="cc-lbl">Subscribers</div>.*?'
        r'<div class="cc-val">)[\d,]+(</div>\s*<div class="cc-lbl">Views</div>.*?'
        r'<div class="cc-val">)[\d,]+(</div>\s*<div class="cc-lbl">Videos</div>)',
        rf'\g<1>{fmt(stats["jv_subs"])}\g<2>{fmt(stats["jv_views"])}\g<3>{fmt(stats["jv_videos"])}\4',
        content,
        flags=re.DOTALL,
    )
    if n:
        changes.append(f"Deck JV: {fmt(stats['jv_subs'])} subs, {fmt(stats['jv_views'])} views, {stats['jv_videos']} videos")

    # JV top video views (deck)
    content, n = re.subn(
        r'(<div class="cc-name jv">.*?<div class="cc-hl-val">.*?<span>)[\d,]+ views(</span>)',
        rf'\g<1>{fmt(stats["jv_top_views"])} views\2',
        content,
        flags=re.DOTALL,
    )
    if n:
        changes.append(f"Deck JV top views -> {fmt(stats['jv_top_views'])}")

    # CiT card (deck format)
    content, n = re.subn(
        r'(<div class="cc-name cit">Caught It Trending</div>.*?'
        r'<div class="cc-val">)[\d,]+(</div>\s*<div class="cc-lbl">Subscribers</div>.*?'
        r'<div class="cc-val">)[\d,]+(</div>\s*<div class="cc-lbl">Views</div>.*?'
        r'<div class="cc-val">)[\d,]+(</div>\s*<div class="cc-lbl">Videos</div>)',
        rf'\g<1>{fmt(stats["cit_subs"])}\g<2>{fmt(stats["cit_views"])}\g<3>{fmt(stats["cit_videos"])}\4',
        content,
        flags=re.DOTALL,
    )
    if n:
        changes.append(f"Deck CiT: {fmt(stats['cit_subs'])} subs, {fmt(stats['cit_views'])} views, {stats['cit_videos']} videos")

    # CiT top video (deck) — title short form + views
    cit_short_title = stats["cit_top_title"].split(" -- ")[0][:40]
    content, n = re.subn(
        r'(<div class="cc-name cit">.*?<div class="cc-hl-val">).*?(<span>)[\d,]+ views(</span>)',
        rf'\g<1>{cit_short_title} -- \g<2>{fmt(stats["cit_top_views"])} views\3',
        content,
        flags=re.DOTALL,
    )
    if n:
        changes.append(f"Deck CiT top -> {cit_short_title} ({fmt(stats['cit_top_views'])} views)")

    # Combined summary (deck)
    content, n = re.subn(
        r'(<div class="rs-big">)[\d,]+\+?(</div>\s*<div class="rs-small">Combined Views)',
        rf'\g<1>{round_combined(stats["combined_views"])}\2',
        content,
    )
    if n:
        changes.append(f"Deck combined -> {round_combined(stats['combined_views'])}")

    content, n = re.subn(
        r'(<div class="rs-big">)\d+(</div>\s*<div class="rs-small">Videos Live)',
        rf'\g<1>{stats["total_videos"]}\2',
        content,
    )
    if n:
        changes.append(f"Deck videos live -> {stats['total_videos']}")

    content, n = re.subn(
        r'(<div class="rs-big">)\d+(</div>\s*<div class="rs-small">In Upload Queue)',
        rf'\g<1>{stats["queue_count"]}\2',
        content,
    )
    if n:
        changes.append(f"Deck queue -> {stats['queue_count']}")

    content, n = re.subn(
        r'(<div class="rs-big">)\d+ days(</div>\s*<div class="rs-small">Since Launch)',
        rf'\g<1>{stats["days_since"]} days\2',
        content,
    )
    if n:
        changes.append(f"Deck days since -> {stats['days_since']}")

    changed = content != original
    return content, changes, changed


def main():
    dry_run = "--dry-run" in sys.argv
    status_only = "--status" in sys.argv

    stats = load_stats()

    if status_only:
        print("=== Current Channel Stats ===")
        print(f"JV:  {fmt(stats['jv_subs'])} subs | {fmt(stats['jv_views'])} views | {stats['jv_videos']} videos | Top: {stats['jv_top_title']} ({fmt(stats['jv_top_views'])})")
        print(f"CiT: {fmt(stats['cit_subs'])} subs | {fmt(stats['cit_views'])} views | {stats['cit_videos']} videos | Top: {stats['cit_top_title']} ({fmt(stats['cit_top_views'])})")
        print(f"Combined: {fmt(stats['combined_views'])} views | {stats['total_videos']} videos | Queue: {stats['queue_count']} | Days: {stats['days_since']}")
        print(f"JV data: {stats['jv_date']}")
        print(f"CiT data: {stats['cit_date']}")
        return

    all_changes = []
    files_changed = []

    for filepath in [INDEX_HTML, DECK_HTML]:
        name = os.path.basename(filepath)
        content, changes, changed = patch_html(filepath, stats)
        if changed:
            files_changed.append(name)
            all_changes.extend(changes)
            if not dry_run:
                with open(filepath, "w") as f:
                    f.write(content)
                print(f"[UPDATED] {name}")
            else:
                print(f"[DRY RUN] {name} would be updated:")
            for c in changes:
                print(f"  - {c}")
        else:
            print(f"[NO CHANGE] {name} — already up to date")

    if not files_changed:
        print("\nNo changes needed — site is current.")
        return

    if dry_run:
        print(f"\n[DRY RUN] Would update {len(files_changed)} file(s). Run without --dry-run to apply.")
        return

    # Git commit + push
    print("\nCommitting + pushing to GitHub Pages...")
    date_str = datetime.now().strftime("%b %d")
    combined = round_combined(stats["combined_views"])
    msg = f"Auto-update stats {date_str} — {combined} combined views, {stats['total_videos']} videos"

    os.chdir(SCRIPT_DIR)
    subprocess.run(["git", "add"] + [os.path.basename(f) for f in [INDEX_HTML, DECK_HTML]], check=True)
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
