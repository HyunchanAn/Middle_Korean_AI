import json
import re
from pathlib import Path

def filter_translations(input_path: str, output_path: str):
    """
    LLM 역번역 결과물에서 환각(Hallucination) 및 오류 데이터를 휴리스틱으로 걸러냅니다.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    valid_data = []
    rejected_count = 0
    
    # 챗봇 특유의 추임새 필터링
    leakage_patterns = [r"번역[ :]+", r"해석[ :]+", r"현대어[ :]+", r"의미[ :]+", r"여기 번역"]
    
    for line in lines:
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            source = item.get("input", "")
            target = item.get("output", "")
            
            # 1. 길이 검사 (원본 대비 3배 이상 길거나 0.3배 이하로 짧으면 폐기)
            ratio = len(target) / max(len(source), 1)
            if ratio > 3.0 or ratio < 0.3:
                rejected_count += 1
                continue
                
            # 2. 알파벳(a-z) 포함 여부 검사 (순수 한국어/한자 번역에 영어가 섞이면 환각)
            if re.search(r'[a-zA-Z]', target):
                rejected_count += 1
                continue
                
            # 3. 프롬프트 누출(Leakage) 검사
            is_leakage = False
            for pattern in leakage_patterns:
                if re.search(pattern, target):
                    is_leakage = True
                    break
            if is_leakage:
                rejected_count += 1
                continue
                
            valid_data.append(item)
            
        except json.JSONDecodeError:
            continue
            
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in valid_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
    print(f"Total: {len(lines)} | Passed: {len(valid_data)} | Rejected: {rejected_count}")

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent
    input_file = project_root / "data" / "processed" / "synthetic_mk_parallel.jsonl"
    output_file = project_root / "data" / "processed" / "filtered_mk_parallel.jsonl"
    
    if input_file.exists():
        filter_translations(str(input_file), str(output_file))
    else:
        print(f"Input file not found: {input_file}")
