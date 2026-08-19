import os
from dotenv import load_dotenv
load_dotenv()
os.environ["HF_HUB_OFFLINE"] = "1"
from huggingface_hub import InferenceClient

try:
    client = InferenceClient(provider="auto", api_key=os.environ.get("HF_TOKEN"))
    completion = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": "hello"}]
    )
    print("Inference client response:", completion.choices[0].message.content.strip())
except Exception as e:
    print("Error:", e)
