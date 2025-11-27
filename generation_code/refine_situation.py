'''
Module 3: Exemplar-based Refinement

Model Configuration: gpt-4.1
Author: 
    Minki Hong (⚠️ Contact Me: jackyh1@dgu.ac.kr)
    Jangho Choi (⚠️ Contact Me: 2025120382@dgu.ac.kr)
'''

# Import libraries
import os
import pandas as pd
import time
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Setting API
client = OpenAI(api_key=os.getenv("YOUR_OPEN_API_KEY"))
MODEL = "gpt-4.1"
TEMPERATURE = 0.7
MAX_TOKENS = 1024
OUTPUT_DIR = "YOUR_PATH"
INPUT_PATH = "YOUR_PATH_NEEDS_TO_REFINE"

df = pd.read_excel(INPUT_PATH).reset_index(drop=True)

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
        print(f"❗ API 호출 실패: {e}")

# Parse GPT response
def parse_gpt_output(response_text):
    if "[Refined Situation]" in response_text:
        parts = response_text.split("[Refined Situation]")
        scenario = parts[0].replace("[Refined Scenario]", "").strip()
        situation = parts[1].strip()
        return scenario, situation
    else:
        return response_text.strip(), ""

# Insert exemplar based on expert's sample.


# Generate refined situation
def refined_situation(category, norm, scenario, situation):
    system_role = f"""
{'YOUR EXEMPLAR'}
"""
    prompt = f"""
    Norm Category:
    {category}

    Detailed Norm:
    {norm}

    Scenario:
    {scenario}

    Situation:
    {situation}

    Please make sure that the explanation is in English and the conversation is in Chinese in the scenario and situation.
    Keep the form of existing scenarios and situations.
    [Refined Scenario]:
    [Refined Situation]:
    """
    messages = [{"role": "system", "content": system_role},{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.8,
        max_tokens=MAX_TOKENS
    )
    return parse_gpt_output(response.choices[0].message.content)

# Generate dataset
refined_scenarios = []
refined_situations = []

for i in range(len(df)):
    category = df.loc[i, 'Category']
    norm = df.loc[i, 'Norm']
    scenario = df.loc[i, 'Scenario']
    situation = df.loc[i, 'Situation']
    r_scenario, r_situation = refined_situation(category, norm, scenario, situation)
    refined_scenarios.append(r_scenario)
    refined_situations.append(r_situation)

clean_df = pd.DataFrame({
    'Category': df['Category'].values,
    'Norm': df['Norm'].values,
    'Scenario': df['Scenario'].values,
    'Situation': df['Situation'].values,
    'Refined_Scenario': refined_scenarios,
    'Refined_Situation': refined_situations
})

clean_df.to_excel("YOUR_PATH", index=False)