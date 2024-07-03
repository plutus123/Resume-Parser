import re
from dotenv import load_dotenv
import PyPDF2
import os
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extracted_text_from_pdf(pdf_file:str)->[str]:
    with open(pdf_file,'rb') as pdf:
        reader = PyPDF2.PdfReader(pdf,strict=False)
        pdf_text=[]

        for page in reader.pages:
            content = page.extract_text()
            pdf_text.append(content)

        return pdf_text


resume_text = ""
extracted_text = extracted_text_from_pdf("Good_Resume.pdf")
for text in extracted_text:
    split_message = re.split(r'\s+|[,;?!.-]\s*', text.lower())
    resume_text = resume_text+text

print(resume_text)

def parse_personal_information(resume_text):
    name = re.search(r'Name: (.+)', resume_text, re.IGNORECASE)
    email = re.search(r'Email: (.+)', resume_text, re.IGNORECASE)
    phone = re.search(r'Phone: (.+)', resume_text, re.IGNORECASE)
    return {
        "name": name.group(1) if name else None,
        "email": email.group(1) if email else None,
        "phone": phone.group(1) if phone else None,
    }

def parse_education(resume_text):
    education_pattern = re.compile(r'Education: (.+)', re.IGNORECASE)
    education = education_pattern.findall(resume_text)
    return education

def parse_work_experience(resume_text):
    work_pattern = re.compile(r'(\w+ [\w\s]+)\s+\|\s+\(([\w\s]+)\)\s+(\w+\s?\d{2})\s+-\s+(\w+\s?\d{2})')
    work_experience = work_pattern.findall(resume_text)
    parsed_work_experience = [
        {
            "position": match[0],
            "organization": match[1],
            "start_date": match[2],
            "end_date": match[3]
        }
        for match in work_experience
    ]
    return parsed_work_experience

def parse_skills(resume_text):
    skills_pattern = re.compile(r'Skills: (.+)', re.IGNORECASE)
    skills = skills_pattern.findall(resume_text)
    return skills

function = [
    {
        "name": "parse_personal_information",
        "description": "Extracts personal information from the resume",
        "parameters": {
            "type": "object",
            "properties": {
                "Name": {
                    "type": "string",
                    "description": "Name of the person is, e.g. Tushar",
                },
                "Contact_Number": {
                    "type": "string",
                    "description": "Contact of the person is, e.g. +91-9936264750",
                },
                "Email": {
                    "type": "string",
                    "description": "Email account of the person is, e.g. Tushar@gmail.com",
                },
                "Github": {
                    "type": "string",
                    "description": "Github of the person is, e.g. github.com/Tushar",
                },
            },
            "required": ["resume_text"],
        },
    },
    {
        "name": "parse_education",
        "description": "Extracts education details from the resume",
        "parameters": {
            "type": "object",
            "properties": {
                "College": {
                    "type": "string",
                    "description": "Pursuing bachelor's from, e.g. IIT",
                },
                "School": {
                    "type": "string",
                    "description": "Completed class XIIth from, e.g. jaipuria school",
                },
            },
            "required": ["resume_text"],
        },
    },
    {
        "name": "parse_work_experience",
        "description": "Extracts work experience from the resume",
        "parameters": {
            "type": "object",
            "properties": {
                "WorkExperience": {
                    "type": "array",
                    "description": "A list of work experiences with organization, position, and duration",
                    "items": {
                        "type": "object",
                        "properties": {
                            "organization": {"type": "string"},
                            "position": {"type": "string"},
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"}
                        },
                        "required": ["organization", "position", "start_date", "end_date"]
                    }
                },
            },
            "required": ["resume_text"],
        },
    },
    {
        "name": "parse_skills",
        "description": "Extracts skills from the resume",
        "parameters": {
            "type": "object",
            "properties": {
                "Skills": {
                    "type": "string",
                    "description": "Is skilled in, e.g. Machine Learning",
                },
            },
            "required": ["resume_text"],
        },
    },
]

def call_openai_function(prompt):
    """Give LLM a given prompt and get an answer."""
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[{"role": "user", "content": prompt}],
        functions=function,
        function_call="auto",
    )
    output = completion.choices[0].message
    return output

# Generate prompts for each function
personal_information_prompt = f"Extract personal information from the resume text:\n\n{resume_text}"
education_prompt = f"Extract education details from the resume text:\n\n{resume_text}"
work_experience_prompt = f"Extract work experience from the resume text:\n\n{resume_text}"
skills_prompt = f"Extract skills from the resume text:\n\n{resume_text}"


personal_information = call_openai_function(personal_information_prompt)
education = call_openai_function(education_prompt)
work_experience = call_openai_function(work_experience_prompt)
skills = call_openai_function(skills_prompt)

print("Personal Information:", personal_information)
print("Education:", education)
print("Work Experience:", work_experience)
print("Skills:", skills)
