import os
import glob
import json
import torch
from datasets import Dataset
from transformers import (
    PreTrainedTokenizerFast,
    BartForConditionalGeneration,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq
)
import evaluate
import numpy as np

class MiddleKoreanTranslatorTrainer:
    def __init__(self, model_name: str = "gogamza/kobart-base-v2", data_dir: str = "data/processed"):
        self.model_name = model_name
        self.data_dir = data_dir
        
        print(f"Loading Model and Tokenizer: {self.model_name}")
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained(self.model_name)
        self.model = BartForConditionalGeneration.from_pretrained(self.model_name)
        
        # 중세국어 특별 자모(아래아, 반치음, 순경음비읍 등) 및 NFD 처리 확장을 위한 특수 토큰 추가 로직
        # 추후 국립국어원 데이터 분석 후 필요한 vocab을 추가합니다.
        # self.tokenizer.add_tokens(['ㆍ', 'ㅿ', 'ㅸ'])
        # self.model.resize_token_embeddings(len(self.tokenizer))
        
        self.metric = evaluate.load("sacrebleu")

    def load_parallel_corpus(self) -> Dataset:
        """
        data/processed 폴더 안의 모든 jsonl 병렬 데이터(Biblify style)를 취합합니다.
        """
        all_pairs = []
        jsonl_files = glob.glob(os.path.join(self.data_dir, "*.jsonl"))
        
        if not jsonl_files:
            raise FileNotFoundError(f"No .jsonl files found in {self.data_dir}")
            
        print(f"Found {len(jsonl_files)} dataset files. Aggregating...")
        
        for file_path in jsonl_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if "modern_source" in data and "middle_target" in data:
                            all_pairs.append({
                                "modern_source": data["modern_source"],
                                "middle_target": data["middle_target"]
                            })
                    except Exception as e:
                        continue
                        
        print(f"Total {len(all_pairs)} valid parallel pairs loaded.")
        return Dataset.from_list(all_pairs)

    def preprocess_function(self, examples):
        inputs = examples["modern_source"]
        targets = examples["middle_target"]
        
        model_inputs = self.tokenizer(inputs, max_length=128, truncation=True, padding=False)
        
        # labels for decoder
        with self.tokenizer.as_target_tokenizer():
            labels = self.tokenizer(targets, max_length=128, truncation=True, padding=False)
            
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    def compute_metrics(self, eval_preds):
        preds, labels = eval_preds
        if isinstance(preds, tuple):
            preds = preds[0]
            
        decoded_preds = self.tokenizer.batch_decode(preds, skip_special_tokens=True)
        # Replace -100 in the labels as we can't decode them.
        labels = np.where(labels != -100, labels, self.tokenizer.pad_token_id)
        decoded_labels = self.tokenizer.batch_decode(labels, skip_special_tokens=True)
        
        result = self.metric.compute(predictions=decoded_preds, references=[[l] for l in decoded_labels])
        return {"bleu": result["score"]}

    def train(self, output_dir: str = "./models/kobart-middle-korean"):
        raw_dataset = self.load_parallel_corpus()
        
        # Split train/validation (95/5)
        split_dataset = raw_dataset.train_test_split(test_size=0.05, seed=42)
        train_dataset = split_dataset["train"]
        eval_dataset = split_dataset["test"]
        
        print("Tokenizing datasets...")
        tokenized_train = train_dataset.map(self.preprocess_function, batched=True, remove_columns=train_dataset.column_names)
        tokenized_eval = eval_dataset.map(self.preprocess_function, batched=True, remove_columns=eval_dataset.column_names)
        
        data_collator = DataCollatorForSeq2Seq(self.tokenizer, model=self.model)
        
        training_args = Seq2SeqTrainingArguments(
            output_dir=output_dir,
            evaluation_strategy="epoch",
            learning_rate=3e-5,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            weight_decay=0.01,
            save_total_limit=3,
            num_train_epochs=5,
            predict_with_generate=True,
            fp16=torch.cuda.is_available(),
            logging_steps=50,
            report_to="none" # Disable wandb for local test
        )
        
        trainer = Seq2SeqTrainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_train,
            eval_dataset=tokenized_eval,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=self.compute_metrics
        )
        
        print("Starting KoBART Fine-tuning for Middle Korean...")
        trainer.train()
        
        print(f"Saving finalized model to {output_dir}")
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)

if __name__ == "__main__":
    trainer = MiddleKoreanTranslatorTrainer()
    trainer.train()
