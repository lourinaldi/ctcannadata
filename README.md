# Lab Analysis Data Extraction Script

In 2021, in response to a Freedom of Information request (and later, complaint), Connecticut's cannabis regulator began including all cannabis testing laboratory certificates of analysis in the state's public data portal. Unfortunately, the data is not very useful for large-scale analysis in its current form (PDF files linked to in the LAB-ANALYSIS column). This script attempts to rectify this deficiency in an effort to better serve the public interest.

This repository contains a Python script for extracting and analyzing lab analysis data from PDFs and DOCX files linked in a dataset. The script downloads the files, extracts relevant data points, and updates the dataset with this information.

## Warning - Use at Your Own Risk

The script takes a long time to run, because it makes a large number of requests to a state government website, and could potentially be misinterpreted as an attempted denial-of-service attack. The author assumes no responsibility for the actions of others. Proceed at your own risk.

## Dependencies

The script requires the following Python packages:

- `requests`
- `pdfplumber`
- `pandas`
- `python-docx`

To install the required packages using `pip`, run the following command:

```bash
pip install requests pdfplumber pandas python-docx
```

Alternatively, you can install the packages from a `requirements.txt` file with the following content:

```plaintext
requests
pdfplumber
pandas
python-docx
```

Install the packages using:

```bash
pip install -r requirements.txt
```

## Usage

1. Install the dependencies as described above.
2. Run the script `ctcannadata.py` to process the dataset and extract the necessary data points.

```bash
python ctcannadata.py
```

## Script Overview

The script processes a dataset of URLs linking to lab analysis reports in PDF or DOCX format. It downloads these reports, extracts relevant data, and updates the dataset with this information, including:

- Identifying lab names ("Alta Sci", "Analytics Labs", "Northeast Labs")
- Extracting percentages for THCa, THC, CBD
- Extracting moisture content, water activity levels
- Extracting test completion and sample expiration dates
- Pass/fail results for microbial, mycotoxins, pesticides, and heavy metals tests
- Extracting method ID

## Configuration

The script is configured to load data from a given URL. Modify the `data_url` variable in the script to specify a different dataset URL if required:

```python
# Load the dataset from the given URL
data_url = 'https://data.ct.gov/api/views/egd5-wb6r/rows.csv?accessType=DOWNLOAD'
```

## Output

The updated dataset with extracted data is saved to `updated_dataset_with_extracted_data.csv`, containing both the original data and the newly extracted information.

## Known issues

- Some of the COAs in the dataset are read-only Microsoft Word documents with password protection.
  - While `pywin32` allows opening of password-protected Word files, it requires a licensed copy of
Microsoft Office in addition to only being available on Windows. In the interest of keeping this
project portable, the password-protected files will be skipped.

- Some of the PDF-extracted data isn't being properly parsed or ingested.
  - At the very least, the Lab Name column should be a useful addition to the structured data.

## Contributing

Contributions are welcome. Please open issues or submit pull requests with improvements or fixes.

## License

This project is licensed under the GPL 2.0
