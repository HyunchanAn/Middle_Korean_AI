"""
OKHC JSONL 스키마 탐색 스크립트.
캐시된 파일에서 직접 읽어 각 파일별 키 구조와 샘플 레코드를 출력합니다.
"""
import json
import os

SNAPSHOT_DIR = r"data\raw\okhc\cache\datasets--seyoungsong--Open-Korean-Historical-Corpus\snapshots\2d16d39c774ef788069d63223d07e31e038c05df"

# 우선순위 파일: 중세국어 병렬 데이터가 있을 가능성이 높은 파일
PRIORITY_FILES = [
    "aks_kyu_nhm.jsonl",
    "sillok_part_001_of_004.jsonl",
    "gaksa.jsonl",
    "klc_part_001_of_008.jsonl",
    "sjw_part_001_of_015.jsonl",
]

def inspect_file(filepath: str, n_samples: int = 3):
    print(f"\n{'='*60}")
    print(f"FILE: {os.path.basename(filepath)}")
    print('='*60)
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= n_samples:
                break
            try:
                item = json.loads(line)
                print(f"\n[Record {i+1}]")
                print(f"  Keys: {list(item.keys())}")
                # 핵심 필드 출력
                for key in ['id', 'language', 'script', 'corpus', 'category', 'genre']:
                    if key in item:
                        print(f"  {key}: {item[key]!r}")
                # text 필드 (앞 80자)
                for key in ['text', 'original', 'source_text']:
                    if key in item:
                        val = str(item[key])
                        print(f"  {key}: {val[:80]!r}")
                # translation 필드 구조
                if 'translation' in item:
                    t = item['translation']
                    if isinstance(t, dict):
                        print(f"  translation (dict keys): {list(t.keys())}")
                        for k, v in t.items():
                            print(f"    .{k}: {str(v)[:80]!r}")
                    elif isinstance(t, str):
                        print(f"  translation (str): {t[:80]!r}")
                    else:
                        print(f"  translation type: {type(t)}")
            except Exception as e:
                print(f"  [Parse Error] {e}")

if __name__ == "__main__":
    for fname in PRIORITY_FILES:
        fpath = os.path.join(SNAPSHOT_DIR, fname)
        if os.path.exists(fpath):
            inspect_file(fpath, n_samples=3)
        else:
            print(f"\n[MISSING] {fname}")
