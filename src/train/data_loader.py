import json
from datasets import Dataset

def load_and_tokenize_data(json_path, tokenizer, max_length=128):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # period 토큰을 source 앞에 붙여줍니다. (예: "[15C] 나랏말싸미...")
    sources = [item['period'] + " " + item['source'] for item in data]
    targets = [item['target'] for item in data]
    
    # Tokenize 인풋 (중세국어)
    model_inputs = tokenizer(
        sources, max_length=max_length, padding="max_length", truncation=True
    )
    
    # Tokenize 라벨 (현대국어)
    labels = tokenizer(
        targets, max_length=max_length, padding="max_length", truncation=True
    )
    
    # pad 토큰은 로스 계산 시 무시하도록 -100으로 설정
    labels_with_ignore_index = []
    for label in labels["input_ids"]:
        labels_with_ignore_index.append([l if l != tokenizer.pad_token_id else -100 for l in label])
        
    model_inputs["labels"] = labels_with_ignore_index
    
    dataset = Dataset.from_dict(model_inputs)
    return dataset
