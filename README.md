# OCR_Extraction_POC 

MedSight is a patient-facing prescription intelligence tool that extracts medication data from prescription images, checks for drug interactions using official FDA data, and generates patient-friendly instructions with a recommended daily schedule.
 
Built as a proof of concept for the Cotiviti Intern Assessment — **Topic 1: Clinical Natural Language Technology for Health Care: Past, Present, & Future Approaches.**

## How It Works 

MedSight processes a prescription image through two parallel extraction pipelines:
 
- **OCR Pipeline (Past/Present):** OpenCV preprocesses the image (grayscale, denoise, adaptive threshold, deskew, morphological close, border padding) → Tesseract OCR extracts raw text → Mistral Large cleans up OCR errors and extracts structured medication data.
- **Multimodal LLM Pipeline (Future):** The raw image is sent directly to Pixtral Large, which reads the prescription and outputs structured medication data in a single inference call.
Users can toggle between both approaches to compare results.
 
Once medications are extracted through either path, MedSight queries the **openFDA Drug Label API** to retrieve official FDA data for each medication — including drug interactions, dosage guidelines, and safety warnings. This FDA data is then passed to Mistral Large as grounding context, which generates patient-friendly output: what each drug is for, how to take it, which drugs interact, and a recommended timing schedule.
 
Every pharmacological claim traces back to an FDA source rather than unverified model knowledge.

## Architecture
 
```
                    ┌─────────────────┐
                    │  Prescription    │
                    │     Image        │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼                              ▼
    ┌──────────────────┐          ┌──────────────────┐
    │   OCR Pipeline   │          │  Multimodal LLM  │
    │  (Past/Present)  │          │    (Future)       │
    │                  │          │                   │
    │  OpenCV          │          │  Pixtral Large    │
    │  Tesseract OCR   │          │  Image → JSON     │
    │  Mistral Large   │          │  Single call      │
    └────────┬─────────┘          └────────┬──────────┘
             │                              │
             └──────────────┬───────────────┘
                            ▼
                 ┌──────────────────┐
                 │   openFDA API    │
                 │  Drug labels,    │
                 │  interactions,   │
                 │  warnings        │
                 └────────┬─────────┘
                          ▼
                 ┌──────────────────┐
                 │  Mistral Large   │
                 │  FDA-grounded    │
                 │  analysis        │
                 └────────┬─────────┘
                          ▼
                 ┌──────────────────┐
                 │  Patient Output  │
                 │  • Medications   │
                 │  • Interactions  │
                 │  • Schedule      │
                 └──────────────────┘
```


## Tech Stack
 
| Layer | Technology |
|---|---|
| Frontend | Streamlit with custom CSS |
| OCR Pipeline | OpenCV (preprocessing) + Tesseract OCR (extraction) |
| AI Models | Pixtral Large (multimodal extraction) + Mistral Large (text extraction + analysis) |
| Data Grounding | openFDA Drug Label API |
| Language | Python |

## Project Structure
 
```
medsight/
├── app.py                    # Streamlit UI — main entry point
├── ocr.py                    # Image preprocessing + Tesseract OCR
├── extractor.py              # LLM medication extraction (text + multimodal paths)
├── fda_client.py             # openFDA API client for drug label data
├── analyzer.py               # FDA-grounded patient-friendly analysis
├── test_ocr.py               # Test script for OCR pipeline
├── test_extractor.py         # Test script for both extraction paths
├── test_fda_client.py        # Test script for FDA API
├── sample_prescriptions/     # Mock prescription images for demo
│   ├── prescription_1.png
│   └── prescription_2.png
├── requirements.txt
├── .env                      # API keys (not committed)
├── .env.example              # Template for environment variables
└── README.md
```
## Setup
 
### Prerequisites
 
- Python 3.9+
- Tesseract OCR installed on your system
- Mistral AI API key
### Installation
 
```bash
# Clone the repository
git clone https://github.com/your-username/medsight.git
cd medsight
 
# Install Python dependencies
pip install -r requirements.txt
 
# Set up environment variables
cp .env.example .env
# Edit .env and add your Mistral API key
```
 
### Installing Tesseract
 
```bash
# macOS
brew install tesseract
 
# Ubuntu/Debian
sudo apt-get install tesseract-ocr
 
# Windows — download installer from:
# https://github.com/UB-Mannheim/tesseract/wiki
```
 
### Environment Variables
 
Create a `.env` file in the project root:
 
```
MISTRAL_API_KEY=your_mistral_api_key_here
```
 
## Usage
 
### Run the Application
 
```bash
streamlit run app.py
```
 
The app will open at `http://localhost:8501`. Upload a prescription image and toggle between the OCR and Multimodal pipelines to compare results.


## Deliverables
 
| Deliverable | Description |
|---|---|
| Written Report | Two-page APA report on Clinical NLP for Healthcare (Past, Present, Future), with bibliography |
| MedSight POC | This repository — working Streamlit application |
| PowerPoint Deck | Presentation covering the report and POC architecture |
| Video Recording | Presentation walkthrough with live demo |
