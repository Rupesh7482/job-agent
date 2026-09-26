import json
import subprocess
from pathlib import Path


def load_resume(path="data/master_resume.json"):
    with open(path) as f:
        return json.load(f)


def escape_latex(text: str) -> str:
    """Escape characters that break LaTeX compilation."""
    if not text:
        return ""
    replacements = {
        "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
    }
    for char, escaped in replacements.items():
        text = text.replace(char, escaped)
    return text


def build_education(resume: dict) -> str:
    lines = []
    for edu in resume.get("education", []):
        line = f"\\textbf{{{escape_latex(edu.get('degree',''))}}}, {escape_latex(edu.get('institution',''))} \\hfill {escape_latex(edu.get('end',''))}"
        lines.append(line + r" \\")
    return "\n".join(lines)


def build_skills(resume: dict) -> str:
    skills = resume.get("skills", {})
    lines = []
    for category, items in skills.items():
        if items:
            label = category.replace("_", " ").title()
            lines.append(f"\\textbf{{{label}:}} {escape_latex(', '.join(items))} \\\\")
    return "\n".join(lines)


def build_projects(resume: dict) -> str:
    lines = []
    for proj in resume.get("projects", []):
        title = escape_latex(proj.get("title", ""))
        tech = escape_latex(", ".join(proj.get("tech", [])))
        lines.append(f"\\textbf{{{title}}} ({tech})")
        lines.append(r"\begin{itemize}[leftmargin=*,topsep=1pt,itemsep=0pt]")
        for bullet in proj.get("bullets", []):
            lines.append(f"\\item {escape_latex(bullet)}")
        lines.append(r"\end{itemize}")
    return "\n".join(lines)


def build_experience(resume: dict) -> str:
    lines = []
    for exp in resume.get("experience", []):
        title = escape_latex(exp.get("title", ""))
        company = escape_latex(exp.get("company", ""))
        lines.append(f"\\textbf{{{title}}}, {company}")
        lines.append(r"\begin{itemize}[leftmargin=*,topsep=1pt,itemsep=0pt]")
        for bullet in exp.get("bullets", []):
            lines.append(f"\\item {escape_latex(bullet)}")
        lines.append(r"\end{itemize}")
    return "\n".join(lines)


def build_certifications(resume: dict) -> str:
    lines = []
    for cert in resume.get("certifications", []):
        lines.append(f"{escape_latex(cert.get('title',''))} — {escape_latex(cert.get('issuer',''))} \\\\")
    return "\n".join(lines)


def generate_resume_pdf(output_name: str = "resume") -> str:
    resume = load_resume()
    template_path = Path("templates/resume.tex")
    template = template_path.read_text()

    filled = template
    filled = filled.replace("((NAME))", escape_latex(resume.get("name", "")))
    filled = filled.replace("((EMAIL))", escape_latex(resume.get("email", "")))
    filled = filled.replace("((PHONE))", escape_latex(resume.get("phone", "")))
    filled = filled.replace("((GITHUB))", escape_latex(resume.get("links", {}).get("github", "")))
    filled = filled.replace("((LINKEDIN))", escape_latex(resume.get("links", {}).get("linkedin", "")))
    filled = filled.replace("((EDUCATION))", build_education(resume))
    filled = filled.replace("((SKILLS))", build_skills(resume))
    filled = filled.replace("((PROJECTS))", build_projects(resume))
    filled = filled.replace("((EXPERIENCE))", build_experience(resume))
    filled = filled.replace("((CERTIFICATIONS))", build_certifications(resume))

    Path("output").mkdir(exist_ok=True)
    tex_path = Path(f"output/{output_name}.tex")
    tex_path.write_text(filled)

    result = subprocess.run(
        ["tectonic", str(tex_path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Tectonic error output:\n", result.stderr)
        raise RuntimeError("PDF generation failed — see error above.")

    return f"output/{output_name}.pdf"
