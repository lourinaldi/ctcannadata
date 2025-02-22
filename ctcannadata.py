import requests
import pdfplumber
import pandas as pd
import os
import re
from docx import Document
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the dataset directly from the given URL, setting low_memory=False
data_url = 'https://data.ct.gov/api/views/egd5-wb6r/rows.csv?accessType=DOWNLOAD'
logging.info("Loading dataset from URL")
data = pd.read_csv(data_url, low_memory=False)

# Helper function to sanitize URLs by removing the first 8 characters and the last character
def sanitize_url(field):
    if pd.isna(field):
        return None
    if len(field) > 8 and field[-1] == ')':
        return field[8:-1]
    else:
        return None

# Apply the sanitize_url function to the LAB-ANALYSIS column
logging.info("Sanitizing URLs in the dataset")
data['SANITIZED_URL'] = data['LAB-ANALYSIS'].apply(sanitize_url)

# Directory to save PDFs temporarily
pdf_dir = 'temporary_files'
os.makedirs(pdf_dir, exist_ok=True)
logging.info(f"Created temporary directory {pdf_dir}")

def identify_lab_name(text):
    if re.search(r'alta', text, re.IGNORECASE):
        return "Alta Sci"
    if re.search(r'analytics', text, re.IGNORECASE):
        return "Analytics Labs"
    if re.search(r'northeast', text, re.IGNORECASE):
        return "Northeast Labs"
    return "Unknown"

