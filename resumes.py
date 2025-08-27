import os
import csv
from datetime import date, datetime
from openai import OpenAI
import tkinter as tk
import time
start_time = time.time()
# OpenAI API key setup
client = OpenAI(
    api_key = "",
)
# Global variables for file names
EXP_FILE_NOMRAL = "exp.tex"
EXP_FILE_CAP = "expCAP.tex"
TECH_FILE = "tech.tex"
MAINSCRIPT = "bash test.sh"
INTERNSCRIPT = "bash testINTERN.sh"
CAPSCRIPT = "bash testCAP.sh"
CSV_FILE = "E:\\Downloads\\Resumes\\job_applications.csv"


# system_message_exp = """
# Resume Experience Optimizer  
# Revise my professional experience sections to align with the target job description while achieving an 85%+ ATS match score. Follow these steps:

# 1. Job Description Analysis  
#    - Parse the provided job description to identify and rank ATS keywords:  
#      - Core technical competencies (e.g., React, AWS, CI/CD).  
#      - Key methodologies (e.g., Agile, TDD, DevOps).  
#      - Required qualifications (e.g., Azure certifications, security protocols).  
#    - Rank keywords by relevance and frequency in the job description.

# 2. Identify Weakest Line  
#    - For each job experience, identify **only** the weakest or least relevant line (1 per job).  
#    - Replace **this single line** with a new, highly relevant line that:  
#      - Uses the top-ranked ATS keyword from the job description.  
#      - Matches the style and tone of the other lines in the resume.  
#       Remember for C# you need to do C\# as proper latex formatting

# 3. New Line Creation  
#    - Structure the new line as: [Strong Verb] + [Technical Action] .  
#    - Example: "Optimized textnf AWS** cloud infrastructure, reducing operational costs ."  
#    - Ensure the new line flows naturally with the existing content.
#  Remember for C# you need to do C\# as proper latex formatting
# 4. Technical Specificity  
#    - Avoid vague statements. Instead, focus on concrete implementations:  
#      - Instead of: "Worked with cloud platforms."  
#      - Write: "Deployed scalable textbfAzure Kubernetes clusters, improving deployment efficiency"
#  Remember for C# you need to do C\# as proper latex formatting
# 5. Formatting Requirements  
#    - Return **only the revised experience sections**.  
#    - Escape special characters (e.g., & → \&, % → \%).  
#    - Maintain the one-line format for consistency.


