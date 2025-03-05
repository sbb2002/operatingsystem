import json
import huggingface_hub

with open(r'D:\PythonWorkspace\operator_kayoko\config.json', 'r') as js:
    HF_TOKEN = json.load(js)
    HF_TOKEN = HF_TOKEN['HUGGINGFACE_TOKEN']

huggingface_hub.login(HF_TOKEN)


from llama_cpp import Llama
from transformers import AutoTokenizer

model_id = 'Bllossom/llama-3.2-Korean-Bllossom-3B'
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = Llama(
    model_path='llama-3.2-Korean-Bllossom-3B-gguf-Q4_K_M.gguf'
)

instruction = "철수가 20개의 연필을 가지고 있었는데 영희가 절반을 가져가고 민수가 남은 5개를 가져갔으면 철수에게 남은 연필의 갯수는 몇개인가요?"

messages = [
    {"role": "user", "content": f"{instruction}"}
    ]

prompt = tokenizer.apply_chat_template(
    messages, 
    tokenize = False,
    add_generation_prompt=True
)

generation_kwargs = {
    "max_tokens":512,
    "stop":["<|eot_id|>"],
    "echo":True,
    "top_p":0.9,
    "temperature":0.6,
}

resonse_msg = model(prompt, **generation_kwargs)
print(resonse_msg['choices'][0]['text'][len(prompt):])
