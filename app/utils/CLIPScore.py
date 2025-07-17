import torch
import open_clip
from PIL import Image
from io import BytesIO

# 모델은 최초 1회만 로딩
_model, _, _preprocess = open_clip.create_model_and_transforms(
    model_name="ViT-B-32",
    pretrained="laion2b_s34b_b79k"
)
_tokenizer = open_clip.get_tokenizer("ViT-B-32")
_device = "cuda" if torch.cuda.is_available() else "cpu"
_model = _model.to(_device)

def calculate_clip_score(png_bytes: bytes, prompt: str) -> float:
    image = Image.open(BytesIO(png_bytes)).convert("RGB")
    image_tensor = _preprocess(image).unsqueeze(0).to(_device)
    text_tokens = _tokenizer([prompt]).to(_device)

    with torch.no_grad():
        image_features = _model.encode_image(image_tensor)
        text_features = _model.encode_text(text_tokens)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        score = (image_features @ text_features.T).item()

    return round(score, 4)