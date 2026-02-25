import requests
import pandas as pd
import json
import time

# ================= CONFIGURATION =================
SERPER_API_KEY = "your api key"
INPUT_FILE = "input_data.csv"
OUTPUT_FILE = "step1_urls_scaled3.csv"
RESULTS_PER_PAGE = 10 
PAGES_TO_FETCH = 5      

def search_serper(query, page_num=1):
    url = "https://google.serper.dev/search"
    # 'num' controls results per page, 'page' handles pagination
    payload = json.dumps({
        "q": query, 
        "num": RESULTS_PER_PAGE, 
        "page": page_num,
        "gl": "in"
    }) 
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload)
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
        print(f"[{index+1}] Searching: {query}")

        for p in range(1, PAGES_TO_FETCH + 1):
            if p > 1: print(f"   📂 Fetching Page {p}...")
            data = search_serper(query, page_num=p)
            
            if 'organic' in data:
                for item in data['organic']:
                    link = item.get('link', '')
                    title = item.get('title', '')
                    snippet = item.get('snippet', '').lower()
                    
                    # 1. Profile and Keyword Filter
                    if "linkedin.com/in/" not in link or "/dir/" in link: continue
                    if any(k in snippet for k in EX_KEYWORDS): continue
                    
                    # 2. Company Match Filter
                    if in_company.lower() in title.lower() or in_company.lower() in snippet:
                        # Extract Name and Company from Title
                        parts = [p.strip() for p in title.split(" - ")]
                        if len(parts) < 2:
                            parts = [p.strip() for p in title.split(" | ")]

                        all_results.append({
                            "Input Company": in_company,
                            "Input Job Title": in_job,
                            "Input Location": in_loc,
                            "Name": parts[0] if len(parts) > 0 else "N/A",
                            "Found Company": parts[-1] if len(parts) > 1 else in_company, # LAST PART usually company
                            "Found Job Title": parts[1] if len(parts) > 2 else "N/A",
                            "LinkedIn URL": link
                        })
            
            time.sleep(1.5) # Gentle pause between pages

    if all_results:
        df_out = pd.DataFrame(all_results).drop_duplicates(subset=['LinkedIn URL'])
        df_out.to_csv(OUTPUT_FILE, index=False)
        print(f"\n✨ DONE! Total unique profiles saved: {len(df_out)}")
    else:
        print("\n❌ No profiles found.")

if __name__ == "__main__":
    run_step1_scaled()
