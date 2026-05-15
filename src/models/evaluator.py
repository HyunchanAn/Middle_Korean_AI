import json
import os
import re
from sacrebleu.metrics import BLEU, CHRF
from tqdm import tqdm

class MiddleKoreanEvaluator:
    def __init__(self, test_data_path):
        with open(test_data_path, 'r', encoding='utf-8') as f:
            self.test_data = json.load(f)
        self.bleu = BLEU()
        self.chrf = CHRF()
        
        # Hallucination indicators (Modern administrative/tech terms that shouldn't appear in 15th-17th century context)
        self.hallucination_patterns = [
            r"동사무소", r"주민등록", r"컴퓨터", r"인터넷", r"스마트폰", 
            r"아파트", r"지하철", r"버스", r"텔레비전", r"라디오",
            r"민원", r"신고", r"과태료" # These might appear in administrative contexts, but we focus on modern usage
        ]

    def check_hallucination(self, text):
        matches = []
        for pattern in self.hallucination_patterns:
            if re.search(pattern, text):
                matches.append(pattern)
        return matches

    def evaluate(self, translate_func):
        """
        translate_func: A function that takes Middle Korean text and returns Modern Korean.
        """
        results = []
        hypotheses = []
        references = []
        
        print(f"Evaluating {len(self.test_data)} samples...")
        for item in tqdm(self.test_data):
            mk_text = item['middle_korean']
            gt_text = item['modern_korean']
            
            # Translate
            translated = translate_func(mk_text)
            
            # Hallucination check
            h_matches = self.check_hallucination(translated)
            
            hypotheses.append(translated)
            references.append([gt_text])
            
            results.append({
                "id": item['id'],
                "input": mk_text,
                "output": translated,
                "reference": gt_text,
                "hallucinations": h_matches
            })
            
        # Calculate Metrics
        bleu_score = self.bleu.corpus_score(hypotheses, references)
        chrf_score = self.chrf.corpus_score(hypotheses, references)
        
        total_hallucinations = sum(1 for r in results if r['hallucinations'])
        
        report = {
            "metrics": {
                "bleu": bleu_score.score,
                "chrf": chrf_score.score,
                "hallucination_rate": (total_hallucinations / len(self.test_data)) * 100
            },
            "details": results
        }
        
        return report

# Mock Translator for initial testing
def mock_translator(text):
    # Just a dummy that returns something similar to Modern Korean for testing the evaluator
    return text.replace("ᄒᆞ", "하").replace("ᄂᆞ", "나").replace("ᅵ", "이")

if __name__ == "__main__":
    test_path = r"e:\Github\Middle_Korean_AI\data\processed\test_dataset.json"
    evaluator = MiddleKoreanEvaluator(test_path)
    
    # Run evaluation with mock
    report = evaluator.evaluate(mock_translator)
    
    # Save report
    output_report = r"e:\Github\Middle_Korean_AI\data\processed\eval_report_mock.json"
    with open(output_report, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    print(f"\nEvaluation Results:")
    print(f"BLEU: {report['metrics']['bleu']:.2f}")
    print(f"chrF: {report['metrics']['chrf']:.2f}")
    print(f"Hallucination Rate: {report['metrics']['hallucination_rate']:.2f}%")