# 6. Prohibited Actions  
#    - No markdown formatting.  
#    - No commentary or explanations.  
#    - No non-standard syntax.  
#    - **YOU ARE TO REPLACE ONLY ONE BULLET POINT FOR EACH JOB EXPERIENCE. LEAVE THE OTHER BULLET POINTS THE SAME.**
#     - NO DOUBLE STARS AT ALL "**"
#     - Remember for C# you need to do C\# as proper latex formatting
# Output **only** the revised experience sections with the new line added for each job in Latex code. Remember for C# you need to do C\# as proper latex formatting
# """
system_message_exp1MAYOLD = """
Resume Experience Optimizer  
Revise my professional experience sections to align with the target job description while achieving a 90%+ ATS match score. Follow these steps:

1. Job Description Analysis  
   - Extract and rank relevant ATS keywords from the job description:
     - Core technical tools (e.g., React, Java, Spring Boot, Docker, Kubernetes, C++, REST, SQL)
     - Frameworks, libraries, platforms (e.g., Node.js, ASP.NET, Flask)
     - Methodologies (e.g., Agile, TDD, CI/CD, DevOps)
     - Deployment/cloud tech (e.g., AWS, Azure, cloud environments)
     - System-level concepts (e.g., threading, networking, GUI, Linux)

2. Identify Weakest Line  
   - For each job experience entry, identify **only one** bullet point that is the least relevant or impactful.
   - Replace only this single line using a new bullet point that:
     - Incorporates one of the top-ranked keywords from the job description that is **missing or underused** in the resume
     - Still fits the style and content of your past experience

3. Controlled Substitution (if needed)  
   - You are allowed to **substitute interchangeable technologies** to improve ATS match.
     - Examples: Angular ↔ React, PostgreSQL ↔ MySQL, C# ↔ .NET, Jenkins ↔ GitHub Actions, SQL ↔ T-SQL
   - Do NOT insert tools or technologies that are entirely unrelated to anything shown in the resume.

4. New Line Guidelines  
   - Structure the new bullet point using this format:
     - [Action Verb] + [Technical Task or Tool Used] + [Outcome or Impact]
   - Example: "Built Spring Boot microservices with REST APIs and deployed Docker containers to improve reliability."

5. Formatting Requirements  
   - Escape LaTeX-sensitive characters (e.g., & → \\&, % → \\%)
   - Use proper LaTeX formatting for C# as C\\#
   - Return **only the updated LaTeX experience section** — no explanations or extra text
   - Do not use markdown, asterisks, or commentary

6. Prohibited  
   - Do NOT change more than one full bullet per job experience section
   - You may **lightly tweak** up to two other bullets to improve JD alignment
   - Do NOT invent unrelated tools or completely fabricate experiences but some is fine
   Do not start with the same word as the other bullet points

Prioritize keyword alignment and functional equivalence to maximize ATS relevance while keeping bullet points grounded in real technical experience.
"""
system_message_exp1 = """
Resume Experience Optimizer v4 – High-Fidelity JD Alignment

Your task is to revise the "Professional Experience" section of my resume to strongly align with a target job description. You should apply deep modifications that increase keyword relevance, domain alignment, and ATS optimization — while keeping all edits grounded in reality.

========================
STEP 1 – Job Description Parsing
========================
- Extract and rank keywords from the job description:
  - Programming languages, frameworks, databases, tools
  - Methodologies (Agile, CI/CD, TDD)
  - System-level concepts (networking, threading, cloud)
  - Domain or industry language (e.g., financial, healthcare, embedded)
- Prioritize “must have” or repeated terms.
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.

========================
STEP 2 – Replace the Weakest Line
========================
- For each job experience:
  - Identify the weakest or least JD-relevant bullet.
  - Replace it with a **strong, JD-aligned** bullet that:
    - Incorporates one or more high-priority missing keywords from the JD
    - Reflects a plausible task based on my experience or similar tech
    - Uses the format: **[Action Verb] + [Tool or Task] + [Outcome or Impact]**
    - Adds domain-specific phrasing if relevant

> Example:  
> “Built dashboards using React and Redux to support live financial data streams, improving analyst efficiency by 25%”
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.
- all changed bullet popints must be the EAXCT SAME LENGTH IN CHARACTERS as the original bullet points (do not have it longer at all or everything breaks)

========================
STEP 3 – Bold Alignment Overhaul (up to 2 per job)
========================
- You may **substantially rewrite up to two more bullets per job**.
- Use this to:
  - Inject JD-critical tools (e.g., Postgres, Docker, AWS, Kafka)
  - Reframe old experience using newer or transferable tools (e.g., Angular → React)
  - Add phrases related to methodologies, domain context, or deployment practices
  - Mention tools you could realistically explain in an interview, even if used briefly (e.g., Bash, GitLab)
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.

✅ You *may insert tools you haven’t deeply used* if:
  - You’ve used similar/adjacent tech  
  - It’s believable and not a total fabrication  
  - You could realistically explain it in a job interview  

❌ You may NOT:
  - Leave bullet points almost unchanged
- all changed bullet popints must be the EAXCT SAME LENGTH IN CHARACTERS as the original bullet points (do not have it longer at all or everything breaks)

========================
STEP 4 – Clarity, Style, and Format
========================
- Bullet format: **[Action Verb] + [Tech Task or Tool] + [Outcome or Metric]**
- Vary verbs across bullets (e.g., Engineered, Optimized, Integrated, Deployed)
- Avoid vague phrases like “worked on” or “assisted with”
- Never repeat the same verb at the start of multiple bullets in a section
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.

========================
STEP 5 – Output Format
========================
- Output ONLY the updated LaTeX-formatted Professional Experience section
- Format technologies properly (e.g., & → \&, % → \%, C# → C\#)
- Do NOT include markdown, explanations, or commentary
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.
PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.

PLEASE KEEP ALL BULLET POINTS YOU REPLACE WITH THE SAME LENGTH IN CHARACTERS AS THE ORIGINAL BULLET POINTS.
- all changed bullet popints must be the EAXCT SAME LENGTH IN CHARACTERS as the original bullet points (do not have it longer at all or everything breaks)

========================
Your Goal:
========================
Transform each experience entry to feel tailor-built for the job description. Every bullet should clearly reflect a keyword, tool, or responsibility from the JD — with plausible, technically sound phrasing that a hiring manager or recruite 
"""

#This the new prompt that matches ATS better and makes up stuff
system_message_exp2 = """
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




system_message_exp1 = """
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
- Escape LaTeX-sensitive characters (e.g., & → \&, % → \%)
- Format C# as C\#
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



system_message_tech = """Please add any major tech stacks, programming languages, frameworks, and tools relevant to my experience to the provided tech LaTeX content. Only reply with the modified LaTeX code. MAX 9 items for each category, please just add the MAJOR most important ones.
Return back the latex code ONLY (DO NOT ADD '''latex for formating just give me the code raw)  Remember for C# you need to do C\# as proper latex formatting

"""
# File paths to store data
JOB_DESCRIPTIONS_FILE = "job_descriptions.txt"
LATEX_OUTPUT_FILE = "latex_output.txt"
GPT_OUTPUT_FILE = "gpt_output.txt"

