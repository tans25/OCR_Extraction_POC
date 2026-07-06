"""
Call openFDA API to fetch drug label for each extracted medication 
Output is a list of FDA drug labels. 
 
"""


import requests 

BASE_URL = "https://api.fda.gov/drug/label.json"

def _extract_field(response, field_name):
    not_found = "No FDA data available"
    field = response.get(field_name, list)
    if not field or not isinstance(field, list):
        return not_found 
    text = field[0].strip()
    if not text:
        return not_found
    if len(text) > 2000:
        text = text[:2000] + "..."
    return text 


def fetch_drug_label(drug_name):
    name = drug_name.lower().strip()
    not_found = "No FDA data available."
    result = {
        "drug_name": drug_name,
        "indications": not_found, 
        "dosage": not_found, 
        "interactions": not_found,
        "warnings": not_found
    }

    searches = [
        f'openfda.generic_name:"{name}"',
        f'openfda.brand_name:"{name}"',
    ]
    for query in searches:
        try: 
            response = requests.get(
                BASE_URL, 
                params={"search": query, "limit": 1},
                timeout=10
            )
            if response.status_code != 200:
                continue 
            data = response.json()
            results = data.get("results", [])
            if not results:
                continue 
            label = results[0]
 
            result["indications"] = _extract_field(label, "indications_and_usage")
            result["dosage"] = _extract_field(label, "dosage_and_administration")
            result["interactions"] = _extract_field(label, "drug_interactions")
            result["warnings"] = _extract_field(label, "warnings")
 
            return result
        except Exception as e:
            print("Error in calling FDA", e)
            continue 
    return result 

def fetch_all_labels(medications):
    labels = []
    try: 
        for med in medications:
            drug_name = med.get("name", "")
            if drug_name and drug_name != "N/A":
                label = fetch_drug_label(drug_name)
                labels.append(label)
    except Exception as e:
        print("Error in getting labels for all medications: ", e)
    return labels 

 