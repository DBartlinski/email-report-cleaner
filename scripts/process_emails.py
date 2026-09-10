"""
Merge Outlook CSV export(s) from exports/ into one chronological, AI-readable
Markdown file at exports/emails_organized.md.

Usage:
    python scripts/process_emails.py
    python scripts/process_emails.py --start 2025-10-01 --end 2026-09-09 --output exports/emails_2025-10-01_to_2026-09-09.md

Rerun anytime a new CSV (e.g. from ExportMailToCsv.vba) is added to exports/.
Supports two source formats automatically:
  - Outlook "Import/Export Wizard" CSV (no date column) -> date parsed from
    "Sent: <Weekday>, <Month> <Day>, <Year> ..." lines inside Body when present.
  - ExportMailToCsv.vba CSV (has ReceivedTime column) -> exact date used.
"""
import argparse
import csv
import glob
import os
import re
from datetime import datetime

EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports")
OUTPUT_PATH = os.path.join(EXPORTS_DIR, "emails_organized.md")

SAFELINK_RE = re.compile(r"<https?://[^>]*safelinks\.protection\.outlook\.com[^>]*>")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
EXCHANGE_DN_RE = re.compile(r"/[Oo]=EXCHANGELABS/\S*", re.IGNORECASE)
BLANK_LINES_RE = re.compile(r"\n{3,}")
SENT_DATE_RE = re.compile(r"Sent:\s*\w+,\s*(\w+ \d{1,2}, \d{4})")

# Known signature/disclaimer boilerplate lines to drop wherever they appear.
SIGNATURE_LINE_RES = [re.compile(p, re.IGNORECASE) for p in [
    r"^david bartlinski$",
    r"^technical information specialist$",
    r"^department of veterans affairs$",
    r"^office of research (&|and) development communications$",
    r"^vha discovery, education,? and affiliate networks$",
    r"^george h\.? fallon federal building$",
    r"^31 hopkins plaza.*baltimore, md 21201$",
    r"^cell:\s*\+?1?[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{4}$",
    r"^https?://www\.research\.va\.gov/?\s*$",
    r"^sent from my (iphone|ipad|android|galaxy|mobile device)\.?$",
    r"^get outlook for (ios|android)$",
]]


def strip_signature_lines(text):
    kept = [line for line in text.split("\n")
            if not any(p.match(line.strip()) for p in SIGNATURE_LINE_RES)]
    return "\n".join(kept)


# Matches the quoted-history header Outlook inserts above a prior message in a thread.
QUOTE_BLOCK_START_RE = re.compile(
    r"\n\s*From:.*?\n\s*Sent:.*?\n(?:\s*To:.*?\n)?(?:\s*Cc:.*?\n)?\s*Subject:.*?\n",
    re.IGNORECASE | re.DOTALL,
)


def truncate_quoted_history(text):
    match = QUOTE_BLOCK_START_RE.search(text)
    if not match:
        return text
    new_content = text[:match.start()].strip()
    note = "*(quoted prior message(s) in this thread omitted — see their own dated entries)*"
    return f"{new_content}\n\n{note}" if new_content else note


def clean_body(text):
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = SAFELINK_RE.sub("", text)
    text = EXCHANGE_DN_RE.sub("", text)
    text = EMAIL_RE.sub("[redacted-email]", text)
    text = strip_signature_lines(text)
    text = truncate_quoted_history(text)
    # Whitespace-only lines (Outlook uses these as visual spacers) count as blank too.
    text = "\n".join(line if line.strip() else "" for line in text.split("\n"))
    text = BLANK_LINES_RE.sub("\n\n", text)
    return text.strip()


def redact_name(name):
    return EMAIL_RE.sub("[redacted-email]", name or "").strip()


def parse_date(row):
    # New format: explicit ReceivedTime column from the VBA export.
    received = row.get("ReceivedTime")
    if received:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %I:%M:%S %p"):
            try:
                return datetime.strptime(received.strip(), fmt)
            except ValueError:
                continue

    # Fallback: dig a date out of a forwarded/replied "Sent:" line in the body.
    body = row.get("Body") or ""
    match = SENT_DATE_RE.search(body)
    if match:
        try:
            return datetime.strptime(match.group(1), "%B %d, %Y")
        except ValueError:
            pass
    return None


