import os
import csv
import re
from datetime import date, datetime
from openai import OpenAI

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# File configuration
EXP_FILE_NORMAL = "exp.tex"
TECH_FILE = "tech.tex"
SCRIPT_NORMAL = "bash test.sh"
SCRIPT_INTERN = "bash testINTERN.sh"
CSV_DIR = "E:\\Downloads\\Resumes"

JOB_DESCRIPTIONS_FILE = "job_descriptions.txt"
LATEX_OUTPUT_FILE = "latex_output.txt"
# Prompt templates

SYSTEM_MESSAGE_EXP_NORMAL = """
Resume Experience Optimizer — Callback Maximization Edition  
Revise my professional experience sections to strongly align with the target job description and achieve the highest possible ATS match and interview callback rate. You are allowed light, realistic fabrication to support this goal. Follow these updated rules:
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.
========================
1. Job Description Keyword Analysis
========================
- Extract and prioritize high-impact ATS keywords:
  - Core technologies (e.g., React, Spring Boot, Docker, Kubernetes, C#, REST)
  - Frameworks, tools, libraries (e.g., .NET, Jenkins, GitLab, Kafka, Postgres)
  - Dev practices (e.g., CI/CD, Agile, TDD, microservices)
  - System concepts (e.g., cloud, security, performance tuning, scalability)
  - Role-specific responsibilities (e.g., debugging, architecture design, deployment)
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.
===========
2. Bullet Line Strategy
========================
- For each job experience:
  - Replace up to **3 bullet points** with stronger alternatives
  - Target:
    - Low-impact or redundant lines
    - Opportunities to add JD-critical tools, practices, or responsibilities
  - At least **1 bullet must reflect a core responsibility from the job description**
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.
> Example: Replace “Implemented UI updates”  
> with → “Developed React-based data visualizations for finance dashboards, improving transaction audit speed by 40%”
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.
========================
3. Smart Keyword Substitution
========================
- You are encouraged to:
  - Swap equivalent tools (e.g., Angular ↔ React, MongoDB ↔ Postgres)
  - Add tools or methods (e.g., Bash, Kafka, GitLab) **even if not originally used**, as long as:
    - It makes sense in the company context
    - It’s plausible to have been used briefly or learned on the job
    - It’s not a full fabrication of your role
  - Use domain language (e.g., “secure systems”, “cloud-native apps”, “low-latency services”) as found in the job description
========================
4. Bullet Formatting
========================
- Format: [Strong Action Verb] + [Tech/Task] + [Clear Outcome]
- Vary verbs within each job section (e.g., Engineered, Automated, Refactored)
- Include measurable or qualitative results (e.g., reduced bugs by 30%, improved load speed, enhanced reliability)
- Avoid vague language like "worked on," "helped with," or "participated in"
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.
========================
5. Output Rules
========================
- Escape LaTeX-sensitive characters (e.g., & → \\&, % → \\%)
- Format C# as C\\#
- Return only the **LaTeX-formatted updated Professional Experience section**
- No markdown, explanations, or commentary
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.
========================
6. Prohibited
========================
❌ Do NOT fabricate full roles or major technologies with zero plausible overlap  
❌ Do NOT reuse exact same verbs per section  
❌ Do NOT include vague or filler bullets  
✅ DO use JD-aligned tools, systems, phrasing — even if they weren’t in the original resume, as long as they’re defensible  
✅ DO optimize for **both ATS and human readability** — every bullet should sound like it fits the role perfectly
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.
========================
Goal:
========================
Each job experience should feel like it was written **specifically for the job** — using the right stack, language, and impact. You have the freedom to inject believable tools and rewrite lines with precision to boost my callback rate.
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.
- keep the overall length of each bullet point similar to the original
- all changed bullet popints must be the EAXCT SAME LENGTH IN CHARACTERS as the original bullet points (do not have it longer at all or everything breaks)
"""

SYSTEM_MESSAGE_EXP_INTERNSHIP = """
Resume Experience Optimizer – Advanced ATS Edition
Your goal is to maximize ATS match rate and interview callback potential while keeping each bullet EXACTLY the same length (in characters) as the original. No character overflow is allowed.
========================
1. Stack Override Priority
========================
- If the job description includes technologies like React, Python, Go, or Django, you MUST prioritize those over the original resume tools (e.g., Angular, C#), even if it requires light, plausible pivoting.
- You are allowed to drop lower-relevance tools from the original if it improves alignment with the job.
========================
2. Mandatory Keyword Match
========================
- Extract all tools, frameworks, and methodologies from the job description.
- Prioritize keywords in the following order:
  Must-Have Tech > Frameworks > System Concepts > Dev Practices > Soft Skills
- Each important keyword must appear at least once (if possible).
- No keyword may appear more than 3 times.
========================
3. Bullet Rewrite Constraints
========================
- Replace up to 3 bullet points per job experience section.
- Each new bullet point MUST be the exact same number of characters as the one it replaces (character count match is mandatory).
- Vary action verbs across bullets (no repetition in a single section).
- Focus on outcome-oriented, quantifiable results.
  Example: “Developed responsive UI with React and Redux…”
========================
4. Prohibited
========================
❌ No fabrication of major responsibilities
❌ No vague language (“worked on”, “involved in”, etc.)
❌ No repeated metrics or tools across bullets in the same section
❌ No markdown, no commentary
========================
5. Output Format Rules
========================
- Output must be LaTeX-safe: escape all special characters (e.g., & → \\&, % → \\%, C# → C\\#)
- Return only the LaTeX-formatted 'Professional Experience' section
- Validate that all modified bullet points are the same character length as the originals
========================
6. Goal
========================
- Every job experience section should read as if it was tailor-made for the target role.
- You are optimizing for BOTH ATS bots and human readability — inject high-impact tools, domain language, and measurable outcomes.
"""

