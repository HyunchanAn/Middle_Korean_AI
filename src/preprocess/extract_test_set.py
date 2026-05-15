import json
import os

def extract_parallel_pairs(jsonl_path):
    pairs = {}
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            item_id = item['id']
            # Extract base ID without -v0 or -v1
            if item_id.endswith('-v0'):
                base_id = item_id[:-3]
                if base_id not in pairs:
                    pairs[base_id] = {}
                pairs[base_id]['mk'] = item['text']
            elif item_id.endswith('-v1'):
                base_id = item_id[:-3]
                if base_id not in pairs:
                    pairs[base_id] = {}
                pairs[base_id]['ko'] = item['text']
    
    # Filter only complete pairs
    complete_pairs = [
        {"id": bid, "middle_korean": p['mk'], "modern_korean": p['ko']}
        for bid, p in pairs.items()
        if 'mk' in p and 'ko' in p
    ]
    return complete_pairs

if __name__ == "__main__":
    raw_path = r"e:\Github\Middle_Korean_AI\data\raw\okhc\cache\datasets--seyoungsong--Open-Korean-Historical-Corpus\snapshots\2d16d39c774ef788069d63223d07e31e038c05df\aks_kyu_nhm.jsonl"
    output_path = r"e:\Github\Middle_Korean_AI\data\processed\test_dataset.json"
    
    print(f"Extracting pairs from {raw_path}...")
    test_pairs = extract_parallel_pairs(raw_path)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(test_pairs, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully saved {len(test_pairs)} pairs to {output_path}")
