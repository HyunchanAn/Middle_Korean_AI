import os
import sys
import io

# Force UTF-8 encoding for stdin and stdout
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

msg = sys.stdin.read()

lines = msg.split('\n')
if not lines:
    sys.exit(0)

first_line = lines[0].strip()

mapping = {
    "docs: Update README with CPU and ONNX benchmark stats": "docs: 리드미에 CPU와 ONNX 성능시험 결과 덧붙임",
    "feat: Resolve Issues #3, #4, #5, #6, #7, #8": "feat: 문제 3, 4, 5, 6, 7, 8번 마무리지음",
    "test: Add dummy test to prevent pytest failure (exit code 5)": "test: 파이테스트 오류 막으려고 빈 시험 덧붙임",
    "ci: Add GitHub Actions workflow for Python": "ci: 파이썬용 깃허브 액션 작업흐름 덧붙임",
    "fix: Clean annotations/commentary from dataset, remove empty category": "fix: 자료에서 풀이글 지우고 빈 갈래 없앰",
    "feat: Split extra dataset by book sources": "feat: 덧붙인 자료를 책 출처에 따라 나눔",
    "feat: Add extra_parallel dataset (Seokbo, Iryun, Jeongsok)": "feat: 덧붙인 나란한 자료(석보, 이륜, 정속) 덧붙임",
    "chore: Remove secrets.toml from version control": "chore: 판본 관리에서 비밀 파일 빼냄",
    "chore: Include processed dataset for deployment": "chore: 배포용으로 다듬은 자료 품음",
    "feat: Add dataset source to webhook payload": "feat: 웹훅 짐꾸러미에 자료 출처 덧붙임",
    "feat: Add extra ITKC parsers, update UI and docs": "feat: 덧붙인 ITKC 파서 더하고 화면과 문서 거듭남",
    "docs: add references to README": "docs: 리드미에 참고자료 덧붙임",
    "feat: enhance review app UI, fix Hanyang PUA encoding, update profiles": "feat: 검수 앱 화면 낫게 하고 한양 PUA 글자깨짐 고치고 얼굴사진 거듭남",
    "docs: 진짜 사소하고 작은 수정": "docs: 참으로 자잘하고 작은 고침",
    "docs: 사소한 수정": "docs: 자잘한 고침",
    "feat: 학습자료를 위한 대규모 개편 및 보라샘과의 협업 구조 편성 등": "feat: 배울거리를 위한 크게 뜯어고침 및 보라샘과의 품앗이 짜임새 짬 등",
    "Resolve Issue #2: Expand KoBART tokenizer vocab for old Hangul NFD": "fix: 문제 2번 해결 옛한글 NFD를 위해 KoBART 토크나이저 낱말사전 넓힘",
    "Create 이용약정서.txt": "docs: 이용약정서.txt 만듦",
    "docs: add tech badges and RTX 5080 performance benchmark results to README": "docs: 기술 배지와 RTX 5080 성능시험 결과를 리드미에 덧붙임",
    "docs: Update architecture to standalone KoBART & add ITKC/NIKL scraper logic": "docs: 홀로선 KoBART로 짜임새 거듭남 및 ITKC/NIKL 긁어오기 덧붙임",
    "Phase 7 Complete: Bidirectional Translation UI Deployment & Phase 8 Refinement Plan Proposed (Optimized Artifacts)": "feat: 7단계 마무리 양방향 번역 화면 배포 및 8단계 다듬기 바탕 제안함",
    "Explicitly document data sources (NIKH, OKHC, Jangseogak) in README and dev log": "docs: 자료 출처(NIKH, OKHC, 장서각)를 리드미와 개발일지에 뚜렷이 밝힘",
    "Initialize project documentation and set up core structure": "docs: 프로젝트 문서 처음 만들고 알맹이 짜임새 세움",
    "Initial commit": "chore: 첫 올림"
}

if first_line in mapping:
    lines[0] = mapping[first_line]
else:
    for eng, kor in mapping.items():
        if first_line.startswith(eng):
            lines[0] = lines[0].replace(eng, kor)
            break

print('\n'.join(lines))
