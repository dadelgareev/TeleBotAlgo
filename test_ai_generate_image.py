import requests
import os
import uuid

RUNWARE_API_KEY = "56k88IRM1kngTd1PF2QpEdZ1id4TLkAH"

API_URL = "https://api.runware.ai/v1"

task_uuid = str(uuid.uuid4())

payload = [
    {
        "taskType": "imageInference",
        "taskUUID": task_uuid,
        "positivePrompt": "Siam cat",
        "model": "civitai:43331@176425",
        "numberResults": 1,
        "negativePrompt": "low quality",
        "height": 512,
        "width": 512,
        "outputFormat": "PNG",
        "CFGScale": 7,
        "steps": 30
    }
]

headers = {
    "Authorization": f"Bearer {RUNWARE_API_KEY}",
    "Content-Type": "application/json"
}

try:
    response = requests.post(API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "data" in data:
            for image in data.get("data", []):
                if image.get("taskType") == "imageInference":
                    print(f"URL изображения: {image['imageURL']}")
                    image_response = requests.get(image["imageURL"])
                    if image_response.status_code == 200:
                        with open("generated_image.png", "wb") as f:
                            f.write(image_response.content)
                        print("Изображение сохранено как 'generated_image.png'")
                    else:
                        print(f"Не удалось скачать изображение: {image_response.status_code}")
        else:
            print(f"Ошибка в ответе: {data.get('error', 'Неизвестная ошибка')}")
    else:
        print(f"Ошибка: {response.status_code}, {response.text}")
except Exception as e:
    print(f"Запрос не удался: {e}")