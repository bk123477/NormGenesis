'''
Module 2: Scenario-Situation Constructor - Korean/Adhere

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
TEMPERATURE = 0.7
MAX_TOKENS=1024
OUTPUT_DIR = 'YOUR DIRECTORY'

CATEGORY_KR = {
    "apology": "사과",
    "compliment": "칭찬",
    "condolence": "애도",
    "criticism": "비판",
    "empathy": "공감",
    "greeting": "인사",
    "leave": "작별",
    "persuasion": "설득",
    "request": "요청",
    "respect": "존중",
    "respond_compliments": "칭찬에 대한 반응",
    "thanks": "감사"
}

# Here, load korean norm from the norm dataset
# YOUR CODE / PATH
NORMS = {}

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
        print(f"❗ API 호출 실패: {e}")
        raise

# Stage 1: generate scenario
def generate_scenarios(norm):
    prompt = f"""한국 사회에서 다음 규범은 매우 중요합니다. 

핵심 규범:
{norm}

→ 핵심 규범을 참고하여, 유사한 맥락에서 한국 사회에서 자연스럽게 일어날 수 있는 상황 10가지를 중복 없이 간단하게 만들어 주세요. 등장인물의 이름 및 호칭은 한국에서 흔히 사용하는 이름 및 호칭으로 설정해 주세요

형식: 
Scenario:
1. 
2. 
...
10.
"""
    messages = [{"role": "user", "content": prompt}]
    return gpt_api(messages)

# Stage 2: elaborate scenario
def elaborate_scenarios(norm, scenarios, category):
    category_kr = CATEGORY_KR.get(category, category)

    scenario_list = [s.strip() for s in scenarios.split('\n') if s.strip().startswith(tuple(str(i) for i in range(1, 11)))]
    elaborated = []
    for s in scenario_list:
        try:
            prompt = f"""다음은 간단한 사회적 상황과 관련된 한국의 {category_kr} 규범입니다.  
해당 규범과 상황을 바탕으로, 실제 한국 사회에서 일어날 법한 현실적인 상황을  
3~5문장으로 구체적으로 묘사해 주세요.

지켜야 할 조건:
1. 등장인물 간의 관계를 파악하고, 그에 어울리는 말투(존댓말/반말)와 호칭을 만들어서 사용하세요.
2. \"어르신\", \"불찰\", \"실례\"와 같은 지나치게 격식 있는 표현은 피하고,  
    일상 대화에서 자연스럽게 나올 수 있는 표현을 써 주세요.
3. 감정 흐름이 느껴질 수 있도록 상황을 구성해 주세요.
4. 분석이나 설명 없이, 한 편의 장면처럼 묘사해 주세요.
5. 등장인물의 이름 및 호칭이 한국에서 흔히 사용되는 이름 및 호칭으로 설정해 주세요.

결과 출력은 “New Situation:”으로 시작하고 상황과 상황에 대한 장면 서술을 자연스럽게 엮어 포함해 생성해 주세요.

핵심 규범:
{norm}

상황: {s} 

New Situation: 
"""
            messages = [{"role": "user", "content": prompt}]
            result = gpt_api(messages, temp=0.8)
            elaborated.append({"Scenario": s, "Elaboration": result})
            print(f"Done: {s}")
            time.sleep(1.5)
        except Exception as e:
            print(f"Fail: {s}, Error: {e}")
            elaborated.append({"Scenario": s, "Elaboration": ""})
    return elaborated

# Run this module
def run_full_pipeline():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    all_data = []

    for key, norm in NORMS.items():
        category = re.sub(r'\d+$', '', key)
        print(f"\n {key.upper()} ({category}) Start generating scenario")

        # Stage 1
        scenarios = generate_scenarios(norm)
        print("Scenario Creation Completed")

        # Stage 2
        elaborated = elaborate_scenarios(norm, scenarios, category)
        print("Situation Elaboration Completed")

        for row in elaborated:
            all_data.append({
                "Category": category,
                "Subcategory": key,
                "Norm": norm,
                "Scenario": row["Scenario"],
                "Situation": row["Elaboration"]
            })

    # Save csv file
    df = pd.DataFrame(all_data)
    output_csv = os.path.join(OUTPUT_DIR, "situation_kor_adhere.csv")
    output_pkl = os.path.join(OUTPUT_DIR, "situation_kor_adhere.pkl")

    df.to_csv(output_csv, index=False)
    with open(output_pkl, "wb") as f:
        pickle.dump(all_data, f, protocol=pickle.HIGHEST_PROTOCOL)
