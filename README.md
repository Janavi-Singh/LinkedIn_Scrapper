# LinkedIn Profile Scraper (Google Based)

A lightweight Python tool that discovers **LinkedIn profile URLs using Google search** instead of scraping LinkedIn directly.

This approach avoids LinkedIn restrictions while still collecting **targeted professional leads**.

The scraper supports **two Google search providers**:

1. **Serper.dev API** – fast and cost-effective
2. **SERP API** – more stable for large-scale scraping

Both methods fetch Google results and extract **LinkedIn profile links with structured data**.

---

# How It Works

The script sends Google queries like:

```
site:linkedin.com/in "Software Engineer" "Google" "Bangalore"
```

Then it:

1. Fetches Google search results via API
2. Filters irrelevant profiles (ex-employees etc.)
3. Extracts **Name, Job Title, Company**
4. Removes duplicate LinkedIn URLs
5. Exports leads to a CSV file

Example extracted lead:

| Name         | Job Title         | Company | LinkedIn            |
| ------------ | ----------------- | ------- | ------------------- |
| Rahul Sharma | Software Engineer | Google  | linkedin.com/in/... |

---

# Search Approaches

## 1. Serper.dev API (Default)

Used in:

```
main()
```

Best for:

* fast scraping
* lower cost
* small to medium lead generation

Add your key:

```python
SERPER_API_KEY = "your_serper_api_key"
```

Run:

```
python scraper.py
```

---

## 2. SERP API

Used in:

```
serp_main()
```

Best for:

* higher reliability
* large-scale searches

Add your key:

```python
SERP_API_KEY = "your_serp_api_key"
```

Switch entry point:

```python
if __name__ == "__main__":
    serp_main()
```

---

# Input File

Create `input_data.csv` or `input_data.xlsx`.

Example:

| Company | Job Title         | Location  |
| ------- | ----------------- | --------- |
| Google  | Software Engineer | Bengaluru |
| Amazon  | Product Manager   | Hyderabad |
| Infosys | Data Analyst      | Pune      |

---

# Output

The script generates:

```
linkedin_leads.csv
```

Example output:

| Input Company | Name         | Found Job Title   | LinkedIn URL        |
| ------------- | ------------ | ----------------- | ------------------- |
| Google        | Rahul Sharma | Software Engineer | linkedin.com/in/... |

---

# Installation

Install required libraries:

```
pip install requests pandas openpyxl
```

---

# Configuration

Key parameters in the script:

```
RESULTS_PER_PAGE = 10
PAGES_TO_FETCH = 5
```

Example:

```
10 results × 5 pages = 50 profiles per search query
```

---

# Lead Expansion Strategy (Recommended)

To generate **3–4× more leads**, run multiple search variations.

Instead of only:

```
Software Engineer
```

also search:

```
Software Developer
Backend Engineer
SDE
Full Stack Developer
```

Example input expansion:

| Company | Job Title         | Location  |
| ------- | ----------------- | --------- |
| Google  | Software Engineer | Bengaluru |
| Google  | Backend Engineer  | Bengaluru |
| Google  | SDE               | Bengaluru |

This increases lead discovery **without increasing API complexity**.

---

# Notes

* The tool **does not scrape LinkedIn directly**
* It only processes **public Google search results**
* Suitable for **lead generation, recruiting, and market research**
