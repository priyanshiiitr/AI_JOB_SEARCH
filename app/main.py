import asyncio
import json
from pathlib import Path
from telethon import TelegramClient, events
from .ai import extract_job, score_job, tailor_resume
from .config import JOB_GROUP_ID, MIN_MATCH_SCORE, SESSION_DIR, TELEGRAM_API_HASH, TELEGRAM_API_ID, TELEGRAM_PHONE, BASE_DIR
from .db import init_db, insert_job, update_job_match, insert_application
from .resume import render_resume

PROFILE_PATH = BASE_DIR / 'data' / 'master_profile.md'


async def process_job(message_id, raw_text):
    try:
        print('\n[1/5] Extracting job...')
        job = await extract_job(raw_text)
        print(f'      {job.company} | {job.role}')

        job_id = insert_job(job.model_dump(), message_id, raw_text)
        if job_id is None:
            print('[skip] Duplicate Telegram message.')
            return

        profile = PROFILE_PATH.read_text(encoding='utf-8')

        print('[2/5] Matching candidate...')
        match = await score_job(job, profile)
        status = 'READY' if match.score >= MIN_MATCH_SCORE else 'LOW_MATCH'
        update_job_match(job_id, match.score, status)
        print(f'      Match score: {match.score}/100')

        if match.score < MIN_MATCH_SCORE:
            print('[skip] Below MIN_MATCH_SCORE.')
            return

        print('[3/5] Tailoring resume...')
        resume_data = await tailor_resume(job, profile)

        contact = {
            'name': __import__('os').getenv('CANDIDATE_NAME', 'Candidate'),
            'email': __import__('os').getenv('CANDIDATE_EMAIL', ''),
            'phone': __import__('os').getenv('CANDIDATE_PHONE', ''),
            'linkedin': __import__('os').getenv('CANDIDATE_LINKEDIN', ''),
            'github': __import__('os').getenv('CANDIDATE_GITHUB', '')
        }

        print('[4/5] Generating LaTeX/PDF...')
        tex_path, pdf_path = render_resume(resume_data, contact, job.company, job.role, job_id)
        resume_path = str(pdf_path or tex_path)

        method = 'EMAIL' if job.hr_email else 'WEB'
        insert_application(job_id, resume_path, method)

        print('[5/5] READY FOR HUMAN REVIEW')
        print('----------------------------------------')
        print(f'Company:   {job.company}')
        print(f'Role:      {job.role}')
        print(f'Match:     {match.score}/100')
        print(f'Apply URL: {job.apply_url}')
        print(f'HR email:  {job.hr_email}')
        print(f'Resume:    {resume_path}')
        print('----------------------------------------')

    except Exception as exc:
        print(f'[error] {type(exc).__name__}: {exc}')


async def main():
    init_db()
    client = TelegramClient(str(SESSION_DIR / 'job_agent'), TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await client.start(phone=TELEGRAM_PHONE or None)

    me = await client.get_me()
    print(f'Logged in as: {getattr(me, "username", None) or me.phone}')
    print(f'Listening to Telegram chat ID: {JOB_GROUP_ID}')
    print('Press Ctrl+C to stop.')

    @client.on(events.NewMessage(chats=JOB_GROUP_ID))
    async def handler(event):
        text = (event.raw_text or '').strip()
        if text:
            await process_job(event.message.id, text)

    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Stopped.')
