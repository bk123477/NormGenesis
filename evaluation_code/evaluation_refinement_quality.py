'''
Evaluation Refinement Quality

Model Configuration: gpt-4o-mini
Author: 
    Minki Hong (⚠️ Contact Me: jackyh1@dgu.ac.kr)
    Jangho Choi (⚠️ Contact Me: 2025120382@dgu.ac.kr)
'''

# import libraries
import os
import pandas as pd
import time
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
import json
from tqdm import tqdm

# Setting API
client = OpenAI(api_key=os.getenv("YOUR_OPEN_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"
temperature=0

# Build message
def build_message(prompt_text: str):
    return [
        {"role": "system", "content": "Respond ONLY with valid JSON. Do NOT add commentary."},
        {"role": "user", "content": prompt_text.strip()}
    ]

# Task relevance template
TASK_RELEVANCE_PROMPT = """
You are a domain expert who evaluates ONLY *Task Relevance*—
how well each text aligns with the given Social Norm.
Ignore grammar or style.

### Inputs
Social Norm:
{social_norm}

Initial Text:
{initial}

Refined Text:
{refined}

### Scoring
Give each text an integer score 1-5  
(1 = completely unrelated, 5 = perfectly aligned).

### Output (JSON ONLY)
{{
    "criterion": "Task Relevance",
    "initial_score": <int>,
    "refined_score": <int>,
    "explanation_initial": "<≤100 words>",
    "explanation_refined": "<≤100 words>"
}}
"""

# Linguistic quality template
LINGUISTIC_QUALITY_PROMPT = """
You are a professional copy-editor judging ONLY *Linguistic Quality*—
grammar, fluency, and naturalness. Ignore meaning preservation.

### Inputs
Initial Text:
{initial}

Refined Text:
{refined}

### Scoring
1-5  (1 = very poor language, 5 = native-level fluent).

### Output (JSON ONLY)
{{
    "criterion": "Linguistic Quality",
    "initial_score": <int>,
    "refined_score": <int>,
    "explanation_initial": "<≤100 words>",
    "explanation_refined": "<≤100 words>"
}}
"""

# Semantic preservation template
SEMANTIC_PRESERVATION_PROMPT = """
You are a bilingual reviewer judging ONLY *Semantic Preservation*—
how faithfully the Refined text keeps the original meaning and intent
of the Initial text. Ignore style and social-norm fit.

### Inputs
Initial Text:
{initial}

Refined Text:
{refined}

### Scoring
1-5  (1 = meaning lost / contradictory, 5 = meaning identical).

### Output (JSON ONLY)
{{
    "criterion": "Semantic Preservation",
    "score": <int>,
    "explanation": "<≤120 words>"
}}
"""

# Evaluate each criteria
def evaluation(social_norm: str, initial: str, refined: str, model=MODEL):
    task_relevance_prompt_filled = TASK_RELEVANCE_PROMPT.format(
        social_norm=social_norm,
        initial=initial,
        refined=refined
    )
    task_relevance_messages = build_message(task_relevance_prompt_filled)

    linguistic_quality_prompt_filled = LINGUISTIC_QUALITY_PROMPT.format(
        social_norm=social_norm,
        initial=initial,
        refined=refined
    )
    linguistic_quality_messages = build_message(linguistic_quality_prompt_filled)

    semantic_preservation_prompt_filled = SEMANTIC_PRESERVATION_PROMPT.format(
        social_norm=social_norm,
        initial=initial,
        refined=refined
    )
    semantic_preservation_messages = build_message(semantic_preservation_prompt_filled)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=f'TASK RELEVANCE: {task_relevance_messages}\nLINGUISTIC QUALITY: {linguistic_quality_messages}\nSEMANTIC PRESERVATION: {semantic_preservation_messages}'
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        return {"error": f"Failed to evaluate: {str(e)}"}


# ‼️ SAVE YOUR EVALUATION RESULTS USING YOUR OWN CODE:
# YOUR CODE:
