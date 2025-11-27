'''
Module 2: Scenario-Situation Constructor - American/Adhere

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

prefix_list = [
    "apology",
    "compliment",
    "condolence",
    "criticism",
    "empathy",
    "greeting",
    "leave",
    "persuasion",
    "request",
    "respect",
    "respond_compliments",
    "thanks"
]

CATEGORY_ENG = {
    "apology": "apology",
    "compliment": "compliment",
    "condolence": "condolence",
    "criticism": "criticism",
    "empathy": "empathy",
    "greeting": "greeting",
    "leave": "leave",
    "persuasion": "persuasion",
    "request": "request",
    "respect": "respect",
    "respond_compliments": "respond_compliments",
    "thanks": "thanks"
}

# Load norm dataset
jsonl_path = 'YOUR_PATH/american_norm.jsonl'
NORMS = {}
with open(jsonl_path, "r", encoding="utf-8") as f:
    lines = f.readlines()
assert len(lines) == len(prefix_list) * 10, 'Not match'

for i, line in enumerate(lines):
    category_index = i // 10
    item_index = (i % 10) + 1
    prefix = prefix_list[category_index]
    norm_key = f"{prefix}{item_index}"

    data = json.loads(line.strip())
    norm_text = data.get("american_norm")

    if norm_text:
        NORMS[norm_key] = norm_text
    else:
        print(f"❗ Warn: There is no field in {i+1}")


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
        print(f"❗ Fail to call API {e}")
        raise


# Stage 1: generate scenario
def generate_scenarios(norm):
    prompt = f"""Social norms are informal rules that govern behaviors in groups and societies. You are given a social norm, and you are tasked to imagine 10 scenarios that a conversation that entails the Norm can take place in a real-life setting of American society.
    
    Core Norm:
    {norm}

    Based on the core norm, please create 10 simple and non-overlapping situations that could naturally occur in American society in similar contexts. Use common American names and titles for the characters.

    Format:
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
    category_eng = CATEGORY_ENG.get(category, category)
    scenario_list = [s.strip() for s in scenarios.split('\n') if s.strip().startswith(tuple(str(i) for i in range(1, 11)))]
    elaborated = []
    for s in scenario_list:
        try:
            prompt = f"""The following is a social norm related to a simple social situation in American society under the category of {category_eng}.
            Based on the norm and the situation, please describe a realistic scenario that could naturally occur in American society in 3 to 5 sentences.

            Please follow these guidelines:
            1. Understand the relationship between the characters and use appropriate tones and titles accordingly.
            2. Avoid overly formal expressions; use language that sounds natural in everyday conversation.
            3. Create a situation where the emotional flow is clear and relatable.
            4. Describe it as a scene, without analysis or explanation.
            5. Use common American names and titles for the characters.
            Begin your response with "New Situation:" and naturally weave the situation and the descriptive scene together.

            Core Norm:
            {norm}

            Situation: {s}
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

    # Save dataframe to CSV
    df = pd.DataFrame(all_data)
    output_csv = os.path.join(OUTPUT_DIR, "total_norm_scenario_eng.csv")
    output_pkl = os.path.join(OUTPUT_DIR, "total_norm_scenario_eng.pkl")

    df.to_csv(output_csv, index=False)
    with open(output_pkl, "wb") as f:
        pickle.dump(all_data, f, protocol=pickle.HIGHEST_PROTOCOL)
