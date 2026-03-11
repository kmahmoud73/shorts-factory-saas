#!/usr/bin/env python3
"""
update_site_stats.py — Auto-update shortsfactory.io with latest channel stats.

Reads from shorts-factory analytics JSONs, patches index.html + deck.html,
commits + pushes to GitHub Pages. Includes WoW + all-time % change indicators.

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
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SF_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "shorts-factory")
JV_STATS = os.path.join(SF_DIR, "analytics", "channel_stats.json")
CIT_STATS = os.path.join(SF_DIR, "analytics", "cit_channel_stats.json")
UPLOAD_QUEUE = os.path.join(SF_DIR, ".trending_upload_queue.json")
INDEX_HTML = os.path.join(SCRIPT_DIR, "index.html")
DECK_HTML = os.path.join(SCRIPT_DIR, "deck.html")
LAUNCH_DATE = datetime(2026, 2, 19)


def _get_snap_views(snap):
    """Get total views from a snapshot, handling both JV and CiT formats."""
    return snap.get("total_views") or snap.get("total_views_shorts", 0)


def _get_snap_videos(snap):
    """Get video count from a snapshot, handling both formats."""
    if "video_count" in snap:
        return snap["video_count"]
    vids = snap.get("videos", {})
    return len(vids) if isinstance(vids, dict) else 0


def find_snapshot_ago(snapshots, days):
    """Find snapshot closest to N days before the latest snapshot."""
    if len(snapshots) < 2:
        return None
    latest_date = snapshots[-1]["date"][:10]
    target_dt = datetime.strptime(latest_date, "%Y-%m-%d") - timedelta(days=days)
    best = None
    best_diff = float("inf")
    for s in snapshots[:-1]:  # exclude latest itself
        s_dt = datetime.strptime(s["date"][:10], "%Y-%m-%d")
        diff = abs((s_dt - target_dt).days)
        if diff < best_diff:
            best_diff = diff
            best = s
    return best if best_diff <= 3 else None  # within 3 days tolerance


def calc_pct(current, previous):
    """Calculate percentage change. Returns None if not meaningful."""
    if previous is None or previous == 0:
        return None
    if current == previous:
        return 0.0
    return ((current - previous) / previous) * 100


def fmt_pct(pct):
    """Format percentage with sign. Returns (text, css_class).
    Extreme values (>999%) shown as multipliers (e.g., '31x')."""
    if pct is None:
        return "--", "delta-flat"
    if pct == 0:
        return "0%", "delta-flat"
    cls = "delta-up" if pct > 0 else "delta-down"
    sign = "+" if pct > 0 else ""
    if abs(pct) > 999:
        mult = abs(pct) / 100
        return f"{mult:,.0f}x", cls
    if abs(pct) >= 100:
        return f"{sign}{pct:.0f}%", cls
    return f"{sign}{pct:.1f}%", cls


def build_delta_html(wow_pct, at_pct):
    """Build the inner HTML for a delta div: weekly + all-time indicators."""
    wow_text, wow_cls = fmt_pct(wow_pct)
    at_text, at_cls = fmt_pct(at_pct)
    wow_label = f"{wow_text} wk" if wow_text != "--" else "--"
    at_label = f"{at_text} total" if at_text != "--" else "--"
    return (
        f'<span class="wow {wow_cls}">{wow_label}</span>'
        f'<span class="sep">&middot;</span>'
        f'<span class="at {at_cls}">{at_label}</span>'
    )


def load_stats():
    """Load latest stats from both channel JSON files + compute deltas."""
    with open(JV_STATS) as f:
        jv_data = json.load(f)
    with open(CIT_STATS) as f:
        cit_data = json.load(f)

    jv_snaps = jv_data["snapshots"]
    cit_snaps = cit_data["snapshots"]
    jv_latest = jv_snaps[-1]
    cit_latest = cit_snaps[-1]

    jv_top = sorted(jv_latest["per_video"], key=lambda x: x["views"], reverse=True)[0]
    cit_top = sorted(cit_latest["per_video"], key=lambda x: x["views"], reverse=True)[0]

    queue_count = 0
    if os.path.exists(UPLOAD_QUEUE):
        with open(UPLOAD_QUEUE) as f:
            queue_count = len(json.load(f))

    days_since = (datetime.now() - LAUNCH_DATE).days

    # Current values
    jv_subs = jv_data["channel"]["subscribers"]
    jv_views = _get_snap_views(jv_latest)
    jv_videos = _get_snap_videos(jv_latest)
    cit_subs = cit_data["channel"]["subscribers"]
    cit_views = _get_snap_views(cit_latest)
    cit_videos = _get_snap_videos(cit_latest)

    # WoW snapshots (7 days ago)
    jv_week = find_snapshot_ago(jv_snaps, 7)
    cit_week = find_snapshot_ago(cit_snaps, 7)

    # All-time: first snapshot
    jv_first = jv_snaps[0] if jv_snaps else None
    cit_first = cit_snaps[0] if cit_snaps else None

    # Compute deltas
    def deltas(current, week_snap, first_snap, getter):
        week_val = getter(week_snap) if week_snap else None
        first_val = getter(first_snap) if first_snap else None
        wow = calc_pct(current, week_val)
        at = calc_pct(current, first_val)
        return wow, at

    jv_subs_wow, jv_subs_at = deltas(jv_subs, jv_week, jv_first, lambda s: s.get("subscribers", 0))
    jv_views_wow, jv_views_at = deltas(jv_views, jv_week, jv_first, _get_snap_views)
    jv_vids_wow, jv_vids_at = deltas(jv_videos, jv_week, jv_first, _get_snap_videos)

    cit_subs_wow, cit_subs_at = deltas(cit_subs, cit_week, cit_first, lambda s: s.get("subscribers", 0))
    cit_views_wow, cit_views_at = deltas(cit_views, cit_week, cit_first, _get_snap_views)
    cit_vids_wow, cit_vids_at = deltas(cit_videos, cit_week, cit_first, _get_snap_videos)

    return {
        "jv_subs": jv_subs,
        "jv_views": jv_views,
        "jv_videos": jv_videos,
        "jv_top_title": jv_top["title"],
        "jv_top_views": jv_top["views"],
        "cit_subs": cit_subs,
        "cit_views": cit_views,
        "cit_videos": cit_videos,
        "cit_top_title": cit_top["title"],
        "cit_top_views": cit_top["views"],
        "combined_views": jv_views + cit_views,
        "total_videos": jv_videos + cit_videos,
        "queue_count": queue_count,
        "days_since": days_since,
        "jv_date": jv_latest["date"],
        "cit_date": cit_latest["date"],
        # Delta HTML strings (pre-built for injection)
        "jv_subs_delta": build_delta_html(jv_subs_wow, jv_subs_at),
        "jv_views_delta": build_delta_html(jv_views_wow, jv_views_at),
        "jv_vids_delta": build_delta_html(jv_vids_wow, jv_vids_at),
        "cit_subs_delta": build_delta_html(cit_subs_wow, cit_subs_at),
        "cit_views_delta": build_delta_html(cit_views_wow, cit_views_at),
        "cit_vids_delta": build_delta_html(cit_vids_wow, cit_vids_at),
        # Raw percentages for status display
        "_deltas": {
            "jv_subs": (jv_subs_wow, jv_subs_at),
            "jv_views": (jv_views_wow, jv_views_at),
            "jv_videos": (jv_vids_wow, jv_vids_at),
            "cit_subs": (cit_subs_wow, cit_subs_at),
            "cit_views": (cit_views_wow, cit_views_at),
            "cit_videos": (cit_vids_wow, cit_vids_at),
        },
    }


def fmt(n):
    """Format number with commas."""
    return f"{n:,}"


def round_combined(n):
    """Round combined views to nearest 100 with + suffix."""
    rounded = (n // 100) * 100
    return f"{fmt(rounded)}+"


def patch_html(filepath, stats):
    """Patch an HTML file with updated stats + deltas. Returns (new_content, changes_made)."""
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

    # JV result card block (index.html format) — .*? tolerates delta divs
    content, n = re.subn(
        r'(<div class="channel-name jv">The Jersey Vault</div>.*?'
        r'<div class="rs-value">)[\d,]+(</div>.*?<div class="rs-label">Subscribers</div>.*?'
        r'<div class="rs-value">)[\d,]+(</div>.*?<div class="rs-label">Total Views</div>.*?'
        r'<div class="rs-value">)[\d,]+(</div>.*?<div class="rs-label">Videos</div>)',
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
        r'<div class="rs-value">)[\d,]+(</div>.*?<div class="rs-label">Subscribers</div>.*?'
        r'<div class="rs-value">)[\d,]+(</div>.*?<div class="rs-label">Total Views</div>.*?'
        r'<div class="rs-value">)[\d,]+(</div>.*?<div class="rs-label">Videos</div>)',
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

    # --- INDEX.HTML delta patches (all 3 per channel in single pass) ---
    content, n = re.subn(
        r'(<div class="channel-name jv">The Jersey Vault</div>.*?'
        r'<div class="rs-delta">).*?(</div>\s*<div class="rs-label">Subscribers</div>.*?'
        r'<div class="rs-delta">).*?(</div>\s*<div class="rs-label">Total Views</div>.*?'
        r'<div class="rs-delta">).*?(</div>\s*<div class="rs-label">Videos</div>)',
        rf'\1{stats["jv_subs_delta"]}\2{stats["jv_views_delta"]}\3{stats["jv_vids_delta"]}\4',
        content, count=1, flags=re.DOTALL,
    )
    if n:
        changes.append("JV deltas updated (subs/views/videos)")

    content, n = re.subn(
        r'(<div class="channel-name cit">Caught It Trending</div>.*?'
        r'<div class="rs-delta">).*?(</div>\s*<div class="rs-label">Subscribers</div>.*?'
        r'<div class="rs-delta">).*?(</div>\s*<div class="rs-label">Total Views</div>.*?'
        r'<div class="rs-delta">).*?(</div>\s*<div class="rs-label">Videos</div>)',
        rf'\1{stats["cit_subs_delta"]}\2{stats["cit_views_delta"]}\3{stats["cit_vids_delta"]}\4',
        content, count=1, flags=re.DOTALL,
    )
    if n:
        changes.append("CiT deltas updated (subs/views/videos)")

    # --- Channel age badges (index.html: channel-age, deck.html: cc-age) ---
    age_text = f'Live for {stats["days_since"]} days'
    content, n = re.subn(
        r'(<div class="(?:channel-age|cc-age)">)Live for \d+ days(</div>)',
        rf'\g<1>{age_text}\2',
        content,
    )
    if n:
        changes.append(f"Channel age -> {age_text}")

    # --- DECK.HTML patterns ---

    # JV card (deck format)
    content, n = re.subn(
        r'(<div class="cc-name jv">The Jersey Vault</div>.*?'
        r'<div class="cc-val">)[\d,]+(</div>.*?<div class="cc-lbl">Subscribers</div>.*?'
        r'<div class="cc-val">)[\d,]+(</div>.*?<div class="cc-lbl">Views</div>.*?'
        r'<div class="cc-val">)[\d,]+(</div>.*?<div class="cc-lbl">Videos</div>)',
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
        r'<div class="cc-val">)[\d,]+(</div>.*?<div class="cc-lbl">Subscribers</div>.*?'
        r'<div class="cc-val">)[\d,]+(</div>.*?<div class="cc-lbl">Views</div>.*?'
        r'<div class="cc-val">)[\d,]+(</div>.*?<div class="cc-lbl">Videos</div>)',
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

    # --- DECK.HTML delta patches (all 3 per channel in single pass) ---
    content, n = re.subn(
        r'(<div class="cc-name jv">The Jersey Vault</div>.*?'
        r'<div class="cc-delta">).*?(</div>\s*<div class="cc-lbl">Subscribers</div>.*?'
        r'<div class="cc-delta">).*?(</div>\s*<div class="cc-lbl">Views</div>.*?'
        r'<div class="cc-delta">).*?(</div>\s*<div class="cc-lbl">Videos</div>)',
        rf'\1{stats["jv_subs_delta"]}\2{stats["jv_views_delta"]}\3{stats["jv_vids_delta"]}\4',
        content, count=1, flags=re.DOTALL,
    )
    if n:
        changes.append("Deck JV deltas updated (subs/views/videos)")

    content, n = re.subn(
        r'(<div class="cc-name cit">Caught It Trending</div>.*?'
        r'<div class="cc-delta">).*?(</div>\s*<div class="cc-lbl">Subscribers</div>.*?'
        r'<div class="cc-delta">).*?(</div>\s*<div class="cc-lbl">Views</div>.*?'
        r'<div class="cc-delta">).*?(</div>\s*<div class="cc-lbl">Videos</div>)',
        rf'\1{stats["cit_subs_delta"]}\2{stats["cit_views_delta"]}\3{stats["cit_vids_delta"]}\4',
        content, count=1, flags=re.DOTALL,
    )
    if n:
        changes.append("Deck CiT deltas updated (subs/views/videos)")

    changed = content != original
    return content, changes, changed


def main():
    dry_run = "--dry-run" in sys.argv
    status_only = "--status" in sys.argv

    stats = load_stats()

    if status_only:
        d = stats["_deltas"]
        print("=== Current Channel Stats ===")
        print(f"JV:  {fmt(stats['jv_subs'])} subs ({fmt_pct(d['jv_subs'][0])[0]} wk / {fmt_pct(d['jv_subs'][1])[0]} total)")
        print(f"     {fmt(stats['jv_views'])} views ({fmt_pct(d['jv_views'][0])[0]} wk / {fmt_pct(d['jv_views'][1])[0]} total)")
        print(f"     {stats['jv_videos']} videos ({fmt_pct(d['jv_videos'][0])[0]} wk / {fmt_pct(d['jv_videos'][1])[0]} total)")
        print(f"     Top: {stats['jv_top_title']} ({fmt(stats['jv_top_views'])})")
        print(f"CiT: {fmt(stats['cit_subs'])} subs ({fmt_pct(d['cit_subs'][0])[0]} wk / {fmt_pct(d['cit_subs'][1])[0]} total)")
        print(f"     {fmt(stats['cit_views'])} views ({fmt_pct(d['cit_views'][0])[0]} wk / {fmt_pct(d['cit_views'][1])[0]} total)")
        print(f"     {stats['cit_videos']} videos ({fmt_pct(d['cit_videos'][0])[0]} wk / {fmt_pct(d['cit_videos'][1])[0]} total)")
        print(f"     Top: {stats['cit_top_title']} ({fmt(stats['cit_top_views'])})")
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
