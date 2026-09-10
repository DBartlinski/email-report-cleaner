# Email Report Cleaner

Convert Outlook CSV exports to clean, review-ready Markdown files.

## Features

- **Filters** emails by date range
- **Redacts** email addresses and routing IDs for privacy
- **Removes** SafeLink tracking, signatures, and excess spacing
- **Strips** quoted reply history (keeps only new content)
- **Excludes** undated and out-of-range messages
- **Outputs** organized Markdown with summary statistics

## Privacy

✅ **100% Local Processing** — Files are processed on your machine and never leave your device.

## Installation

### Requirements
- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/EMAIL-REPORT-CLEANER.git
   cd EMAIL-REPORT-CLEANER
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Option 1: GUI (Recommended)

**Windows:**
- Double-click `Start Email Report Cleaner.bat`

**macOS/Linux:**
```bash
python app.py
```

Then open your browser to `http://127.0.0.1:5000` and:
1. Upload your Outlook CSV files
2. Set the date range
3. Click "Clean and convert"
4. Download the Markdown file

### Option 2: Command Line

```bash
python app.py
# Then visit http://127.0.0.1:5000 in your browser
```

## Exporting from Outlook

To export emails as CSV:

1. Open Outlook
2. Select the folder you want to export
3. File → Open & Export → Import/Export
4. Choose "Export to a file" → "Comma Separated Values"
5. Save the file
6. Upload to this tool

## Project Structure

```
.
├── app.py                  # Flask web application
├── requirements.txt        # Python dependencies
├── Start Email Report Cleaner.bat  # Windows launcher
├── templates/
│   └── index.html         # Web interface
├── static/
│   ├── app.js            # Frontend logic
│   └── styles.css        # Styling
└── scripts/
    └── process_emails.py  # Core email processing logic
```

## Building & Deployment

### Local Development
```bash
python app.py
```

### Deploy to Render.com (Free)

1. Push to GitHub
2. Create account at [render.com](https://render.com)
3. Create new Web Service
4. Connect your GitHub repo
5. Set Build Command: `pip install -r requirements.txt`
6. Set Start Command: `gunicorn app:app`
7. Deploy

### Deploy to Heroku

```bash
heroku login
heroku create your-app-name
git push heroku main
heroku open
```

## Technologies

- **Backend:** Python Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Processing:** Email parsing and Markdown generation

## License

MIT License — Feel free to use and modify.

## Support

For issues or suggestions, please create an issue on GitHub.
