import json
import unicodedata
import os

def normalize_to_nfd(text: str) -> str:
    """모든 한글 텍스트를 NFD(자모 분리) 형식으로 정규화합니다."""
    return unicodedata.normalize('NFD', text)

def sanitize_dataset(input_file: str, output_file: str):
    """
    오염된 데이터셋을 정화하여 고품질 병렬 코퍼스(Biblify style)로 변환합니다.
    1. 빈 필드 제거
    2. 길이 불일치 제거
    3. 근대 행정 노이즈 제거
    4. NFD 정규화 일괄 적용
    5. modern_source, middle_target 키 구조로 변경
    """
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    clean_pairs = []
    noise_keywords = [
        "隆熙", "光武", "內閣", "總理", "大臣", "觀察使", "報告", "第", "號", "接受", "照覆", "訓令"
    ]

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                # 기존 데이터의 input이 '현대어'인지 '중세어'인지 확인. 
                # (보통 번역 태스크는 input이 현대어, output이 중세어)
                instruction = data.get("instruction", "")
                is_modern_to_middle = "현대어 문장을 중세국어로" in instruction
                
                raw_input = data.get("input", "").strip()
                raw_output = data.get("output", "").strip()

                if not raw_input or not raw_output:
                    continue
                
                # Assign based on instruction direction
                if is_modern_to_middle:
                    modern_text = raw_input
                    middle_text = raw_output
                else:
                    modern_text = raw_output
                    middle_text = raw_input

                # Length check
                ratio = len(modern_text) / len(middle_text) if len(middle_text) > 0 else 0
                if ratio > 4 or ratio < 0.25:
                    continue
                
                # Noise check
                if any(kw in modern_text for kw in noise_keywords) or any(kw in middle_text for kw in noise_keywords):
                    continue
                
                # Normalization
                middle_text_nfd = normalize_to_nfd(middle_text)
                modern_text_nfc = unicodedata.normalize('NFC', modern_text) # 현대어는 보통 NFC

                clean_pairs.append({
                    "modern_source": modern_text_nfc,
                    "middle_target": middle_text_nfd
                })

            except Exception as e:
                continue
                
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        for pair in clean_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
            
    print(f"데이터 정화 완료. {len(clean_pairs)}쌍의 Clean 데이터 확보. -> {output_file}")

if __name__ == "__main__":
    input_path = r"e:\Github\Middle_Korean_AI\data\processed\final_bidirectional_train.jsonl"
    output_path = r"e:\Github\Middle_Korean_AI\data\processed\clean_parallel_corpus.jsonl"
    sanitize_dataset(input_path, output_path)
