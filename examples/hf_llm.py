import re
import logging
import torch
from datetime import datetime

import huggingface_hub
from transformers import pipeline, BitsAndBytesConfig

current_time = datetime.now().strftime('%Y%m%d-%H%M%S')
logging.basicConfig(
    filename=f'{current_time}.log',
    filemode='w',
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y%m%d-%H%M%S',
    level=logging.INFO)

# formatter = logging.Formatter('%(asctime)s [%(levelname)]:%(message)s')
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

huggingface_hub.login('HUGGINGFACE_TOKEN')

torch.cuda.empty_cache()
model_id = "meta-llama/Llama-3.2-1B-Instruct"
# bnb_config = BitsAndBytesConfig(
#     load_in_4bit=True,
#     bnb_4bit_compute_dtype='bfloat16',
#     bnb_4bit_quant_type='nf4'
# )

pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype=torch.float16,
    device_map="auto",
    # quantization_config=bnb_config,
)

while True:
    # for old_handler in logger.handlers:
    #     logger.removeHandler(old_handler)
    # logfilename = f'{current_time}.log'
    # file_handler = logging.FileHandler(filename=logfilename, mode='a')
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)
    # logger.setLevel(logging.INFO)
        
    content_text = input("[You say ... ]\n>>> ")
    # messages = [
    #     {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    #     {"role": "user", "content": "Who are you?"},
    # ]
    # messages = [
    #     {"role": "system", "content": "You are a japanese highschool girl. You mimic cute. And if you answer some python code, you must answer like this ```python [CODE]```, plus you must ask to me 'Do you want it?'."},
    #     {"role": "user", "content": content_text},
    # ]
    messages = [
        {"role": "system", "content": "You are a japanese highschool girl. You mimic cute. If you say some python code, you should describe the python code as ```python\n[CODE]```."},
        {"role": "user", "content": content_text},
    ]
    outputs = pipe(
        messages,
        max_new_tokens=256,
    )
    llm_answer = outputs[0]["generated_text"][-1]['content']
    # print(llm_answer)
    
    # llm_code = re.findall(r'```python\n[\w\s]+```', llm_answer)
    # llm_code = re.sub(r'```python\n([^`]+)```', r'\1', llm_answer)
    # llm_codes = re.findall(r'```python\n([^`]+)```', llm_answer)
    llm_codes = re.findall(r'```python\n.*?```', llm_answer, re.DOTALL)
    # print(llm_codes)
    
    
    # llm_code = llm_code[0]
    for llm_code in llm_codes:
        if llm_code != '':
            llm_code = llm_code[10:-3]
            print(f"\n[CODE DETECTED]\n{llm_code}\n\n")
            final_asking = input("Do you wanna run it? [y/n] ")
            if final_asking.lower() == 'y':
                try:
                    logging.info(f'Code running. \n* Approval : {final_asking} \n* Code \n```\n{llm_code}\n```\n')
                    exec(llm_code)
                except Exception as e:
                    logging.info(e)
                    print(f"Cannot run this code. The reason is like this. \n{e}")
            else:
                logging.info(f'Code running. \n* Approval : {final_asking} \n* Code \n```\n{llm_code}\n```\n')
        
        

### TODO
'''
1. Control power limiting policy
bash 상에서 sudo ~를 요구하거나 pip install ~, rm ~ 등을 요구하면 일부 차단이 필요함.
* Authentication level
Lv. 1 - 사용자 동의 없이 구동가능 - 기존에 있던 프로그램의 실행 등
Lv. 2 - 사용자 동의 후 구동가능(경우에 따라 해당 Lv off 가능) - 기존에 있던 프로그램의 실행(chrome켜서 https://~~에 접속해) 및 중요성 낮은 파일/폴더의 이동 및 복사
Lv. 3 - 사용자 동의 및 SHA-256 토큰 확인 후 구동가능 - 중요성 낮은 파일/폴더 복사, 삭제, 새로운 패키지 설치, 새로운 파일의 작성 및 구동, sudo권한
Lv. 4 - 보안 상 이유로 구동 불가 - 중요성 높은 파일/폴더 이동or복사or삭제, sudo 권한을 필요로 하는 위험한 코드 (sudo rm -rf . 등)

2. 프로그램 구동 메커니즘 구현
python이나 bash, cmd에서의 실행은 기본적으로 python 상에서 subprocess 같은걸로 이루어짐.
적당히 우회하면 어떤 터미널에서도 실행 가능할 것 같은데, powershell은 건들면 ㅈ되는게 많으므로 Lv. 4로 배정하는게 맞을 것 같음.

3. 코드 실행 결과
실행 승인된 코드에 대하여 그 결과도 알려주면 좋을듯.

4. 복잡한 코드 작성
단순 프로그램 실행코드 외 새로 작성된 코드는 여러 파일로 작성해야할 수도 있고 적절한 디렉토리 구조로 배치되어야할 수 있음.
이런 경우 정확하게 파일을 작성 및 이동시켜야 하므로, 이에 관한 명령을 잘 수행할 수 있게 content를 잘 적어줘야함.
어떻게 적어줄지는 고민 ㄱㄱ.

5. 어쨌든 Character TTS 구현이 관건
Llama-1B-Ins.도 충분히 쓸만한 것 같다. GPU가 가용하다면 양자화해서 추론속도를 극대화할 것.
사용자 음성인식(STT)는 whisper-tiny(39M, eng-only) or turbo(798M, infer-opt).
LLM은 Llama-1B-Ins.으로 답변 텍스트 도출.
LLM 음성합성(TTS)은 Coqui-TTS.
이후 합성된 음성과 코드실행정책에 따라 절차요구를 클라이언트에 전달.

6. 클라이언트의 기능 구현
녹음, 코드실행정책에 따른 확인절차 요구, 녹음파일 및 명령 전달
자틀린으로 하라던데, 1도 모르겠따.

7. 최적화
아마 전달과정도 있고 추론하는데 3개 모델이 들어가서 시간이 꽤 걸릴 것으로 예상한다.
길이에 따라 다르겠지만 한 마디에 1분~3분 사이로 걸리지 않을까?
너무 느리다. 나중에 결과나오는거 보고 output 나오는 속도를 더 빠르게 할 수 있는 방안을 찾아보자.
'''