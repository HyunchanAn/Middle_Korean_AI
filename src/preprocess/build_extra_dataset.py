import os
import json
import unicodedata
from hypua2jamo import translate

def normalize_middle_korean(text: str) -> str:
    """Convert Hanyang PUA to standard Jamo and NFD normalize"""
    text = translate(text)
    return unicodedata.normalize('NFD', text)

def build_extra_dataset():
    input_file = "data/raw/extra_materials.json"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return
        
    with open(input_file, "r", encoding="utf-8") as f:
        articles = json.load(f)
        
    os.makedirs("data/processed", exist_ok=True)
    
    # Map record prefix to output file name
    file_map = {
        "P13_SS": "data/processed/seokbo_parallel.jsonl",
        "P02_IR": "data/processed/iryun_parallel.jsonl",
        "P03_JS": "data/processed/jeongsok_parallel.jsonl"
    }
    
    # Keep track of file handles and counts
    file_handles = {}
    counts = {"seokbo": 0, "iryun": 0, "jeongsok": 0, "extra": 0}
    
    for prefix, path in file_map.items():
        file_handles[prefix] = open(path, "w", encoding="utf-8")
    
    # Fallback for unknown
    file_handles["default"] = open("data/processed/extra_parallel.jsonl", "w", encoding="utf-8")
    
    for article in articles:
        mk_text = normalize_middle_korean(article["middle_korean"])
        mod_text = article["modern_korean"]
        record_id = article["record_id"]
        
        target_prefix = "default"
        target_name = "extra"
        for prefix in file_map.keys():
            if record_id.startswith(prefix):
                target_prefix = prefix
                if prefix == "P13_SS": target_name = "seokbo"
                elif prefix == "P02_IR": target_name = "iryun"
                elif prefix == "P03_JS": target_name = "jeongsok"
                break
                
        if mk_text.strip() and mod_text.strip():
            out_data = {
                "input": mk_text,
                "output": mod_text,
                "metadata": {
                    "source": target_name,
                    "record_id": record_id
                }
            }
            file_handles[target_prefix].write(json.dumps(out_data, ensure_ascii=False) + "\n")
            counts[target_name] += 1
            
    for f in file_handles.values():
        f.close()
        
    for name, count in counts.items():
        if count > 0:
            print(f"{name} dataset built. Total pairs: {count}")

if __name__ == "__main__":
    build_extra_dataset()
