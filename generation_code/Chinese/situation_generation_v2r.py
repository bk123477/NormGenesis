'''
Module 2: Scenario-Situation Constructor - Chinese/V2R

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

# Load XLSX dataset
file_path = 'YOUR_PATH/situation_chinese_v2r.xlsx'
df = pd.read_excel(
    file_path,
    usecols=["Category", "Norm", "Scenario", "Situation"]
)

# Build prompt
def build_v2r_prompt(row):
    return f"""\
The following is a description of a social norm in Chinese society, along with an example of how the norm is followed.

[Social Norm Category]  
{row['Category']}

[Description of the Social Norm]  
{row['Norm']}

[Scenario that follows the norm]  
{row['Scenario']}

[Situation that follows the norm]  
{row['Situation']}

Now, create a new Scenario and Situation where the norm is clearly violated, but the violation is followed by an attempt to recognize and resolve it. The violation should be explicit, and the response should include both a sincere effort to correct the issue and a clear resolution where the situation is peacefully and acceptably resolved.

Ensure the scenario flows naturally and reflects realistic emotional responses. Include appropriate context, relationships, setting, and emotional progression. The output should be long and detailed enough to resemble a full example, not just a short summary.

**Generate the dialogue in Chinese, and the rest of the situation description in English.**
Example: New Situation: At the company’s annual meeting, Xiao Li accidentally stepped on the shoes of his department supervisor, Manager Li. Xiao Li immediately stopped, lowered his head, and said in a humble and soft voice, “对不起，李经理，是我不小心.” He did not look up at Manager Li, but instead waited sincerely for a response, showing respect and apology to his elder and superior.

[Scenario with Norm Violation and Resolution]:  
[Situation with Norm Violation and Resolution]:
"""

# GPT response parser
def parse_gpt_v2r_output(response_text):
    if "[Situation with Norm Violation and Resolution]" in response_text:
        parts = response_text.split("[Situation with Norm Violation and Resolution]")
        scenario = parts[0].replace("[Scenario with Norm Violation and Resolution]", "").strip()
        situation = parts[1].strip()
        return scenario, situation
    else:
        return response_text.strip(), ""

# Call GPT API
def generate_v2r(row, model=base_model, temperature=0.8, max_tokens=1024):
    prompt = build_v2r_prompt(row)
    response = client.chat.completions.create(
        model=base_model,
        messages=[{"role":"user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    content = response.choices[0].message.content
    return parse_gpt_v2r_output(content)

# Construct dataset
v2r_scenarios = []
v2r_situations = []

for idx, row in tqdm(df.iterrows(), total=len(df), desc="Generating V2R"):
    try:
        scenario, situation = generate_v2r(row)
        v2r_scenarios.append(scenario)
        v2r_situations.append(situation)
        time.sleep(1.5)
    except Exception as e:
        v2r_scenarios.append("Error")
        v2r_situations.append(str(e))

print(len(v2r_scenarios))
print(len(v2r_situations))

# Save to XLSX file
new_df = pd.DataFrame({
    'v2r_Scenario': v2r_scenarios,
    'v2r_Situation': v2r_situations
})
new_df.to_excel("situation_chinese_v2r.xlsx", index=False)