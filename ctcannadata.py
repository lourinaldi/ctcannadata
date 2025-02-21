import requests
import pdfplumber
import pandas as pd
import os
import re

# Load the dataset directly from the given URL, setting low_memory=False
data_url = 'https://data.ct.gov/api/views/egd5-wb6r/rows.csv?accessType=DOWNLOAD'
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
data['SANITIZED_URL'] = data['LAB-ANALYSIS'].apply(sanitize_url)

# Directory to save PDFs temporarily
pdf_dir = 'temporary_pdfs'
os.makedirs(pdf_dir, exist_ok=True)

# Function to download and analyze PDFs
def analyze_lab_reports():
    lab_names = []
    thca_values = []
    thc_values = []
    cbd_values = []
    moisture_values = []
    water_activity_values = []
    test_completion_dates = []
    sample_expiration_dates = []
    microbial_pass_fail = []
    mycotoxins_pass_fail = []
    pesticides_pass_fail = []
    heavy_metals_pass_fail = []
    method_ids = []
    
    for index, row in data.iterrows():
        pdf_url = row['SANITIZED_URL']
        
        if not pdf_url:
            lab_names.append("Invalid URL")
            thca_values.append(None)
            thc_values.append(None)
            cbd_values.append(None)
            moisture_values.append(None)
            water_activity_values.append(None)
            test_completion_dates.append(None)
            sample_expiration_dates.append(None)
            microbial_pass_fail.append(None)
            mycotoxins_pass_fail.append(None)
            pesticides_pass_fail.append(None)
            heavy_metals_pass_fail.append(None)
            method_ids.append(None)
            continue

        try:
            # Download the PDF
            response = requests.get(pdf_url)
            pdf_path = os.path.join(pdf_dir, f"temp_{index}.pdf")
            
            with open(pdf_path, 'wb') as f:
                f.write(response.content)

            # Extract text using pdfplumber
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text()

            # Identify the lab from the text
            if "Analytics Labs" in text:
                lab_name = "Analytics Labs"
            elif "Northeast Labs" in text:
                lab_name = "Northeast Labs"
            elif "AltaSci" in text or "Alta Sci" in text:
                lab_name = "Alta Sci"
            else:
                lab_name = "Unknown"
            lab_names.append(lab_name)

            # Extract additional data points
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
            
            thca_values.append(float(thca_match.group(1)) if thca_match else None)
            thc_values.append(float(thc_match.group(1)) if thc_match else None)
            cbd_values.append(float(cbd_match.group(1)) if cbd_match else None)
            moisture_values.append(float(moisture_match.group(1)) if moisture_match else None)
            water_activity_values.append(float(water_activity_match.group(1)) if water_activity_match else None)
            test_completion_dates.append(completion_date_match.group(1) if completion_date_match else None)
            sample_expiration_dates.append(expiration_date_match.group(1) if expiration_date_match else None)
            microbial_pass_fail.append("Pass" if microbial_pass_fail_match else "Fail")
            mycotoxins_pass_fail.append("Pass" if mycotoxins_pass_fail_match else "Fail")
            pesticides_pass_fail.append("Pass" if pesticides_pass_fail_match else "Fail")
            heavy_metals_pass_fail.append("Pass" if heavy_metals_pass_fail_match else "Fail")
            method_ids.append(method_id_match.group(1) if method_id_match else None)
            
            # Optionally, you can remove the temporary PDF after processing
            os.remove(pdf_path)
        
        except Exception as e:
            lab_names.append("Error")
            thca_values.append(None)
            thc_values.append(None)
            cbd_values.append(None)
            moisture_values.append(None)
            water_activity_values.append(None)
            test_completion_dates.append(None)
            sample_expiration_dates.append(None)
            microbial_pass_fail.append(None)
            mycotoxins_pass_fail.append(None)
            pesticides_pass_fail.append(None)
            heavy_metals_pass_fail.append(None)
            method_ids.append(None)
            print(f"Failed to process PDF from URL {pdf_url}: {e}")
    
    return lab_names, thca_values, thc_values, cbd_values, moisture_values, water_activity_values, test_completion_dates, sample_expiration_dates, microbial_pass_fail,  mycotoxins_pass_fail, pesticides_pass_fail, heavy_metals_pass_fail, method_ids

# Analyze lab reports and add results to dataset
(analyzed_lab_names, thca_values, thc_values, cbd_values, moisture_values, water_activity_values,
 test_completion_dates, sample_expiration_dates, microbial_pass_fail, mycotoxins_pass_fail,
 pesticides_pass_fail, heavy_metals_pass_fail, method_ids) = analyze_lab_reports()

data['Lab Name'] = analyzed_lab_names
data['THCa (%)'] = thca_values
data['THC (%)'] = thc_values
data['CBD (%)'] = cbd_values
data['Moisture (%)'] = moisture_values
data['Water Activity (aw)'] = water_activity_values
data['Test Completion Date'] = test_completion_dates
data['Sample Expiration Date'] = sample_expiration_dates
data['Microbial Pass/Fail'] = microbial_pass_fail
data['Mycotoxins Pass/Fail'] = mycotoxins_pass_fail
data['Pesticides Pass/Fail'] = pesticides_pass_fail
data['Heavy Metals Pass/Fail'] = heavy_metals_pass_fail
data['Method ID'] = method_ids

# Save the updated dataset
data.to_csv('updated_dataset_with_extracted_data.csv', index=False)

