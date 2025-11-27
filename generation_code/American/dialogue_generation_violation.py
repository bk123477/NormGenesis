'''
Module 4: Dialogue Generator - American/Violation

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
CSV_PATH = 'YOUR_PATH/situation_american_violation.csv'
OUTPUT_PATH = 'YOUR_PATH/dialogue_american_violation.csv'

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
The following is a description of a social norm in American society, along with an example of how the norm is followed.

[Social Norm Category]  
{category}

[Description of the Social Norm]  
{norm}

[Scenario that follows the norm]  
{scenario}

[Situation that follows the norm]  
{situation}

Now, based on the above scenario and situation, generate a realistic dialogue between two people where the social norm is clearly violated.  
The violation must be explicit and meaningful, and **no attempt should be made to resolve or correct the behavior**. The emotional flow and interpersonal tension should remain realistic and believable, but the issue must be left unresolved.

The dialogue should:
- Be written in natural, everyday English.
- Include realistic emotional tension and subtle interpersonal dynamics.
- Be structured as a conversation between two people.
- Clearly indicate who is speaking by name before each line.
- Reflect both the **Scenario** and **Situation** above in detail.
- End with the issue still unresolved.

Use the following format:

Dialogue:
Mike: (phone rings loudly) Hold on, I need to take this.
Emily: (annoyed) Mike, seriously? We’re in a theater.
Mike: (shrugs) Yeah, but this is important.
Emily: (disappointed) You always say that. What about everyone else here?
Mike: (defensive) It’s not like I’m the only one who's ever done this.
Emily: (quietly) You just don’t get it, do you...
Mike: (still on his phone) I’ll just be a second. Chill out.

[END]

→ Your Dialogue:"""
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

        try:
            dialogue = generate_dialogue(category, norm, scenario, situation)
            dialogues.append(dialogue)
            
            time.sleep(1)
        except Exception as e:
            
            dialogues.append("")
    
    df["Dialogue"] = dialogues
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    