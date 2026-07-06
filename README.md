# Restaurant Bon Printer

Automatically prints kitchen/sushi/bar tickets when an order comes in from Glide or n8n.

---

## Project structure

```
restaurant-bon-printer/
├── bon_printer.py   # Logic to build + send ESC/POS tickets
├── app.py           # FastAPI web service (backend)
├── requirements.txt # Python dependencies
├── .gitignore       # Files not to commit to GitHub
└── README.md        # This file
```

---

## STEP 0 — Git setup (your current exercise)

These are the first Git commands you'll run on a real project.
Run them one by one in a terminal (WSL or Linux):

```bash
# 1. Create the project folder and cd into it
mkdir restaurant-bon-printer
cd restaurant-bon-printer

# 2. Copy the 4 files into this folder (bon_printer.py, app.py, requirements.txt, .gitignore)

# 3. Initialize a Git repo
git init

# 4. Check status — you should see 4 "untracked" files
git status

# 5. Stage all files (add them to the "commit staging area")
git add .

# 6. Check again — files should now be green (staged)
git status

# 7. First commit — clear message, written in present tense
git commit -m "feat: add bon printer service with FastAPI endpoint"

# 8. View commit history
git log --oneline
```

Next, push to GitHub:

```bash
# Create a new repo on github.com (name it: restaurant-bon-printer, keep it Private)
# Then run the commands GitHub suggests, something like:

git remote add origin https://github.com/YOUR_USERNAME/restaurant-bon-printer.git
git branch -M main
git push -u origin main
```

**Checkpoint:** Go to github.com, open your repo, and see the 4 files there = you've completed this step.

---

## STEP 1 — Test offline (no printer needed)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dry_run test — simulated printing to the terminal
python bon_printer.py
```

You should see 3 tickets printed to the screen for table 5.

---

## STEP 2 — Run the web service

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser: http://localhost:8000/docs
→ FastAPI auto-generates a test API page here (Swagger UI).

Test with curl:

```bash
curl -X POST http://localhost:8000/order \
  -H "Content-Type: application/json" \
  -d '{
    "ban": "5",
    "dry_run": true,
    "items": [
      {"ten": "Edamame",       "so_luong": 1, "tram": "bep"},
      {"ten": "Ramen bo",      "so_luong": 2, "tram": "bep"},
      {"ten": "Salmon nigiri", "so_luong": 4, "tram": "sushi"},
      {"ten": "Tra xanh",      "so_luong": 2, "tram": "bar"}
    ]
  }'
```

---

## STEP 3 — Plug in a real printer

1. Buy a thermal printer with a LAN port (recommended: Xprinter XP-C300H, ~2.2 million VND)
2. Plug it into the router, go to the router's admin page and assign a static IP to the printer
3. Edit `PRINTER_CONFIG` in `bon_printer.py`:
   ```python
   PRINTER_CONFIG = {
       "bep":   {"ip": "192.168.1.101", "port": 9100},
       "sushi": {"ip": "192.168.1.102", "port": 9100},
   }
   ```
4. Test the connection:
   ```bash
   # If you get a response = the printer is online
   nc -zv 192.168.1.101 9100
   ```
5. Re-run the curl command above with `"dry_run": false`

---

## Learning roadmap through this project

| Stage        | What you learn       | Applied to the project                        |
|--------------|-----------------------|------------------------------------------------|
| **Current**  | Git & GitHub          | Init repo, commit, push to GitHub               |
| Stage 3      | Python + SQL          | Add a database to store orders per table, compute bills |
| Stage 4      | Backend + REST API    | Add auth, menu CRUD endpoints, connect to Glide |
| Stage 5      | Claude Code           | Use AI to write tests, refactor, debug          |
| Stage 6      | AI Agents             | Agent auto-suggests upsells, detects losses     |

Each stage, you'll open a new branch, finish the work, and merge into main — following a real Git workflow.
