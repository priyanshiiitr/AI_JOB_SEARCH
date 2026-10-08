import re
import shutil
import subprocess
from jinja2 import Template
from .config import BASE_DIR, RESUME_DIR
from .ai import ResumeData

TEMPLATE_PATH = BASE_DIR / 'resume' / 'template.tex'


def latex_escape(value):
    replacements = {
        '\\': r'\\textbackslash{}', '&': r'\\&', '%': r'\\%', '$': r'\\$',
        '#': r'\\#', '_': r'\\_', '{': r'\\{', '}': r'\\}',
        '~': r'\\textasciitilde{}', '^': r'\\textasciicircum{}'
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def bullets(items):
    lines = ['\\begin{itemize}[leftmargin=*,noitemsep,topsep=0pt]']
    for item in items:
        lines.append(f'\\item {latex_escape(str(item))}')
    lines.append('\\end{itemize}')
    return '\n'.join(lines)


def render_resume(data: ResumeData, contact, company, role, job_id):
    template = Template(TEMPLATE_PATH.read_text(encoding='utf-8'))

    exp_blocks = []
    for item in data.experience:
        employer = latex_escape(str(item.get('company', '')))
        title = latex_escape(str(item.get('role', '')))
        exp_blocks.append(f'\\textbf{{{employer}}} \\hfill {title}\n{bullets(item.get("bullets", []))}')

    project_blocks = []
    for item in data.projects:
        name = latex_escape(str(item.get('name', '')))
        tech = latex_escape(str(item.get('technologies', '')))
        project_blocks.append(f'\\textbf{{{name}}} \\hfill {tech}\n{bullets(item.get("bullets", []))}')

    links = [x for x in [contact.get('email'), contact.get('phone'), contact.get('linkedin'), contact.get('github')] if x]

    tex = template.render(
        name=latex_escape(contact.get('name', 'Candidate')),
        contact_line=' | '.join(latex_escape(str(x)) for x in links),
        summary=latex_escape(data.summary),
        skills=latex_escape(', '.join(data.skills)),
        experience='\n\n'.join(exp_blocks),
        projects='\n\n'.join(project_blocks),
        education=latex_escape(data.education)
    )

    safe_company = re.sub(r'[^a-zA-Z0-9]+', '-', company).strip('-').lower() or 'company'
    safe_role = re.sub(r'[^a-zA-Z0-9]+', '-', role).strip('-').lower() or 'role'
    stem = f'{safe_company}-{safe_role}-{job_id}'
    tex_path = RESUME_DIR / f'{stem}.tex'
    tex_path.write_text(tex, encoding='utf-8')

    if shutil.which('pdflatex') is None:
        return tex_path, None

    result = subprocess.run(
        ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', '-output-directory', str(RESUME_DIR), str(tex_path)],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        tex_path.with_suffix('.compile.log').write_text(result.stdout + '\n' + result.stderr, encoding='utf-8')
        return tex_path, None

    pdf_path = tex_path.with_suffix('.pdf')
    return tex_path, pdf_path if pdf_path.exists() else None
