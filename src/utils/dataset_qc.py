import json
import unicodedata
import os
import re

def analyze_dataset(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    stats = {
        "total_rows": 0,
        "empty_input": 0,
        "empty_output": 0,
        "short_text": 0,
        "length_mismatch": 0,
        "modern_noise": 0,  # 19th-20th century administrative terms
        "nfd_normalized": 0,
        "nfc_normalized": 0,
        "samples": []
    }

    noise_keywords = [
        "隆熙", "光武", "內閣", "總理", "大臣", "觀察使", "報告", "第", "號", "接受", "照覆"
    ]

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stats["total_rows"] += 1
            try:
                data = json.loads(line)
                input_text = data.get("input", "").strip()
                output_text = data.get("output", "").strip()

                # 1. Empty Check
                if not input_text:
                    stats["empty_input"] += 1
                if not output_text:
                    stats["empty_output"] += 1
                
                if not input_text or not output_text:
                    continue

                # 2. Length Mismatch (Ratio > 4 or < 0.25)
                ratio = len(input_text) / len(output_text) if len(output_text) > 0 else 0
                if ratio > 4 or ratio < 0.25:
                    stats["length_mismatch"] += 1

                # 3. Modern Administrative Noise
                if any(kw in input_text for kw in noise_keywords) or any(kw in output_text for kw in noise_keywords):
                    stats["modern_noise"] += 1

                # 4. Normalization Check
                is_nfd = any('\u1100' <= char <= '\u11FF' for char in input_text + output_text)
                if is_nfd:
                    stats["nfd_normalized"] += 1
                else:
                    stats["nfc_normalized"] += 1

            except Exception as e:
                print(f"Error parsing line {stats['total_rows']}: {e}")

    print("\n=== Dataset Quality Report ===")
    print(f"Total Rows: {stats['total_rows']}")
    print(f"Empty Input: {stats['empty_input']} ({stats['empty_input']/stats['total_rows']*100:.1f}%)")
    print(f"Empty Output: {stats['empty_output']} ({stats['empty_output']/stats['total_rows']*100:.1f}%)")
    print(f"Length Mismatch: {stats['length_mismatch']} ({stats['length_mismatch']/stats['total_rows']*100:.1f}%)")
    print(f"Modern/Admin Noise: {stats['modern_noise']} ({stats['modern_noise']/stats['total_rows']*100:.1f}%)")
    print(f"NFD Normalized: {stats['nfd_normalized']}")
    print(f"NFC Normalized: {stats['nfc_normalized']}")
    
    clean_rows = stats['total_rows'] - stats['empty_input'] - stats['empty_output'] - stats['length_mismatch'] - stats['modern_noise']
    print(f"\nPotential 'Clean' 15th-century Rows: {max(0, clean_rows)}")

if __name__ == "__main__":
    analyze_dataset(r"e:\Github\Middle_Korean_AI\data\processed\final_bidirectional_train.jsonl")
