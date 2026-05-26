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
    output_file = "data/processed/extra_parallel.jsonl"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return
        
    with open(input_file, "r", encoding="utf-8") as f:
        articles = json.load(f)
        
    processed_count = 0
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f_out:
        for article in articles:
            mk_text = normalize_middle_korean(article["middle_korean"])
            mod_text = article["modern_korean"]
            
            if mk_text.strip() and mod_text.strip():
                out_data = {
                    "input": mk_text,
                    "output": mod_text,
                    "metadata": {
                        "source": "itkc_extra",
                        "record_id": article["record_id"]
                    }
                }
                f_out.write(json.dumps(out_data, ensure_ascii=False) + "\n")
                processed_count += 1
                
    print(f"Extra dataset built. Total pairs: {processed_count}")

if __name__ == "__main__":
    build_extra_dataset()