# Function to save job description with a timestamp
def save_job_description(job_description, company_name="Unknown"):
    with open(JOB_DESCRIPTIONS_FILE, "a") as file:
        file.write(f"--- Job Description for {company_name} ---\n")
        file.write(f"{job_description}\n")
        file.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

# Function to save the LaTeX-formatted resume output
def save_latex_output(content, company_name="Unknown"):
    with open(LATEX_OUTPUT_FILE, "a") as file:
        file.write(f"--- LaTeX Output for {company_name} ---\n")
        file.write(f"{content}\n")
        file.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

# Function to save GPT-generated resume output
def save_gpt_output(content, company_name="Unknown"):
    with open(GPT_OUTPUT_FILE, "a") as file:
        file.write(f"--- GPT Output for {company_name} ---\n")
        file.write(f"{content}\n")
        file.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")







def get_csv_file_path():
    today = date.today().strftime("%Y-%m-%d")
    return f"E:\\Downloads\\Resumes\\job_applications_{today}.csv"

# Create CSV file if it doesn't exist
def ensure_csv_exists():
    csv_file = get_csv_file_path()
    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Company Name', 'Company Link', 'Date Applied'])


# Helper functions for reading, writing files, and communicating with OpenAI
def grab_old_resume(file_name):
    with open(file_name, "r") as file:
        return file.read()

def write_back(file_name, content):
    with open(file_name, "w") as file:
        file.write(content)

def grab_new_resume(ask, sys):
    response = client.chat.completions.create(
        model='gpt-4o-mini',  # Specify the model
        messages=[
            {"role": "system", "content": sys},
            {"role": "user", "content": ask}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    
    # Accessing the content of the response
    content = response.choices[0].message.content.strip()
    return content

def add_to_csv(company_name, company_link):
    ensure_csv_exists()
    csv_file = get_csv_file_path()
    today = date.today().strftime("%Y-%m-%d")
    with open(csv_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([company_name, company_link, today])


def sanitize_filename(filename):
    # Replace characters that aren't suitable for filenames
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

# Main processing function
def process_resume(job_description, company_name, company_link, exp_file=EXP_FILE_NOMRAL, tech_file=TECH_FILE, script=MAINSCRIPT, system_message_exp=system_message_exp1):
    # Process Experience section
    old_exp_content = grab_old_resume(exp_file) 
    ask_exp = f"JOB DESCRIPTION: {job_description}\nCurrent Resume Experience: {old_exp_content}" 

    modified_exp_content = grab_new_resume(ask_exp, system_message_exp)  # ASK CHAT FOR NEW RESUME
    
    print(f"SENT GPT AND GOT --- {time.time() - start_time} seconds ---")
    
    # Save the LaTeX output to the file
    save_latex_output(modified_exp_content, company_name)
    
    # Process Tech section
    old_tech_content = grab_old_resume(tech_file)
    ask_tech = f"JOB DESCRIPTION: {job_description}\nCurrent Resume Skills: {old_tech_content}"
    modified_tech_content = grab_new_resume(ask_tech, system_message_tech)
    

    # Save the job description to the file
    save_job_description(job_description, company_name)
    
    # Hardcode the writing file to exp2.tex for experience section
    write_back("exp2.tex", modified_exp_content)
    
    # Run a script to compile or process the modified LaTeX files
    print(script)
    print("*******************************************************************")
    os.system(script)
    
    # Rename the output file with company name
    safe_company_name = sanitize_filename(company_name)
    new_filename = f"{safe_company_name}_Vivek_Patel_Resume.pdf"
    output_path = f"E:\\Downloads\\Resumes\\{new_filename}"

    # Copy the file from the source location to the new output location
    os.system(f"copy E:\\Downloads\\Resumes\\Vivek_Patel_Resume.pdf \"{output_path}\"")

    # Add entry to CSV
    add_to_csv(company_name, company_link)
    
    print(f"Resume saved as {new_filename} and added to tracking CSV")

# Updated functions to accept company info
def get_job_description_normal(job_description, company_name="Unknown", company_link=""):
    process_resume(job_description, company_name, company_link)

def get_job_description_intern(job_description, company_name="Unknown", company_link="", ):
    process_resume(job_description, company_name, company_link, system_message_exp=system_message_exp2)

# def get_job_description_cap(job_description, company_name="Unknown", company_link=""):
#     process_resume(job_description, company_name, company_link, exp_file=EXP_FILE_CAP, script=CAPSCRIPT)