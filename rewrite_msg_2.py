import sys
import io

sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

msg = sys.stdin.read()
lines = msg.split('\n')

if lines:
    first_line = lines[0].strip()
    mapping = {
        "feat: 검수 앱 화면 낫게 하고 한양 PUA 글자깨짐 고치고 얼굴사진 거듭남": "feat: 검수 앱 화면 고치고 한양 PUA 글자깨짐 고치고 얼굴사진 더함",
        "feat: 덧붙인 ITKC 파서 더하고 화면과 문서 거듭남": "feat: 덧붙인 ITKC 파서 더하고 화면과 문서 고침"
    }
    
    if first_line in mapping:
        lines[0] = mapping[first_line]
    else:
        for old_msg, new_msg in mapping.items():
            if first_line.startswith(old_msg):
                lines[0] = lines[0].replace(old_msg, new_msg)
                break

print('\n'.join(lines))
