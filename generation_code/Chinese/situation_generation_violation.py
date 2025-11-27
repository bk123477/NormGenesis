'''
Module 2: Scenario-Situation Constructor - Chinese/Violation

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
file_path = 'YOUR_PATH/situation_chinese_violation.xlsx'
df = pd.read_csv(file_path, usecols=["Category", "Norm", "Scenario", "Situation"])

# Build prompt
def build_violation_prompt(row):
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

Now, create a new Scenario and Situation in which this norm is clearly violated. The violation must be explicit, but the emotional flow and behavior must remain realistic and natural. **Do not include any attempts to resolve the violation.** Only the violation itself should be depicted.

Make sure the relationship between characters, setting, and emotional progression are clearly reflected. The expressions should be detailed and realistic—write with the depth and length of a full example, not a brief summary.

**Generate the dialogue in Chinese, and the rest situation description in English.**
Example: New Situation: At the company’s annual meeting, Xiao Li accidentally stepped on the shoes of his department supervisor, Manager Li. Xiao Li immediately stopped, lowered his head, and said in a humble and soft voice, “对不起，李经理，是我不小心.” He did not look up at Manager Li, but instead waited sincerely for a response, showing respect and apology to his elder and superior.

[Scenario with Norm Violation]:  
[Situation with Norm Violation]:
"""

# GPT response parser
def parse_gpt_violation_output(response_text):
    if "[Situation with Norm Violation]" in response_text:
        parts = response_text.split("[Situation with Norm Violation]")
        scenario = parts[0].replace("[Scenario with Norm Violation]", "").strip()
        situation = parts[1].strip()
        return scenario, situation
    else:
        return response_text.strip(), ""

# Call GPT API
def generate_violation(row, model=base_model, temperature=0.8, max_tokens=1024):
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

for idx, row in tqdm(df.iterrows(), total=len(df), desc="Generating violation"):
    try:
        scenario, situation = generate_violation(row)
        violation_scenarios.append(scenario)
        violation_situations.append(situation)
        time.sleep(1.5)
    except Exception as e:
        violation_scenarios.append("Error")
        violation_situations.append(str(e))

# Save to XLSX file
new_df = pd.DataFrame({
    'Violation_Scenario': violation_scenarios,
    'Violation_Situation': violation_situations
})
new_df.to_excel("situation_chinese_violation.xlsx", index=False)