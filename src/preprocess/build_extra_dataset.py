import os
import re
import json
import unicodedata
from hypua2jamo import translate

def normalize_middle_korean(text: str) -> str:
    """Convert Hanyang PUA to standard Jamo and NFD normalize"""
    text = translate(text)
    return unicodedata.normalize('NFD', text)

def clean_modern_korean(text: str) -> str:
    """현대어 번역에서 역자 주석, 해설, 부가 설명 등을 제거하여 순수 번역문만 남긴다.

    제거 대상:
      - 【...】 괄호 안의 주석/역주 전체
      - 〈역자 주〉 이후의 모든 텍스트 (역자 해설)
      - [상두산 설법] 같은 소제목 태그
    """
    # 1. 【...】 주석 제거 (닫히는 괄호가 있는 경우)
    text = re.sub(r'【[^】]*】', '', text)
    # 1-1. 닫히지 않는 【 이후 텍스트도 전부 제거 (문장 끝까지 주석이 이어지는 경우)
    idx = text.find('【')
    if idx != -1:
        text = text[:idx]
    # 2. 〈역자 주〉 또는 〈역주〉 이후 텍스트 전부 잘라내기
    for marker in ['〈역자 주〉', '〈역주〉', '역자 주']:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
    # 3. [소제목] 제거
    text = re.sub(r'\[[^\]]*\]', '', text)
    # 4. 연속 공백 정리
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_middle_korean(text: str) -> str:
    """원문(옛한글)에서 페이지 표기, 소제목 등 비본문 요소를 제거한다.

    제거 대상:
      - [상두산 설법] 같은 소제목 태그
      - 석보상절 6:표지, 석보상절 6:1ㄱ 등 페이지 라벨
      - 이륜행실형제도 1ㄴ(옥산서원본) 등 판본 표기
    """
    # 1. [소제목] 제거
    text = re.sub(r'\[[^\]]*\]', '', text)
    # 2. 석보상절 페이지 라벨 제거 (예: 석보상절 6:1ㄱ, 석보상절 6:표지)
    #    패턴: "석보상절" + 공백? + 권수(숫자) + ":" + (표지 | 숫자+[ㄱㄴ])
    text = re.sub(r'석보상절\s*\d+:(?:표지|\d+[ㄱㄴ])', '', text)
    # 3. 정속언해 페이지 라벨 제거 (예: 정속언해:12ㄴ)
    text = re.sub(r'정속언해\s*(?::\d+[ㄱㄴ])?', '', text, count=0)
    # 3. 이륜행실도 판본 표기 제거 (예: 이륜행실형제도 1ㄴ(옥산서원본))
    text = re.sub(r'이륜행실[^\s]*도\s*\d+[ㄱㄴ](?:\([^)]*\))?', '', text)
    # 4. 연속 공백 정리
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def build_extra_dataset():
    input_file = "data/raw/extra_materials.json"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return
        
    with open(input_file, "r", encoding="utf-8") as f:
        articles = json.load(f)
        
    os.makedirs("data/processed", exist_ok=True)
    
    # 문헌별 출력 파일 매핑
    file_map = {
        "P13_SS": ("data/processed/seokbo_parallel.jsonl", "seokbo"),
        "P02_IR": ("data/processed/iryun_parallel.jsonl", "iryun"),
        "P03_JS": ("data/processed/jeongsok_parallel.jsonl", "jeongsok")
    }
    
    file_handles = {}
    counts = {}
    
    for prefix, (path, name) in file_map.items():
        file_handles[prefix] = open(path, "w", encoding="utf-8")
        counts[name] = 0
    
    skipped = 0
    
    for article in articles:
        record_id = article["record_id"]
        
        # 문헌 식별
        target_prefix = None
        target_name = None
        for prefix, (_, name) in file_map.items():
            if record_id.startswith(prefix):
                target_prefix = prefix
                target_name = name
                break
        
        if target_prefix is None:
            skipped += 1
            continue
        
        # 원문 정규화: 비본문 요소 제거 -> PUA 변환 + NFD
        # (clean_middle_korean은 NFD 이전에 실행해야 한국어 패턴이 정상 매칭됨)
        mk_text = clean_middle_korean(article["middle_korean"])
        mk_text = normalize_middle_korean(mk_text)
        
        # 현대어 정규화: 주석/역자해설 제거
        mod_text = clean_modern_korean(article["modern_korean"])
                
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
    
    # 기타 파일은 비어 있으므로 삭제
    extra_path = "data/processed/extra_parallel.jsonl"
    if os.path.exists(extra_path):
        os.remove(extra_path)
        
    for name, count in counts.items():
        if count > 0:
            print(f"{name} dataset built. Total pairs: {count}")
    if skipped > 0:
        print(f"(Skipped {skipped} unrecognized records)")

if __name__ == "__main__":
    build_extra_dataset()
