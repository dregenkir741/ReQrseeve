import os
import json
import httpx
from dotenv import load_dotenv
from .models import ExtractedTask, Plan
import uuid

load_dotenv()

AUTHORIZATION_KEY = os.getenv("GIGACHAT_CREDENTIALS")
VERIFY_SSL = os.getenv("GIGACHAT_VERIFY_SSL", "true").lower() != "false"

def get_token() -> str:
    """Получает access token по Authorization Key."""
    auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Authorization": f"Basic {AUTHORIZATION_KEY}",  # не Bearer
        "RqUID": str(uuid.uuid4()),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"scope": "GIGACHAT_API_PERS"}
    with httpx.Client(verify=VERIFY_SSL) as client:
        response = client.post(auth_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]


def chat_completion(messages: list[dict], model="GigaChat") -> dict:
    """Отправляет сообщения и возвращает полный ответ API (словарь)."""
    token = get_token()
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "model": model,
        "messages": messages,
    }
    with httpx.Client(verify=VERIFY_SSL) as client:
        response = client.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()

EXTRACTION_PROMPT = """Ты — ассистент по извлечению задач.
Твоя задача — найти в тексте пользователя все упоминания целей, задач, идей, желаний и планов.
Верни их в виде плоского списка (массива) объектов JSON.
Каждый объект должен содержать:
- id: порядковый номер задачи в виде строки ("1", "2", ...)
- title: короткий заголовок задачи, не длиннее 10 слов
- context_hints: массив строк с ключевыми условиями выполнения задачи: место, необходимые ресурсы (например, телефон, ноутбук), временные ограничения (если указаны), другие важные детали.
Если в тексте несколько задач — верни их все. Если задач нет — верни пустой массив.
Не добавляй никаких комментариев, выведи только JSON."""

def extract_tasks(text: str) -> list[ExtractedTask]:
    messages = [
        {"role": "system", "content": EXTRACTION_PROMPT},
        {"role": "user", "content": text}
    ]
    completion = chat_completion(messages)
    raw_content = completion["choices"][0]["message"]["content"]
    data = json.loads(raw_content)

    if isinstance(data, list):
        tasks_data = data
    else:
        tasks_data = data.get("tasks", [])

    result = []
    for item in tasks_data:
        if isinstance(item, dict):
            task = ExtractedTask(
                title=item.get("title", "Без названия"),
                context_hints=item.get("context_hints", [])
            )
            result.append(task)
    return result

if __name__ == "__main__":
    test_text = "Надо сходить в магазин за хлебом, позвонить другу, выучить Python и полить цветы на подоконнике"
    tasks = extract_tasks(test_text)
    print("=== Извлечённые задачи ===")
    for t in tasks:
        print(f"- {t.title} | {t.context_hints}")