def load_rows(csv_path):
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def build_email_record(row):
    date = parse_date(row)
    from_name = redact_name(row.get("SenderName") or row.get("From: (Name)"))
    to_name = redact_name(row.get("ToNames") or row.get("To: (Name)"))
    cc_name = redact_name(row.get("CcNames") or row.get("CC: (Name)"))
    return {
        "date": date,
        "subject": (row.get("Subject") or "(no subject)").strip(),
        "from": from_name,
        "to": to_name,
        "cc": cc_name,
        "body": clean_body(row.get("Body")),
    }


def render_email(record):
    header = f"### {record['date'].strftime('%Y-%m-%d')} — {record['subject']}" if record["date"] \
        else f"### (undated) — {record['subject']}"
    meta_parts = [f"**From:** {record['from']}" if record["from"] else None,
                  f"**To:** {record['to']}" if record["to"] else None,
                  f"**Cc:** {record['cc']}" if record["cc"] else None]
    meta = "  \n".join(p for p in meta_parts if p)
    lines = [header]
    if meta:
        lines.append(meta)
    lines.append("")
    lines.append(record["body"] or "*(empty body)*")
    lines.append("\n---\n")
    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", help="Only include dated emails on/after this date (YYYY-MM-DD)")
    parser.add_argument("--end", help="Only include dated emails on/before this date (YYYY-MM-DD)")
    parser.add_argument("--output", help="Output markdown path (default: exports/emails_organized.md)")
    return parser.parse_args()


def build_markdown(csv_paths, start=None, end=None, include_undated=False):
    dated, undated = [], []
    out_of_range = 0
    for path in csv_paths:
        for row in load_rows(path):
            record = build_email_record(row)
            if not record["date"]:
                undated.append(record)
            elif (start and record["date"] < start) or (end and record["date"] > end):
                out_of_range += 1
            else:
                dated.append(record)

    dated.sort(key=lambda r: r["date"])

    months = {}
    for record in dated:
        key = record["date"].strftime("%Y-%m")
        months.setdefault(key, []).append(record)

    out = ["# Email Archive — Organized for Review\n"]
    for month_key in sorted(months):
        label = datetime.strptime(month_key, "%Y-%m").strftime("%B %Y")
        out.append(f"## {month_key} ({label})\n")
        for record in months[month_key]:
            out.append(render_email(record))

    if undated and include_undated:
        out.append("## Undated (needs manual review)\n")
        for record in undated:
            out.append(render_email(record))

    markdown = "\n".join(out)
    stats = {
        "total": len(dated) + len(undated) + out_of_range,
        "included": len(dated) + (len(undated) if include_undated else 0),
        "dated": len(dated),
        "undated": len(undated),
        "out_of_range": out_of_range,
    }
    return markdown, stats


def main():
    args = parse_args()
    start = datetime.strptime(args.start, "%Y-%m-%d") if args.start else None
    end = datetime.strptime(args.end, "%Y-%m-%d").replace(hour=23, minute=59, second=59) if args.end else None
    output_path = args.output or OUTPUT_PATH

    csv_paths = sorted(set(glob.glob(os.path.join(EXPORTS_DIR, "*.csv"))) |
                        set(glob.glob(os.path.join(EXPORTS_DIR, "*.CSV"))))
    if not csv_paths:
        print(f"No CSV files found in {EXPORTS_DIR}")
        return

    markdown, stats = build_markdown(csv_paths, start, end, include_undated=not (start or end))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Processed {stats['total']} emails from {len(csv_paths)} file(s).")
    print(f"  In range:    {stats['dated']}")
    print(f"  Undated:     {stats['undated']}{'  (excluded from date-filtered output)' if (start or end) else ''}")
    print(f"  Out of range: {stats['out_of_range']}")
    print(f"Output written to {output_path}")


if __name__ == "__main__":
    main()
