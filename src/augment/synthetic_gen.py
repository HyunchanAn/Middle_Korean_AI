import os
import json
import asyncio
from typing import List, Dict
from pathlib import Path

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

class SyntheticGenerator:
    """
    Handles synthetic data generation using LLMs via Back-translation.
    Targets OpenAI-compatible API (OpenAI, vLLM, Ollama, etc.)
    """
    def __init__(self, model_name: str = "gemma4", api_key: str = None, base_url: str = None):
        # Ollama 기본 주소 및 더미 API 키 설정
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "ollama")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1")
        
        if AsyncOpenAI:
            self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
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

    async def generate_translation_async(self, mk_text: str, retries: int = 3) -> str:
        if not self.client:
            print("WARNING: OpenAI client not initialized. Returning mock translation.")
            return "[MOCK 번역] " + mk_text[:30] + "..."
            
        for attempt in range(retries):
            try:
                response = await self.client.chat.completions.create(
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
                print(f"Error during translation (Attempt {attempt+1}/{retries}): {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        return ""

async def process_batch(gen: SyntheticGenerator, mk_sentences: List[str], batch_size: int = 10) -> List[Dict]:
    results = []
    for i in range(0, len(mk_sentences), batch_size):
        batch = mk_sentences[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(mk_sentences) + batch_size - 1)//batch_size}...")
        
        tasks = [gen.generate_translation_async(text) for text in batch]
        translations = await asyncio.gather(*tasks)
        
        for mk_text, mod_text in zip(batch, translations):
            if mod_text:  # filtering empty results
                results.append({
                    "instruction": "다음 중세국어 문장을 현대어로 번역하세요.",
                    "input": mk_text,
                    "output": mod_text
                })
    return results

def process_corpus(input_path: str, output_path: str, max_samples: int = None):
    gen = SyntheticGenerator()
    
    # 더미 데이터 생성 로직 (파일이 없을 경우 대비)
    if not os.path.exists(input_path):
        print(f"Warning: {input_path} not found. Skipping generation.")
        return
        
    with open(input_path, 'r', encoding='utf-8') as f:
        mk_sentences = json.load(f)
        
    if max_samples:
        mk_sentences = mk_sentences[:max_samples]
        
    print(f"Loaded {len(mk_sentences)} sentences. Starting async back-translation...")
    
    results = asyncio.run(process_batch(gen, mk_sentences, batch_size=5))
            
    with open(output_path, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
            
    print(f"Saved {len(results)} pairs to {output_path}")

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent.parent
    input_file = project_root / "data" / "processed" / "unlabeled_mk_sentences.json"
    output_file = project_root / "data" / "processed" / "synthetic_mk_parallel.jsonl"
    
    process_corpus(input_file, output_file)
