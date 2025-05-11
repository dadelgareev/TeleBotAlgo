import requests
import uuid

API_KEY = 'nRfev7IWZOhqRA2ZIOuT6df3UC2gOcmd'
URL = 'https://api.runware.ai/v1'

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + API_KEY
}

task_uuid = uuid.uuid4()

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