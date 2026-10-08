# Telegram Job Application Agent

A local-first V1 for monitoring a private Telegram job group with your own Telegram account, extracting jobs with a local LLM, scoring them against your master profile, and generating a tailored LaTeX resume/PDF.

## What it does

Telegram private group -> Telethon user client -> local Ollama -> job extraction -> candidate match -> tailored resume -> PDF -> review queue.

V1 deliberately does **not** auto-submit applications. It also does not bypass CAPTCHAs, OTPs, login challenges, or anti-bot controls, and it never invents candidate facts.

## Windows setup

### 1. Clone

```powershell
git clone https://github.com/priyanshiiitr/AI_JOB_SEARCH.git
cd AI_JOB_SEARCH
```

### 2. Python environment

```powershell
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

### 3. Telegram API credentials

Go to https://my.telegram.org -> API development tools and create an app.

Copy `.env.example` to `.env` and fill in:

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_PHONE`

Then discover your chat IDs:

```powershell
python scripts/list_chats.py
```

Copy the private group's/channel's numeric ID into `JOB_GROUP_ID`.

### 4. Local AI

Install Ollama, then:

```powershell
ollama pull qwen3:4b
```

Keep Ollama running before starting the agent.

### 5. Candidate profile

Edit `data/master_profile.md` and add your real education, experience, projects and skills. This is the source of truth used for resume tailoring.

Put your contact details in `.env`.

### 6. Start the agent

```powershell
python -m app.main
```

The first run will ask you for your Telegram login code and, when enabled, your Telegram 2FA password. A Telethon session is stored under `sessions/`; never commit it.

## Output

Generated `.tex` files are written to `output/resumes/`.

If `pdflatex` is installed and available on PATH, a PDF is generated automatically too. On Windows, MiKTeX is an easy way to install a LaTeX compiler.

## Next V2

The intended next layer is: one-click review -> personalized HR email -> Playwright adapters for supported application portals -> application tracking. These should remain human-approved at first.
