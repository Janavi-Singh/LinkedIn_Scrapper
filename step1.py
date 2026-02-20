import requests
import pandas as pd
import json
import time

# ================= CONFIGURATION =================
SERPER_API_KEY = "Your api key"
INPUT_FILE = "input_data.csv"       # Columns: Company, Job Title, Location
OUTPUT_FILE = "step1_urls.csv"

def search_serper(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "num": 10, "gl": "in"}) 
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload)
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return {}

def run_step1():
    print("--- 🕵️ STEP 1: FINDING URLS ---")
    try:
        df = pd.read_csv(INPUT_FILE) if INPUT_FILE.endswith('.csv') else pd.read_excel(INPUT_FILE)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    results = []

    for index, row in df.iterrows():
        company = str(row.get('Company', '')).strip()
        job = str(row.get('Job Title', '')).strip()
        loc = str(row.get('Location', '')).strip()
        
        # --- OPTIMIZED QUERY ---
        # Uses exact phrase matching, 'intitle' for the headline, and 'Present'/'Current' for active roles
        query = f'site:linkedin.com/in/ intitle:"{company}" "{job}" ("Present" OR "Current") {loc}'
        print(f"[{index+1}] Searching: {query}")
        
        data = search_serper(query)
        
        if 'organic' in data:
            for item in data['organic']:
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                link = item.get('link', '')
                
                # --- OPTIMIZED VALIDATION ---
                # 1. Must be a profile (/in/), NOT a directory (/dir/) or a post.
                # 2. The company name MUST appear in the title (headline) or snippet (preview).
                is_profile = "/in/" in link and "/dir/" not in link
                mentions_company = company.lower() in title.lower() or company.lower() in snippet.lower()
                
                if is_profile and mentions_company: 
                    # Clean up the name by splitting standard LinkedIn title formats
                    clean_name = title.split(" - ")[0].split(" | ")[0].strip()
                    
                    results.append({
                        "Search Query": query,
                        "Name": clean_name,
                        "Company Targeted": company,
                        "LinkedIn URL": link
                    })
        
        time.sleep(1.5) # Safety delay to avoid overwhelming the API

    # Save unique URLs only
    df_out = pd.DataFrame(results).drop_duplicates(subset=['LinkedIn URL'])
    df_out.to_csv(OUTPUT_FILE, index=False)
    print(f"--- ✅ STEP 1 DONE. Saved {len(df_out)} unique profiles to {OUTPUT_FILE} ---")

if __name__ == "__main__":
    run_step1()
