import streamlit as st
import json
import os
from pathlib import Path

# 구글 시트 웹훅 URL 확인
HAS_WEBHOOK = "gsheets_webhook_url" in st.secrets

st.set_page_config(page_title="중세국어 번역 데이터 검수기", layout="wide")

# 로컬 JSON 백업 경로 설정
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"
FILTERED_FILE = DATA_DIR / "filtered_mk_parallel.jsonl"
SAMGANG_FILE = DATA_DIR / "samgang_parallel.jsonl"
REVIEWED_FILE = DATA_DIR / "reviewed_mk_parallel.jsonl"

def load_data(target_file):
    if not target_file.exists():
        return []
    with open(target_file, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def save_reviewed_item(item, status):
    item['review_status'] = status
    with open(REVIEWED_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    st.title("📖 중세국어 번역 데이터 검수기")
    st.markdown("**검수자: 유보라 선생님** 전용 검수 플랫폼입니다. 잘부탁드립니다 뽀샘 ^0^")
    
    # 1. 구글 시트 웹훅 연동 체크
    if HAS_WEBHOOK:
        st.success("☁️ Google Sheets 연동(WebHook) 활성화 상태입니다.")
    else:
        st.info("💾 로컬 파일 시스템 저장 모드로 동작 중입니다.")
        
    dataset_options = {
        "합성 데이터 (Gemma)": FILTERED_FILE,
        "삼강행실도 파싱 원본 (ITKC)": SAMGANG_FILE,
        "석보상절 파싱 원본 (ITKC)": DATA_DIR / "seokbo_parallel.jsonl",
        "이륜행실도 파싱 원본 (ITKC)": DATA_DIR / "iryun_parallel.jsonl",
        "정속언해 파싱 원본 (ITKC)": DATA_DIR / "jeongsok_parallel.jsonl",
        "기타 파싱 원본 (ITKC)": DATA_DIR / "extra_parallel.jsonl"
    }
    
    dataset_option = st.sidebar.selectbox(
        "검수할 데이터셋 선택",
        list(dataset_options.keys())
    )
    
    target_file = dataset_options[dataset_option]
        
    # 데이터 로드 및 세션 상태 관리 (로컬 백업용)
    if 'current_dataset' not in st.session_state or st.session_state.current_dataset != dataset_option:
        st.session_state.current_dataset = dataset_option
        st.session_state.raw_data = load_data(target_file)
        st.session_state.current_idx = 0
        
    data = st.session_state.raw_data
    idx = st.session_state.current_idx
    
    if len(data) == 0:
        st.warning(f"선택한 데이터셋({dataset_option})이 존재하지 않거나 비어 있습니다.")
        return
        
    if idx >= len(data):
        st.balloons()
        st.success("🎉 모든 데이터 검수가 완료되었습니다!")
        return
        
    current_item = data[idx]
    
    # 상단 컨트롤 바가 들어갈 자리 (스크롤 방지)
    control_container = st.container()
    # UI 구조
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📜 15세기 옛말 (원문)")
        st.info(current_item.get("input", ""))
        
    with col2:
        st.subheader("💡 인공지능 요즘말 (현대어)")
        output_text = current_item.get("output", "")
        # 스크롤바가 절대 생기지 않도록 아주 넉넉하게 줄 수와 픽셀을 계산합니다.
        estimated_lines = output_text.count('\n') + (len(output_text) // 25) + 5
        dynamic_height = max(350, estimated_lines * 35)
        
        edited_translation = st.text_area(
            "어색한 부분이 있다면 직접 고쳐주세요:", 
            value=output_text, 
            height=dynamic_height
        )
        
    st.divider()
    
    # 공통 액션 처리 함수
    def process_action(status, translation):
        current_item["output"] = translation
        
        # 1. 로컬 백업 저장
        save_reviewed_item(current_item, status)
        
        # 2. 구글 시트 업데이트 (연동되어 있을 경우)
        if HAS_WEBHOOK:
            try:
                import requests
                webhook_url = st.secrets["gsheets_webhook_url"]
                payload = {
                    "순번": idx + 1,
                    "말뭉치": st.session_state.current_dataset,
                    "옛말": current_item.get("input", ""),
                    "요즘말": translation,
                    "결과": status
                }
                # 구글 앱스 스크립트로 POST 요청 (에러 방지를 위해 타임아웃 3초 설정)
                res = requests.post(webhook_url, json=payload, timeout=3)
                if res.status_code != 200:
                    st.error(f"시트 기록 실패 (상태 코드: {res.status_code})")
            except Exception as e:
                st.error(f"시트 기록 중 오류가 발생했습니다: {e}")
                
        st.session_state.current_idx += 1
        st.rerun()

    # 버튼 액션 (상단 컨테이너에 렌더링)
    with control_container:
        c_prev, c_next, c_pass, c_fix, c_drop = st.columns([1, 1, 2, 2, 2])
        
        with c_prev:
            if st.button("⬅️ 이전", disabled=(idx == 0), use_container_width=True):
                st.session_state.current_idx -= 1
                st.rerun()
        with c_next:
            if st.button("다음 ➡️", disabled=(idx >= len(data) - 1), use_container_width=True):
                st.session_state.current_idx += 1
                st.rerun()
        with c_pass:
            if st.button("✅ 통과", use_container_width=True, type="primary"):
                process_action("통과", edited_translation)
                
        with c_fix:
            if st.button("✏️ 고침", use_container_width=True):
                process_action("고침", edited_translation)
                
        with c_drop:
            if st.button("❌ 버림", use_container_width=True):
                process_action("버림", edited_translation)
            
    st.progress((idx) / len(data))
    st.caption(f"진행도: {idx} / {len(data)}")

if __name__ == "__main__":
    main()
