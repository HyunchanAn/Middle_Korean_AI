import json
import torch
import torch.nn.functional as F
from pathlib import Path
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration, BartModel
from peft import PeftModel, PeftConfig

def load_models(base_model_name="gogamza/kobart-base-v2", lora_path="models/lora_model_bidirectional_v3"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Base Model on {device}...")
    tokenizer = PreTrainedTokenizerFast.from_pretrained(base_model_name)
    base_model = BartForConditionalGeneration.from_pretrained(base_model_name)
    
    # Load LoRA if exists
    if Path(lora_path).exists():
        print(f"Loading LoRA from {lora_path}...")
        model = PeftModel.from_pretrained(base_model, lora_path)
    else:
        print(f"LoRA weights not found at {lora_path}. Using base model.")
        model = base_model
        
    model = model.to(device)
    model.eval()
    
    # Encoder for similarity
    print("Loading Encoder for Similarity Filtering...")
    encoder = BartModel.from_pretrained(base_model_name).encoder.to(device)
    encoder.eval()
    
    return tokenizer, model, encoder, device

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

def compute_similarity(tokenizer, encoder, device, source, target):
    with torch.no_grad():
        encoded_src = tokenizer([source], padding=True, truncation=True, return_tensors='pt').to(device)
        encoded_tgt = tokenizer([target], padding=True, truncation=True, return_tensors='pt').to(device)
        
        output_src = encoder(**encoded_src)
        output_tgt = encoder(**encoded_tgt)
        
        vec_src = mean_pooling(output_src, encoded_src['attention_mask'])
        vec_tgt = mean_pooling(output_tgt, encoded_tgt['attention_mask'])
        
        sim = F.cosine_similarity(vec_src, vec_tgt).item()
    return sim

def run_pipeline():
    project_root = Path(__file__).resolve().parent.parent.parent
    input_file = project_root / "data" / "raw" / "unlabeled_mk_sentences.json"
    output_file = project_root / "data" / "synthetic" / "auto_expanded_mk.jsonl"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if not input_file.exists():
        print(f"Input file not found: {input_file}")
        return
        
    with open(input_file, 'r', encoding='utf-8') as f:
        sentences = json.load(f)
        
    tokenizer, model, encoder, device = load_models()
    
    print(f"Starting auto-expansion pipeline for {len(sentences)} sentences...")
    
    passed_data = []
    rejected = 0
    threshold = 0.7
    
    for idx, source in enumerate(sentences):
        # 1. Inference
        inputs = tokenizer(source, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=128)
        target = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 2. Similarity Filter
        sim = compute_similarity(tokenizer, encoder, device, source, target)
        
        if sim >= threshold:
            passed_data.append({
                "input": source,
                "output": target,
                "similarity": round(sim, 4),
                "source": "auto_expansion"
            })
        else:
            rejected += 1
            
        if (idx + 1) % 50 == 0:
            print(f"[{idx+1}/{len(sentences)}] Passed: {len(passed_data)}, Rejected: {rejected}")
            
    # 3. Export to JSONL (Ready for Google Sheets / Streamlit UI)
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in passed_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
    print(f"Pipeline finished! Total Passed: {len(passed_data)}, Rejected: {rejected}")
    print(f"Data saved to {output_file} - Ready to be loaded into Streamlit / Google Sheets.")

if __name__ == "__main__":
    run_pipeline()
