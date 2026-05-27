import json
import unicodedata
from transformers import PreTrainedTokenizerFast
import numpy as np

def measure_nfd_overhead(tokenizer_name="gogamza/kobart-base-v2", sample_file="data/processed/seokbo_parallel.jsonl"):
    print(f"--- NFD vs NFC Sequence Length Validation ---")
    tokenizer = PreTrainedTokenizerFast.from_pretrained(tokenizer_name)
    
    nfd_lengths = []
    nfc_lengths = []
    
    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                item = json.loads(line)
                
                # 원본 텍스트 (우리의 데이터셋은 기본적으로 NFD 정규화 또는 옛한글 조합이 포함되어 있음)
                text_nfd = item.get("input", "")
                if not text_nfd:
                    text_nfd = item.get("middle_korean", "")
                
                if not text_nfd:
                    continue
                
                # 강제로 NFD 적용
                text_nfd = unicodedata.normalize('NFD', text_nfd)
                # NFC로 변환
                text_nfc = unicodedata.normalize('NFC', text_nfd)
                
                tokens_nfd = tokenizer.encode(text_nfd)
                tokens_nfc = tokenizer.encode(text_nfc)
                
                nfd_lengths.append(len(tokens_nfd))
                nfc_lengths.append(len(tokens_nfc))
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    if not nfd_lengths:
        print("No valid data found to measure.")
        return

    avg_nfd = np.mean(nfd_lengths)
    avg_nfc = np.mean(nfc_lengths)
    
    max_nfd = np.max(nfd_lengths)
    max_nfc = np.max(nfc_lengths)
    
    increase_ratio = (avg_nfd / avg_nfc - 1) * 100 if avg_nfc > 0 else 0
    
    print(f"Total samples tested: {len(nfd_lengths)}")
    print(f"Average Tokens (NFC): {avg_nfc:.2f}")
    print(f"Average Tokens (NFD): {avg_nfd:.2f}")
    print(f"Average Length Increase: {increase_ratio:.2f}%")
    print(f"Max Tokens (NFC): {max_nfc}")
    print(f"Max Tokens (NFD): {max_nfd}")
    
    print("\n[Analysis]")
    if increase_ratio > 20:
        print("경고: NFD로 인한 시퀀스 길이 증가율이 20%를 초과합니다. 이는 Autoregressive 디코딩 시 유의미한 성능 저하(Latency 증가)를 유발할 수 있습니다.")
    else:
        print("NFD로 인한 시퀀스 길이 증가가 허용 가능한 범위 내에 있습니다.")

if __name__ == "__main__":
    measure_nfd_overhead()
