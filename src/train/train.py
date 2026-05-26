import sys
from pathlib import Path
from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer, DataCollatorForSeq2Seq

# src 폴더 경로 인식
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

from src.train.model_setup import setup_model_and_tokenizer
from src.train.data_loader import load_and_tokenize_data

def main():
    model_name = "gogamza/kobart-base-v2"
    train_file = str(root_dir / "data" / "processed" / "dummy_train.json")
    output_dir = str(root_dir / "models" / "kobart_middle_korean")
    
    print("Setting up model and tokenizer...")
    model, tokenizer = setup_model_and_tokenizer(model_name)
    
    print("Loading and tokenizing dataset...")
    dataset = load_and_tokenize_data(train_file, tokenizer)
    
    # 훈련용/검증용 분리 (더미 데이터이므로 20% 분리)
    split = dataset.train_test_split(test_size=0.2)
    train_dataset = split['train']
    eval_dataset = split['test']
    
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
    
    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        eval_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        weight_decay=0.01,
        save_total_limit=3,
        num_train_epochs=3,
        predict_with_generate=True,
        fp16=False,  # CUDA 사용 시 True 권장
        logging_dir=str(root_dir / "logs"),
        logging_steps=2,
        use_cpu=True # 테스트용으로 CPU 강제 사용 설정 (환경에 따라 제거 가능)
    )
    
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        processing_class=tokenizer,
    )
    
    print("Starting training loop...")
    trainer.train()
    print("Training finished successfully!")

if __name__ == "__main__":
    main()
