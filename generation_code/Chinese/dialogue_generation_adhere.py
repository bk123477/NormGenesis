'''
Module 4: Dialogue Generator - Chinese/Adhere

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
CSV_PATH = 'YOUR_PATH/situation_chinese_adhere.xlsx'
OUTPUT_PATH = 'YOUR_PATH/dialogue_chinese_adhere.xlsx'

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
The following is a description of a social norm in Chinese society, along with an example of how the norm is followed.
[Social Norm Category]  
{category}

[Description of the Social Norm]  
{norm}

[Scenario that follows the norm]  
{scenario}

[Situation that follows the norm]  
{situation}

Based on the above information, generate a natural and realistic dialogue between two people that reflects the situation where the chinese norm is being followed.  
Make sure the dialogue reflects both the **Scenario** and the **Situation** above.

The dialogue should:
- Be in a natural, everyday conversational style.
- Be written in Chinese.
- Be structured as a conversation between two people.
- Clearly indicate who is speaking by name before each line.
- Stay focused on the context of the norm being followed.

Use the following format:

Dialogue:
小明: 哎，没事没事，我手机响了，不好意思啊
图书管理员: 别管它，赶紧关掉
李某: 哎呀，真的不好意思，我们没素质了
明: 没事没事，是我没听见
图书管理员: 还是赶紧关掉吧，图书馆里要安静
小明: 好的，谢谢劳驾
图书管理员: 不客气，欢迎常来图书馆
明: 谢谢，再见了
李某: 也谢谢，我们会注意的
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
        scenario = row.get("Refined_Scenario", "")
        situation = row.get("Refined_Situation", "")

        try:
            dialogue = generate_dialogue(category, norm, scenario, situation)
            dialogues.append(dialogue)
            
            time.sleep(1)
        except Exception as e:
            
            dialogues.append("")
    
    df["Dialogue"] = dialogues
    df.to_excel(OUTPUT_PATH, index=False)
    