# 🕵️‍♂️ LinkedIn Profile Scraper (Serper API)

## 📌 Overview
This Python script automates the process of discovering highly relevant LinkedIn profile URLs using Google Search via the Serper.dev API. 

Instead of searching directly on LinkedIn (which can lead to account restrictions), this tool acts as a "White Hat" scraper. It reads a list of target companies, job titles, and locations, paginates through multiple pages of Google results, smartly filters out irrelevant profiles (like ex-employees), and exports a clean CSV of targeted leads.

## ✨ Key Features
* Deep Pagination: Automatically fetches multiple pages of Google results (default: 5 pages / 50 profiles per query) to maximize lead volume.
* Smart Filtering: Automatically excludes directories and ex-employees by scanning snippets for negative keywords (`ex-`, `former`, `past`, `previously`, etc.).
* Company Match Verification: Ensures the target company is actually mentioned in the search title or snippet before saving.
* Auto-Parsing: Cleans and splits the Google Search title to extract the lead's Name, Current Job Title, and Current Company.
* De-duplication: Automatically removes duplicate URLs before exporting to keep your data clean.

## 🛠️ Prerequisites
* Python 3.7+ installed on your machine.
* A free API key from [Serper.dev](https://serper.dev/).

Install the required Python libraries:
```bash
pip install requests pandas openpyxl

```

*(Note: `openpyxl` is required if your input file is an Excel `.xlsx` file).*

## 🚀 Setup & Usage

### 1. Prepare your input data

Create a file named `input_data.csv` (or `input_data.xlsx`) in the same folder as the script. It **must** have the following exact column headers:

**Input Table Format (`input_data.csv`)**
| Company | Job Title | Location |
| :--- | :--- | :--- |
| Google | Software Engineer | Bengaluru |
| Amazon | Product Manager | Hyderabad |
| Microsoft | Data Scientist | Pune |

### 2. Add your API Key

Open the Python script and replace the placeholder in the Configuration section with your actual API key:

```python
SERPER_API_KEY = "your_actual_api_key_here"

```

### 3. Run the script

Execute the script from your terminal:

```bash
python your_script_name.py

```

## ⚙️ Configuration Options

You can tweak the variables at the top of the script to change how it behaves:

* `INPUT_FILE`: Change this if your starting file has a different name.
* `OUTPUT_FILE`: The name of the final generated CSV (default: `step1_urls_scaled3.csv`).
* `RESULTS_PER_PAGE`: Number of results Google returns per page (default: 10).
* `PAGES_TO_FETCH`: How deep Google should search per query (default: 5 pages = up to 50 results per query).

## 📂 Output Format

The script will generate a file named `step1_urls_scaled3.csv`. The output will be neatly organized into the following columns:

**Output Table Format (`step1_urls_scaled3.csv`)**
| Input Company | Input Job Title | Input Location | Name | Found Company | Found Job Title | LinkedIn URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Google | Software Engineer | Bengaluru | Janavi Singh | Google | Software Engineer | https://www.google.com/search?q=https://linkedin.com/in/janavisingh... |
| Amazon | Product Manager | Hyderabad | John Doe | Amazon | Product Manager | https://www.google.com/search?q=https://linkedin.com/in/johndoe... |

## ⚠️ Important Notes

* **Regional Targeting:** The script uses `"gl": "in"` in the API payload. This forces Google to return results localized to **India**. If you are searching for leads in other countries, you should change this to `"us"`, `"uk"`, or remove the `"gl"` parameter entirely.
* **Rate Limits:** The script includes a `time.sleep(1.5)` pause between page fetches to respect API rate limits and avoid connection errors.

```

