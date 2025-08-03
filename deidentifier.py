import re
import base64
import hashlib
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()  # Load variables from .env file

FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    raise ValueError("FERNET_KEY not set in .env file")

fernet = Fernet(FERNET_KEY.encode())

# Encryption and decryption functions
def encrypt_value(value):
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(value):
    return fernet.decrypt(value.encode()).decode()

def encrypt_mapping(mapping):
    return {k: encrypt_value(v) for k, v in mapping.items()}

def decrypt_mapping(mapping):
    return {k: decrypt_value(v) for k, v in mapping.items()}

#Regex Patterns
patterns = {
    "HOSPITALNAME": r"Hospital Name:\s?.*",
    "HOSPITALADDRESS": r"(?:Hospital|Clinic|Facility) Address:\s?.*",
    "PROVIDERNAME": r"(?:Provider|Physician):\s?.*",
    "SOCIALWORKER": r"(?:Social Worker|Case Manager):\s?.*",
    "NAME": r"(?:Patient Name|Patient):\s?.*",
    "DOB": r"(?:Date of Birth|DOB|DoB):\s?.*",
    "MEDICALRECORDNUMBER": r"(?:Medical record number|MRN):\s?.*",
    "SSN": r"(SSN|Social Security Number):\s?.*",
    "PHONE": r"Phone(?: number)?:\s?.*",
    "FAXNUMBER": r"Fax(?: number| no\.)?:\s?.*",
    "EMAIL": r"Email:\s?.*",
    "URL": r"(?:URL|Website):\s*\S+",
    "ADDRESS": r"Address:\s?.*",
    "BENEFICIARYNUMBER": r"Health plan beneficiary number:\s?.*",
    "DEVICEIDENTIFIER": r"(?:Device identifier|Device ID):\s?.*",
    "SERIALNUMBER": r"(?:Pacemaker serial numbers?|Device serial numbers?):\s?.*",
    "CODE": r"Code:\s?.*",
    "LICENSENUMBER": r"(?:License|License No\.?) number:\s?.*",
    "ACCOUNTNUMBER": r"(?:Account|Bank Account|Insurance Account):\s?.*",
    "CERTIFICATENUMBER": r"Certificate number:\s?.*",
    "HEALTHINSURANCE": r"(?:Health Insurance|Insurance Info\.?):\s?.*",
    "GROUPNUMBER": r"Group no\.\s?.*",
    "BIOMETRIC": r"Biometric(?: data)?:\s?.*",
    "MEDICAID": r"(?:Medicaid|Medicare|Insurance) account:\s?.*",
}

#Function to redact PHI 
def deidentify_text(text):
    mapping = {}
    counts = {label: 0 for label in patterns}
    patient_name = None

    # 1. First step: Handle predefined patterns
    for label, pattern in patterns.items():
        regex = re.compile(pattern, flags=re.IGNORECASE)

        def replacer(match):
            nonlocal patient_name
            counts[label] += 1
            key = f"__{label}#{counts[label]}__"
            full_line = match.group(0)

            if label == "ALLERGIES" and "NSAIDs" in full_line:
                parts = full_line.split("(", 1)
                mapping[key] = "(" + parts[1].strip()
                return f"{parts[0].strip()} {key}"

            if ":" in full_line:
                parts = full_line.split(":", 1)
                mapping[key] = parts[1].strip()

                if label == "NAME" and "Patient" in parts[0]:
                    patient_name = parts[1].strip()

                return f"{parts[0]}: {key}"
            else:
                mapping[key] = full_line
                return key

        text = regex.sub(replacer, text)

    # 2. Now, handle the patient's name references across the entire text
    if patient_name:
        escaped_name = re.escape(patient_name)
        
        # Replace all instances of the patient's name
        while re.search(rf"\b{escaped_name}\b", text):
            counts["NAME"] += 1
            key = f"__NAME#{counts['NAME']}__"
            mapping[key] = patient_name
            text = re.sub(rf"\b{escaped_name}\b", key, text, count=1)

        # Handle titles (Dr., Mr., Mrs., Ms.) references to the patient
        title_matches = re.findall(r"(?:Dr\.|Mr\.|Mrs\.|Ms\.)\s[A-Z][a-z]+", text)
        last_name = patient_name.split()[-1]
        for match in title_matches:
            if last_name in match:
                counts["NAME"] += 1
                key = f"__NAME#{counts['NAME']}__"
                mapping[key] = match
                text = text.replace(match, key, 1)

    return text, mapping

def redact_allergies(text, mapping, start_count=0):
    allergy_section_pattern = r"(Allergies:)(.*?)(?=:)"
    count = start_count

    def redact_match(match):
        nonlocal count
        section_header = match.group(1)
        allergies_content = match.group(2)

        def replace_parens(parens_match):
            nonlocal count
            key = f"__ALLERGY#{count+1}__"
            original = parens_match.group(1)  # just the inside of ()
            key = f"__ALLERGY#{count+1}__"
            mapping[key] = original
            count += 1
            return f"({key})"

        redacted_allergies = re.sub(r"\((.*?)\)", replace_parens, allergies_content)
        return section_header + redacted_allergies

    redacted_text = re.sub(allergy_section_pattern, redact_match, text, flags=re.DOTALL)
    return redacted_text, mapping
