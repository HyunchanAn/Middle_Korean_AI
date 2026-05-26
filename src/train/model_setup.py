from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration

def setup_model_and_tokenizer(model_name="gogamza/kobart-base-v2"):
    # KoBART 토크나이저 및 모델 로드
    tokenizer = PreTrainedTokenizerFast.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)
    
    # 15세기, 17세기 등 시대별 특수 토큰 추가
    special_tokens_dict = {'additional_special_tokens': ['[15C]', '[17C]']}
    num_added_toks = tokenizer.add_special_tokens(special_tokens_dict)
    
    if num_added_toks > 0:
        print(f"Added {num_added_toks} special tokens to tokenizer.")
        # 새로운 토큰이 추가되었으므로 모델의 임베딩 레이어 크기를 재조정
        model.resize_token_embeddings(len(tokenizer))
        
    return model, tokenizer
