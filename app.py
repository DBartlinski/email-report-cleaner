import csv
import os
import tempfile
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from scripts.process_emails import build_markdown

ROOT = Path(__file__).resolve().parent
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 250 * 1024 * 1024


def parse_day(value, end_of_day=False):
    parsed = datetime.strptime(value, "%Y-%m-%d")
    if end_of_day:
        parsed = parsed.replace(hour=23, minute=59, second=59)
    return parsed


def validate_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as source:
        headers = csv.DictReader(source).fieldnames or []
    missing = {"Subject", "Body"} - set(headers)
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(sorted(missing))}")


@app.get("/")
def index():
    return render_template("index.html", today=datetime.now().date().isoformat())


@app.post("/api/convert")
def convert():
    uploads = [item for item in request.files.getlist("files") if item.filename]
    if not uploads:
        return jsonify(error="Choose at least one Outlook CSV file."), 400

    start_value = request.form.get("start", "").strip()
    end_value = request.form.get("end", "").strip()
    if not start_value or not end_value:
        return jsonify(error="Choose both a start date and an end date."), 400

    try:
        start = parse_day(start_value)
        end = parse_day(end_value, end_of_day=True)
    except ValueError:
        return jsonify(error="Dates must use YYYY-MM-DD format."), 400
    if start > end:
        return jsonify(error="The start date must be on or before the end date."), 400

    try:
        with tempfile.TemporaryDirectory(prefix="email-report-cleaner-") as temp_dir:
            paths = []
            for index, upload in enumerate(uploads):
                if Path(upload.filename).suffix.lower() != ".csv":
                    return jsonify(error=f"{upload.filename} is not a CSV file."), 400
                path = os.path.join(temp_dir, f"upload-{index}.csv")
                upload.save(path)
                validate_csv(path)
                paths.append(path)

            markdown, stats = build_markdown(paths, start=start, end=end, include_undated=False)
    except (UnicodeDecodeError, csv.Error) as error:
        return jsonify(error=f"A CSV could not be read: {error}"), 400
    except ValueError as error:
        return jsonify(error=str(error)), 400

    filename = f"emails_organized_{start_value}_to_{end_value}.md"
    return jsonify(markdown=markdown, stats=stats, filename=filename, files=len(uploads))


@app.errorhandler(413)
def too_large(_error):
    return jsonify(error="The combined upload is larger than 250 MB."), 413


if __name__ == "__main__":
    url = "http://127.0.0.1:5179"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=5179, debug=False)
