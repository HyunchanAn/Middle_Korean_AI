import json
import argparse
from transformers import PreTrainedTokenizerFast
from collections import Counter
import unicodedata

def find_missing_tokens(corpus_path: str, model_name: str = "gogamza/kobart-base-v2"):
    print(f"Loading Tokenizer: {model_name}")
    tokenizer = PreTrainedTokenizerFast.from_pretrained(model_name)
    
    unk_token = tokenizer.unk_token
    unk_token_id = tokenizer.unk_token_id
    
    missing_chars_counter = Counter()
    total_unks = 0
    total_tokens = 0
    
    print(f"Scanning corpus: {corpus_path}")
    with open(corpus_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if "middle_target" in data:
                    text = data["middle_target"]
                    # NFD 보장 (이미 되어있겠지만 안전하게)
                    text = unicodedata.normalize('NFD', text)
                    
                    tokens = tokenizer.tokenize(text)
                    token_ids = tokenizer.encode(text)
                    
                    total_tokens += len(tokens)
                    
                    if unk_token in tokens:
                        # Find which characters are actually unknown.
                        # Since tokenization might lose character mapping, 
                        # we can test each character individually against the tokenizer.
                        for char in text:
                            # Skip standard whitespace
                            if char.isspace():
                                continue
                            
                            char_tokenized = tokenizer.tokenize(char)
                            if len(char_tokenized) > 0 and char_tokenized[0] == unk_token:
                                missing_chars_counter[char] += 1
                                total_unks += 1
                                
            except Exception as e:
                continue
                
    print("\n--- Tokenization Report ---")
    print(f"Total tokens processed (approx): {total_tokens}")
    print(f"Total UNK occurrences detected: {total_unks}")
    
    print("\n--- Missing Characters (Candidates for add_tokens) ---")
    if not missing_chars_counter:
        print("No UNK tokens found! Vocabulary is sufficient.")
    else:
        for char, count in missing_chars_counter.most_common():
            hex_code = f"U+{ord(char):04X}"
            name = unicodedata.name(char, "UNKNOWN_NAME")
            print(f"'{char}' ({hex_code}) - {name}: {count} times")
            
    # Return as a list of missing characters to easily pass to add_tokens later
    return list(missing_chars_counter.keys())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find missing NFD old Hangul tokens.")
    parser.add_argument("--corpus", type=str, default="../../data/processed/clean_parallel_corpus.jsonl", help="Path to jsonl corpus")
    args = parser.parse_args()
    
    missing = find_missing_tokens(args.corpus)
    if missing:
        print(f"\nSuggestion for train_translator.py:")
        print(f"new_tokens = {missing}")
