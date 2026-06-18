import os
from bs4 import BeautifulSoup
from pathlib import Path

# The downloaded HTML files
files = {
    "main": r"C:\Users\sg\.gemini\antigravity-ide\brain\be90fc14-ed41-450d-a004-3341f44010e5\.system_generated\steps\198\content.md",
    "hancaum": r"C:\Users\sg\.gemini\antigravity-ide\brain\be90fc14-ed41-450d-a004-3341f44010e5\.system_generated\steps\205\content.md",
    "hwunmincengum-enhai": r"C:\Users\sg\.gemini\antigravity-ide\brain\be90fc14-ed41-450d-a004-3341f44010e5\.system_generated\steps\206\content.md",
    "inflect": r"C:\Users\sg\.gemini\antigravity-ide\brain\be90fc14-ed41-450d-a004-3341f44010e5\.system_generated\steps\207\content.md",
    "uninflect": r"C:\Users\sg\.gemini\antigravity-ide\brain\be90fc14-ed41-450d-a004-3341f44010e5\.system_generated\steps\208\content.md",
    "ywongbiechenka": r"C:\Users\sg\.gemini\antigravity-ide\brain\be90fc14-ed41-450d-a004-3341f44010e5\.system_generated\steps\209\content.md"
}

out_dir = Path(r"e:\Github\Middle_Korean_AI\scp-ko-15c.wikidot")
out_dir.mkdir(parents=True, exist_ok=True)

for name, path in files.items():
    if not os.path.exists(path):
        print(f"File not found: {path}")
        continue
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # extract everything after --- which is the raw html
    if "---" in content:
        html = content.split("---", 1)[1]
    else:
        html = content
        
    soup = BeautifulSoup(html, 'html.parser')
    page_content = soup.find(id="page-content")
    
    if page_content:
        # Convert to text preserving some structure
        text = page_content.get_text(separator='\n', strip=True)
        out_file = out_dir / f"{name}.md"
        with open(out_file, 'w', encoding='utf-8') as out_f:
            out_f.write(f"# SCP-KO-15C {name}\n\n")
            out_f.write(text)
        print(f"Saved {name}.md")
    else:
        print(f"Could not find #page-content in {name}")

# Create a summary index markdown
index_md = out_dir / "README.md"
with open(index_md, 'w', encoding='utf-8') as f:
    f.write("# SCP-KO-15C 중세 국어 사전 데이터\n\n")
    f.write("이 폴더는 `http://scp-ko-15c.wikidot.com/` 사이트에서 스크래핑한 중세국어 어휘 사전 및 자료들을 포함하고 있습니다. 이 사이트는 중세국어 어형 및 악센트(방점), 활용례 등을 체계적으로 기록하려 한 프로젝트로, 모델 학습 및 어휘 사전 추출에 유용한 기초 자료가 될 수 있습니다.\n\n")
    f.write("## 파일 목록\n")
    f.write("- `main.md`: 고전 한국어 사전 메인 및 기초 어휘/동사 목록\n")
    f.write("- `hancaum.md`: 중세 한자음 목록\n")
    f.write("- `hwunmincengum-enhai.md`: 훈민정음 언해 어휘 정리\n")
    f.write("- `inflect.md`: 활용례 - 용언/어미\n")
    f.write("- `uninflect.md`: 활용례 - 체언\n")
    f.write("- `ywongbiechenka.md`: 용비어천가 어휘 정리\n")

print("Done extracting scp-ko-15c data.")
