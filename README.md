# Daily Job Outreach Bot (runs free, forever, on GitHub Actions)

Every day this bot: finds startup websites matching your search keywords →
scrapes each site for a public HR/careers email → sends your outreach email
+ resume from tarunjit.biswas@yahoo.com → remembers who it already emailed
so no company gets contacted twice.

It runs entirely on GitHub's servers on a schedule. Your laptop does not
need to be on. No credit card / billing account is required — everything
here uses GitHub's free tier and Yahoo Mail's free SMTP.

## Setup (one-time, ~10 minutes)

### 1. Create the repo
Create a **new GitHub repository** (private is fine) and push all these files to it.

### 2. Add your resume
Put your resume file in the repo root and name it `resume.pdf`
(or change `resume_path` in `config.yaml` to match your filename).

### 3. Create a Yahoo App Password
You can't use your normal Yahoo password for this — Yahoo requires a
generated "App Password" for scripts/apps.
1. Make sure 2-Step Verification is turned on: https://login.yahoo.com/account/security
2. On that same Account Security page, find **"Generate app password"**
   (sometimes under "Other ways to sign in")
3. Create one (name it anything, e.g. "outreach-bot")
4. Copy the app password shown — you'll paste it in step 4.

### 4. Add a GitHub Secret
In your repo: **Settings → Secrets and variables → Actions → New repository secret**
Add:
- `EMAIL_APP_PASSWORD` → the app password from step 3

(Your sender address itself, `tarunjit.biswas@yahoo.com`, is already set in
`config.yaml` — only the password needs to be a secret.)

### 5. Allow the workflow to commit
The bot needs to save its "already emailed" list back to the repo.
Go to **Settings → Actions → General → Workflow permissions** and select
**"Read and write permissions"**, then Save.

### 6. Review `config.yaml`
Your subject line and full email body are already filled in exactly as you
wrote them. Things you may still want to adjust:
- `search_queries` — the kind of startups you want found
- `daily_new_candidates` / `daily_send_limit` — how many per day (default: 10 / 8)
- `exclude_domains` — add more junk domains here if you see them in results

### 7. Turn it on
Push everything to GitHub. The workflow (`.github/workflows/daily_outreach.yml`)
runs automatically every day at the scheduled time (default 9:00 AM IST —
edit the `cron:` line to change it; it's written in UTC).

You can also trigger a run manually anytime: **Actions tab → Daily Job
Outreach → Run workflow** — good for testing before you wait for the schedule.

## How deduplication works
Every domain the bot tries (successfully emailed or not) is recorded in
`data/sent_log.json` / `data/skipped_log.json`. The workflow commits these
files back to the repo after every run, so the next day's run always starts
from the up-to-date list and never re-contacts the same company.

## Costs — genuinely $0
- GitHub Actions: private repos get 2,000 free minutes/month; this job takes
  under 2 minutes/day (~60/month) — nowhere close to the limit. Public repos
  get unlimited minutes. No card required for the free tier.
- Yahoo SMTP: free, generous daily sending limits (you'll be sending far fewer
  than the cap given `daily_send_limit`).
- DuckDuckGo search + site scraping: free, no API key.

## Things to know (read this before you turn it loose)
- **Discovery isn't perfect.** Scraping the open web for a startup's public
  HR email is inherently hit-or-miss — plenty of companies don't list one
  anywhere public. Expect some days to yield only a handful of good leads,
  not a full `daily_new_candidates` worth. Tune `search_queries` over time
  based on what `data/skipped_log.json` shows you.
- **Keep volume modest.** The `daily_send_limit` default (8) is intentional —
  low-volume, personalized-looking outreach is both more effective and much
  less likely to get your account flagged than a mass blast.
- **DuckDuckGo's HTML markup can change.** If `discover.py` ever starts
  returning zero results, their result page structure likely shifted slightly
  — the regex in `scripts/discover.py` may need a small update.
- **Review the sent log early on.** Check `data/sent_log.json` after the
  first couple of runs to confirm it's finding real HR contacts and not
  junk addresses, and adjust `exclude_domains` / preferred prefixes in
  `scripts/find_email.py` as needed.
- **This sends the same fixed email to everyone it finds.** The body doesn't
  auto-insert a company name (your draft is written as a generic direct
  outreach letter, which is why). If you'd rather it open with something
  like "I came across {company}...", say so and I'll wire that back in.
