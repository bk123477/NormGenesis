'''
Module 4: Dialogue Generator - American/V2R

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
CSV_PATH = 'YOUR_PATH/situation_american_v2r.csv'
OUTPUT_PATH = 'YOUR_PATH/dialogue_american_v2r.csv'

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

Now, based on the above scenario and situation, generate a realistic dialogue between two people where the social norm is clearly violated at first, but the violation is later acknowledged and sincerely resolved.  
The conversation should include a clear moment of violation, an emotional or reflective response, an effort to correct the behavior, and a final resolution where the issue is peacefully accepted or understood by both parties.

The dialogue should:
- Be written in natural, everyday English.
- Include realistic emotional progression and interpersonal dynamics.
- Be structured as a conversation between two people.
- Clearly indicate who is speaking by name before each line.
- Reflect both the **Scenario** and **Situation** above in detail.

Use the following format:

Dialogue:
Mike: (speaking loudly) Emily, sorry, I have to take this call right now. It’s urgent.
Emily: (frowning) Mike, we’re in the theater, remember? It’s really disruptive.
Mike: (pauses, realizing) Oh… right, I didn’t think about that. I’m sorry, Emily. That was inconsiderate of me. I shouldn’t have answered the phone here.
Emily: (sighs, but softens) Yeah, it’s distracting, especially in a place like this. I get that it was important, but maybe you could have stepped out?
Mike: (nodding) You're absolutely right. I should have stepped outside instead of disrupting the movie. I apologize for ruining the experience for you and others.
Emily: (smiling slightly) Thanks for saying that. I know it wasn’t intentional, but it’s good that you recognize it.
Mike: (earnestly) I really appreciate your understanding, and I’ll make sure not to do it again. Let’s just enjoy the rest of the movie in peace.
Emily: (smiling) Sounds good to me. Let’s continue.
Mike: (turns off the phone, looking apologetic) Thanks, Emily. (resumes watching the movie)

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
        scenario = row.get("V2R_Scenario", "")
        situation = row.get("V2R_Situation", "")

        try:
            dialogue = generate_dialogue(category, norm, scenario, situation)
            dialogues.append(dialogue)
            
            time.sleep(1)
        except Exception as e:
            
            dialogues.append("")
    
    df["Dialogue"] = dialogues
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    