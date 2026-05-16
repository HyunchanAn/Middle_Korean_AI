import torch
import time
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
import numpy as np
import json
import os

def benchmark_inference(model_name="gogamza/kobart-base-v2", num_samples=100, max_length=128):
    print(f"--- Performance Benchmark for {model_name} ---")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Target Device: {device}")
    
    if device == "cuda":
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")

    tokenizer = PreTrainedTokenizerFast.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name).to(device)
    model.eval()

    # Sample Middle Korean sentences (Dummy for timing)
    sample_texts = [
        "나랏말ᄊᆞ미 듕구익에 달아 문ᄍᆞ와로 서르 ᄉᆞᄆᆞᆺ디 아니ᄒᆞᆯᄊᆡ",
        "이런 젼ᄎᆞ로 어린 ᄇᆡᆨ셩이 니르고져 홀 배 이셔도",
        "ᄆᆞᄎᆞᆷ내 제 프들 시러 펴디 못ᄒᆞᆯ 노미 하니라",
        "내 이ᄅᆞᆯ 윙ᄒᆞ야 어엿비 너겨 새로 스믈여ᄃᆞᆯ ᄍᆞᄅᆞᆯ ᄆᆡᆼᄀᆞ노니",
        "사ᄅᆞᆷ마다 ᄒᆡᅇᅧ 수비 니겨 날로 ᄡᅮ메 편안킈 ᄒᆞ고져 ᄒᆞᆯ ᄲᅮ니니라"
    ] * (num_samples // 5)

    # Warm-up
    print("Warming up...")
    for _ in range(10):
        with torch.no_grad():
            inputs = tokenizer(sample_texts[0], return_tensors="pt").to(device)
            _ = model.generate(**inputs, max_length=max_length)

    # Latency & Throughput Test
    print(f"Running Inference on {num_samples} samples...")
    latencies = []
    
    if device == "cuda":
        starter, ender = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        
        with torch.no_grad():
            for text in sample_texts:
                inputs = tokenizer(text, return_tensors="pt").to(device)
                
                starter.record()
                _ = model.generate(**inputs, max_length=max_length)
                ender.record()
                
                torch.cuda.synchronize()
                curr_latency = starter.elapsed_time(ender) # in ms
                latencies.append(curr_latency)
    else:
        with torch.no_grad():
            for text in sample_texts:
                start_time = time.time()
                inputs = tokenizer(text, return_tensors="pt").to(device)
                _ = model.generate(**inputs, max_length=max_length)
                latencies.append((time.time() - start_time) * 1000)

    avg_latency = np.mean(latencies)
    p95_latency = np.percentile(latencies, 95)
    throughput = 1000 / avg_latency if avg_latency > 0 else 0

    # Memory Usage
    vram_used = 0
    if device == "cuda":
        vram_used = torch.cuda.memory_allocated(0) / (1024 ** 2) # MB

    results = {
        "model": model_name,
        "device": torch.cuda.get_device_name(0) if device == "cuda" else "CPU",
        "num_samples": num_samples,
        "avg_latency_ms": float(avg_latency),
        "p95_latency_ms": float(p95_latency),
        "throughput_fps": float(throughput),
        "vram_allocated_mb": float(vram_used)
    }

    print("\n--- Results ---")
    print(f"Avg Latency: {avg_latency:.2f} ms")
    print(f"P95 Latency: {p95_latency:.2f} ms")
    print(f"Throughput: {throughput:.2f} sentences/sec")
    print(f"VRAM Allocated: {vram_used:.2f} MB")

    # Save to file
    output_path = "data/processed/perf_results.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    benchmark_inference()
