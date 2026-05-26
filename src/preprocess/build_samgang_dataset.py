import os
import json
import unicodedata
from hypua2jamo import translate

def normalize_middle_korean(text: str) -> str:
    """Convert Hanyang PUA to standard Jamo and NFD normalize"""
    text = translate(text)
    return unicodedata.normalize('NFD', text)

def main():
    raw_path = "data/raw/samgang_haengsildo.json"
    out_path = "data/processed/samgang_parallel.jsonl"
    
    if not os.path.exists(raw_path):
        print(f"File not found: {raw_path}")
        return
        
    with open(raw_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    processed = []
    for item in data:
        # Get texts
        mk_text = item.get("middle_korean", "").strip()
        modern_text = item.get("modern_korean", "").strip()
        org_text = item.get("original", "").strip()
        
        if not mk_text or not modern_text:
            continue
            
        # NFD normalize
        mk_text_nfd = normalize_middle_korean(mk_text)
        
        # We create training pairs. The instruction is consistent with dummy_train.
        # "다음 중세국어 문장을 현대어로 번역하세요."
        entry = {
            "instruction": "다음 중세국어 문장을 현대어로 번역하세요.",
            "input": mk_text_nfd,
            "output": modern_text,
            "metadata": {
                "source": "samgang_haengsildo",
                "record_id": item["record_id"],
                "original_hanja": org_text
            }
        }
        processed.append(entry)
        
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        for p in processed:
            f.write(json.dumps(p, ensure_ascii=False) + '\n')
            
    print(f"Built {len(processed)} parallel pairs in {out_path}.")

if __name__ == "__main__":
    main()
