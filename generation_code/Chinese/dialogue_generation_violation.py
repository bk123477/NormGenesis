'''
Module 4: Dialogue Generator - Chinese/Violation

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
CSV_PATH = 'YOUR_PATH/situation_chinese_violation.xlsx'
OUTPUT_PATH = 'YOUR_PATH/dialogue_chinese_violation.xlsx'

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
The following is a description of a social norm in Chinese society.
[Social Norm Category]  
{category}

[Description of the Social Norm]  
{norm}

And the following is a scenario & situation which this norm is clearly violated.
[Scenario that Violation]  
{scenario}

[Situation that Violation] 
{situation}

Based on the above information, generate  a realistic dialogue between two people where the social norm is clearly violated.
The violation must be explicit and meaningful, and **no attempt should be made to resolve or correct the behavior**. The emotional flow and interpersonal tension should remain realistic and believable, but the issue must be left unresolved.

The dialogue should:
- Be written in natural, everyday Chinese.
- Include realistic emotional tension and subtle interpersonal dynamics.
- Be structured as a conversation between two people.
- Clearly indicate who is speaking by name before each line.
- Reflect both the **Scenario** and **Situation** above in detail.
- End with the issue still unresolved.

Use the following format:

Dialogue:
小明: 哎，没事没事，不就是响了一下吗。
图书管理员: (皱眉) 这里是图书馆，请保持安静。
李某: (小声嘟囔) 也没多大点声，至于这么凶吗。
明: (耸耸肩，小声) 真是小题大做了。

(短暂沉默，气氛变得有些尴尬，但小明和李某并没有表现出明显的歉意)

图书管理员: (轻叹) 请尽快把手机关掉，不要影响其他人。
小明: (敷衍地) 好好好，知道了。
李某: (低声嘀咕) 真麻烦。

(两人草草地把手机调了静音，但并没有认真道歉或反省，图书管理员无奈地摇了摇头，气氛仍然有些僵硬)
[END]

→ Your Dialogue:"""
    messages = [{"role": "user", "content": prompt}]
    return gpt_api(messages)

# Run module
def run_dialogue_generation():
    df = pd.read_excel(CSV_PATH).reset_index(drop=True)

    dialogues = []
    for idx, row in df.iterrows():
        category = row.get("Category", "")
        norm = row.get("Norm", "")
        scenario = row.get("Violation_Scenario", "")
        situation = row.get("Violation_Situation", "")

        try:
            dialogue = generate_dialogue(category, norm, scenario, situation)
            dialogues.append(dialogue)
            
            time.sleep(1)
        except Exception as e:
            
            dialogues.append("")
    
    df["Dialogue"] = dialogues
    df.to_excel(OUTPUT_PATH, index=False)
    