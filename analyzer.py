"""
analyzer.py - Takes in the medications extracted from the prescription and the official FDA drug label for each extracted drug. 
It prompts the Mistral LLM to generate an simple analysis including dosage, instructions, drug interactions with warning, and schedule of medicine to be taken. 
Output is in the JSON format. 

"""


import os 
import json 
from dotenv import load_dotenv 
from mistralai.client import Mistral 

load_dotenv()

ANALYSIS_PROMPT = """You are a patient-friendly medication advisor. You will receive:
1. A list of medications extracted from a prescription
2. Official FDA drug label data for each medication (interactions, dosage, warnings)
 
Using ONLY the FDA data provided as your source of truth, generate a patient-friendly analysis.
 
Respond ONLY with a JSON object in this exact format:
{
    "medications": [
        {
            "name": "...",
            "purpose": "Simple 1-sentence explanation of what this drug does",
            "how_to_take": "Plain-English instructions (e.g., 'Take with food')",
            "important_notes": "Key warnings in simple language"
        }
    ],
    "interactions": [
        {
            "drugs": ["Drug A", "Drug B"],
            "severity": "high" | "moderate" | "low",
            "description": "Plain-English explanation of the interaction",
            "recommendation": "What the patient should do about it"
        }
    ],
    "schedule": {
        "morning": "What to take and how",
        "afternoon": "What to take and how",
        "evening": "What to take and how",
        "as_needed": "Any PRN medications"
    },
    "general_advice": "1-2 sentences of overall guidance"
}
 
Rules:
- Use simple, non-medical language a patient can understand
- Base ALL interaction warnings on the FDA data provided — do not invent interactions
- If the FDA data says "No FDA data available" for a drug, note that information is limited
- Be specific about timing and ordering when drugs interact
- Keep each field concise — 1-2 sentences max
"""

def _build_context(medications, fda_labels):
    """
    Builds context using list of medications and official FDA labels for each drug 

    Input: 
    medications: list of extracted medications 
    fda_labels: list of official FDA drug label 

    Output: String containing dosage, frequency, instructions, indications, drug interactions, and warnings for each medication separated by a new line. 
    """
    fda_map = {}
    for label in fda_labels:
        name = label["drug_name"].strip().lower()
        fda_map[name] = label 
    sections = []
    sections.append("EXTRACTED MEDICATIONS FROM PRESCRIPTION:")
    sections.append("-" * 40)
 
    for med in medications:
        name = med.get("name", "Unknown")
        dosage = med.get("dosage", "N/A")
        frequency = med.get("frequency", "N/A")
        instructions = med.get("instructions", "N/A")
 
        sections.append(f"\nMedication: {name}")
        sections.append(f"  Dosage: {dosage}")
        sections.append(f"  Frequency: {frequency}")
        sections.append(f"  Instructions: {instructions}")
 
        # Attach FDA data if available
        fda = fda_map.get(name.strip().lower())
        if fda:
            sections.append(f"\n  --- FDA LABEL DATA for {name} ---")
            sections.append(f"  Indications: {fda['indications']}")
            sections.append(f"  Dosage info: {fda['dosage']}")
            sections.append(f"  Drug interactions: {fda['interactions']}")
            sections.append(f"  Warnings: {fda['warnings']}")
        else:
            sections.append(f"  --- No FDA label data found for {name} ---")
 
    sections.append("\n" + "=" * 40)
    sections.append("Based on the above medications and their FDA data, provide a patient-friendly analysis.")

    return "\n".join(sections)



def analyze_medications(medications, fda_labels):
    """
    Builds context using medications and fda labels and prompts Mistral LLM for patient-friendly drug analysis. 
 
    Input: 
    medications: list of extracted medications 
    fda_labels: list of official FDA drug label 

    Output: JSON format containing drug analysis. 
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("Please provide valid LLM API Key.")
    client = Mistral(api_key)

    context = _build_context(medications, fda_labels)

    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {"role": "system", "content": ANALYSIS_PROMPT},
            {"role": "user", "content": context}
        ],
        temperature=0.2, 
        response_format={"type": "json_object"}
    )

    raw_content = response.choices[0].message.content
    clean = raw_content.strip().removeprefix("```json").removesuffix("```").strip()
 
    try:
        result = json.loads(clean)
    except json.JSONDecodeError:
        raise ValueError(f"LLM returned invalid JSON:\n{raw_content}")
 
    return result

