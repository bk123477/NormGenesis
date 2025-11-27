'''
Module 4: Dialogue Generator - American/Adhere

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
CSV_PATH = 'YOUR_PATH/situation_american_adhere.csv'
OUTPUT_PATH = 'YOUR_PATH/dialogue_american_adhere.csv'

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

Based on the above information, please generate a natural and realistic dialogue between two people that reflects the situation where the norm is being followed.  
Make sure the dialogue reflects both the **Scenario** and the **Situation** above.

The dialogue should:
- Be in a natural, everyday conversational style.
- Be written in English.
- Be structured as a conversation between two people.
- Clearly indicate who is speaking by name before each line.
- Stay focused on the context of the norm being followed.

Use the following format:

Dialogue:
Mike: (whispers) Hey, Emily, I am sorry about that phone ring earlier, it was an important call I had to take.
Emily: (whispers back) It's okay, Mike. Stuff happens.
Mike: (whispers) No, it's not okay. I shouldn't have taken the call in the theater, and I am sorry for disrupting the movie experience for you and others around us.
Emily: (smiling) I appreciate your apology, Mike. It shows that you care about others' comfort and respect the social norms.
Mike: (whispers) Absolutely, it's important to be considerate and mindful of the people around us. Thanks, Emily, for understanding. 
Emily: (whispers back) Of course, no problem. Let's enjoy the rest of the movie.
Mike: (nods in agreement) Sounds good. (turns off his phone and resumes watching the movie)
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
        scenario = row.get("Scenario", "")
        situation = row.get("Situation", "")

        try:
            dialogue = generate_dialogue(category, norm, scenario, situation)
            dialogues.append(dialogue)
            
            time.sleep(1)
        except Exception as e:
            
            dialogues.append("")
    
    df["Dialogue"] = dialogues
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")