SYSTEM_MESSAGE_TECH = """Please add any major tech stacks, programming languages, frameworks, and tools relevant to my experience to the provided tech LaTeX content. Only reply with the modified LaTeX code. MAX 9 items for each category, please just add the MAJOR most important ones.
Return back the latex code ONLY (DO NOT ADD '''latex for formating just give me the code raw)  Remember for C# you need to do C\\# as proper latex formatting
"""


# ---------------------------------------
# Helper functions
# ---------------------------------------

def _file_path(name: str) -> str:
    return os.path.join(CSV_DIR, name)


def get_csv_file_path() -> str:
    today = date.today().strftime("%Y-%m-%d")
    return _file_path(f"job_applications_{today}.csv")


def ensure_csv_exists() -> None:
    csv_file = get_csv_file_path()
    if not os.path.exists(csv_file):
        with open(csv_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Company Name", "Company Link", "Date Applied"])


def add_to_csv(company_name: str, company_link: str) -> None:
    ensure_csv_exists()
    csv_file = get_csv_file_path()
    today = date.today().strftime("%Y-%m-%d")
    with open(csv_file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([company_name, company_link, today])


def save_job_description(job_description: str, company_name: str) -> None:
    with open(JOB_DESCRIPTIONS_FILE, "a") as file:
        file.write(f"--- Job Description for {company_name} ---\n{job_description}\n")
        file.write(f"Timestamp: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n")


def save_latex_output(content: str, company_name: str) -> None:
    with open(LATEX_OUTPUT_FILE, "a") as file:
        file.write(f"--- LaTeX Output for {company_name} ---\n{content}\n")
        file.write(f"Timestamp: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n")


def grab_old_resume(file_name: str) -> str:
    with open(file_name, "r") as file:
        return file.read()


def write_back(file_name: str, content: str) -> None:
    with open(file_name, "w") as file:
        file.write(content)


def grab_new_resume(prompt: str, system_message: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def sanitize_filename(filename: str) -> str:
    for char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        filename = filename.replace(char, '_')
    return filename


def rate_match(resume_text: str, job_description: str) -> int:
    prompt = (
        "Resume:\n" + resume_text +
        "\n\nJob Description:\n" + job_description +
        "\n\nRate how well the resume matches the job description as a percentage from 0 to 100. "
        "Respond with only the number."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You return only an integer between 0 and 100."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=10,
        temperature=0,
    )
    text = response.choices[0].message.content.strip()
    numbers = re.findall(r"\d+", text)
    return int(numbers[0]) if numbers else 0


# ---------------------------------------
# Resume processing
# ---------------------------------------

def process_resume(job_description: str, company_name: str, company_link: str,
                   exp_file: str = EXP_FILE_NORMAL,
                   tech_file: str = TECH_FILE,
                   script: str = SCRIPT_NORMAL,
                   system_message_exp: str = SYSTEM_MESSAGE_EXP_NORMAL,
                   variants: int = 3) -> int:
    old_exp = grab_old_resume(exp_file)
    ask_exp = f"JOB DESCRIPTION: {job_description}\nCurrent Resume Experience: {old_exp}"

    best_exp = ""
    best_score = -1
    for _ in range(variants):
        candidate_exp = grab_new_resume(ask_exp, system_message_exp)
        score = rate_match(candidate_exp, job_description)
        if score > best_score:
            best_score = score
            best_exp = candidate_exp

    save_latex_output(best_exp, company_name)

    old_tech = grab_old_resume(tech_file)
    ask_tech = f"JOB DESCRIPTION: {job_description}\nCurrent Resume Skills: {old_tech}"
    grab_new_resume(ask_tech, SYSTEM_MESSAGE_TECH)

    save_job_description(job_description, company_name)
    write_back("exp2.tex", best_exp)
    os.system(script)

    safe_name = sanitize_filename(company_name)
    new_filename = f"{safe_name}_Vivek_Patel_Resume.pdf"
    source = _file_path("Vivek_Patel_Resume.pdf")
    destination = _file_path(new_filename)
    os.system(f"copy {source} \"{destination}\"")
    add_to_csv(company_name, company_link)
    print(f"Resume saved as {new_filename} and added to tracking CSV")

    return best_score


def get_job_description_normal(job_description: str, company_name: str = "Unknown", company_link: str = "", variants: int = 3) -> int:
    return process_resume(job_description, company_name, company_link, variants=variants)


def get_job_description_intern(job_description: str, company_name: str = "Unknown", company_link: str = "", variants: int = 3) -> int:
    return process_resume(job_description, company_name, company_link,
                          script=SCRIPT_INTERN,
                          system_message_exp=SYSTEM_MESSAGE_EXP_INTERNSHIP,
                          variants=variants)
