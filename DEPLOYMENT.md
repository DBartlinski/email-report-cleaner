# Push to GitHub

Follow these steps to push your project to GitHub.

## 1. Create a GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Name: `email-report-cleaner` (or whatever you prefer)
3. Description: "Convert Outlook CSV exports to clean Markdown files"
4. Choose Public or Private
5. Click "Create repository"

## 2. Initialize Git Locally

```bash
cd "path/to/End of year"
git init
git add .
git commit -m "Initial commit: Email Report Cleaner"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/email-report-cleaner.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your actual GitHub username.

## 3. Verify on GitHub

- Go to your GitHub repo
- You should see all files uploaded
- README.md will display automatically

## 4. Deploy (Optional)

### To Render.com (Recommended for this app)

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Fill in:
   - **Name:** `email-report-cleaner`
   - **Build Command:** `pip install -r requirements.txt && pip install gunicorn`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3
6. Click "Create Web Service"
7. Render will deploy automatically on every push to main

Your app will be live at: `https://your-app-name.onrender.com`

### To Heroku

```bash
heroku login
heroku create email-report-cleaner
pip install gunicorn
echo "gunicorn==22.0.0" >> requirements.txt
git add requirements.txt
git commit -m "Add gunicorn for production"
git push origin main
git push heroku main
heroku open
```

## 5. Share

Send others:
- The GitHub link: `https://github.com/YOUR-USERNAME/email-report-cleaner`
- Or the deployed URL if you deployed to Render/Heroku

## Note

Your **local version stays unchanged** — this just uploads to GitHub.
