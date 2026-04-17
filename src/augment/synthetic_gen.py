import os
import json
from typing import List, Dict

class SyntheticGenerator:
    """
    Handles synthetic data generation using LLMs.
    Targets Gemma 4 / Llama 3.1 8B via vLLM or OpenAI-compatible API.
    """
    def __init__(self, model_name: str = "Gemma-4-26B-MoE", api_key: str = None):
        self.model_name = model_name
        self.api_key = api_key
        # In a real environment, we'd initialize local vLLM or API client here.

    def create_augmentation_prompt(self, context_pairs: List[Dict[str, str]], target_count: int = 5) -> str:
        """
        Creates a few-shot prompt for generating synthetic Middle Korean pairs.
        """
        prompt = (
            "당신은 중세 국어 전문가입니다. 다음의 중세 국어-현대어 번역 쌍을 참고하여, "
            "비슷한 문법 구조와 어휘를 가진 새로운 중세 국어 문장과 그에 대응하는 현대어 번역을 생성하세요.\n"
            "주의사항:\n"
            "1. 옛한글(아래아, 방점, 순경음 등)을 정확히 사용하세요.\n"
            "2. 15세기~17세기 문체 특징을 유지하세요.\n"
            "3. 방점을 포함하여 생성하세요.\n\n"
        )
        
        # Add few-shot examples
        for pair in context_pairs:
            prompt += f"중세국어: {pair['middle']}\n현대어: {pair['modern']}\n\n"
            
        prompt += f"이제 새로운 번역 쌍을 {target_count}개 생성하세요. 형식은 JSONL로 출력하세요.\n"
        return prompt

    def generate(self, seed_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Simulates generation process.
        """
        print(f"Generating synthetic data using {self.model_name}...")
        # actual inference call would go here
        return []

if __name__ == "__main__":
    gen = SyntheticGenerator()
    examples = [
        {"middle": "나랏말〯싸미〮 댱귁〮에〮 달 servants 〮아〮", "modern": "나라의 말이 중국과 달라"},
        {"middle": "닐굽〮 디〮위〮예〮 닐오〮니〮", "modern": "일곱 번에 이르니"}
    ]
    test_prompt = gen.create_augmentation_prompt(examples)
    print("--- Generated Prompt ---")
    print(test_prompt)
