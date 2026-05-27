import json
import re
from pathlib import Path
import torch
import torch.nn.functional as F
from transformers import PreTrainedTokenizerFast, BartModel

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

def filter_translations_with_embeddings(input_path: str, output_path: str, threshold: float = 0.5):
    """
    LLM 역번역 결과물에서 환각(Hallucination) 및 오류 데이터를 휴리스틱과 임베딩 코사인 유사도로 걸러냅니다.
    (Issue #7 구현)
    """
    print("Loading KoBART for embedding similarity...")
    tokenizer = PreTrainedTokenizerFast.from_pretrained("gogamza/kobart-base-v2")
    # Using BartModel to access encoder hidden states
    model = BartModel.from_pretrained("gogamza/kobart-base-v2").eval()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    valid_data = []
    rejected_heuristic = 0
    rejected_similarity = 0
    
    # 챗봇 특유의 추임새 필터링
    leakage_patterns = [r"번역[ :]+", r"해석[ :]+", r"현대어[ :]+", r"의미[ :]+", r"여기 번역"]
    
    for idx, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            source = item.get("input", "")
            target = item.get("output", "")
            
            # --- 1. Heuristic Filter ---
            ratio = len(target) / max(len(source), 1)
            if ratio > 3.0 or ratio < 0.3:
                rejected_heuristic += 1
                continue
                
            if re.search(r'[a-zA-Z]', target):
                rejected_heuristic += 1
                continue
                
            is_leakage = False
            for pattern in leakage_patterns:
                if re.search(pattern, target):
                    is_leakage = True
                    break
            if is_leakage:
                rejected_heuristic += 1
                continue
                
            # --- 2. Continuous Embedding Similarity Filter ---
            # Encode both source and target using the encoder
            with torch.no_grad():
                encoded_src = tokenizer([source], padding=True, truncation=True, return_tensors='pt').to(device)
                encoded_tgt = tokenizer([target], padding=True, truncation=True, return_tensors='pt').to(device)
                
                # Pass through the encoder
                output_src = model.encoder(**encoded_src)
                output_tgt = model.encoder(**encoded_tgt)
                
                # Mean pooling
                vec_src = mean_pooling(output_src, encoded_src['attention_mask'])
                vec_tgt = mean_pooling(output_tgt, encoded_tgt['attention_mask'])
                
                # Cosine Similarity
                sim = F.cosine_similarity(vec_src, vec_tgt).item()
                
            if sim < threshold:
                rejected_similarity += 1
                continue
                
            item["similarity_score"] = round(sim, 4)
            valid_data.append(item)
            
            if (idx + 1) % 100 == 0:
                print(f"Processed {idx + 1}/{len(lines)}...")
                
        except json.JSONDecodeError:
            continue
            
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in valid_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
    print(f"Total: {len(lines)} | Passed: {len(valid_data)}")
    print(f"Rejected by Heuristic: {rejected_heuristic}")
    print(f"Rejected by Similarity (thresh={threshold}): {rejected_similarity}")

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent
    input_file = project_root / "data" / "processed" / "synthetic_mk_parallel.jsonl"
    output_file = project_root / "data" / "processed" / "filtered_mk_parallel_v2.jsonl"
    
    if input_file.exists():
        filter_translations_with_embeddings(str(input_file), str(output_file), threshold=0.7)
    else:
        print(f"Input file not found: {input_file}")
