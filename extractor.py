"""

extractor.py - Extracts patient information - patient name, prescriber, date - and medication information including name, dosage, frequency, instructions, quantity, and refils 
from either OCR extracted raw text or from the image directly. 
Output is in JSON for both text and image. 

"""


import os 
import json 
from dotenv import load_dotenv 
from mistralai.client import Mistral 
import base64

load_dotenv()

EXTRACTION_PROMPT = """You are a clinical pharmacology assistant. Your job is to extract medication 
information from a medical prescription.
 
First, determine if the input appears to be from a medical prescription.
- If it is NOT a prescription, set "is_valid" to false and provide a reason.
- If it IS a prescription, extract all medications.
 
For each medication, provide:
- "name": the correct medication name (fix any misspellings)
- "dosage": strength/dose (e.g., "500mg")
- "frequency": how often to take it (e.g., "three times daily")
- "instructions": any additional instructions (e.g., "with food", "before breakfast")
- "quantity": number dispensed if mentioned
- "refills": number of refills if mentioned
 
Respond ONLY with a JSON object in this exact format, no other text:
{
    "is_valid": true,
    "confidence": "high",
    "medications": [
        {
            "name": "...",
            "dosage": "...",
            "frequency": "...",
            "instructions": "...",
            "quantity": "...",
            "refills": "..."
        }
    ],
    "patient_name": "...",
    "prescriber": "...",
    "date": "..."
}
 
If a field is not found, use "N/A".
If the input is not a prescription:
{
    "is_valid": false,
    "confidence": "high",
    "reason": "This does not appear to be a medical prescription.",
    "medications": [],
    "patient_name": "N/A",
    "prescriber": "N/A",
    "date": "N/A"
}
"""

def _get_client():
    """Create Mistral LLM client using Mistral API key."""
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        raise ValueError("Please provide valid LLM API Key.")
    client = Mistral(api_key=api_key)
    return client 

def _parse_response(raw_content: str) -> dict:
    """Parse and validate LLM JSON response."""
    clean = raw_content.strip().removeprefix("```json").removesuffix("```").strip()
 
    try:
        result = json.loads(clean)
    except json.JSONDecodeError:
        raise ValueError(f"LLM returned invalid JSON:\n{raw_content}")
 
    if "medications" not in result:
        raise ValueError("LLM response missing 'medications' key.")
 
    return result

def extract_medications(ocr_text):
    """
    Extracts medication information from ocr extracted raw text. 

    Input: 
    Raw string OCR extracted text 

    Output: 
    Json dictionary containing patient information - patient name, prescriber name, date - 
    and medication information including name, dosage, frequency, instruction, quantity, and refils. 
    """
    try:
        client = _get_client()
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role":"system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": f"Extract medications from this prescription text:\n\n{ocr_text}"}
            ],
            temperature=0.1, 
            response_format={'type':'json_object'},
        )
        raw_content = response.choices[0].message.content 
        clean = raw_content.strip().removeprefix("```json").removesuffix("```").strip()
        result = json.loads(clean)
    
        if "medications" not in result:
            raise ValueError("LLM response missing 'medications' key.")
        
        return result 
    except Exception as e:
        print("Error in extraction", e)
        return ''

def extract_from_image(image_bytes, mime_type):
    """
    Extract patient and medication information directly from the image by prompting Mistral LLM 
 
    Input: 
    image_bytes: raw bytes of the prescription image
    mime_type: MIME type of the image (image/png, image/jpeg, etc.)
 
    Output: 
    JSON dictionary with patient and medication information, metadata, and validation fields
    """
    client = _get_client()
 
    # Encode image as base64 data URI
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_uri = f"data:{mime_type};base64,{b64_image}"
 
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract all medications from this prescription image.",
                    },
                    {
                        "type": "image_url",
                        "image_url": data_uri,
                    },
                ],
            },
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
 
    return _parse_response(response.choices[0].message.content)
