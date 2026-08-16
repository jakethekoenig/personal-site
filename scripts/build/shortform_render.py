"""Shared rendering helpers for short-form thread cards and pages."""

from datetime import datetime, timezone


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
    noun = "post" if thread_data.get("source") == "bluesky" else "tweet"
    if count != 1:
        noun += "s"
    return f"🧵 Thread ({count} {noun})"
