from pathlib import Path
import base64
from langchain_openai import ChatOpenAI

# Инициализация модели (как у тебя)
llm = ChatOpenAI(
    openai_api_base="https://api.mistral.ai/v1",
    model="mistral-large-latest",
    api_key="ZvMLZdits0HwToXTM3E9NopLVyQgImAs",
    temperature=0
)


def build_prompt(user_text: str = "") -> str:
    base_prompt = (
        "Ты исторический ассистент. "
        "Проанализируй изображение и определи, изображена ли на нем значимая историческая личность. "
        "Если да, назови ее и дай краткую биографию. "
        "Если нет — так и скажи. Не выдумывай."
    )

    if user_text.strip():
        return base_prompt + "\n\nТекст пользователя:\n" + user_text

    return base_prompt


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def process_image(image_path: str, text: str = "") -> str:
    path = Path(image_path)
    if not path.exists():
        return "Ошибка: изображение не найдено."

    prompt = build_prompt(text)
    image_base64 = encode_image(image_path)

    # Mistral multimodal формат
    message = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image_base64}"
                },
            ],
        }
    ]

    response = llm.invoke(message)

    return response.content