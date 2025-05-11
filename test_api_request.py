import requests
import uuid

API_KEY = 'nRfev7IWZOhqRA2ZIOuT6df3UC2gOcmd'
URL = 'https://api.runware.ai/v1'

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + API_KEY
}

task_uuid = str(uuid.uuid4())

payload = [
    {
        "taskType": "imageInference",
        "taskUUID": task_uuid,
        "positivePrompt": "a cat",
        "width": 512,
        "height": 512,
        "model": "runware:100@1",
        "numberResults": 1
    }
]

response = requests.post(URL, headers=headers, json=payload)

if "data" in response.json():
    data = response.json().get('data')[0]
    image_url = data.get('imageURL')
    print(image_url)

#print(response.json())