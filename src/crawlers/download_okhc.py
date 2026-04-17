"""
OKHC (Open Korean Historical Corpus) 병렬 코퍼스 수집기.

스키마 탐색 결과 (2026-04-15):
- `translation` 필드는 AKS/KLC 등 대부분 파일에서 빈 딕셔너리 `{}`임.
- 대신 동일 book_id에 대해 -v0 (한문/원문), -v1 (현대어) 버전이 쌍으로 존재함.
- gaksa_modern.jsonl 등 일부 파일은 별도로 국역본을 제공함.

병렬 쌍 추출 전략:
1. [v0/v1 쌍 추출] id에서 '-v0', '-v1' 패턴을 가진 레코드를 매칭.
2. [sillok 특화] sillok은 동일 doc_id에 원문/국역이 별도 필드로 존재하는지 확인.
3. [gaksa_modern] gaksa.jsonl (원문) + gaksa_modern.jsonl (국역) 파일 크로스 매칭.
"""
import os
import sys
import json
import re
from collections import defaultdict
from tqdm import tqdm
import pandas as pd

# 프로젝트 루트를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.preprocess.normalize import normalize_nfd, clean_noise

# 캐시 스냅샷 경로 (이미 다운로드됨)
SNAPSHOT_DIR = os.path.join(
    "data", "raw", "okhc", "cache",
    "datasets--seyoungsong--Open-Korean-Historical-Corpus",
    "snapshots", "2d16d39c774ef788069d63223d07e31e038c05df"
)

# 출력 경로
OUTPUT_PATH = os.path.join("data", "processed", "okhc_parallel.jsonl")


def extract_v_pairs(filepath: str) -> list[dict]:
    """
    동일 book_id에서 -v0 (원문) / -v1 (현대어) 쌍을 추출한다.
    -v0: 한문 또는 한글 원문
    -v1: 현대어 번역
    """
    # id -> text 인덱스 구축
    index = defaultdict(dict)

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line)
                item_id = item.get("id", "")
                # -v0 또는 -v1 패턴 감지
                m = re.match(r"^(.+)-v(\d+)$", item_id)
                if m:
                    base_id = m.group(1)
                    version = int(m.group(2))
                    text = item.get("text", "").strip()
                    if text:
                        index[base_id][version] = {
                            "text": text,
                            "script": item.get("script", ""),
                            "corpus": item.get("corpus", ""),
                            "source": item.get("source", ""),
                        }
            except Exception:
                continue

    pairs = []
    for base_id, versions in index.items():
        if 0 in versions and 1 in versions:
            v0 = versions[0]  # 원문
            v1 = versions[1]  # 현대어
            orig = normalize_nfd(v0["text"])
            modern = clean_noise(v1["text"])
            if len(orig) > 10 and len(modern) > 10:
                pairs.append({
                    "id": base_id,
                    "original": orig,
                    "modern_korean": modern,
                    "script": v0["script"],
                    "corpus": v0["corpus"],
                    "source": v0["source"],
                    "strategy": "v0_v1_pair",
                    "origin": os.path.basename(filepath),
                })
    return pairs


def extract_gaksa_pairs(original_file: str, modern_file: str) -> list[dict]:
    """
    gaksa.jsonl (한문 원문) + gaksa_modern.jsonl (현대어 번역)을
    공통 id를 기준으로 매칭한다.
    """
    # 현대어 파일 인덱싱
    modern_index = {}
    with open(modern_file, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="Indexing gaksa_modern"):
            try:
                item = json.loads(line)
                text = item.get("text", "").strip()
                if text:
                    modern_index[item.get("id", "")] = text
            except Exception:
                continue

    pairs = []
    with open(original_file, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="Matching gaksa pairs"):
            try:
                item = json.loads(line)
                item_id = item.get("id", "")
                modern_text = modern_index.get(item_id, "")
                orig_text = item.get("text", "").strip()
                if orig_text and modern_text and len(modern_text) > 10:
                    pairs.append({
                        "id": item_id,
                        "original": normalize_nfd(orig_text),
                        "modern_korean": clean_noise(modern_text),
                        "script": item.get("script", ""),
                        "corpus": item.get("corpus", ""),
                        "source": item.get("source", ""),
                        "strategy": "gaksa_cross_match",
                        "origin": "gaksa",
                    })
            except Exception:
                continue
    return pairs


def main(limit: int = 50000):
    os.makedirs("data/processed", exist_ok=True)
    all_pairs = []

    # --- 전략 1: v0/v1 쌍 추출 대상 파일 ---
    v_pair_files = [
        "aks_kyu_nhm.jsonl",
        "klc_part_001_of_008.jsonl",
        "klc_part_002_of_008.jsonl",
        "klc_part_003_of_008.jsonl",
        "klc_part_004_of_008.jsonl",
        "sagi.jsonl",
        "goryeosa.jsonl",
        "kisu_literary.jsonl",
    ]

    for fname in v_pair_files:
        if len(all_pairs) >= limit:
            break
        fpath = os.path.join(SNAPSHOT_DIR, fname)
        if not os.path.exists(fpath):
            print(f"[SKIP] 파일 없음: {fname}")
            continue
        print(f"\n[v0/v1 추출] {fname} ...")
        pairs = extract_v_pairs(fpath)
        print(f"  -> {len(pairs)}개 쌍 추출")
        all_pairs.extend(pairs)

    # --- 전략 2: gaksa 크로스 매칭 ---
    gaksa_orig = os.path.join(SNAPSHOT_DIR, "gaksa.jsonl")
    gaksa_modern = os.path.join(SNAPSHOT_DIR, "gaksa_modern.jsonl")
    if os.path.exists(gaksa_orig) and os.path.exists(gaksa_modern):
        print("\n[gaksa 크로스매칭] ...")
        pairs = extract_gaksa_pairs(gaksa_orig, gaksa_modern)
        print(f"  -> {len(pairs)}개 쌍 추출")
        all_pairs.extend(pairs)

    # 중복 제거 (id 기준)
    seen = set()
    deduped = []
    for p in all_pairs:
        if p["id"] not in seen:
            seen.add(p["id"])
            deduped.append(p)

    # limit 적용
    deduped = deduped[:limit]

    # 저장
    if deduped:
        df = pd.DataFrame(deduped)
        df.to_json(OUTPUT_PATH, orient="records", lines=True, force_ascii=False)
        print(f"\n[완료] 총 {len(deduped)}개 병렬 쌍 저장 -> {OUTPUT_PATH}")
        print("\n전략별 분포:")
        print(df["strategy"].value_counts().to_string())
        print("\n코퍼스별 분포:")
        print(df["corpus"].value_counts().head(10).to_string())
    else:
        print("\n[실패] 병렬 쌍을 찾지 못했습니다.")


if __name__ == "__main__":
    main(limit=50000)
