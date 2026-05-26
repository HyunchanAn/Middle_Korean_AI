# Middle Korean AI (NMT-MK)

![Status](https://img.shields.io/badge/Status-v3.0_Phase_8-97ca00?style=flat-square)
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

*측정 일시: 2026-05-16 | 테스트 코드: `src/tests/performance_benchmark.py`*

## 프로젝트 개요
본 프로젝트는 15세기에서 17세기 사이의 중세국어(옛한글) 문헌을 현대어로 정교하게 번역하는 AI 모델을 구축하는 것을 목표로 합니다. 데이터가 부족한 중세국어의 특성을 극복하기 위해 대규모 언어 모델을 통한 데이터 증강과 역사 문헌 데이터베이스 크롤링 파이프라인을 구축합니다.

## 데이터 소스 (Data Sources)
본 프로젝트는 다음의 신뢰도 높은 역사 문헌 데이터베이스를 주요 소스로 활용합니다.
- 국립국어원(NIKL) 모두의 말뭉치: 국어 역사자료 말뭉치 (15~17세기 언해본 병렬 코퍼스)
- 한국고전종합DB(ITKC): 세종한글고전 (소학언해, 삼강행실도, 석보상절 등 순수 15세기 중세국어 원문)
- *주의: 한문 원문 기반의 조선왕조실록 및 근대 행정 문서는 환각(Hallucination) 방지를 위해 철저히 배제됨.*

## 기술 로드맵 및 사양
하드웨어 인프라
- CPU: AMD Ryzen 9 9900X
- GPU: NVIDIA RTX 5080 (16GB VRAM)
- RAM: 64GB DDR5

모델 아키텍처
- 오프라인 데이터 증강 모델: Gemma-2-27B / Llama-3.1-70B (데이터 합성용)
- 실시간 번역 전용 모델: KoBART (Encoder-Decoder) 전이학습 (Inference 경량화)
- 텍스트 표준화: NFD (자모 분리) 기반 옛한글 유니코드 정규화

## 디렉토리 구조
- configs/: 학습 하이퍼파라미터 및 설정 파일
- data/: 초도 수집 데이터 및 정규화 완료된 코퍼스
- src/:
  - api/: FastAPI 웹 서비스 및 프론트엔드 정적 파일
  - augment/: LLM 기반 합성 데이터 생성 로직
  - crawlers/: 국사편찬위원회 등 역사 DB 크롤러
  - models/: 학습 및 추론 엔진 (Inference v3)
  - preprocess/: 옛한글 정규화 및 데이터셋 빌더
  - utils/: 공통 유틸리티
- lora_model_bidirectional_v3/: 최종 양방향 번역 LoRA 어댑터

## 현재 진행 상황
- **Phase 8 (데이터 재구축 및 아키텍처 개편)**: 
  - 기존 864쌍의 오염된 데이터(근대 노이즈 포함)를 전면 폐기하고 372쌍의 순수 데이터 확보.
  - 대형 언어 모델(Gemma)에 의존하던 번역 방식을 버리고, 독자적인 경량 번역 모델(KoBART) 학습 파이프라인 구축.
  - **[해결됨]** KoBART 토크나이저의 NFD 옛한글 처리 문제(`[UNK]` 방지)를 해결하기 위해 동적 Vocabulary 확장 로직 구현 완료 (Issue #2).
  - 국립국어원 '국어 역사자료 말뭉치' 이용 신청 완료 후 데이터 대기 중.

## 배포 및 서비스 계획
- 자체 학습한 경량 번역 모델(Encoder-Decoder)을 활용하여 Hugging Face Spaces 기반의 오픈소스 AI 웹 서비스로 배포 예정.
- 국어사 연구자 및 학생들을 위한 비영리 학술 보조 도구로 무료 개방.
