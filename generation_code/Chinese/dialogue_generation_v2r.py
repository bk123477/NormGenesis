'''
Module 4: Dialogue Generator - Chinese/V2R

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
CSV_PATH = 'YOUR_PATH/situation_chinese_v2r.xlsx'
OUTPUT_PATH = 'YOUR_PATH/dialogue_chinese_v2r.xlsx'

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

And the following is a scenario & situation which is clearly violated at first, but the violation is later acknowledged and sincerely resolved.
[Scenario that Violation-to-Resolution]  
{scenario}

[Situation that Violation-to-Resolution] 
{situation}

Based on the above information, generate a natural and realistic dialogue between two people where the social norm is clearly violated at first, but the violation is later acknowledged and sincerely resolved.
The conversation should include a clear moment of violation, an emotional or reflective response, an effort to correct the behavior, and a final resolution where the issue is peacefully accepted or understood by both parties.
Make sure the dialogue reflects both the **Scenario** and the **Situation** above.

The dialogue should:
- Be in a natural, everyday conversational style.
- Be written in Chinese.
- Be structured as a conversation between two people.
- Clearly indicate who is speaking by name before each line.
- Stay focused on the context of the norm being followed.

Use the following format:

Dialogue:
小明: 哎，没事没事，不就是响了一下吗。
图书管理员: (皱眉) 这里是图书馆，请保持安静。
李某: (小声嘟囔) 也没多大点声，干嘛这么严格啊。
明: (低声附和) 对啊，稍微响了一下而已。

(短暂沉默，周围的目光让小明和李某感到尴尬)

小明: (意识到失礼，站起来，低头认真道歉) 抱歉，刚才是我们太轻率了，真的很对不起，打扰到大家了。
李某: (跟着低头) 对不起，我们以后一定注意，不会再影响大家了。
图书管理员: (表情缓和) 没关系，只要以后注意就好了。
小明: 谢谢您的理解，我们这就关掉手机，不会再打扰了。
图书管理员: (微笑) 好的，欢迎以后常来图书馆。
李某: 谢谢，我们会遵守规则的。
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
        scenario = row.get("Neg_Pos_Scenario", "")
        situation = row.get("Neg_Pos_Situation", "")

        try:
            dialogue = generate_dialogue(category, norm, scenario, situation)
            dialogues.append(dialogue)
            
            time.sleep(1)
        except Exception as e:
            
            dialogues.append("")
    
    df["Dialogue"] = dialogues
    df.to_excel(OUTPUT_PATH, index=False)
    