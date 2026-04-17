NMT-MK: 중세국어 신경망 기계 번역 시스템 개발 계획
본 프로젝트는 15세기~17세기 중세국어(옛한글) 문헌을 현대어로 번역하는 AI 모델을 구축하는 것을 목표로 합니다. RTX 5080(16GB VRAM) 환경에서 최적의 학습 효율을 정하고, 데이터 부재 문제를 해결하기 위한 자동화된 파이프라인을 구축합니다.

User Review Required
IMPORTANT

옛한글 렌더링 및 유니코드 표준화 중세국어는 NFD(자모 분리) 형식이 표준입니다. 사용자의 요청에 따라 방점을 포함한 상태로 수집 및 학습을 진행하며, 모든 텍스트는 NFD 표준화를 거칩니다.

TIP

시대별 도메인 태그 활용 번역의 정교함을 위해 프롬프트에 <15th_century>, <16th_century>, <17th_century>와 같은 시대 태그를 명시적으로 포함하여 시대별 문법 특성을 모델이 학습하도록 합니다.

Proposed Changes
1. 프로젝트 구조 및 환경 설정
프로젝트의 확장성과 유지보수를 위해 표준적인 AI 프로젝트 구조를 채택합니다.

[NEW] [Directory Structure]
data/: raw (수집 데이터), processed (정규화 완료), synthetic (LLM 증강 데이터)
src/:
crawlers/: 국사편찬위원회, 장서각 등 스크래핑 스크립트
preprocess/: 유니코드 정규화, 형태소 분석, 토크나이저 확장
models/: Unsloth 기반 학습 및 추론 코드
utils/: 공통 유틸리티 (로깅, 파일 핸들링)
configs/: 학습 하이퍼파라미터 및 크롤러 설정
2. Phase 1: 데이터 파이프라인 (Data Engineering)
가장 시급한 병렬 코퍼스 확보를 위해 수집 및 증강 시스템을 구축합니다.

[NEW] 
scrapers/history_db.py
국사편찬위원회(history.go.kr) 및 장서각 웹사이트 비동기 크롤러.
Playwright를 사용하여 동적 페이지 대응.
[NEW] 
preprocess/normalize.py
unicodedata를 활용하여 모든 텍스트를 NFD로 통일.
옛한글 자모 결합 규칙 및 방점 제거/유지 옵션 구현.
[NEW] 
augment/synthetic_gen.py
Llama 3.1 8B를 활용하여 소량의 Ground Truth에서 대량의 가상 번역 쌍 생성 (Self-Correction 워크플로우 포함).
3. Phase 2: 모델 아키텍처 및 학습 (Model & Training)
RTX 5080 16GB VRAM에 최적화된 QLoRA 학습 환경을 구축합니다.

Base Model: Gemma 4 26B (MoE) (사용자 제안에 따라 최신 Gemma 4 아키텍처 우선 검토. 16GB VRAM에서 4-bit QLoRA 학습이 가능하며, Llama 3.1 8B 대비 한국어 추론 능력을 비교 검증 예정)
Framework: Unsloth (4-bit QLoRA 지원 여부 확인 후 적용)
Strategy:
Vocab Expansion: 중세국어 특유의 고어를 토크나이저에 추가하여 [UNK] 발생 최소화.
Context Window: 4096 토큰 유지 (메모리 효율 고려).
Gradient Accumulation: GPU 메모리 한계를 극복하기 위해 배치 사이즈 보완.
Open Questions
시대별 구분 여부: 15세기(용비어천가 등)와 17세기(소학언해 등)의 언어적 차이가 큽니다. 단일 모델로 갈지, 아니면 입력 프롬프트에 <15th_century>와 같은 시대 태그를 부여할지 결정이 필요합니다.
방점(Tone mark) 처리: 모델 학습 시 방점을 포함할 것인지, 아니면 노이즈로 간주하여 제거할 것인지에 대한 실험이 필요합니다.
Verification Plan
Automated Tests
pytest를 통한 유니코드 정규화 함수 검증 (NFC <-> NFD 변환 정확도).
크롤러의 데이터 유효성 검사 (Text Null 여부 및 Parallel Pair 매칭 확인).
Manual Verification
Streamlit을 활용한 간이 비교 도구 제작: 원문 - 합성 번역 - 정답 비교.
국문학적 지식이 있는 사용자(PM)의 샘플 문장 정성 평가.