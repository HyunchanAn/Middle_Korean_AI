import os
import json
import requests
import time
from bs4 import BeautifulSoup
from typing import List, Dict

BASE_URL = "http://db.sejongkorea.org/front/detail.do"

# bkCode, recordId_prefix
TARGETS = [
    ("P13_SS_v006", "P13_SS_e01_v006"), # 석보상절 6
    ("P13_SS_v009", "P13_SS_e01_v009"),
    ("P13_SS_v011", "P13_SS_e01_v011"),
    ("P13_SS_v013", "P13_SS_e01_v013"),
    ("P13_SS_v019", "P13_SS_e01_v019"),
    ("P13_SS_v020", "P13_SS_e01_v020"),
    ("P13_SS_v021", "P13_SS_e01_v021"),
    ("P02_IR_v001", "P02_IR_e01"), # 이륜행실도
    ("P03_JS_v001", "P03_JS_e01")  # 정속언해
]

def get_all_links(bkCode: str, root_id: str) -> List[str]:
    url = f"{BASE_URL}?bkCode={bkCode}&recordId={root_id}"
    response = requests.get(url, timeout=10)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = []
    # Just collect all recordId links that start with root_id
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'recordId=' in href and root_id in href:
            rid = href.split('recordId=')[1].split('&')[0]
            if rid != root_id and rid not in links:
                links.append(rid)
    return links

def parse_article(bkCode: str, record_id: str) -> Dict[str, str]:
    url = f"{BASE_URL}?bkCode={bkCode}&recordId={record_id}"
    response = requests.get(url, timeout=10)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    def get_clean_text(class_name):
        div = soup.find('div', class_=class_name)
        if not div:
            return ""
        for tag in div.find_all(class_='pp_sup_hover'):
            tag.decompose()
        for tag in div.find_all(['sup']):
            tag.decompose()
        return div.get_text(strip=True)

    org_text = get_clean_text('tx_org')
    eh_text = get_clean_text('tx_eh')
    trans_text = get_clean_text('tx_trans')
    
    return {
        "record_id": record_id,
        "original": org_text,
        "middle_korean": eh_text,
        "modern_korean": trans_text
    }

def main():
    print("Starting Extra ITKC Crawler...", flush=True)
    all_articles = []
    
    for bkCode, root in TARGETS:
        print(f"Fetching links for root: {root}", flush=True)
        child_links = get_all_links(bkCode, root)
        print(f"Found {len(child_links)} links.", flush=True)
        
        # We might have links to intermediate menus, or direct links. Let's just visit them all.
        for idx, child_id in enumerate(child_links):
            article_data = parse_article(bkCode, child_id)
            if article_data["middle_korean"] and article_data["modern_korean"]:
                all_articles.append(article_data)
                print(f"  [OK] Extracted from {child_id} ({idx+1}/{len(child_links)})", flush=True)
            time.sleep(0.1)
            
    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/extra_materials.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    print(f"Completed parsing. Total articles saved: {len(all_articles)}", flush=True)

if __name__ == "__main__":
    main()
