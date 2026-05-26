import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image

class KoreanTROCR:
    """
    Hugging Face 기반 한국어 TrOCR 로컬 추론 엔진
    """
    def __init__(self, model_id="ddobokki/ko-trocr", device=None):
        if device is None:
            # 기본적으로 CUDA가 가능하면 사용, 아니면 CPU
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"Loading TrOCR model '{model_id}' on {self.device}...")
        self.processor = TrOCRProcessor.from_pretrained(model_id)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_id).to(self.device)
        print("Model loaded successfully.")

    def extract_text(self, image: Image.Image) -> str:
        """
        PIL 이미지를 입력받아 추출된 텍스트 문자열 반환
        """
        image = image.convert("RGB")
        pixel_values = self.processor(images=image, return_tensors="pt").pixel_values.to(self.device)
        
        with torch.no_grad():
            generated_ids = self.model.generate(
                pixel_values, 
                max_length=256,
                num_beams=4,
                early_stopping=True
            )
            
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return generated_text.strip()
