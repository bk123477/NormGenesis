'''
Module 2: Scenario-Situation Constructor - Korean/Violation

Model Configuration: gpt-4.1
Author: 
    Minki Hong (⚠️ Contact Me: jackyh1@dgu.ac.kr)
    Jangho Choi (⚠️ Contact Me: 2025120382@dgu.ac.kr)
'''

# Import libraries
import os
from pydantic import BaseModel
import openai
from datasets import load_dataset
import json, jsonlines
import re
import random
import numpy as np
import sys
import pandas as pd
from tqdm import tqdm
import time

# Setting API
client = openai.OpenAI(api_key=os.getenv("YOUR_OPEN_API_KEY"))

base_model = 'gpt-4.1'
MAX_TOKENS=1024
OUTPUT_DIR = 'YOUR DIRECTORY'

# Load CSV dataset
file_path = 'YOUR_PATH/situation_korean_violation.csv'
df = pd.read_csv(file_path, usecols=["Category", "Norm", "Scenario", "Situation"])

# Build prompt
def build_violation_prompt(row):
    return f"""\
다음은 한국의 사회적 규범에 대한 설명과 준수 예시입니다.
[사회적 규범 카테고리]
{row['Category']}

[사회적 규범 설명]
{row['Norm']}

[규범을 준수한 Scenario]
{row['Scenario']}

[규범을 준수한 Situation]
{row['Situation']}

이제 위 규범을 위반하는 Scenario와 Situation을 생성하세요. 단, 위반은 명백하지만 현실적인 흐름과 감정 표현이 자연스러워야 합니다. 또한, 규범의 위반만이 존재해야 합니다. 문제가 생기면 해결하려고 하지 마세요. 인물 간의 관계, 장소, 감정 흐름이 자연스럽게 드러나도록 구성하세요. 표현은 너무 짧지 않게, 예시 수준의 길이로 작성하세요.

[규범을 위반한 Scenario]:
[규범을 위반한 Situation]:
"""

# GPT response parser
def parse_gpt_violation_output(response_text):
    if "[규범을 위반한 Situation]" in response_text:
        parts = response_text.split("[규범을 위반한 Situation]")
        scenario = parts[0].replace("[규범을 위반한 Scenario]", "").strip()
        situation = parts[1].strip()
        return scenario, situation
    else:
        return response_text.strip(), ""

# Call GPT API
def generate_violation(row, model=base_model, temperature=0.8, max_tokens=800):
    prompt = build_violation_prompt(row)
    response = client.chat.completions.create(
        model=base_model,
        messages=[{"role":"user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    content = response.choices[0].message.content
    return parse_gpt_violation_output(content)

# Construct dataset
violation_scenarios = []
violation_situations = []

for idx, row in tqdm(df.iterrows(), total=len(df), desc="Generating violations"):
    try:
        scenario, situation = generate_violation(row)
        violation_scenarios.append(scenario)
        violation_situations.append(situation)
        time.sleep(1.5)
    except Exception as e:
        violation_scenarios.append("Error")
        violation_situations.append(str(e))

# Save to CSV file
new_df = pd.DataFrame({
    'Violation_Scenario': violation_scenarios,
    'Violation_Situation': violation_situations
})

new_df.to_csv("violation_output_clean.csv", index=False, encoding="utf-8-sig")