def extract_text_from_pdf(pdf_content):
    logging.debug("Extracting text from PDF")
    text = ""
    with pdfplumber.open(BytesIO(pdf_content)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_doc(doc_content):
    logging.debug("Extracting text from DOCX")
    text = ""
    doc = Document(BytesIO(doc_content))
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def detect_file_type(file_content):
    # Check the first few bytes to determine the file type
    if file_content[:4] == b'%PDF':
        return 'pdf'
    elif file_content[:2] == b'PK':
        # PK: Files that are compressed with PKZIP (zip archives)
        return 'docx'
    return 'unknown'

def process_file(index, row):
    file_results = row.to_dict()  # Include original row data
    file_url = row['SANITIZED_URL']
    logging.info(f"Processing row {index} with URL: {file_url}")
    
    if not file_url:
        logging.warning(f"Invalid URL at row {index}")
        file_results.update({
            'Lab Name': "Invalid URL",
            'THCa (%)': None,
            'THC (%)': None,
            'CBD (%)': None,
            'Moisture (%)': None,
            'Water Activity (aw)': None,
            'Test Completion Date': None,
            'Sample Expiration Date': None,
            'Microbial Pass/Fail': None,
            'Mycotoxins Pass/Fail': None,
            'Pesticides Pass/Fail': None,
            'Heavy Metals Pass/Fail': None,
            'Method ID': None
        })
        return file_results

    try:
        # Download the file
        logging.info(f"Downloading file from URL {file_url}")
        response = requests.get(file_url)
        file_content = response.content
        
        file_type = detect_file_type(file_content)
        
        if file_type == 'pdf':
            text = extract_text_from_pdf(file_content)
        elif file_type == 'docx':
            text = extract_text_from_doc(file_content)
        else:
            logging.warning(f"Unsupported file type at row {index}")
            file_results.update({
                'Lab Name': "Unsupported file type",
                'THCa (%)': None,
                'THC (%)': None,
                'CBD (%)': None,
                'Moisture (%)': None,
                'Water Activity (aw)': None,
                'Test Completion Date': None,
                'Sample Expiration Date': None,
                'Microbial Pass/Fail': None,
                'Mycotoxins Pass/Fail': None,
                'Pesticides Pass/Fail': None,
                'Heavy Metals Pass/Fail': None,
                'Method ID': None
            })
            return file_results

        # Identify the lab from the text
        lab_name = identify_lab_name(text)
        logging.info(f"Identified lab name as {lab_name}")

        # Extract additional data points using regex
        thca_match = re.search(r'THCa\s.*?(\d+\.\d+)\s*%', text)
        thc_match = re.search(r'Δ9\s*THC\s.*?(\d+\.\d+)\s*%', text)
        cbd_match = re.search(r'CBD\s.*?(\d+\.\d+)\s*%', text)
        moisture_match = re.search(r'Moisture\s.*?(\d+\.\d+)\s*%', text)
        water_activity_match = re.search(r'Water\s*Activity\s.*?(\d+\.\d+)\s*aw', text)
        completion_date_match = re.search(r'Completed:\s*(\d{2}/\d{2}/\d{4})', text)
        expiration_date_match = re.search(r'Expiration:\s*(\d{2}/\d{2}/\d{4})', text)
        microbial_pass_fail_match = re.search(r'Microbials?\s*[\S\s]*?Pass', text)
        mycotoxins_pass_fail_match = re.search(r'(?i)Mycotoxins?\s*[\S\s]*?Pass', text)
        pesticides_pass_fail_match = re.search(r'(Pesticides?|Pesticids?)\s*[\S\s]*?Pass', text)
        heavy_metals_pass_fail_match = re.search(r'Heavy\s*Metals?\s*[\S\s]*?Pass', text)
        method_id_match = re.search(r'Instrument\s*ID:\s*(\w+)', text)

        file_results.update({
            'Lab Name': lab_name,
            'THCa (%)': float(thca_match.group(1)) if thca_match else None,
            'THC (%)': float(thc_match.group(1)) if thc_match else None,
            'CBD (%)': float(cbd_match.group(1)) if cbd_match else None,
            'Moisture (%)': float(moisture_match.group(1)) if moisture_match else None,
            'Water Activity (aw)': float(water_activity_match.group(1)) if water_activity_match else None,
            'Test Completion Date': completion_date_match.group(1) if completion_date_match else None,
            'Sample Expiration Date': expiration_date_match.group(1) if expiration_date_match else None,
            'Microbial Pass/Fail': "Pass" if microbial_pass_fail_match else "Fail",
            'Mycotoxins Pass/Fail': "Pass" if mycotoxins_pass_fail_match else "Fail",
            'Pesticides Pass/Fail': "Pass" if pesticides_pass_fail_match else "Fail",
            'Heavy Metals Pass/Fail': "Pass" if heavy_metals_pass_fail_match else "Fail",
            'Method ID': method_id_match.group(1) if method_id_match else None
        })

    except Exception as e:
        logging.error(f"Failed to process file from URL {file_url} at row {index}: {e}")
        file_results.update({
            'Lab Name': "Error",
            'THCa (%)': None,
            'THC (%)': None,
            'CBD (%)': None,
            'Moisture (%)': None,
            'Water Activity (aw)': None,
            'Test Completion Date': None,
            'Sample Expiration Date': None,
            'Microbial Pass/Fail': None,
            'Mycotoxins Pass/Fail': None,
            'Pesticides Pass/Fail': None,
            'Heavy Metals Pass/Fail': None,
            'Method ID': None
        })

    return file_results

def append_to_csv(file_results, output_file, header=False):
    df = pd.DataFrame([file_results])
    df.to_csv(output_file, mode='a', header=header, index=False)

# Function to download and analyze PDFs and DOCX files in parallel
def analyze_lab_reports_in_parallel(output_file):
    logging.info("Starting parallel processing of lab reports")

    # Initialize the output file with headers before processing
    columns = data.columns.tolist() + [
        'Lab Name', 'THCa (%)', 'THC (%)', 'CBD (%)', 'Moisture (%)', 'Water Activity (aw)',
        'Test Completion Date', 'Sample Expiration Date', 'Microbial Pass/Fail', 'Mycotoxins Pass/Fail',
        'Pesticides Pass/Fail', 'Heavy Metals Pass/Fail', 'Method ID'
    ]
    pd.DataFrame(columns=columns).to_csv(output_file, index=False)  # Write header

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(process_file, index, row): index for index, row in data.iterrows()
        }
        
        for future in as_completed(futures):
            file_results = future.result()
            logging.info(f"Completed processing row {futures[future]}")
            append_to_csv(file_results, output_file)

    logging.info("Completed parallel processing of all lab reports")

# Define output file
output_file = 'updated_dataset_with_extracted_data.csv'

# Analyze lab reports and save results to CSV in real-time
analyze_lab_reports_in_parallel(output_file)

logging.info("Script completed successfully")
