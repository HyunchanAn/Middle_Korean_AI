import json
import re
import os
from pathlib import Path

def is_hanja_heavy(text, threshold=0.15):
    """Check if the text has a Hanja character ratio exceeding the threshold."""
    if not text.strip():
        return False
    # Unicode ranges for CJK Unified Ideographs
    hanja_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')
    hanja_chars = hanja_pattern.findall(text)
    
    # Exclude whitespaces for ratio calculation to be more strict
    text_len = len(text.replace(" ", "").replace("\n", ""))
    if text_len == 0:
        return False
        
    ratio = len(hanja_chars) / text_len
    return ratio > threshold

def has_modern_keywords(text):
    """Check for late Joseon / Japanese colonial era administrative keywords."""
    keywords = [
        r"報告", r"隆熙", r"光武", r"委員", r"裁判", r"總理大臣", 
        r"照會", r"指令", r"內閣", r"議政府", r"大韓", r"度支部", 
        r"內部大臣", r"建陽", r"外部大臣", r"勅書", r"完文", r"左開"
    ]
    pattern = re.compile('|'.join(keywords))
    return bool(pattern.search(text))

def filter_corpus(input_path, output_path):
    print(f"Reading from: {input_path}")
    salvaged_count = 0
    total_count = 0
    
    salvaged_data = []
    
    with open(input_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            if not line.strip():
                continue
            total_count += 1
            data = json.loads(line)
            
            text_to_check = data.get("input", "") + "\n" + data.get("output", "")
            
            if is_hanja_heavy(text_to_check, threshold=0.15):
                continue
                
            if has_modern_keywords(text_to_check):
                continue
                
            salvaged_data.append(data)
            salvaged_count += 1
            
    print(f"Filtering complete. Total: {total_count} -> Salvaged: {salvaged_count} (Discarded: {total_count - salvaged_count})")
    
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for data in salvaged_data:
            outfile.write(json.dumps(data, ensure_ascii=False) + "\n")
            
    print(f"Saved salvaged data to: {output_path}")

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent
    input_file = project_root / "data" / "processed" / "final_bidirectional_train.jsonl"
    output_file = project_root / "data" / "processed" / "salvaged_corpus.jsonl"
    
    filter_corpus(input_file, output_file)
