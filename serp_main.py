import requests
import pandas as pd
import time
import json

# ================= CONFIGURATION =================
# Replace with your API key from serpapi.com
SERPAPI_KEY = "Your serp api key" 

INPUT_FILE = "input_data.csv"
OUTPUT_FILE = "result_serpapi.csv"
RESULTS_PER_PAGE = 10 
PAGES_TO_FETCH = 5      

def search_serpapi(query, page_num=1):
    url = "https://serpapi.com/search"
    start_offset = (page_num - 1) * RESULTS_PER_PAGE
    
    params = {
        "engine": "google",
        "q": query, 
        "num": RESULTS_PER_PAGE, 
        "start": start_offset,
        "gl": "in",
        "api_key": SERPAPI_KEY
    } 
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() 
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return {}

def run_step1_scaled():
    print(f"--- 🚀 STEP 1: SCALING TO {RESULTS_PER_PAGE * PAGES_TO_FETCH} PROFILES PER QUERY ---")
    try:
        df = pd.read_csv(INPUT_FILE) if INPUT_FILE.endswith('.csv') else pd.read_excel(INPUT_FILE)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    all_results = []
    EX_KEYWORDS = ["ex-", "former", "past", "previous", "was at", "previously"]

    for index, row in df.iterrows():
        in_company = str(row.get('Company', '')).strip()
        in_job = str(row.get('Job Title', '')).strip()
        in_loc = str(row.get('Location', '')).strip()
        
        query = f'LinkedIn profile {in_company} {in_job} {in_loc}'
        print(f"\n[{index+1}] Searching: {query}")

        for p in range(1, PAGES_TO_FETCH + 1):
            if p > 1: print(f"   📂 Fetching Page {p}...")
            data = search_serpapi(query, page_num=p)
            
            if 'organic_results' in data:
                for item in data['organic_results']:
                    link = item.get('link', '')
                    raw_title = item.get('title', '')
                    snippet = item.get('snippet', '').lower()
                    
                    # 1. Profile and Keyword Filter
                    if "linkedin.com/in/" not in link or "/dir/" in link: continue
                    if any(k in snippet for k in EX_KEYWORDS): continue
                    
                    # 2. Extract and Clean the Headline
                    # Remove the standard Google Search suffixes
                    clean_title = raw_title.replace(" | LinkedIn", "").replace(" - LinkedIn", "").strip()
                    
                    # Normalize the first separator to isolate the Name
                    normalized_title = clean_title.replace(" | ", " - ")
                    parts = normalized_title.split(" - ")
                    
                    name = parts[0].strip() if len(parts) > 0 else "N/A"
                    
                    # Everything after the name is the Complete Headline
                    complete_headline = " - ".join(parts[1:]).strip() if len(parts) > 1 else "N/A"
                    
                    # 3. Attempt to split the Headline into Job and Company
                    found_job = "N/A"
                    found_company = "N/A"
                    
                    if complete_headline != "N/A":
                        # Normalize common separators used inside headlines
                        hl_normalized = complete_headline.replace(" at ", " | ").replace(" @ ", " | ").replace(" - ", " | ")
                        hl_parts = [p.strip() for p in hl_normalized.split(" | ") if p.strip()]
                        
                        if len(hl_parts) > 1:
                            found_job = hl_parts[0]
                            found_company = hl_parts[-1] # Assume the last part is the company
                        else:
                            # If we can't split it, dump it into the Job column, 
                            # or Company column if the target company is in the string
                            if in_company.lower() in complete_headline.lower():
                                found_company = complete_headline
                            else:
                                found_job = complete_headline

                    # 4. Save Results
                    if in_company.lower() in raw_title.lower() or in_company.lower() in snippet:
                        all_results.append({
                            "Input Company": in_company,
                            "Input Job Title": in_job,
                            "Input Location": in_loc,
                            "Name": name,
                            "Complete Headline": complete_headline, # <-- NEW COLUMN
                            "Found Company": found_company,
                            "Found Job Title": found_job,
                            "LinkedIn URL": link
                        })
            else:
                break
            
            time.sleep(3) 

    if all_results:
        df_out = pd.DataFrame(all_results).drop_duplicates(subset=['LinkedIn URL'])
        df_out.to_csv(OUTPUT_FILE, index=False)
        print(f"\n✨ DONE! Total unique profiles saved: {len(df_out)}")
    else:
        print("\n❌ No profiles found.")

if __name__ == "__main__":
    run_step1_scaled()
