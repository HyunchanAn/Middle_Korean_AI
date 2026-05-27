import argparse
import torch
import time
import numpy as np
import json
import os
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration

def benchmark_inference(model_name="gogamza/kobart-base-v2", num_samples=100, max_length=128, device_arg="cuda", quantize=None):
    print(f"--- Performance Benchmark for {model_name} ---")
    
    device = "cuda" if torch.cuda.is_available() and device_arg != "cpu" else "cpu"
    print(f"Target Device: {device}")
    
    if device == "cuda":
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")

    tokenizer = PreTrainedTokenizerFast.from_pretrained(model_name)
    
    # Model Loading based on quantize config
    if quantize == "onnx_int8":
        print("Using ONNX Runtime with INT8 dynamic quantization...")
        from optimum.onnxruntime import ORTModelForSeq2SeqLM
        
        onnx_path = f"models/onnx_{model_name.replace('/', '_')}"
        if not os.path.exists(onnx_path):
            print("Exporting model to ONNX...")
            model = ORTModelForSeq2SeqLM.from_pretrained(model_name, export=True)
            model.save_pretrained(onnx_path)
            tokenizer.save_pretrained(onnx_path)
        else:
            model = ORTModelForSeq2SeqLM.from_pretrained(onnx_path)
            
        print("Dynamic Quantizing ONNX model for CPU...")
        from optimum.onnxruntime.configuration import AutoQuantizationConfig
        from optimum.onnxruntime import ORTQuantizer
        
        quantized_path = onnx_path + "_quantized"
        if not os.path.exists(quantized_path):
            quantizer = ORTQuantizer.from_pretrained(model)
            qconfig = AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=True)
            quantizer.quantize(save_dir=quantized_path, quantization_config=qconfig)
            
        model = ORTModelForSeq2SeqLM.from_pretrained(quantized_path)
        model_size_mb = get_dir_size(quantized_path)
    else:
        model = BartForConditionalGeneration.from_pretrained(model_name).to(device)
        model.eval()
        model_size_mb = 0 # Not calculated for PyTorch models

    # Sample Middle Korean sentences (Dummy for timing)
    sample_texts = [
        "나랏말ᄊᆞ미 듕구익에 달아 문ᄍᆞ와로 서르 ᄉᆞᄆᆞᆺ디 아니ᄒᆞᆯᄊᆡ",
        "이런 젼ᄎᆞ로 어린 ᄇᆡᆨ셩이 니르고져 홀 배 이셔도",
        "ᄆᆞᄎᆞᆷ내 제 프들 시러 펴디 못ᄒᆞᆯ 노미 하니라",
        "내 이ᄅᆞᆯ 윙ᄒᆞ야 어엿비 너겨 새로 스믈여ᄃᆞᆯ ᄍᆞᄅᆞᆯ ᄆᆡᆼᄀᆞ노니",
        "사ᄅᆞᆷ마다 ᄒᆡᅇᅧ 수비 니겨 날로 ᄡᅮ메 편안킈 ᄒᆞ고져 ᄒᆞᆯ ᄲᅮ니니라"
    ] * (max(1, num_samples // 5))

    # Warm-up
    print("Warming up...")
    if quantize == "onnx_int8":
        for _ in range(3):
            inputs = tokenizer(sample_texts[0], return_tensors="pt")
            _ = model.generate(**inputs, max_length=max_length)
    else:
        for _ in range(10):
            with torch.no_grad():
                inputs = tokenizer(sample_texts[0], return_tensors="pt").to(device)
                _ = model.generate(**inputs, max_length=max_length)

    # Latency & Throughput Test
    print(f"Running Inference on {num_samples} samples...")
    latencies = []
    
    if device == "cuda" and quantize != "onnx_int8":
        starter, ender = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        
        with torch.no_grad():
            for text in sample_texts[:num_samples]:
                inputs = tokenizer(text, return_tensors="pt").to(device)
                
                starter.record()
                _ = model.generate(**inputs, max_length=max_length)
                ender.record()
                
                torch.cuda.synchronize()
                curr_latency = starter.elapsed_time(ender) # in ms
                latencies.append(curr_latency)
    else:
        # CPU or ONNX runtime
        for text in sample_texts[:num_samples]:
            start_time = time.time()
            inputs = tokenizer(text, return_tensors="pt")
            if device != "cpu" and quantize != "onnx_int8":
                inputs = {k: v.to(device) for k, v in inputs.items()}
                
            if quantize == "onnx_int8":
                _ = model.generate(**inputs, max_length=max_length)
            else:
                with torch.no_grad():
                    _ = model.generate(**inputs, max_length=max_length)
            latencies.append((time.time() - start_time) * 1000)

    avg_latency = np.mean(latencies)
    p95_latency = np.percentile(latencies, 95)
    throughput = 1000 / avg_latency if avg_latency > 0 else 0

    # Memory Usage
    vram_used = 0
    if device == "cuda" and quantize != "onnx_int8":
        vram_used = torch.cuda.memory_allocated(0) / (1024 ** 2) # MB

    results = {
        "model": model_name,
        "device": torch.cuda.get_device_name(0) if device == "cuda" else "CPU",
        "quantize": quantize,
        "num_samples": num_samples,
        "avg_latency_ms": float(avg_latency),
        "p95_latency_ms": float(p95_latency),
        "throughput_fps": float(throughput),
        "vram_allocated_mb": float(vram_used),
        "model_size_mb": float(model_size_mb)
    }

    print("\n--- Results ---")
    print(f"Avg Latency: {avg_latency:.2f} ms")
    print(f"P95 Latency: {p95_latency:.2f} ms")
    print(f"Throughput: {throughput:.2f} sentences/sec")
    if device == "cuda":
        print(f"VRAM Allocated: {vram_used:.2f} MB")
    if quantize == "onnx_int8":
        print(f"ONNX Quantized Model Size: {model_size_mb:.2f} MB")

    # Save to file
    output_path = f"data/processed/perf_results_{device}_{quantize}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    return results

def get_dir_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total / (1024 * 1024)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="gogamza/kobart-base-v2")
    parser.add_argument("--device", type=str, choices=["cuda", "cpu"], default="cuda")
    parser.add_argument("--quantize", type=str, choices=["onnx_int8"], default=None)
    parser.add_argument("--samples", type=int, default=20)
    args = parser.parse_args()
    
    benchmark_inference(args.model, args.samples, 128, args.device, args.quantize)
