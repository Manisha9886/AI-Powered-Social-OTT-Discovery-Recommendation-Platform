import os
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

from dotenv import load_dotenv
load_dotenv()

hf_token = os.getenv("HF_TOKEN")
hf_model = "mistralai/Mistral-7B-Instruct-v0.3"
API_URL = "https://api-inference.huggingface.co/models/" + hf_model + "/v1/chat/completions"
headers = {"Authorization": f"Bearer {hf_token}"}
payload = {
    "model": hf_model,
    "messages": [{"role": "user", "content": "hello"}],
    "max_tokens": 100
}
try:
    response = requests.post(API_URL, headers=headers, json=payload, verify=False)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", e)
