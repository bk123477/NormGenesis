'''
Module 4: Dialogue Generator - Korean/Adhere

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
EXCEL_PATH = 'YOUR_PATH/situation_korean_adhere.xlsx'
OUTPUT_PATH = 'YOUR_PATH/dialogue_korean_adhere.xlsx'

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
다음은 한국의 사회적 규범에 대한 설명과 준수 예시입니다.

[사회적 규범 카테고리]
{category}

[사회적 규범 설명]
{norm}

[규범을 준수한 Scenario]
{scenario}

[규범을 준수한 Situation]
{situation}

해당 내용을 바탕으로 Situation에 대한 Dialogue를 생성해 주세요. 
Dialogue는 두 사람 간의 대화 형식으로 작성해 주세요. 
대화의 주제는 규범을 준수하는 상황에 대한 것입니다. 
대화의 내용은 자연스럽고 일상적인 대화로 구성되어야 하며, 
각 인물의 이름과 대사로 구분되어야 합니다. 
대화는 다음과 같은 형식으로 작성해 주세요.

Dialogue:
철수: 민지야, 정말 미안해. 내가 장난이 너무 심했지?
민지: 아니야 철수야, 네가 그렇게 말해줘서 괜찮아졌어.
철수: 그래도 마음에 걸리네... 정말 미안해.
민지: 괜찮아, 다음부터는 조심해 줘.
철수: 응.. 미안해!
[끝]

→ 당신의 대화:"""
    messages = [{"role": "user", "content": prompt}]
    return gpt_api(messages)

# Run module
def run_dialogue_generation():
    df = pd.read_excel(EXCEL_PATH).reset_index(drop=True)

    dialogues = []
    for idx, row in df.iterrows():
        category = row.get("Category", "")
        norm = row.get("Norm", "")
        scenario = row.get("Scenario", "")
        situation = row.get("Situation", "")

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
    df.to_excel(OUTPUT_PATH, index=False)