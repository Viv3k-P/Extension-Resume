import os
import csv
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
SYSTEM_MESSAGE_EXP_NORMAL = (
    "Rewrite my professional experience section to align with the job "
    "description. Replace the weakest bullet in each job with one that "
    "matches important keywords. Return only LaTeX code."
)

SYSTEM_MESSAGE_EXP_INTERNSHIP = (
    "Tailor my experience section for an internship application using "
    "keywords from the job description. Return only LaTeX code."
)

SYSTEM_MESSAGE_TECH = (
    "Update the technical skills section based on the job description. "
    "Provide up to nine items per category and return LaTeX code only."
)


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


# ---------------------------------------
# Resume processing
# ---------------------------------------

def process_resume(job_description: str, company_name: str, company_link: str,
                   exp_file: str = EXP_FILE_NORMAL,
                   tech_file: str = TECH_FILE,
                   script: str = SCRIPT_NORMAL,
                   system_message_exp: str = SYSTEM_MESSAGE_EXP_NORMAL) -> None:
    old_exp = grab_old_resume(exp_file)
    ask_exp = f"JOB DESCRIPTION: {job_description}\nCurrent Resume Experience: {old_exp}"
    new_exp = grab_new_resume(ask_exp, system_message_exp)
    save_latex_output(new_exp, company_name)

    old_tech = grab_old_resume(tech_file)
    ask_tech = f"JOB DESCRIPTION: {job_description}\nCurrent Resume Skills: {old_tech}"
    grab_new_resume(ask_tech, SYSTEM_MESSAGE_TECH)

    save_job_description(job_description, company_name)
    write_back("exp2.tex", new_exp)
    os.system(script)

    safe_name = sanitize_filename(company_name)
    new_filename = f"{safe_name}_Vivek_Patel_Resume.pdf"
    source = _file_path("Vivek_Patel_Resume.pdf")
    destination = _file_path(new_filename)
    os.system(f"copy {source} \"{destination}\"")
    add_to_csv(company_name, company_link)
    print(f"Resume saved as {new_filename} and added to tracking CSV")


def get_job_description_normal(job_description: str, company_name: str = "Unknown", company_link: str = "") -> None:
    process_resume(job_description, company_name, company_link)


def get_job_description_intern(job_description: str, company_name: str = "Unknown", company_link: str = "") -> None:
    process_resume(job_description, company_name, company_link,
                   script=SCRIPT_INTERN,
                   system_message_exp=SYSTEM_MESSAGE_EXP_INTERNSHIP)
