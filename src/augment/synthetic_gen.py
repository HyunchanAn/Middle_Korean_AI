import os
import json
import time
from typing import List, Dict
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class SyntheticGenerator:
    """
    Handles synthetic data generation using LLMs via Back-translation.
    Targets OpenAI-compatible API (OpenAI, vLLM, etc.)
    """
    def __init__(self, model_name: str = "gemma4", api_key: str = None, base_url: str = None):
        # Ollama 기본 주소 및 더미 API 키 설정
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "ollama")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1")
        
        if OpenAI:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None

    def create_backtranslation_prompt(self, mk_text: str) -> str:
        prompt = (
            "당신은 중세 국어(15세기~17세기) 전문가입니다. "
            "다음 중세 국어 원문을 현대 국어로 자연스럽게 번역하세요.\n\n"
            "주의사항:\n"
            "1. 옛말의 의미를 살리되, 현대인이 읽기 편한 문장으로 번역할 것.\n"
            "2. 직역보다는 의미 단위의 의역을 우선할 것.\n"
            "3. 번역된 현대어 문장만 출력할 것 (기타 부연 설명 생략).\n\n"
            f"[중세국어 원문]\n{mk_text}\n\n[현대어 번역]\n"
        )
        return prompt

    def generate_translation(self, mk_text: str) -> str:
        if not self.client:
            print("WARNING: OpenAI client not initialized. Returning mock translation.")
            return "[MOCK 번역] " + mk_text[:30] + "..."
            
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "당신은 중세 국어를 현대어로 번역하는 언어 전문가입니다."},
                    {"role": "user", "content": self.create_backtranslation_prompt(mk_text)}
                ],
                temperature=0.3,
                max_tokens=1024
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error during translation: {e}")
            return ""

def process_corpus(input_path: str, output_path: str, max_samples: int = None):
    gen = SyntheticGenerator()
    
    with open(input_path, 'r', encoding='utf-8') as f:
        mk_sentences = json.load(f)
        
    if max_samples:
        mk_sentences = mk_sentences[:max_samples]
        
    print(f"Loaded {len(mk_sentences)} sentences. Starting back-translation...")
    
    results = []
    for i, mk_text in enumerate(mk_sentences):
        print(f"Processing {i+1}/{len(mk_sentences)}...")
        modern_text = gen.generate_translation(mk_text)
        
        # Save in the Biblify instruction format
        pair = {
            "instruction": "다음 중세국어 문장을 현대어로 번역하세요.",
            "input": mk_text,
            "output": modern_text
        }
        results.append(pair)
        
        # Rate limiting delay if using real API
        if gen.client:
            time.sleep(0.5) 
            
    with open(output_path, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
            
    print(f"Saved {len(results)} pairs to {output_path}")

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent
    input_file = project_root / "data" / "processed" / "unlabeled_mk_sentences.json"
    output_file = project_root / "data" / "processed" / "synthetic_mk_parallel.jsonl"
    
    # 전체 1,200문장 번역 실행
    process_corpus(input_file, output_file)
