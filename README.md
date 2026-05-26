# Middle Korean AI (NMT-MK)

![Status](https://img.shields.io/badge/Status-Phase_10-97ca00?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.14-007ec6?style=flat-square&logo=python&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-PyTorch_%26_KoBART-e05d44?style=flat-square&logo=pytorch&logoColor=white)
![Hardware](https://img.shields.io/badge/Hardware-RTX_5080-fe7d37?style=flat-square&logo=nvidia&logoColor=white)
![UI](https://img.shields.io/badge/UI-FastAPI_%26_Streamlit-007ec6?style=flat-square&logo=fastapi&logoColor=white)

중세국어 신경망 기계 번역 시스템 개발 프로젝트

## 성능 및 평가 결과 (Performance & Evaluation)
본 프로젝트는 **RTX 5080 (16GB)** 환경에서 최적화된 추론 성능을 제공합니다. 아래는 베이스라인 모델(`KoBART-base-v2`)을 대상으로 한 성능 측정 결과입니다.

| 평가 항목 | 측정 방법 | 결과 값 |
| :--- | :--- | :--- |
| **Inference Latency** | Avg / P95 (100 samples) | **352.87 ms** / 565.65 ms |
| **Throughput** | Sequences per second | **2.83 seq/s** |
| **GPU Memory Usage** | VRAM Allocated | **504.71 MB** |
| **BLEU Score** | sacrebleu Baseline | **9.62** |
| **chrF Score** | sacrebleu Baseline | **11.36** |
| **Hallucination Rate** | Modern Term Detection | **0.58 %** |

*측정 일시: 2026-05-16 (이전 v2 모델 기준. 현재 Phase 10이 완료되어 총 1,600여 쌍의 순수 15세기 v3 데이터셋이 확보되었으며, 곧 모델 v3 학습이 진행될 예정입니다.)*

### 🚀 향후 벤치마크 로드맵 (Issue #3)
현재 지표는 High-end 데스크탑 사양(RTX 5080) 기준입니다. 추후 실제 웹 서비스 배포 환경을 고려하여 다음을 측정할 계획입니다.
- **CPU Inference**: Hugging Face Spaces 기본 사양(2코어 CPU, 16GB RAM)에서의 Latency 및 Throughput 재측정
- **모델 경량화 실험**: ONNX Runtime 전환 및 8-bit 양자화(Quantization) 적용 시의 BLEU score 보존율과 속도 향상 비율 비교 분석

## 프로젝트 개요
본 프로젝트는 15세기에서 17세기 사이의 중세국어(옛한글) 문헌을 현대어로 정교하게 번역하는 AI 모델을 구축하는 것을 목표로 합니다. 데이터가 부족한 중세국어의 특성을 극복하기 위해 대규모 언어 모델을 통한 데이터 증강과 역사 문헌 데이터베이스 크롤링 파이프라인을 구축합니다.

### 👥 프로젝트 참여자 (Contributors)

<table>
  <tr>
    <td align="center"><img src="profile_HyunchanAn.jpg" width="150px;" alt="Hyunchan An"/><br /><sub><b>Hyunchan An</b></sub><br />리드 개발<br /><a href="https://x.com/DDS_HCAn">Twitter</a></td>
    <td align="center"><img src="profile_UBora.jpg" width="150px;" alt="유보라"/><br /><sub><b>유보라</b></sub><br />중세국어 번역 데이터 검수<br /><a href="https://chzzk.id/Ubora">Chzzk</a> | <a href="https://x.com/B0R4_S2C">Twitter</a></td>
  </tr>
</table>

## 데이터 소스 (Data Sources)
본 프로젝트는 다음의 신뢰도 높은 역사 문헌 데이터베이스를 주요 소스로 활용합니다.
- 한국고전종합DB(ITKC): 세종한글고전 (소학언해, 삼강행실도, 석보상절 등 순수 15세기 중세국어 원문)
- [SCP-KO-15C 중세 국어 자료실](http://scp-ko-15c.wikidot.com/): 중세국어 어형, 악센트 및 어휘 사전 구축을 위한 레퍼런스 데이터 (루트 경로 `data/raw/scp-ko-15c.wikidot/`에 아카이빙)
- *주의: 한문 원문 기반의 조선왕조실록 및 근대 행정 문서는 환각(Hallucination) 방지를 위해 배제됨.*

## 기술 로드맵 및 사양
하드웨어 인프라
- CPU: AMD Ryzen 9 9900X
- GPU: NVIDIA RTX 5080 (16GB VRAM)
- RAM: 64GB DDR5

모델 아키텍처
- 오프라인 데이터 증강 모델: Ollama 기반 로컬 LLM (gemma4 등)
- 실시간 번역 전용 모델: KoBART (Encoder-Decoder) 전이학습 (Inference 경량화)
- 텍스트 표준화: NFD (자모 분리) 기반 옛한글 유니코드 정규화 및 토크나이저 어휘 사전(Vocabulary) 동적 확장

## 🚀 시작하기 (Getting Started)
외부 개발자 및 협업자가 로컬에서 프로젝트를 구동하기 위한 가이드입니다.

### 1. 환경 설정 및 의존성 설치
본 프로젝트는 Python 3.14 이상 환경을 권장합니다.
```bash
pip install -r src/requirements.txt
```

### 2. 번역 API 서버 (FastAPI) 구동
RESTful 형태의 중세국어 번역 서버를 시작합니다.
```bash
uvicorn src.api.app:app --reload
```

## 디렉토리 구조
- `data/`
  - `raw/`: 원시 데이터 및 `scp-ko-15c.wikidot` 아카이브 등
  - `processed/`: 옛한글 정규화 및 필터링 완료 코퍼스 (`samgang_parallel.jsonl` 등)
- `models/`: 모델 체크포인트 보관소 (`kobart-middle-korean`)
- `notebooks/`: 실험용 주피터 노트북
- `src/`
  - `api/`: FastAPI 서버 및 Streamlit 앱 (`app.py`, `review_app.py`, `ocr_app.py`)
  - `augment/`: LLM 기반 합성 데이터 생성 (`synthetic_gen.py`, `filter_data.py`)
  - `crawlers/`: 역사 DB 크롤러 (`itkc_scraper.py` 등)
  - `models/`: 추론, OCR, 평가 스크립트
  - `preprocess/`: 옛한글 NFD 정규화 및 데이터셋 전처리 (`build_samgang_dataset.py` 등)
  - `train/`: 학습 스크립트 (`train.py`, `model_setup.py`)
  - `utils/`: 기타 유틸리티 (`dataset_qc.py` 등)
- `lora_model_bidirectional_v3/`: 최종 양방향 번역 LoRA 어댑터 가중치 (학습 예정)

## 현재 진행 상황
- **Phase 8~10 (데이터 재구축 및 모델 학습 파이프라인 완성)**: 
  - **[해결됨]** 근대 한문 노이즈가 섞인 기존 864쌍 데이터를 한자 비율 및 특정 키워드로 필터링하여 454쌍의 순수 데이터 구출 (Issue #1).
  - **[해결됨]** 1,200여 개의 15세기 원문을 활용하는 LLM 역번역(Back-translation) 데이터 증강 파이프라인 구축 (Issue #1).
  - **[해결됨]** KoBART 토크나이저의 NFD 옛한글 처리 문제(`[UNK]` 방지)를 해결하기 위해 동적 Vocabulary 확장 및 모델 차원 조정 로직 구현 완료 (Phase 9).
  - **[해결됨]** 생성된 역번역 데이터의 환각(Hallucination) 현상을 차단하기 위한 1차 자동 길이/키워드 필터링 로직 구현 (Phase 10).
  - **[해결됨]** 검수자를 위한 Streamlit + Google Sheets 기반의 실시간 광클릭 검수 웹 애플리케이션(`review_app.py`) 개발 완료 (Phase 10).

## 배포 및 서비스 계획
- 자체 학습한 경량 번역 모델(Encoder-Decoder)을 활용하여 Hugging Face Spaces 기반의 오픈소스 AI 웹 서비스로 배포 예정.
- 국어사 연구자 및 학생들을 위한 비영리 학술 보조 도구로 무료 개방.

## 라이선스 및 이용약관 (License & Terms of Use)
본 프로젝트는 오픈소스 생태계와 외부 공공 데이터를 적극 활용하고 있으며, 다음의 이용약관 및 라이선스를 철저히 준수합니다.
1. **외부 AI 모델 라이선스**:
   - `gogamza/kobart-base-v2` (SKT KoBART): 오픈소스 라이선스에 따라 비영리 및 연구 목적으로 활용 중입니다.
   - `ddobokki/ko-trocr` (OCR 엔진): Hugging Face에 공개된 오픈소스 모델로, 관련 오픈소스 라이선스를 준수합니다.
2. **외부 데이터셋 주의사항**:
   - [SCP-KO-15C] 등 위키닷 기반 데이터는 크리에이티브 커먼즈 저작자표시-동일조건변경허락(CC-BY-SA 3.0) 라이선스를 따릅니다.
   - 외부 기관의 인가된 코퍼스를 추가로 확보할 경우 원문 복제 및 외부 배포 금지 조항을 엄격히 준수하며, 프로젝트는 번역/인식 모델의 가중치(Weights)만 배포합니다.

## 참고문헌 (References)
본 프로젝트의 학습 및 검증에 활용되거나 추가 수집 대상으로 지정된 고문헌 자료들입니다. (출처: [한국고전종합DB - 세종한글고전](http://db.sejongkorea.org/))

### 📖 석보상절 (釋譜詳節, 1447년)
세종의 명으로 수양대군(세조)이 부처의 일대기와 설법을 엮어 편찬한 최초의 산문 자료.
- [역주 석보상절 제6](http://db.sejongkorea.org/front/detail.do?bkCode=P13_SS_v006&recordId=P13_SS_e01_v006)
- [역주 석보상절 제9](http://db.sejongkorea.org/front/detail.do?bkCode=P13_SS_v009&recordId=P13_SS_e01_v009)
- [역주 석보상절 제11](http://db.sejongkorea.org/front/detail.do?bkCode=P13_SS_v011&recordId=P13_SS_e01_v011)
- [역주 석보상절 제13](http://db.sejongkorea.org/front/detail.do?bkCode=P13_SS_v013&recordId=P13_SS_e01_v013)
- [역주 석보상절 제19](http://db.sejongkorea.org/front/detail.do?bkCode=P13_SS_v019&recordId=P13_SS_e01_v019)
- [역주 석보상절 제20](http://db.sejongkorea.org/front/detail.do?bkCode=P13_SS_v020&recordId=P13_SS_e01_v020)
- [역주 석보상절 제21](http://db.sejongkorea.org/front/detail.do?bkCode=P13_SS_v021&recordId=P13_SS_e01_v021)

### 📖 삼강행실도 (三綱行實圖, 1432년 / 언해본 1481년)
조선 초기 백성들의 윤리 교화를 위해 편찬된 서적으로, 삽화와 함께 중세국어 원문이 기록되어 있습니다.
- [역주 삼강행실효자도](http://db.sejongkorea.org/front/detail.do?bkCode=P01_SG_v001&recordId=P01_SG_e01_v001_0000)
- [역주 삼강행실충신도](http://db.sejongkorea.org/front/detail.do?bkCode=P01_SG_v001&recordId=P01_SG_e01_v002_0000)
- [역주 삼강행실열녀도](http://db.sejongkorea.org/front/detail.do?bkCode=P01_SG_v001&recordId=P01_SG_e01_v003_0000)

### 📖 기타 교화 문헌
- **이륜행실도 (二倫行實圖, 1518년)**: [역주 이륜행실도](http://db.sejongkorea.org/front/detail.do?bkCode=P02_IR_v001&recordId=P02_IR_e01)
- **정속언해 (正俗諺解, 1518년)**: [역주 정속언해](http://db.sejongkorea.org/front/detail.do?bkCode=P03_JS_v001&recordId=P03_JS_e01)
