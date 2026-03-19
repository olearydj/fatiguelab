# Getting Started Guide

This guide covers everything you need to follow along with the demo. When in doubt about anything not covered here, ask Claude.

## The Approach

We build software in a repeating cycle:

1. Write code
2. Check that it works (run it)
3. Add tests (prove it works)
4. Commit changes (save a checkpoint)

Then repeat. Each cycle produces a working state you can always return to.

The key principle: start simple, verify, then build more. Never move forward on broken code.

## Setup

You need two tools installed: `git` (version control) and `uv` (Python project manager).

### Mac

Open Terminal (Applications → Utilities → Terminal) and run:

```bash
xcode-select --install
```

This installs git. Then install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Close and reopen Terminal so the new commands are available.

### Windows

Download and install Git from https://git-scm.com. During installation, accept the defaults.

Install uv by opening PowerShell and running:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Close and reopen PowerShell so the new commands are available.

### Verify both work

```bash
git --version
uv --version
```

Both should print a version number. If either says "command not found", close and reopen your terminal and try again.

## The Terminal

The terminal is a text-based way to interact with your computer. You type commands, press Enter, and see the output. It's how developers run code, manage files, and use tools like git.

### How to open it

- Mac: Applications → Utilities → Terminal (or press Cmd+Space and type "Terminal")
- Windows: Search for "PowerShell" in the Start menu

### Where you are

The terminal is always "in" a folder on your computer, called the working directory. When you run a command, it operates on files in that folder.

```bash
pwd               # print working directory - shows where you are
ls                # list files in the current folder
cd foldername     # change directory - move into a folder
cd ..             # go up one folder
```

### Running things

```bash
python3 script.py           # run a Python script
uv run python script.py     # run a Python script using the project's dependencies
uv run pytest tests.py      # run tests
```

### Stopping things

- Ctrl+C stops a running program (like a web server)
- Ctrl+D closes the terminal session

### Two terminals at once

When running a web app, you need the server running in one terminal and use a second terminal for other commands. Just open a new terminal window.

### Getting help

For anything else, ask Claude. "How do I _____ in the terminal?" always works.

## Version Control with Git

Git saves snapshots of your project called commits. Each commit records what changed and why. If something breaks, you can go back.

### The three commands you need

```bash
git status              # see what's changed since your last commit
git add filename.py     # stage a file to be included in the next commit
git commit -m "message" # save a snapshot with a description
```

### Reading git status

- "Untracked files" - new files git doesn't know about yet
- "Modified" - files that changed since the last commit
- "Changes to be committed" - files staged and ready for the next commit

### Viewing history

```bash
git log --oneline       # see all commits, one line each
```

## How Web Apps Work

A web app has two halves that talk to each other.

### Backend (the server)

A Python program that runs on your computer. It does the actual work: calculations, data processing, business logic. In our project, this is `app.py` wrapping `fatigue_calc.py`.

The server listens for requests and sends back responses. It speaks JSON, a structured text format that looks like this:

```json
{"cumulative_damage": 0.004871, "probability": 0.34}
```

### Frontend (the browser)

An HTML file that runs in your web browser. It's what the user sees and interacts with. Made of three parts:

- HTML defines structure - headings, buttons, forms, layout
- CSS defines style - colors, fonts, spacing, how things look
- JavaScript defines behavior - what happens when you click a button, how to fetch data from the server and update the page

In our project, this is all in `static/index.html`.

### How they connect

1. You open `http://localhost:8000` in your browser
2. The browser loads the HTML page from the server
3. When you interact (add a task, select a model), JavaScript sends a request to the server
4. The server runs the calculation and sends back JSON
5. JavaScript updates the page with the results

"localhost" means your own computer. "8000" is the port number - like a door number on a building. The server listens on that door for incoming requests.

### API endpoints

An endpoint is a specific URL the server responds to. Our app has two:

- `GET /api/models` - returns the list of available models and their input fields
- `POST /api/assess` - accepts task data, returns damage and probability results

GET means "give me information." POST means "here's some data, process it."

### Testing a web app

We test at two levels:

- Unit tests verify the math is correct (does the formula produce the right number?)
- API tests verify the server works (does the endpoint return the right response?)

The frontend is tested manually by using it in the browser. For a production app you'd add automated browser tests too, but for a demo, eyes are enough.

## Glossary

### Project terms

- cumulative damage (CD) - a number representing total tissue wear from all tasks in a workday; higher means more damage; 1.0 means theoretical failure
- damage per cycle (DPC) - how much damage one single repetition causes; tiny for light tasks, large for heavy ones
- S-N curve - a graph showing how many repetitions (N) a material can survive at a given stress level (S); the foundational relationship that drives all three models
- Palmgren-Miner rule - damage from different tasks adds up linearly; do the math for each task separately, then sum
- logistic regression - a formula that converts cumulative damage into a probability (0-100%); the final step in each model
- OMNI-RES scale - a 0-10 rating of how hard a physical exertion feels, used by the DUET model; 0 is extremely easy, 10 is extremely hard
- LiFFT - Lifting Fatigue Failure Tool; assesses low back risk from lifting
- DUET - Distal Upper Extremity Tool; assesses hand/wrist/forearm risk from repetitive exertion
- Shoulder Tool - assesses shoulder risk from reaching and handling

### Development terms

- terminal - text-based interface for running commands on your computer
- working directory - the folder the terminal is currently operating in
- git - version control system that tracks changes to files over time
- commit - a saved snapshot of your project at a point in time
- repository (repo) - a project folder tracked by git
- Python - the programming language used for the calculation engine and server
- script - a file containing code that can be run directly
- dependency - a library or package your project needs to work (e.g. FastAPI)
- uv - a tool that manages Python versions, dependencies, and project environments
- `uv run` - runs a command using the project's Python environment and dependencies

### Web terms

- server - a program that listens for requests and sends responses
- localhost - your own computer, when acting as a server
- port - a number that identifies which program on your computer should handle a request (like a door number)
- API - application programming interface; the set of endpoints the server exposes
- endpoint - a specific URL the server responds to
- JSON - a text format for structured data; how the frontend and backend communicate
- HTML - defines what's on the page (headings, buttons, text)
- CSS - defines how the page looks (colors, layout, fonts)
- JavaScript (JS) - defines what the page does (respond to clicks, fetch data, update content)
- frontend - the part that runs in the browser; what the user sees
- backend - the part that runs on the server; where the logic lives
- GET / POST - types of HTTP requests; GET retrieves data, POST sends data for processing
- FastAPI - a Python framework for building web APIs quickly
- static files - files served to the browser as-is (HTML, CSS, JS), not generated dynamically
