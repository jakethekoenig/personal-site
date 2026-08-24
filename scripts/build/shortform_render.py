"""Shared rendering helpers for short-form cards and pages."""

import html as html_lib
from datetime import datetime, timezone
from urllib.parse import urlparse


TWITTER_ICON_SVG = '''<svg class="twitter-icon" viewBox="0 0 24 24" width="16" height="16">
    <path fill="#1da1f2" d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
</svg>'''


def post_service(url):
    """Identify the service for a public post URL."""
    hostname = urlparse(url).hostname or ""
    hostname = hostname.lower().removeprefix("www.")
    if hostname in {"twitter.com", "x.com"}:
        return "twitter"
    if hostname == "bsky.app":
        return "bluesky"
    return "other"


def source_links_html(post_data):
    """Render one source link per service from the first logical post."""
    posts = post_data.get("posts") or []
    urls = posts[0] if posts and isinstance(posts[0], list) else []
    links = []
    rendered_services = set()
    for url in urls:
        service = post_service(url)
        if service in rendered_services:
            continue
        rendered_services.add(service)
        escaped_url = html_lib.escape(url, quote=True)
        if service == "bluesky":
            links.append(
                '<a href="%s" target="_blank" class="tweet-bluesky-link" '
                'title="View original post on Bluesky">'
                '<span class="post-source">Bluesky</span></a>' % escaped_url
            )
        elif service == "twitter":
            links.append(
                '<a href="%s" target="_blank" class="tweet-twitter-link" '
                'title="View original post on X">%s</a>'
                % (escaped_url, TWITTER_ICON_SVG)
            )
        else:
            links.append(
                '<a href="%s" target="_blank" class="tweet-source-link" '
                'title="View original post">Source</a>' % escaped_url
            )
    return "".join(links)


def shortform_sort_key(post_data):
    """Sort by the precise source timestamp, then by the source's sortable ID."""
    value = post_data.get("original_date")
    parsed = None

    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            try:
                parsed = datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y")
            except ValueError:
                pass

    if parsed is None:
        value = post_data.get("Date", "")
        for date_format in ("%Y-%m-%d", "%m/%d/%Y"):
            try:
                parsed = datetime.strptime(value, date_format).replace(
                    tzinfo=timezone.utc,
                )
                break
            except ValueError:
                pass

    timestamp = parsed.timestamp() if parsed is not None else float("-inf")
    return timestamp, str(post_data.get("tweet_id", ""))


def parse_thread_parts(thread_content):
    if not thread_content.startswith("# Thread"):
        return []

    parts = []
    for section in thread_content.split("## Tweet ")[1:]:
        if not section.strip():
            continue
        lines = section.splitlines()
        content_lines = []
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.strip():
                content_lines.append(line)
        if content_lines:
            parts.append("\n".join(content_lines).strip())
    return parts


def render_thread_content(thread_content, render_markdown, fallback=""):
    parts = parse_thread_parts(thread_content)
    if not parts:
        parts = [fallback]

    rendered_parts = []
    for part in parts:
        rendered = render_markdown(part).replace(
            "<img ", '<img class="tweet-image" ',
        )
        rendered_parts.append(
            """
            <div class="thread-tweet">
                <div class="thread-tweet-number"></div>
                <div class="thread-tweet-content">
                    %s
                </div>
            </div>
            """ % rendered
        )

    return '<div class="thread-content">\n%s\n</div>' % "".join(rendered_parts)


def thread_indicator_text(thread_data):
    count = thread_data.get("thread_length", 1)
    noun = "post"
    if count != 1:
        noun += "s"
    return f"🧵 Thread ({count} {noun})"
