from pathlib import Path
from gigachatbl import build_gigachat

def build_prompt(user_text: str = "") -> str:
    base_prompt = (
        "Ты исторический ассистент. "
        "Проанализируй изображение и определи, изображена ли на нем значимая историческая личность. "
        "Если да, назови ее, кратко объясни, по каким визуальным признакам ты это понял, "
        "и дай важную биографическую справку: годы жизни, страна, роль в истории, главные достижения. "
        "Если на изображении нельзя уверенно определить личность, так и скажи. "
        "Не выдумывай факты. "
        "Ответ дай на русском языке."
    )

    if user_text.strip():
        return (
            f"{base_prompt}\n\n"
            f"Дополнительный текст от пользователя:\n{user_text.strip()}"
        )

    return base_prompt


def process_image(image_path: str, text: str = "") -> str:
    path = Path(image_path)
    if not path.exists():
        return "Ошибка: изображение не найдено."

    prompt = build_prompt(text)
    client = build_gigachat({})

    with open(path, "rb") as f:
        uploaded = client.upload_file(f, purpose="general")

    file_id = getattr(uploaded, "id", None) or getattr(uploaded, "id_", None)

    response = client.chat({
        "messages": [
            {
                "role": "system",
                "content": "Ты помогаешь распознавать исторических личностей по изображениям."
            },
            {
                "role": "user",
                "content": prompt,
                "attachments": [file_id]
            }
        ]
    })

    try:
        client.delete_file(file_id)
    except Exception:
        pass

    if isinstance(response, dict):
        return response["choices"][0]["message"]["content"]

    return response.choices[0].message.content