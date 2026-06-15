import streamlit as st
import json
import os
from pathlib import Path

import streamlit.components.v1 as components

# 구글 시트 웹훅 URL 확인
HAS_WEBHOOK = "gsheets_webhook_url" in st.secrets

st.set_page_config(page_title="중세국어 번역 데이터 검수기", layout="wide")

# CSS 주입: 옛한글 렌더링 최적화 폰트 및 텍스트 박스 스타일
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_20-10-21@1.0/HCRBatang.woff');

.mk-text {
    font-family: 'HCRBatang', 'Malgun Gothic', serif;
    font-size: 28px !important;
    line-height: 1.6;
    padding: 15px;
    background-color: #262730;
    border-radius: 8px;
    color: #FAFAFA;
}
</style>
""", unsafe_allow_html=True)

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
        "정속언해 파싱 원본 (ITKC)": DATA_DIR / "jeongsok_parallel.jsonl"
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
        st.markdown(f'<div class="mk-text">{current_item.get("input", "")}</div>', unsafe_allow_html=True)
        
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

    # 키보드 단축키 이벤트 리스너 주입 (마우스 없이 검수 진행)
    components.html(
        """
        <script>
        const doc = window.parent.document;
        
        function triggerClick(text) {
            const buttons = Array.from(doc.querySelectorAll('button'));
            const btn = buttons.find(b => b.innerText.includes(text));
            if(btn) {
                btn.click();
            }
        }
        
        if (!window.parent._mk_keyboard_listener_added) {
            window.parent._mk_keyboard_listener_added = true;
            doc.addEventListener('keydown', function(e) {
                // 텍스트 영역(요즘말 수정)에서 타이핑 중일 때는 일반 단축키 무시
                if (doc.activeElement.tagName === 'TEXTAREA' || doc.activeElement.tagName === 'INPUT') {
                    // 단, Ctrl+Enter 조합 시 '고침' 버튼 트리거
                    if (e.ctrlKey && e.key === 'Enter') {
                        triggerClick('고침');
                        e.preventDefault();
                    }
                    return;
                }
                
                switch(e.key) {
                    case 'ArrowLeft':
                        triggerClick('이전');
                        break;
                    case 'ArrowRight':
                        triggerClick('다음');
                        break;
                    case '1':
                    case 'Enter':
                        triggerClick('통과');
                        break;
                    case '3':
                    case 'Delete':
                    case 'Backspace':
                        triggerClick('버림');
                        break;
                }
            });
        }
        </script>
        """,
        height=0,
        width=0,
    )

if __name__ == "__main__":
    main()
