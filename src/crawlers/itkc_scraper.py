import os
import json
import requests
import time
from bs4 import BeautifulSoup
from typing import List, Dict

BASE_URL = "http://db.sejongkorea.org/front/detail.do"
ROOT_IDS = [
    "P01_SG_e01_v001_0000", # 삼강행실효자도
    "P01_SG_e01_v002_0000", # 삼강행실충신도
    "P01_SG_e01_v003_0000"  # 삼강행실열녀도
]

def get_child_links(root_id: str) -> List[str]:
    url = f"{BASE_URL}?bkCode=P01_SG_v001&recordId={root_id}"
    response = requests.get(url, timeout=10)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = []
    prefix = root_id[:-4]
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'recordId=' in href and prefix in href:
            rid = href.split('recordId=')[1].split('&')[0]
            if rid != root_id and rid not in links and rid.endswith('0'):
                links.append(rid)
    return links

def parse_article(record_id: str) -> Dict[str, str]:
    url = f"{BASE_URL}?bkCode=P01_SG_v001&recordId={record_id}"
    response = requests.get(url, timeout=10)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    def get_clean_text(class_name):
        div = soup.find('div', class_=class_name)
        if not div:
            return ""
        for tag in div.find_all(class_='pp_sup_hover'):
            tag.decompose()
        # Also remove standard footnote marks if they exist outside pp_sup_hover
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
    print("Starting ITKC Crawler...", flush=True)
    all_articles = []
    
    for root in ROOT_IDS:
        print(f"Fetching links for root: {root}", flush=True)
        child_links = get_child_links(root)
        print(f"Found {len(child_links)} articles.", flush=True)
        
        # Process all articles
        for idx, child_id in enumerate(child_links):
            print(f"  Parsing {child_id} ({idx+1}/{len(child_links)})...", flush=True)
            article_data = parse_article(child_id)
            if article_data["middle_korean"] and article_data["modern_korean"]:
                all_articles.append(article_data)
            time.sleep(0.1)
            
    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/samgang_haengsildo.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    print(f"Completed parsing. Total articles saved: {len(all_articles)}", flush=True)

if __name__ == "__main__":
    main()
