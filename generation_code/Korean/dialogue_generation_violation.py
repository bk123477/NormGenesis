'''
Module 4: Dialogue Generator - Korean/Violation

Model Configuration: gpt-4.1
Author: 
    Minki Hong (⚠️ Contact Me: jackyh1@dgu.ac.kr)
    Jangho Choi (⚠️ Contact Me: 2025120382@dgu.ac.kr)
'''

# Import libraries
import os
import time
import pandas as pd
import pickle
import json
import re
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Setting API
client = OpenAI(api_key=os.getenv("YOUR_OPEN_API_KEY"))

MODEL = 'gpt-4.1'
TEMPERATURE = 0.9
MAX_TOKENS=1024
OUTPUT_DIR = 'YOUR DIRECTORY'
CSV_PATH = "YOUR_PATH/situation_korean_violation.csv"
OUTPUT_PATH = "YOUR_PATH/dialogue_korean_violation.csv"

# Call GPT API
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def gpt_api(messages, temp=TEMPERATURE, max_tokens=MAX_TOKENS):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=temp,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❗ Fail to call: {e}")
        raise

# Generate Dialogue
def generate_dialogue(category, norm, scenario, situation):
    prompt = f"""
다음은 한국의 사회적 규범에 대한 설명과 규범을 위반한 예시입니다.

[사회적 규범 카테고리]
{category}

[사회적 규범 설명]
{norm}

[규범을 위반한 Scenario]
{scenario}

[규범을 위반한 Situation]
{situation}

해당 내용을 바탕으로 Situation에 대한 Dialogue를 생성해 주세요. 
Dialogue는 두 사람 간의 대화 형식으로 작성해 주세요. 
대화의 주제는 규범을 위반하는 상황에 대한 것입니다.
문제를 해결하려고 하지 마세요. 규범이 위반한 상황이 존재하며, 대화의 끝까지 규범 위반이 해결되지 않습니다.
대화의 내용은 자연스럽고 일상적인 대화로 구성되어야 하며, 
각 인물의 이름과 대사로 구분되어야 합니다. 
대화는 다음과 같은 형식으로 작성해 주세요.

Dialogue:
정 부장: 민수 씨, 이 보고서 여기 수치 잘못됐어요. 지난 분기 자료가 그대로 들어갔잖아요.
민수: (모니터에서 눈도 안 떼며) 아, 네. 그럴 수도 있죠.
정 부장: …그럴 수도 있다뇨? 발표 자료인데 이런 실수가 반복되면 곤란하잖아요.
민수: (작게 한숨 쉬며) 아니 뭐, 요즘 너무 일 많아서 그렇죠. 제가 이것만 하는 것도 아니고요.
정 부장: (표정 굳으며) 지금 제 말이 귀찮다는 겁니까?
민수: 그런 건 아닌데요... 굳이 이렇게까지 말씀하실 일은 아닌 것 같아서요.
(회의실 분위기가 싸늘하게 가라앉고, 동료들은 말없이 눈을 돌린다)
[끝]

→ 당신의 대화:"""
    messages = [{"role": "user", "content": prompt}]
    return gpt_api(messages)

# Run module
def run_dialogue_generation():
    df = pd.read_csv(CSV_PATH).reset_index(drop=True)

    dialogues = []
    for idx, row in df.iterrows():
        category = row.get("Category", "")
        norm = row.get("Norm", "")
        scenario = row.get("Violation_Scenario", "")
        situation = row.get("Violation_Situation", "")

        if pd.isna(norm) or pd.isna(situation):
            dialogues.append("")
            continue

        try:
            dialogue = generate_dialogue(category, norm, scenario, situation)
            dialogues.append(dialogue)
            
            time.sleep(1)
        except Exception as e:
            
            dialogues.append("")
        
    df["Dialogue"] = dialogues
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    