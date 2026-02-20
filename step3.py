import pandas as pd
import re
import os

# ================= CONFIGURATION =================
INPUT_GOALS = "input_data.csv"
STEP1_DATA = "step1_urls.csv"
SCRAPED_DUMP = "step2_dump.csv"
FINAL_EXCEL = "LinkedIn_Report_1.xlsx"

# Standardizing city names
LOCATION_MAP = {
    "bangalore": ["bengaluru", "blr", "karnataka"],
    "mumbai": ["bombay", "navimumbai", "maharashtra"],
    "delhi": ["ncr", "gurgaon", "gurugram", "noida", "new delhi"],
    "hyderabad": ["secunderabad", "telangana"],
    "pune": ["poona", "maharashtra"]
}

def clean_val(val):
    return str(val).strip().lower()

def extract_current_role(raw_dump, target_company):
    """
    Finds ALL blocks containing 'Present' and picks the one 
    most likely to be the Experience section.
    """
    dump = str(raw_dump)
    # Split by newlines or pipes to get clean lines
    lines = [line.strip() for line in re.split(r'[\n|·]', dump) if line.strip()]
    
    found_title = "N/A"
    found_company = "N/A"
    
    # Iterate through lines to find 'Present' or 'Current'
    for i, line in enumerate(lines):
        if re.search(r"\b(present|current)\b", line, re.I):
            # LinkedIn Experience Pattern:
            # lines[i-2] = Job Title
            # lines[i-1] = Company Name
            # lines[i]   = Date (Present)
            
            potential_comp = lines[i-1] if i-1 >= 0 else "Unknown"
            potential_title = lines[i-2] if i-2 >= 0 else "Unknown"
            
            # If this specific 'Present' block matches our target company, 
            # we prioritize it and stop searching.
            if target_company.lower() in potential_comp.lower():
                return potential_title, potential_comp
            
            # Otherwise, we store the first 'Present' we find as the default
            if found_company == "N/A":
                found_title, found_company = potential_title, potential_comp
                
    return found_title, found_company

def run_final_matching():
    print("--- 🛠️  Running Deterministic Matching... ---")
    
    try:
        df_goals = pd.read_csv(INPUT_GOALS)
        df_step1 = pd.read_csv(STEP1_DATA)
        df_scraped = pd.read_csv(SCRAPED_DUMP)
    except Exception as e:
        print(f"❌ Load Error: {e}")
        return

    # Use Step 1 for the 'Source of Truth' on Names
    name_map = dict(zip(df_step1['LinkedIn URL'], df_step1['Name']))
    final_report = []

    for _, row_scr in df_scraped.iterrows():
        url = row_scr.get('LinkedIn URL')
        raw_text = row_scr.get('Raw Text Dump', '')
        
        if pd.isna(url) or len(str(raw_text)) < 50:
            continue

        # 1. Map Name and Goal
        person_name = name_map.get(url, "Unknown")
        
        # Pull original targets from Step 1 file
        target_info = df_step1[df_step1['LinkedIn URL'] == url]
        if target_info.empty: continue
        
        target_comp = str(target_info.iloc[0].get('Company Targeted', ''))
        
        # Pull Job/Loc targets from Input Goals
        goal_row = df_goals[df_goals['Company'].str.lower() == target_comp.lower()]
        target_job = goal_row.iloc[0]['Job Title'] if not goal_row.empty else "N/A"
        target_loc = goal_row.iloc[0]['Location'] if not goal_row.empty else "N/A"

        # 2. Extract Experience based on 'Present' anchors
        actual_title, actual_company = extract_current_role(raw_text, target_comp)

        # 3. Validation Logic
        comp_match = "Match" if target_comp.lower() in actual_company.lower() else "Mismatch"
        
        # Location Validation
        profile_loc = str(row_scr.get('Location', 'N/A'))
        loc_match = "Mismatch"
        synonyms = [target_loc.lower()] + LOCATION_MAP.get(target_loc.lower(), [])
        if any(s in profile_loc.lower() or s in raw_text[:1000].lower() for s in synonyms):
            loc_match = "Match"

        final_report.append({
            "Person Name": person_name,
            "LinkedIn URL": url,
            "Input Company": target_comp,
            "Company Status": comp_match,
            "Input Job Title": target_job,
            "Input Location": target_loc,
            "Location Status": loc_match
        })

    # Save to Excel
    df_output = pd.DataFrame(final_report).drop_duplicates(subset=['LinkedIn URL'])
    df_output.to_excel(FINAL_EXCEL, index=False, engine='openpyxl')
    
    print(f"--- ✅ Report Generated: {FINAL_EXCEL} ---")

if __name__ == "__main__":
    run_final_matching()