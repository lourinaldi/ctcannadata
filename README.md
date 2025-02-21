# Medical Marijuana and Adult-Use Cannabis Brand Report Analysis

In 2021, in response to a Freedom of Information request (and later, complaint), Connecticut's cannabis regulator began including all cannabis testing laboratory certificates of analysis in the state's public data portal. Unfortunately, the data is not very useful for large-scale analysis in its current form (PDF files linked to in the LAB-ANALYSIS column). This script attempts to rectify this deficiency in an effort to better serve the public interest.

This script analyzes medical marijuana and adult-use cannabis brand reports from the Connecticut Department of Consumer Protection. It downloads PDF reports linked in the dataset, extracts valuable data from those reports, and augments the dataset with the extracted information.

## Dataset Source

The dataset is sourced from [data.ct.gov](https://data.ct.gov/Health-and-Human-Services/Medical-Marijuana-and-Adult-Use-Cannabis-Brand-Reg/egd5-wb6r/data).

## Setup

### Warning - Use at Your Own Risk

The script takes a long time to run, because it makes a large number of requests to a state government website, and could potentially be misinterpreted as an attempted denial-of-service attack. The author assumes no responsibility for the actions of others. Proceed at your own risk.

### Methodology

The script performs the following tasks:

- Load Dataset: Fetches the dataset from the given URL.
- Sanitize URLs: Sanitizes URLs in the LAB-ANALYSIS column by removing the first 8 characters and the last character.
- Download and Analyze PDFs: Downloads PDFs, extracts text using pdfplumber, and identifies the lab name.
- Extract Additional Data: Extracts various data points such as cannabinoid content, moisture, water activity, test dates, and pass/fail statuses.
- Augment Dataset: Adds the extracted data to the dataset.
- Save Dataset: Saves the updated dataset to a CSV file.

### Prerequisites

- Python 3.x
- Required Python libraries:
  - `requests`
  - `pdfplumber`
  - `pandas`
  - `os`
  - `re`

### Installing dependencies

You can install the required Python libraries using pip:

```sh

pip install requests pdfplumber pandas

